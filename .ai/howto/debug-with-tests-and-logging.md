# How to Debug with Tests and Logging

## Core Debugging Philosophy

**NEVER create temporary test files or debugging scripts.** All debugging must be done through:

1. **Unit Tests**: Write tests to reproduce and verify fixes
2. **Loguru Logging**: Use structured logging for investigation
3. **Existing Test Infrastructure**: Leverage the comprehensive test suite

## Debugging Workflow

### 1. Reproduce the Issue with a Unit Test

**First Step**: Write a failing test that demonstrates the bug

```python
# test/unit_test/tools/design_linters/test_bug_reproduction.py
import pytest
from pathlib import Path
from tools.design_linters.rules.solid.srp_rules import TooManyMethodsRule

class TestBugReproduction:
    """Test suite for reproducing and verifying bug fixes."""

    def test_reproduce_method_count_bug(self):
        """Reproduce the method counting bug with specific code pattern."""
        # Arrange - Create the exact code that causes the issue
        source_code = '''
class ExampleClass:
    def method_one(self): pass
    def method_two(self): pass
    @property
    def not_a_method(self): pass  # This might be counted incorrectly
    @staticmethod
    def static_method(): pass
        '''

        # Act - Run the rule that's failing
        rule = TooManyMethodsRule({"max_methods": 5})
        violations = rule.check_code(source_code, Path("test_file.py"))

        # Assert - Document the expected vs actual behavior
        # This should fail initially, proving the bug exists
        assert len(violations) == 0, "Property and static methods should not count as regular methods"

    def test_edge_case_that_fails(self):
        """Document the specific edge case causing the failure."""
        # This test should fail, proving the bug
        # After fixing, it should pass
        pass
```

### 2. Add Loguru Logging for Investigation

**Use Loguru for structured debugging**:

```python
from loguru import logger

class TooManyMethodsRule(BaseRule):
    def check_node(self, node: ast.ClassDef, file_path: Path, source_lines: list[str]) -> list[LintViolation]:
        """Check class for too many methods."""
        logger.debug("Checking class: {class_name} in {file}",
                    class_name=node.name, file=file_path)

        methods = self._count_methods(node)
        logger.debug("Found {count} methods in class {class_name}: {method_names}",
                    count=len(methods),
                    class_name=node.name,
                    method_names=[m.name for m in methods])

        if len(methods) > self.max_methods:
            logger.warning("Class {class_name} exceeds method limit: {count} > {limit}",
                          class_name=node.name, count=len(methods), limit=self.max_methods)
            return [self._create_violation(node, file_path, source_lines, len(methods))]

        return []

    def _count_methods(self, class_node: ast.ClassDef) -> list[ast.FunctionDef]:
        """Count methods, excluding properties and static methods."""
        methods = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                # Debug logging to understand what we're counting
                decorators = [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list]
                logger.debug("Examining method {method}: decorators={decorators}",
                           method=node.name, decorators=decorators)

                # Skip properties and static methods
                if not any(dec in ['property', 'staticmethod', 'classmethod'] for dec in decorators):
                    methods.append(node)
                    logger.debug("Counting method: {method}", method=node.name)
                else:
                    logger.debug("Skipping decorated method: {method}", method=node.name)

        return methods
```

### 3. Run Tests to Observe Logging

```bash
# Run specific test with debug logging
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_bug_reproduction.py::TestBugReproduction::test_reproduce_method_count_bug -v -s --log-cli-level=DEBUG

# Run with Loguru configuration
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_bug_reproduction.py -v -s --capture=no
```

### 4. Fix the Issue Based on Test and Logs

**Implement the fix**:

```python
def _count_methods(self, class_node: ast.ClassDef) -> list[ast.FunctionDef]:
    """Count methods, properly excluding decorators."""
    methods = []

    for node in class_node.body:  # Only direct children, not all descendants
        if isinstance(node, ast.FunctionDef):
            # Check for exclusion decorators
            is_property = any(
                isinstance(d, ast.Name) and d.id == 'property'
                for d in node.decorator_list
            )
            is_static = any(
                isinstance(d, ast.Name) and d.id in ['staticmethod', 'classmethod']
                for d in node.decorator_list
            )

            if not (is_property or is_static):
                methods.append(node)
                logger.debug("Counted method: {method}", method=node.name)
            else:
                logger.debug("Excluded decorated method: {method}", method=node.name)

    return methods
```

