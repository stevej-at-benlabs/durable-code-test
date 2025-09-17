#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/stevejackson/Projects/durable-code-test/tools')

import tempfile
from pathlib import Path
from design_linters.framework.analyzer import PythonAnalyzer, DefaultLintOrchestrator
from design_linters.framework.rule_registry import DefaultRuleRegistry
from design_linters.rules.literals.magic_number_rules import MagicNumberRule, MagicComplexRule

# Exactly mimic the test setup
registry = DefaultRuleRegistry()
analyzer = PythonAnalyzer()
orchestrator = DefaultLintOrchestrator(
    rule_registry=registry,
    analyzers={'.py': analyzer}
)

# Register literal rules
registry.register_rule(MagicNumberRule())
registry.register_rule(MagicComplexRule())

# Create test file with magic number and ignore directive
test_code = '''
def calculate():
    return 42  # design-lint: ignore[literals.magic-number]
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    test_file = Path(f.name)

try:
    print("=== Test Code ===")
    print(repr(test_code))

    print("\n=== Using Orchestrator (like test) ===")
    violations = orchestrator.lint_file(test_file)
    print(f"Violations from orchestrator: {len(violations)}")
    for v in violations:
        print(f"  - {v.rule_id} at line {v.line}: {v.message}")

    print(f"\n=== Analyzing Context ===")
    context = analyzer.analyze_file(test_file)
    print(f"Line ignores: {context.line_ignores}")

    print(f"\n=== Testing Rule Directly ===")
    rule = MagicNumberRule()
    direct_violations = rule.check(context)
    print(f"Direct rule violations: {len(direct_violations)}")

finally:
    import os
    os.unlink(test_file)
