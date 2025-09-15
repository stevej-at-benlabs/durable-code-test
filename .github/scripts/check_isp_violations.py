#!/usr/bin/env python3
"""
Interface Segregation Principle (ISP) Violation Checker

This script analyzes code changes for violations of the Interface Segregation Principle using Claude AI.
The ISP states that clients should not be forced to depend on interfaces they don't use.
No class should be forced to implement methods it doesn't need.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

import anthropic
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ISPViolation:
    """Represents a potential ISP violation in the code."""
    file: str
    line_range: str
    severity: str  # high, medium, low
    description: str
    suggestion: str
    code_snippet: str
    interface_name: Optional[str] = None
    unused_methods: Optional[List[str]] = None


@dataclass
class AnalysisResult:
    """Results of the ISP analysis."""
    violations: List[ISPViolation]
    summary: str
    severity: str  # overall severity
    comment: str  # formatted comment for PR


class ISPAnalyzer:
    """Analyzes code changes for Interface Segregation Principle violations using Claude AI."""

    def __init__(self, api_key: str):
        """Initialize the analyzer with Claude API credentials."""
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 8192

    def get_file_diff(self, base_sha: str, head_sha: str, file_path: str) -> str:
        """Get the diff for a specific file between two commits."""
        try:
            result = subprocess.run(
                ['git', 'diff', f'{base_sha}...{head_sha}', '--', file_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting diff for {file_path}: {e}")
            return ""

    def get_file_content(self, sha: str, file_path: str) -> str:
        """Get the content of a file at a specific commit."""
        try:
            result = subprocess.run(
                ['git', 'show', f'{sha}:{file_path}'],
                capture_output=True,
                text=True,
                check=False  # Don't raise on error (file might be new)
            )
            if result.returncode != 0:
                # File might be new, try to read from current working directory
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except FileNotFoundError:
                    return ""
            return result.stdout
        except Exception as e:
            logger.error(f"Error getting content for {file_path}: {e}")
            return ""

    def analyze_changes(self, base_sha: str, head_sha: str, changed_files: List[str]) -> AnalysisResult:
        """Analyze changes for ISP violations."""
        violations = []

        # Filter for code files only
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cs', '.go', '.rb', '.php', '.cpp', '.c', '.h', '.hpp'}
        code_files = [f for f in changed_files if any(f.endswith(ext) for ext in code_extensions)]

        if not code_files:
            logger.info("No code files to analyze")
            return AnalysisResult(
                violations=[],
                summary="No code files changed",
                severity="none",
                comment="✅ **ISP Check Skipped**: No code files were modified in this PR."
            )

        logger.info(f"Analyzing {len(code_files)} changed files")

        # Limit files to avoid API rate limits
        if len(code_files) > 10:
            logger.warning(f"Too many files ({len(code_files)}). Analyzing only first 10 to avoid rate limits.")
            code_files = code_files[:10]

        # Analyze each file
        for file_path in code_files:
            logger.info(f"Analyzing {file_path}")

            diff = self.get_file_diff(base_sha, head_sha, file_path)
            new_content = self.get_file_content(head_sha, file_path)

            if not new_content:
                continue

            file_violations = self.analyze_file_for_isp(file_path, diff, new_content)
            violations.extend(file_violations)

        # Generate summary and comment
        severity = self.calculate_overall_severity(violations)
        summary = self.generate_summary(violations)
        comment = self.format_pr_comment(violations, summary, severity)

        return AnalysisResult(
            violations=violations,
            summary=summary,
            severity=severity,
            comment=comment
        )

    def analyze_file_for_isp(self, file_path: str, diff: str, content: str) -> List[ISPViolation]:
        """Analyze a single file for ISP violations using Claude AI."""

        prompt = f"""Analyze this code for violations of the Interface Segregation Principle (ISP).

The ISP states that:
1. Clients should not be forced to depend on interfaces they don't use
2. Interfaces should be focused and cohesive
3. Large interfaces should be split into smaller, more specific ones
4. No class should be forced to implement methods it doesn't need

Common ISP violations include:
- Fat interfaces with many unrelated methods
- Classes implementing interfaces but leaving methods empty or throwing NotImplementedError
- Interfaces mixing different concerns (e.g., data access + business logic)
- Classes depending on interface methods they never call
- Abstract base classes with too many abstract methods

File: {file_path}

Diff:
```
{diff[:3000]}  # Limit diff size
```

Full Content:
```
{content[:5000]}  # Limit content size
```

Analyze for ISP violations and return a JSON response with this structure:
{{
  "violations": [
    {{
      "line_range": "lines X-Y",
      "severity": "high|medium|low",
      "description": "Clear description of the ISP violation",
      "suggestion": "Specific suggestion for fixing the violation",
      "code_snippet": "Relevant code showing the violation",
      "interface_name": "Name of the problematic interface/class if applicable",
      "unused_methods": ["list", "of", "unused", "methods"] // if applicable
    }}
  ]
}}

