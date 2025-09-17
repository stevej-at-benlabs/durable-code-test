#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

import tempfile
from pathlib import Path
from design_linters.framework.analyzer import PythonAnalyzer, DefaultLintOrchestrator
from design_linters.framework.rule_registry import DefaultRuleRegistry
from design_linters.rules.literals.magic_number_rules import MagicNumberRule

# Create test file with magic number and ignore directive
test_code = '''
def calculate():
    return 42  # design-lint: ignore[literals.magic-number]
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = Path(f.name)

try:
    # Set up the linter
    registry = DefaultRuleRegistry()
    analyzer = PythonAnalyzer()
    orchestrator = DefaultLintOrchestrator(
        rule_registry=registry,
        analyzers={'.py': analyzer}
    )
    registry.register_rule(MagicNumberRule())

    # Analyze the file
    print("=== Test Code ===")
    print(test_code)
    print("\n=== Analysis ===")

    # First, let's see what the analyzer produces
    context = analyzer.analyze_file(test_file)
    print(f"File path: {context.file_path}")
    print(f"File content: {repr(context.file_content)}")
    print(f"File ignores: {context.file_ignores}")
    print(f"Line ignores: {context.line_ignores}")
    print(f"Ignore next line: {context.ignore_next_line}")

    # Now let's run the linter
    violations = orchestrator.lint_file(test_file)
    print(f"\n=== Violations ===")
    for v in violations:
        print(f"Rule: {v.rule_id}, Line: {v.line}, Message: {v.message}")

    # Test the ignore functions directly
    print(f"\n=== Direct Function Tests ===")
    from design_linters.framework.interfaces import should_ignore_node, has_file_level_ignore
    import ast

    tree = ast.parse(test_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == 42:
            print(f"Found magic number node on line {node.lineno}")
            result = should_ignore_node(node, test_code, 'literals.magic-number')
            print(f"should_ignore_node result: {result}")
            break

    file_ignore_result = has_file_level_ignore(test_code, 'literals.magic-number')
    print(f"has_file_level_ignore result: {file_ignore_result}")

finally:
    import os
    os.unlink(test_file)
