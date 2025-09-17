#!/usr/bin/env python3
"""
Purpose: Pluggable design linter framework package initialization
Scope: Exports main framework classes and provides unified API
Overview: This module provides the public API for the pluggable design linter
    framework. It enables a rule-based architecture where different design
    principles can be implemented as pluggable rules with unified reporting,
    configuration management, and execution orchestration.
Dependencies: All framework submodules
Exports: Core framework classes and factory functions
Interfaces: Unified API for framework consumers
Implementation: Plugin architecture with dependency injection support
"""

# Core interfaces
from .interfaces import (
    LintRule,
    ASTLintRule,
    FileBasedLintRule,
    LintViolation,
    LintContext,
    LintReporter,
    LintAnalyzer,
    LintOrchestrator,
    RuleRegistry,
    ConfigurationProvider,
    Severity
)

# Rule management
from .rule_registry import (
    DefaultRuleRegistry,
    CategorizedRuleRegistry,
    RuleDiscoveryService
)

# Reporting system
from .reporters import (
    TextReporter,
    JSONReporter,
    SARIFReporter,
    GitHubActionsReporter,
    ReporterFactory
)

# Analysis and orchestration
from .analyzer import (
    PythonAnalyzer,
    DefaultLintOrchestrator,
    ContextualASTVisitor,
    LintResults
)

# Main public API
__all__ = [
    # Core interfaces
    'LintRule',
    'ASTLintRule',
    'FileBasedLintRule',
    'LintViolation',
    'LintContext',
    'LintReporter',
    'LintAnalyzer',
    'LintOrchestrator',
    'RuleRegistry',
    'Severity',

    # Rule management
    'DefaultRuleRegistry',
    'CategorizedRuleRegistry',
    'RuleDiscoveryService',

    # Reporting
    'TextReporter',
    'JSONReporter',
    'SARIFReporter',
    'GitHubActionsReporter',
    'ReporterFactory',

    # Analysis
    'PythonAnalyzer',
    'DefaultLintOrchestrator',
    'LintResults',

    # Factory functions
    'create_orchestrator',
    'create_rule_registry',
    'discover_rules'
]


def create_orchestrator(rule_packages: list[str] = None,
                       config: dict = None) -> LintOrchestrator:
    """Create a fully configured linter orchestrator.

    Args:
        rule_packages: List of package names to discover rules from
        config: Configuration dictionary for rules and analysis

    Returns:
        Configured LintOrchestrator instance
    """
    # Create rule registry and discover rules
    registry = DefaultRuleRegistry()

    if rule_packages:
        discovery = RuleDiscoveryService()
        for package in rule_packages:
            try:
                discovery.discover_from_package(package, registry)
            except ImportError:
                pass  # Package not available, skip

    # Create analyzers
    analyzers = {'python': PythonAnalyzer()}

    # Create reporters
    reporters = {
        'text': TextReporter(),
        'json': JSONReporter(),
        'sarif': SARIFReporter(),
        'github': GitHubActionsReporter()
    }

    return DefaultLintOrchestrator(
        rule_registry=registry,
        analyzers=analyzers,
        reporters=reporters
    )


def create_rule_registry(auto_discover: bool = True) -> RuleRegistry:
    """Create and optionally populate a rule registry.

    Args:
        auto_discover: Whether to automatically discover rules from known packages

    Returns:
        Configured RuleRegistry instance
    """
    registry = CategorizedRuleRegistry()

    if auto_discover:
        # Try to discover rules from known rule packages
        known_packages = [
            'tools.design_linters.rules.solid',
            'tools.design_linters.rules.complexity',
            'tools.design_linters.rules.style'
        ]

        discovery = RuleDiscoveryService()
        for package in known_packages:
            try:
                discovery.discover_from_package(package, registry)
            except ImportError:
                pass  # Package not available, skip

    return registry


def discover_rules(*package_paths: str) -> int:
    """Discover rules from specified packages.

    Args:
        package_paths: Package paths to discover rules from

    Returns:
        Number of rules discovered
    """
    registry = DefaultRuleRegistry()
    discovery = RuleDiscoveryService()

    total_discovered = 0
    for package_path in package_paths:
        try:
            count = discovery.discover_from_package(package_path, registry)
            total_discovered += count
        except ImportError:
            pass

    return total_discovered


# Convenience function for quick linting
def lint_files(file_paths: list[str],
              rule_packages: list[str] = None,
              output_format: str = 'text',
              config: dict = None) -> str:
    """Convenience function to lint files and get formatted output.

    Args:
        file_paths: List of file paths to lint
        rule_packages: List of rule packages to use
        output_format: Output format ('text', 'json', 'sarif', 'github')
        config: Configuration for rules and analysis

    Returns:
        Formatted linting report
    """
    from pathlib import Path

    orchestrator = create_orchestrator(rule_packages, config)
    all_violations = []

    for file_path in file_paths:
        path = Path(file_path)
        if path.is_file():
            violations = orchestrator.lint_file(path, config)
            all_violations.extend(violations)
        elif path.is_dir():
            violations = orchestrator.lint_directory(path, config)
            all_violations.extend(violations)

    return orchestrator.generate_report(all_violations, output_format)
