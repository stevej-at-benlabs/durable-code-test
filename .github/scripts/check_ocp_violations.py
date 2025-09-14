#!/usr/bin/env python3
"""
Open-Closed Principle (OCP) Violation Checker

This script analyzes code changes for violations of the Open-Closed Principle using Claude AI.
The OCP states that software entities should be open for extension but closed for modification.
"""

import argparse
import json
import os
import subprocess
import sys
from typing import List, Dict, Any, Optional
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
class OCPViolation:
    """Represents a potential OCP violation in the code."""
    file: str
    line_range: str
    severity: str  # high, medium, low
    description: str
    suggestion: str
    code_snippet: str


@dataclass
class AnalysisResult:
    """Results of the OCP analysis."""
    violations: List[OCPViolation]
    summary: str
    severity: str  # overall severity
    comment: str  # formatted comment for PR


class OCPAnalyzer:
    """Analyzes code changes for Open-Closed Principle violations using Claude AI."""

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
        """Analyze changes for OCP violations."""
        violations = []

        # Filter for code files only
        code_extensions = {'.py', '.js', '.ts', '.java', '.cs', '.go', '.rb', '.php', '.cpp', '.c', '.h', '.hpp'}
        code_files = [f for f in changed_files if Path(f).suffix in code_extensions]

        if not code_files:
            logger.info("No code files to analyze")
            return AnalysisResult(
                violations=[],
                summary="No code files changed",
                severity="none",
                comment="✅ **OCP Check Passed**: No code files to analyze."
            )

        # Prepare context for Claude
        file_diffs = {}
        file_contents = {}

        for file_path in code_files:
            diff = self.get_file_diff(base_sha, head_sha, file_path)
            if diff:
                file_diffs[file_path] = diff
                file_contents[file_path] = {
                    'before': self.get_file_content(base_sha, file_path),
                    'after': self.get_file_content(head_sha, file_path)
                }

        if not file_diffs:
            logger.info("No diffs to analyze")
            return AnalysisResult(
                violations=[],
                summary="No changes to analyze",
                severity="none",
                comment="✅ **OCP Check Passed**: No code changes to analyze."
            )

        # Analyze with Claude
        violations = self._analyze_with_claude(file_diffs, file_contents)

        # Determine overall severity
        severity = self._determine_overall_severity(violations)

        # Generate summary and comment
        summary = self._generate_summary(violations)
        comment = self._format_pr_comment(violations, summary, severity)

        return AnalysisResult(
            violations=violations,
            summary=summary,
            severity=severity,
            comment=comment
        )

    def _analyze_with_claude(self, file_diffs: Dict[str, str], file_contents: Dict[str, Dict[str, str]]) -> List[OCPViolation]:
        """Use Claude to analyze the code for OCP violations."""

        # Prepare the prompt
        prompt = self._create_analysis_prompt(file_diffs, file_contents)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.1,
                system="""You are an expert software architect specializing in SOLID principles, particularly the Open-Closed Principle (OCP).

The Open-Closed Principle states: "Software entities (classes, modules, functions, etc.) should be open for extension but closed for modification."

Common OCP violations include:
1. Modifying existing classes/functions to add new functionality instead of extending them
2. Switch/if-else chains that need modification when adding new types
3. Directly modifying concrete implementations instead of using abstractions
4. Hard-coded dependencies that require changes when requirements change
5. Violation of dependency inversion (depending on concretions rather than abstractions)

Your task is to analyze code changes and identify potential OCP violations. Be specific and provide actionable suggestions.

Respond with a JSON array of violations. Each violation should have:
- file: the file path
- line_range: approximate line numbers (e.g., "45-67")
- severity: "high", "medium", or "low"
- description: clear explanation of the violation
- suggestion: specific suggestion for fixing it
- code_snippet: relevant code snippet showing the violation

If no violations are found, return an empty array: []""",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            response_text = response.content[0].text

            # Extract JSON from the response
            try:
                # Try to find JSON array in the response
                import re
                json_match = re.search(r'\[[\s\S]*\]', response_text)
                if json_match:
                    violations_data = json.loads(json_match.group())
                else:
                    violations_data = json.loads(response_text)

                violations = []
                for v in violations_data:
                    violations.append(OCPViolation(
                        file=v.get('file', ''),
                        line_range=v.get('line_range', ''),
                        severity=v.get('severity', 'low'),
                        description=v.get('description', ''),
                        suggestion=v.get('suggestion', ''),
                        code_snippet=v.get('code_snippet', '')
                    ))
                return violations

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {e}")
                logger.error(f"Response was: {response_text}")
                return []

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return []

    def _create_analysis_prompt(self, file_diffs: Dict[str, str], file_contents: Dict[str, Dict[str, str]]) -> str:
        """Create the prompt for Claude analysis."""
        prompt_parts = ["Please analyze the following code changes for Open-Closed Principle violations:\n"]

        for file_path, diff in file_diffs.items():
            prompt_parts.append(f"\n=== File: {file_path} ===\n")
            prompt_parts.append(f"Diff:\n```diff\n{diff}\n```\n")

            if file_path in file_contents:
                contents = file_contents[file_path]
                if contents['after']:
                    # Show a portion of the full file for context
                    lines = contents['after'].split('\n')
                    if len(lines) > 200:
                        # Show first 100 and last 100 lines for context
                        context = '\n'.join(lines[:100]) + '\n...\n' + '\n'.join(lines[-100:])
                    else:
                        context = contents['after']
                    prompt_parts.append(f"Full file content (after changes):\n```\n{context}\n```\n")

        prompt_parts.append("\nAnalyze these changes for OCP violations and return your findings as a JSON array.")

        return ''.join(prompt_parts)

    def _determine_overall_severity(self, violations: List[OCPViolation]) -> str:
        """Determine the overall severity based on individual violations."""
        if not violations:
            return "none"

        severities = [v.severity for v in violations]
        if "high" in severities:
            return "high"
        elif "medium" in severities:
            return "medium"
        elif "low" in severities:
            return "low"
        return "none"

    def _generate_summary(self, violations: List[OCPViolation]) -> str:
        """Generate a summary of the violations."""
        if not violations:
            return "No Open-Closed Principle violations detected."

        high = sum(1 for v in violations if v.severity == "high")
        medium = sum(1 for v in violations if v.severity == "medium")
        low = sum(1 for v in violations if v.severity == "low")

        parts = []
        if high > 0:
            parts.append(f"{high} high")
        if medium > 0:
            parts.append(f"{medium} medium")
        if low > 0:
            parts.append(f"{low} low")

        severity_text = ", ".join(parts)
        return f"Found {len(violations)} potential OCP violation(s): {severity_text} severity."

    def _format_pr_comment(self, violations: List[OCPViolation], summary: str, severity: str) -> str:
        """Format a nice comment for the PR."""
        if not violations:
            return "✅ **OCP Check Passed**: No Open-Closed Principle violations detected in this PR."

        # Determine emoji based on severity
        emoji = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"

        comment_parts = [
            f"{emoji} **Open-Closed Principle Analysis**\n",
            f"{summary}\n",
            "\n---\n\n"
        ]

        # Group violations by file
        by_file = {}
        for v in violations:
            if v.file not in by_file:
                by_file[v.file] = []
            by_file[v.file].append(v)

        for file_path, file_violations in by_file.items():
            comment_parts.append(f"### 📁 `{file_path}`\n\n")

            for v in file_violations:
                severity_badge = "🔴" if v.severity == "high" else "🟡" if v.severity == "medium" else "🟢"
                comment_parts.append(f"{severity_badge} **Lines {v.line_range}** - {v.severity.upper()} severity\n\n")
                comment_parts.append(f"**Issue:** {v.description}\n\n")

                if v.code_snippet:
                    comment_parts.append(f"```\n{v.code_snippet}\n```\n\n")

                comment_parts.append(f"**Suggestion:** {v.suggestion}\n\n")
                comment_parts.append("---\n\n")

        comment_parts.append("\n### 📚 About the Open-Closed Principle\n\n")
        comment_parts.append("The OCP states that software entities should be **open for extension** but **closed for modification**. ")
        comment_parts.append("This means you should be able to add new functionality without changing existing code.\n\n")
        comment_parts.append("**Common solutions:**\n")
        comment_parts.append("- Use abstractions (interfaces, abstract classes)\n")
        comment_parts.append("- Apply Strategy, Template Method, or Factory patterns\n")
        comment_parts.append("- Dependency injection\n")
        comment_parts.append("- Polymorphism over conditionals\n")

        return ''.join(comment_parts)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Check for Open-Closed Principle violations')
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

    # Get list of changed files
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=ACMRT', f'{args.base_sha}...{args.head_sha}'],
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting changed files: {e}")
        sys.exit(1)

    logger.info(f"Analyzing {len(changed_files)} changed files")

    # Analyze changes
    analyzer = OCPAnalyzer(api_key)
    results = analyzer.analyze_changes(args.base_sha, args.head_sha, changed_files)

    # Save results to file
    results_dict = {
        'violations': [asdict(v) for v in results.violations],
        'summary': results.summary,
        'severity': results.severity,
        'comment': results.comment,
        'timestamp': datetime.now().isoformat(),
        'pr_number': args.pr_number,
        'repo': args.repo
    }

    with open('ocp_analysis_results.json', 'w') as f:
        json.dump(results_dict, f, indent=2)

    logger.info(f"Analysis complete: {results.summary}")

    # Exit with appropriate code
    if results.severity == "high":
        sys.exit(1)  # Fail the check for high severity
    else:
        sys.exit(0)  # Pass for medium/low/none


if __name__ == '__main__':
    main()