### 5. Verify Fix with Tests

```bash
# Run the reproduction test - should now pass
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_bug_reproduction.py::TestBugReproduction::test_reproduce_method_count_bug -v

# Run full test suite to ensure no regressions
make test-unit
```

## Debugging Best Practices

### Test-Driven Debugging

**Always follow this pattern**:

1. **Red**: Write a failing test that reproduces the bug
2. **Green**: Implement minimal fix to make test pass
3. **Refactor**: Clean up code while keeping tests passing
4. **Verify**: Run full test suite to ensure no regressions

```python
class TestDebugExample:
    """Example of proper debugging with tests."""

    def test_bug_reproduction_step_1_failing(self):
        """Step 1: Reproduce the exact failure condition."""
        # This test should fail initially
        result = buggy_function("problematic_input")
        assert result == "expected_output"  # Will fail, proving bug exists

    def test_bug_fix_verification_step_2(self):
        """Step 2: Verify the fix works correctly."""
        # After implementing fix, this should pass
        result = fixed_function("problematic_input")
        assert result == "expected_output"

    def test_edge_cases_step_3(self):
        """Step 3: Test edge cases to prevent regressions."""
        # Test boundary conditions
        assert fixed_function("") == ""
        assert fixed_function(None) is None
        # etc.
```

### Structured Logging with Loguru

**Use contextual logging**:

```python
from loguru import logger

class DesignLinterRule:
    def __init__(self, config: dict):
        self.config = config
        # Log configuration at initialization
        logger.debug("Initializing rule {rule_name} with config: {config}",
                    rule_name=self.__class__.__name__, config=config)

    def check_file(self, file_path: Path) -> list[LintViolation]:
        """Check file for violations."""
        logger.info("Analyzing file: {file}", file=file_path)

        try:
            with open(file_path, 'r') as f:
                source = f.read()

            violations = self._analyze_source(source, file_path)

            logger.info("Analysis complete for {file}: {count} violations found",
                       file=file_path, count=len(violations))

            return violations

        except Exception as e:
            logger.error("Failed to analyze {file}: {error}",
                        file=file_path, error=str(e))
            raise

    def _analyze_source(self, source: str, file_path: Path) -> list[LintViolation]:
        """Analyze source code for violations."""
        violations = []

        # Log parsing step
        logger.debug("Parsing AST for {file}", file=file_path)
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.warning("Syntax error in {file}: {error}", file=file_path, error=str(e))
            return []

        # Log analysis steps
        for node in ast.walk(tree):
            if self._should_check_node(node):
                logger.debug("Checking {node_type} at line {line}",
                           node_type=type(node).__name__, line=getattr(node, 'lineno', 'unknown'))

                node_violations = self._check_node(node, file_path)
                violations.extend(node_violations)

                if node_violations:
                    logger.debug("Found {count} violations in {node_type}",
                               count=len(node_violations), node_type=type(node).__name__)

        return violations
```

### Logging Configuration for Debugging

```python
# In test files or debugging context
import sys
from loguru import logger

# Configure detailed logging for debugging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    colorize=True
)

# For specific debugging sessions, add file logging
logger.add(
    "debug.log",
    level="DEBUG",
    rotation="1 MB",
    retention="1 day",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
)
```

## Forbidden Debugging Practices

### ❌ DO NOT Create Temporary Files

```python
# NEVER do this:
def debug_issue():
    # Bad: Creating temporary test files
    with open("temp_debug.py", "w") as f:
        f.write("test code")

    # Bad: Creating debug scripts
    with open("debug_script.py", "w") as f:
        f.write("import module; module.problematic_function()")
```

### ❌ DO NOT Use Print Statements

```python
# NEVER do this:
def problematic_function(data):
    print(f"Debug: data = {data}")  # Bad
    result = process_data(data)
    print(f"Debug: result = {result}")  # Bad
    return result
```

### ❌ DO NOT Skip Test Infrastructure

```python
# NEVER do this:
def quick_test():
    # Bad: Bypassing test framework
    result = my_function("test_input")
    if result != "expected":
        print("Bug found!")
```

## ✅ Proper Debugging Examples

### Example 1: Magic Number Detection Bug

