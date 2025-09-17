#!/usr/bin/env python3
"""
Purpose: Unified reporting system for linting violations
Scope: Provides multiple output formats and filtering capabilities
Overview: This module implements a comprehensive reporting system that can
    format linting violations in multiple output formats (text, JSON, SARIF,
    GitHub Actions). It supports filtering, severity-based formatting,
    and customizable output templates for different use cases.
Dependencies: json for JSON output, typing for type hints
Exports: TextReporter, JSONReporter, SARIFReporter, GitHubActionsReporter
Interfaces: Implements LintReporter interface
Implementation: Strategy pattern for different output formats
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .interfaces import LintReporter, LintViolation, Severity


class TextReporter(LintReporter):
    """Human-readable text output reporter."""

    def __init__(self, show_context: bool = True, show_suggestions: bool = True):
        """Initialize text reporter with display options."""
        self.show_context = show_context
        self.show_suggestions = show_suggestions

    def generate_report(self, violations: List[LintViolation],
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate human-readable text report."""
        if not violations:
            return "✅ No linting violations found!"

        lines = []

        # Add header with summary
        lines.append(self._generate_header(violations, metadata))
        lines.append("")

        # Group violations by file
        violations_by_file = self._group_by_file(violations)

        for file_path, file_violations in violations_by_file.items():
            lines.append(f"📁 {file_path}")
            lines.append("─" * (len(str(file_path)) + 3))

            for violation in sorted(file_violations, key=lambda v: v.line):
                lines.append(self._format_violation(violation))

            lines.append("")

        # Add summary
        lines.append(self._generate_summary(violations))

        return "\n".join(lines)

    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return ['text', 'txt']

    def _generate_header(self, violations: List[LintViolation],
                        metadata: Optional[Dict[str, Any]]) -> str:
        """Generate report header."""
        total = len(violations)
        by_severity = self._count_by_severity(violations)

        header_parts = [
            f"🔍 Design Linting Report",
            f"📊 Found {total} violation{'s' if total != 1 else ''}",
        ]

        if metadata:
            if 'timestamp' in metadata:
                header_parts.append(f"🕒 Generated: {metadata['timestamp']}")
            if 'files_analyzed' in metadata:
                header_parts.append(f"📄 Files analyzed: {metadata['files_analyzed']}")

        severity_parts = []
        if by_severity.get(Severity.ERROR, 0) > 0:
            severity_parts.append(f"❌ {by_severity[Severity.ERROR]} errors")
        if by_severity.get(Severity.WARNING, 0) > 0:
            severity_parts.append(f"⚠️ {by_severity[Severity.WARNING]} warnings")
        if by_severity.get(Severity.INFO, 0) > 0:
            severity_parts.append(f"ℹ️ {by_severity[Severity.INFO]} info")

        if severity_parts:
            header_parts.append(f"📈 Breakdown: {', '.join(severity_parts)}")

        return "\n".join(header_parts)

    def _format_violation(self, violation: LintViolation) -> str:
        """Format a single violation for text output."""
        severity_icon = self._get_severity_icon(violation.severity)

        main_line = (f"  {severity_icon} Line {violation.line}:{violation.column} "
                    f"[{violation.rule_id}] {violation.message}")

        lines = [main_line]

        if self.show_context and violation.description:
            lines.append(f"    📝 {violation.description}")

        if self.show_suggestions and violation.suggestion:
            lines.append(f"    💡 Suggestion: {violation.suggestion}")

        return "\n".join(lines)

    def _get_severity_icon(self, severity: Severity) -> str:
        """Get icon for severity level."""
        icons = {
            Severity.ERROR: "❌",
            Severity.WARNING: "⚠️",
            Severity.INFO: "ℹ️"
        }
        return icons.get(severity, "❓")

    def _group_by_file(self, violations: List[LintViolation]) -> Dict[str, List[LintViolation]]:
        """Group violations by file path."""
        groups = {}
        for violation in violations:
            file_path = violation.file_path
            if file_path not in groups:
                groups[file_path] = []
            groups[file_path].append(violation)
        return groups

    def _count_by_severity(self, violations: List[LintViolation]) -> Dict[Severity, int]:
        """Count violations by severity."""
        counts = {Severity.ERROR: 0, Severity.WARNING: 0, Severity.INFO: 0}
        for violation in violations:
            counts[violation.severity] += 1
        return counts

    def _generate_summary(self, violations: List[LintViolation]) -> str:
        """Generate summary statistics."""
        total_files = len(set(v.file_path for v in violations))
        total_rules = len(set(v.rule_id for v in violations))
        by_severity = self._count_by_severity(violations)

        summary_lines = [
            "📋 Summary:",
            f"  • Total violations: {len(violations)}",
            f"  • Files affected: {total_files}",
            f"  • Rules triggered: {total_rules}",
        ]

        if by_severity[Severity.ERROR] > 0:
            summary_lines.append(f"  • Critical issues requiring immediate attention: {by_severity[Severity.ERROR]}")

        return "\n".join(summary_lines)


