#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

import tempfile
import ast
from pathlib import Path
from design_linters.framework.analyzer import PythonAnalyzer
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
    # Set up components
    analyzer = PythonAnalyzer()
    rule = MagicNumberRule()

    # Analyze the file to get context
    context = analyzer.analyze_file(test_file)

    print("=== Context Analysis ===")
    print(f"File path: {context.file_path}")
    print(f"Line ignores: {context.line_ignores}")
    print(f"File content length: {len(context.file_content) if context.file_content else 0}")

    # Run the rule directly on the context
    print("\n=== Running Rule Directly ===")
    violations = rule.check(context)
    print(f"Violations from rule.check(): {len(violations)}")
    for v in violations:
        print(f"  - {v.rule_id} at line {v.line}: {v.message}")

    # Let's monkey patch to add debug prints
    print("\n=== Adding Debug Patches ===")

    from design_linters.framework.interfaces import should_ignore_node

    original_should_ignore_node = should_ignore_node

    def debug_should_ignore_node(node, file_content, rule_id):
        result = original_should_ignore_node(node, file_content, rule_id)
        if hasattr(node, 'lineno') and hasattr(node, 'value'):
            print(f"DEBUG: should_ignore_node(line={node.lineno}, value={node.value}, rule={rule_id}) = {result}")
        return result

    # Patch the function
    import design_linters.framework.interfaces
    design_linters.framework.interfaces.should_ignore_node = debug_should_ignore_node

    # Run again with debug
    print("\n=== Running Rule with Debug ===")
    violations = rule.check(context)
    print(f"Violations with debug: {len(violations)}")

finally:
    import os
    os.unlink(test_file)