```python
# test/unit_test/tools/design_linters/test_magic_number_debug.py
import pytest
import ast
from pathlib import Path
from tools.design_linters.rules.literals.magic_number_rules import MagicNumberRule

class TestMagicNumberBugFix:
    """Debug magic number detection in complex expressions."""

    def test_reproduce_complex_expression_bug(self):
        """Reproduce bug where complex expressions aren't handled correctly."""
        source_code = '''
def calculate_area(radius):
    return 3.14159 * radius ** 2  # Should detect 3.14159 as magic number

def process_data(items):
    return items[:5]  # Should NOT detect 5 in slice notation
        '''

        rule = MagicNumberRule({"ignore_slice_indices": True})
        tree = ast.parse(source_code)
        violations = []

        from loguru import logger
        logger.debug("Testing complex expression handling")

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                logger.debug("Found constant: {value} at line {line}, context: {context}",
                           value=node.value, line=node.lineno,
                           context=type(node.parent).__name__ if hasattr(node, 'parent') else 'unknown')

        violations = rule.check_code(source_code, Path("test.py"))

        # Should find 3.14159 but not 5 (in slice)
        magic_numbers_found = [v.message for v in violations if "3.14159" in v.message]
        slice_numbers_found = [v.message for v in violations if "5" in v.message]

        assert len(magic_numbers_found) == 1, "Should detect 3.14159 as magic number"
        assert len(slice_numbers_found) == 0, "Should not detect slice indices when configured to ignore"
```

### Example 2: SOLID Rule Debugging

```python
# test/unit_test/tools/design_linters/test_srp_debug.py
import pytest
from tools.design_linters.rules.solid.srp_rules import TooManyMethodsRule
from loguru import logger

class TestSRPRuleDebugging:
    """Debug SRP rule method counting logic."""

    def test_method_counting_edge_cases(self):
        """Test method counting with various Python constructs."""
        source_code = '''
class ComplexClass:
    def __init__(self): pass

    def regular_method(self): pass

    @property
    def computed_value(self): return 42

    @staticmethod
    def utility_function(): pass

    @classmethod
    def from_dict(cls, data): pass

    async def async_method(self): pass

    def _private_method(self): pass
        '''

        rule = TooManyMethodsRule({"max_methods": 4})

        # Enable debug logging for this test
        logger.debug("Testing method counting for complex class")

        violations = rule.check_code(source_code, Path("test.py"))

        # Log what was actually counted
        logger.debug("Violations found: {count}", count=len(violations))
        for violation in violations:
            logger.debug("Violation: {message}", message=violation.message)

        # Should count: __init__, regular_method, async_method, _private_method = 4 methods
        # Should NOT count: property, staticmethod, classmethod
        assert len(violations) == 0, "Should not exceed 4 method limit when excluding decorators"
```

## Running Debug Tests

### Execute with Full Logging

```bash
# Run specific debug test with full logging
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_magic_number_debug.py::TestMagicNumberBugFix::test_reproduce_complex_expression_bug -v -s --log-cli-level=DEBUG

# Run with custom log format
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_srp_debug.py -v -s --log-cli-format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
```

### Debug Test Development Cycle

```bash
# 1. Write failing test
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_debug.py::test_reproduce_bug -v
# Should fail, proving bug exists

# 2. Add logging to understand issue
# Edit source code to add logger.debug statements

# 3. Run test again with logging
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_debug.py::test_reproduce_bug -v -s --log-cli-level=DEBUG
# Analyze log output to understand root cause

# 4. Implement fix
# Edit source code based on insights from logging

# 5. Verify fix
PYTHONPATH=/home/stevejackson/Projects/durable-code-test/tools python -m pytest test/unit_test/tools/design_linters/test_debug.py::test_reproduce_bug -v
# Should now pass

# 6. Run full test suite
make test-unit
# Ensure no regressions
```

## Summary

**Always use this debugging approach**:

1. ✅ **Write unit tests** to reproduce issues
2. ✅ **Use Loguru logging** for investigation
3. ✅ **Follow TDD cycle**: Red → Green → Refactor
4. ✅ **Run tests through proper infrastructure**
5. ✅ **Document findings in test names and comments**

**Never**:
- ❌ Create temporary files for debugging
- ❌ Use print statements instead of logging
- ❌ Skip the test framework
- ❌ Debug without tests to verify fixes

This approach ensures that all debugging efforts contribute to the project's test coverage and leave behind valuable regression tests for future development.