class JSONReporter(LintReporter):
    """JSON output reporter for programmatic consumption."""

    def __init__(self, pretty_print: bool = True):
        """Initialize JSON reporter."""
        self.pretty_print = pretty_print

    def generate_report(self, violations: List[LintViolation],
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate JSON report."""
        report_data = {
            'metadata': metadata or {},
            'summary': self._generate_summary(violations),
            'violations': [v.to_dict() for v in violations]
        }

        if self.pretty_print:
            return json.dumps(report_data, indent=2, default=str)
        else:
            return json.dumps(report_data, default=str)

    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return ['json']

    def _generate_summary(self, violations: List[LintViolation]) -> Dict[str, Any]:
        """Generate summary statistics."""
        by_severity = {}
        by_rule = {}
        by_file = {}

        for violation in violations:
            # Count by severity
            sev_key = violation.severity.value
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1

            # Count by rule
            by_rule[violation.rule_id] = by_rule.get(violation.rule_id, 0) + 1

            # Count by file
            by_file[violation.file_path] = by_file.get(violation.file_path, 0) + 1

        return {
            'total_violations': len(violations),
            'total_files': len(by_file),
            'total_rules_triggered': len(by_rule),
            'by_severity': by_severity,
            'by_rule': by_rule,
            'by_file': by_file
        }


class SARIFReporter(LintReporter):
    """SARIF (Static Analysis Results Interchange Format) reporter."""

    def generate_report(self, violations: List[LintViolation],
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate SARIF format report."""
        sarif_data = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "design-linters",
                            "version": metadata.get('version', '1.0.0') if metadata else '1.0.0',
                            "informationUri": "https://github.com/your-org/design-linters",
                            "rules": self._generate_rule_definitions(violations)
                        }
                    },
                    "results": [self._violation_to_sarif(v) for v in violations]
                }
            ]
        }

        return json.dumps(sarif_data, indent=2)

    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return ['sarif']

    def _generate_rule_definitions(self, violations: List[LintViolation]) -> List[Dict[str, Any]]:
        """Generate SARIF rule definitions."""
        rules_seen = {}
        for violation in violations:
            if violation.rule_id not in rules_seen:
                rules_seen[violation.rule_id] = {
                    "id": violation.rule_id,
                    "shortDescription": {"text": violation.message},
                    "fullDescription": {"text": violation.description},
                    "defaultConfiguration": {
                        "level": self._severity_to_sarif_level(violation.severity)
                    }
                }
        return list(rules_seen.values())

    def _violation_to_sarif(self, violation: LintViolation) -> Dict[str, Any]:
        """Convert violation to SARIF result format."""
        return {
            "ruleId": violation.rule_id,
            "level": self._severity_to_sarif_level(violation.severity),
            "message": {"text": violation.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": violation.file_path},
                        "region": {
                            "startLine": violation.line,
                            "startColumn": violation.column
                        }
                    }
                }
            ]
        }

    def _severity_to_sarif_level(self, severity: Severity) -> str:
        """Convert our severity to SARIF level."""
        mapping = {
            Severity.ERROR: "error",
            Severity.WARNING: "warning",
            Severity.INFO: "note"
        }
        return mapping.get(severity, "note")


class GitHubActionsReporter(LintReporter):
    """Reporter for GitHub Actions workflow annotations."""

    def generate_report(self, violations: List[LintViolation],
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate GitHub Actions annotations format."""
        annotations = []

        for violation in violations:
            annotation_type = self._severity_to_gh_type(violation.severity)
            file_path = violation.file_path

            annotation = (f"::{annotation_type} file={file_path},"
                         f"line={violation.line},col={violation.column},"
                         f"title={violation.rule_id}::{violation.message}")

            annotations.append(annotation)

        return "\n".join(annotations)

    def get_supported_formats(self) -> List[str]:
        """Get supported output formats."""
        return ['github', 'gh-actions']

    def _severity_to_gh_type(self, severity: Severity) -> str:
        """Convert severity to GitHub Actions annotation type."""
        mapping = {
            Severity.ERROR: "error",
            Severity.WARNING: "warning",
            Severity.INFO: "notice"
        }
        return mapping.get(severity, "notice")


class ReporterFactory:
    """Factory for creating appropriate reporters."""

    @staticmethod
    def create_reporter(format_name: str, **kwargs) -> LintReporter:
        """Create reporter for specified format."""
        format_map = {
            'text': TextReporter,
            'txt': TextReporter,
            'json': JSONReporter,
            'sarif': SARIFReporter,
            'github': GitHubActionsReporter,
            'gh-actions': GitHubActionsReporter,
        }

        reporter_class = format_map.get(format_name.lower())
        if not reporter_class:
            raise ValueError(f"Unsupported format: {format_name}")

        return reporter_class(**kwargs)

    @staticmethod
    def get_available_formats() -> List[str]:
        """Get list of available output formats."""
        return ['text', 'json', 'sarif', 'github']
