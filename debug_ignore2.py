#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

import tempfile
import ast
from pathlib import Path
from design_linters.framework.interfaces import should_ignore_node

# Create test file with magic number and ignore directive
test_code = '''
def calculate():
    return 42  # design-lint: ignore[literals.magic-number]
'''

print("=== Test Code ===")
print(repr(test_code))
print("\n=== Manual AST Analysis ===")

tree = ast.parse(test_code)
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and node.value == 42:
        print(f"Found constant node: {node.value} on line {node.lineno}")
        print(f"Node type: {type(node)}")

        # Test the should_ignore_node function
        result = should_ignore_node(node, test_code, 'literals.magic-number')
        print(f"should_ignore_node(node, test_code, 'literals.magic-number') = {result}")

        # Let's debug the function step by step
        lines = test_code.split('\n')
        print(f"Lines: {lines}")
        print(f"Line {node.lineno}: {repr(lines[node.lineno - 1])}")

        # Check if our pattern matching works
        line_content = lines[node.lineno - 1]
        if '# design-lint: ignore[' in line_content:
            print("Found ignore directive in line")

            # Test pattern extraction
            from design_linters.framework.interfaces import _extract_ignore_pattern, _matches_rule_pattern
            pattern = _extract_ignore_pattern(line_content, 'ignore')
            print(f"Extracted pattern: {pattern}")

            if pattern:
                matches = _matches_rule_pattern('literals.magic-number', pattern)
                print(f"Pattern matches rule: {matches}")
        break

print("\n=== Now test with file ===")

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = Path(f.name)

try:
    # Test reading the file and checking ignores
    with open(test_file, 'r') as f:
        file_content = f.read()

    print(f"File content: {repr(file_content)}")

    tree = ast.parse(file_content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == 42:
            result = should_ignore_node(node, file_content, 'literals.magic-number')
            print(f"should_ignore_node with file content: {result}")
            break

finally:
    import os
    os.unlink(test_file)
