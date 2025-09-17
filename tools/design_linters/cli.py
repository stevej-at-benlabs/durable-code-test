#!/usr/bin/env python3
"""
Purpose: Unified CLI for the pluggable design linter framework
Scope: Replaces individual linter CLIs with a single, extensible interface
Overview: This module provides a unified command-line interface that replaces
    all the individual linter CLIs (srp_analyzer.py, magic_number_detector.py,
    print_statement_linter.py, etc.) with a single, extensible tool that uses
    the pluggable framework architecture.
Dependencies: Framework components, argparse for CLI, pathlib for file operations
Exports: Main CLI interface and configuration management
Interfaces: Provides backward compatibility with existing linter usage
Implementation: Uses framework orchestrator with automatic rule discovery
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .framework import (
    create_orchestrator,
    create_rule_registry,
    LintViolation,
    Severity,
    ReporterFactory
)


class DesignLinterCLI:
    """Unified command-line interface for design linting."""

    def __init__(self):
        """Initialize CLI with framework components."""
        self.orchestrator = None
        self.logger = logging.getLogger(__name__)

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with provided arguments."""
        if args is None:
            args = sys.argv[1:]

        try:
            parsed_args = self._parse_arguments(args)
            self._setup_logging(parsed_args.verbose)

            # Initialize orchestrator with rule discovery
            self.orchestrator = self._create_orchestrator(parsed_args)

            # Execute linting
            violations = self._execute_linting(parsed_args)

            # Generate and output report
            self._output_results(violations, parsed_args)

            # Return appropriate exit code
            return self._determine_exit_code(violations, parsed_args)

        except KeyboardInterrupt:
            print("\n❌ Linting interrupted by user", file=sys.stderr)
            return 130
        except Exception as e:
            print(f"❌ Error during linting: {e}", file=sys.stderr)
            if parsed_args.verbose if 'parsed_args' in locals() else False:
                import traceback
                traceback.print_exc()
            return 1

    def _parse_arguments(self, args: List[str]) -> argparse.Namespace:
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(
            description='Unified Design Linter - Check code for SOLID principles and style violations',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Lint single file
  design-linter myfile.py

  # Lint directory with specific rules
  design-linter src/ --rules solid.srp.too-many-methods,literals.magic-number

  # Output as JSON
  design-linter src/ --format json

  # Show available rules
  design-linter --list-rules

  # Backward compatibility
  design-linter myfile.py --legacy srp  # Same as old srp_analyzer.py
            """
        )

        # Input files/directories
        parser.add_argument(
            'paths',
            nargs='*',
            help='Files or directories to lint (default: current directory)'
        )

        # Rule selection
        parser.add_argument(
            '--rules',
            help='Comma-separated list of rule IDs to run (default: all enabled rules)'
        )

        parser.add_argument(
            '--exclude-rules',
            help='Comma-separated list of rule IDs to exclude'
        )

        parser.add_argument(
            '--categories',
            help='Comma-separated list of rule categories to run (e.g., solid,style,literals)'
        )

        # Output format
        parser.add_argument(
            '--format',
            choices=['text', 'json', 'sarif', 'github'],
            default='text',
            help='Output format (default: text)'
        )

        parser.add_argument(
            '--output',
            help='Output file (default: stdout)'
        )

        # Severity filtering
        parser.add_argument(
            '--min-severity',
            choices=['error', 'warning', 'info'],
            default='info',
            help='Minimum severity level to report (default: info)'
        )

        # Configuration
        parser.add_argument(
            '--config',
            help='Configuration file path'
        )

        parser.add_argument(
            '--strict',
            action='store_true',
            help='Use strict rule configuration'
        )

        parser.add_argument(
            '--lenient',
            action='store_true',
            help='Use lenient rule configuration'
        )

        # Backward compatibility
        parser.add_argument(
            '--legacy',
            choices=['srp', 'magic', 'print', 'nesting', 'header'],
            help='Run in legacy mode (backward compatibility with old linters)'
        )

        # Utility options
        parser.add_argument(
            '--list-rules',
            action='store_true',
            help='List all available rules and exit'
        )

        parser.add_argument(
            '--list-categories',
            action='store_true',
            help='List all available rule categories and exit'
        )

        # Control options
        parser.add_argument(
            '--fail-on-error',
            action='store_true',
            help='Exit with non-zero code if errors are found'
        )

        parser.add_argument(
            '--recursive',
            action='store_true',
            default=True,
            help='Recursively lint directories (default: True)'
        )

        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )

        return parser.parse_args(args)

    def _setup_logging(self, verbose: bool):
        """Setup logging configuration."""
        level = logging.DEBUG if verbose else logging.WARNING
        logging.basicConfig(
            format='%(levelname)s: %(message)s',
            level=level
        )

    def _create_orchestrator(self, args: argparse.Namespace):
        """Create and configure the linting orchestrator."""
        # Discover rules from known packages
        rule_packages = [
            'design_linters.rules.solid',
            'design_linters.rules.literals',
            'design_linters.rules.style',
            'design_linters.rules.logging'
        ]

        # Load configuration
        config = self._load_configuration(args)

        # Create orchestrator with rule discovery
        orchestrator = create_orchestrator(rule_packages, config)

        if args.list_rules:
            self._list_rules(orchestrator)
            sys.exit(0)

        if args.list_categories:
            self._list_categories(orchestrator)
            sys.exit(0)

        return orchestrator

    def _load_configuration(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Load configuration from file and command line arguments."""
        config = {
            'rules': {},
            'include': ['**/*.py'],
            'exclude': ['__pycache__/**', '.git/**', '.venv/**']
        }

        # Load from config file if specified
        if args.config:
            config.update(self._load_config_file(args.config))

        # Apply command line overrides
        if args.strict:
            config.update(self._get_strict_config())
        elif args.lenient:
            config.update(self._get_lenient_config())

        # Apply legacy mode configuration
        if args.legacy:
            config.update(self._get_legacy_config(args.legacy))

        # Rule filtering
        if args.rules:
            enabled_rules = args.rules.split(',')
            config['rules'] = {rule: {'enabled': True} for rule in enabled_rules}

        if args.exclude_rules:
            excluded_rules = args.exclude_rules.split(',')
            for rule in excluded_rules:
                config['rules'][rule] = {'enabled': False}

        return config

    def _execute_linting(self, args: argparse.Namespace) -> List[LintViolation]:
        """Execute linting on specified paths."""
        paths = args.paths or ['.']
        all_violations = []

        config = self._load_configuration(args)

        for path_str in paths:
            path = Path(path_str)

            if path.is_file():
                violations = self.orchestrator.lint_file(path, config)
                all_violations.extend(violations)
            elif path.is_dir():
                violations = self.orchestrator.lint_directory(path, config, args.recursive)
                all_violations.extend(violations)
            else:
                self.logger.warning(f"Path not found: {path}")

        # Filter by severity
        if hasattr(args, 'min_severity'):
            all_violations = self._filter_by_severity(all_violations, args.min_severity)

        return all_violations

    def _output_results(self, violations: List[LintViolation], args: argparse.Namespace):
        """Output linting results in the specified format."""
        if not violations:
            if args.format == 'text':
                print("✅ No design violations found!")
            return

        # Generate report
        report = self.orchestrator.generate_report(violations, args.format)

        # Output to file or stdout
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            if args.verbose:
                print(f"📁 Report written to {args.output}")
        else:
            print(report)

    def _determine_exit_code(self, violations: List[LintViolation], args: argparse.Namespace) -> int:
        """Determine appropriate exit code."""
        if not args.fail_on_error:
            return 0

        error_count = sum(1 for v in violations if v.severity == Severity.ERROR)
        return 1 if error_count > 0 else 0

    def _list_rules(self, orchestrator):
        """List all available rules."""
        rules = orchestrator.rule_registry.get_all_rules()

        print("📋 Available Rules:")
        print("=" * 50)

        by_category = {}
        for rule in rules:
            for category in rule.categories or ['uncategorized']:
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(rule)

        for category, category_rules in sorted(by_category.items()):
            print(f"\n🏷️  {category.upper()}")
            print("-" * 20)
            for rule in sorted(category_rules, key=lambda r: r.rule_id):
                severity_icon = self._get_severity_icon(rule.severity)
                print(f"  {severity_icon} {rule.rule_id:<30} {rule.rule_name}")
                if hasattr(rule, 'description'):
                    print(f"     {rule.description}")

    def _list_categories(self, orchestrator):
        """List all available rule categories."""
        rules = orchestrator.rule_registry.get_all_rules()
        categories = set()
        for rule in rules:
            categories.update(rule.categories or ['uncategorized'])

        print("🏷️  Available Categories:")
        print("=" * 25)
        for category in sorted(categories):
            category_rules = [r for r in rules if category in (r.categories or ['uncategorized'])]
            print(f"  • {category:<15} ({len(category_rules)} rules)")

    def _filter_by_severity(self, violations: List[LintViolation], min_severity: str) -> List[LintViolation]:
        """Filter violations by minimum severity level."""
        severity_order = {'info': 0, 'warning': 1, 'error': 2}
        min_level = severity_order.get(min_severity, 0)

        return [v for v in violations if severity_order.get(v.severity.value, 0) >= min_level]

    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level."""
        icons = {
            Severity.ERROR: "❌",
            Severity.WARNING: "⚠️",
            Severity.INFO: "ℹ️"
        }
        return icons.get(severity, "❓")

    def _load_config_file(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        import json
        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config file {config_path}: {e}")
            return {}

    def _get_strict_config(self) -> Dict[str, Any]:
        """Get strict rule configuration."""
        return {
            'rules': {
                'solid.srp.too-many-methods': {'config': {'max_methods': 8}},
                'solid.srp.class-too-big': {'config': {'max_class_lines': 100}},
                'literals.magic-number': {'config': {'allowed_numbers': {0, 1}}},
            }
        }

    def _get_lenient_config(self) -> Dict[str, Any]:
        """Get lenient rule configuration."""
        return {
            'rules': {
                'solid.srp.too-many-methods': {'config': {'max_methods': 25}},
                'solid.srp.class-too-big': {'config': {'max_class_lines': 500}},
                'style.print-statement': {'enabled': False},
            }
        }

    def _get_legacy_config(self, legacy_mode: str) -> Dict[str, Any]:
        """Get configuration for legacy mode compatibility."""
        legacy_configs = {
            'srp': {
                'rules': {rule: {'enabled': False} for rule in ['literals.magic-number', 'style.print-statement']},
                'categories': ['solid']
            },
            'magic': {
                'rules': {rule: {'enabled': False} for rule in ['solid.srp.too-many-methods', 'style.print-statement']},
                'categories': ['literals']
            },
            'print': {
                'rules': {rule: {'enabled': False} for rule in ['solid.srp.too-many-methods', 'literals.magic-number']},
                'categories': ['style']
            }
        }
        return legacy_configs.get(legacy_mode, {})


def main():
    """Main entry point for the unified design linter CLI."""
    cli = DesignLinterCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