Focus on actual ISP violations, not general code quality issues.
Return an empty violations array if no ISP violations are found.
Be specific about line numbers and provide actionable suggestions."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text if response.content else ""

            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    violations = []

                    for v in result.get('violations', []):
                        violations.append(ISPViolation(
                            file=file_path,
                            line_range=v.get('line_range', 'Unknown'),
                            severity=v.get('severity', 'medium'),
                            description=v.get('description', 'ISP violation detected'),
                            suggestion=v.get('suggestion', 'Consider refactoring'),
                            code_snippet=v.get('code_snippet', ''),
                            interface_name=v.get('interface_name'),
                            unused_methods=v.get('unused_methods')
                        ))

                    return violations
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    return []
            else:
                logger.warning(f"No JSON found in response for {file_path}")
                return []

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []

    def calculate_overall_severity(self, violations: List[ISPViolation]) -> str:
        """Calculate the overall severity based on individual violations."""
        if not violations:
            return "none"

        severities = [v.severity for v in violations]
        if 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        else:
            return 'low'

    def generate_summary(self, violations: List[ISPViolation]) -> str:
        """Generate a summary of the ISP analysis."""
        if not violations:
            return "No ISP violations detected"

        high = sum(1 for v in violations if v.severity == 'high')
        medium = sum(1 for v in violations if v.severity == 'medium')
        low = sum(1 for v in violations if v.severity == 'low')

        parts = []
        if high > 0:
            parts.append(f"{high} high")
        if medium > 0:
            parts.append(f"{medium} medium")
        if low > 0:
            parts.append(f"{low} low")

        return f"Found {len(violations)} ISP violation(s): {', '.join(parts)} severity"

    def format_pr_comment(self, violations: List[ISPViolation], summary: str, severity: str) -> str:
        """Format a comment for the pull request."""
        if not violations:
            return "✅ **ISP Check Passed**: No Interface Segregation Principle violations detected in this PR."

        # Determine emoji based on severity
        emoji = "🔴" if severity == 'high' else "🟡" if severity == 'medium' else "🟢"

        comment = f"""## {emoji} Interface Segregation Principle (ISP) Check

{summary}

---

"""

        # Group violations by file
        files = {}
        for v in violations:
            if v.file not in files:
                files[v.file] = []
            files[v.file].append(v)

        # Format violations by file
        for file_path, file_violations in files.items():
            comment += f"### 📁 `{file_path}`\n\n"

            for v in file_violations:
                severity_emoji = "🔴" if v.severity == 'high' else "🟡" if v.severity == 'medium' else "🟢"
                comment += f"{severity_emoji} **Lines {v.line_range}** - {v.severity.upper()} severity\n\n"
                comment += f"**Issue:** {v.description}\n\n"

                if v.interface_name:
                    comment += f"**Interface:** `{v.interface_name}`\n\n"

                if v.unused_methods:
                    comment += f"**Unused Methods:** {', '.join([f'`{m}`' for m in v.unused_methods])}\n\n"

                if v.code_snippet:
                    comment += f"```\n{v.code_snippet}\n```\n\n"

                comment += f"**Suggestion:** {v.suggestion}\n\n"
                comment += "---\n\n"

        # Add educational footer
        comment += """### 📚 About Interface Segregation Principle

The ISP states that **clients should not be forced to depend on interfaces they don't use**. This promotes:
- Smaller, focused interfaces
- Better separation of concerns
- Reduced coupling between components
- Easier testing and maintenance

**Common solutions:**
- Split large interfaces into smaller, role-specific ones
- Use interface composition instead of inheritance
- Apply the Single Responsibility Principle to interfaces
- Consider using protocol/trait-based design
"""

        return comment


def get_changed_files(base_sha: str, head_sha: str) -> List[str]:
    """Get the list of files changed between two commits."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=ACMRT', f'{base_sha}...{head_sha}'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting changed files: {e}")
        return []


def main():
    """Main entry point for the ISP violation checker."""
    parser = argparse.ArgumentParser(description='Check for Interface Segregation Principle violations')
    parser.add_argument('--base-sha', required=True, help='Base commit SHA')
    parser.add_argument('--head-sha', required=True, help='Head commit SHA')
    parser.add_argument('--pr-number', required=True, help='Pull request number')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')

    args = parser.parse_args()

    # Get API key from environment
    api_key = os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        logger.error("CLAUDE_API_KEY environment variable not set")
        sys.exit(1)

    # Get changed files
    changed_files = get_changed_files(args.base_sha, args.head_sha)
    logger.info(f"Found {len(changed_files)} changed files")

    # Analyze changes
    analyzer = ISPAnalyzer(api_key)
    result = analyzer.analyze_changes(args.base_sha, args.head_sha, changed_files)

    # Save results to file for the GitHub Action to read
    output_file = 'isp_analysis_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'violations': [asdict(v) for v in result.violations],
            'summary': result.summary,
            'severity': result.severity,
            'comment': result.comment
        }, f, indent=2)

    logger.info(f"Analysis complete: {result.summary}")

    # Exit with appropriate code
    if result.severity == 'high':
        sys.exit(1)  # Fail the check for high severity violations
    else:
        sys.exit(0)  # Pass for medium/low/none


if __name__ == '__main__':
    main()
