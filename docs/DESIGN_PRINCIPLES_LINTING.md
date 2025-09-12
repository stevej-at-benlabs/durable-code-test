# Design Principles Linting Strategy

## Overview
This document outlines strategies for automatically detecting violations of SOLID principles and other design patterns that are traditionally considered "subjective" but are crucial for durable code.

## 1. Single Responsibility Principle (SRP) Detection

### Metrics-Based Approach

#### Class/Module Cohesion Metrics
- **LCOM (Lack of Cohesion of Methods)**: Classes with LCOM > 1 likely violate SRP
- **Method Count**: Classes with > 7 methods are suspects
- **Import Diversity**: Modules importing from > 5 different domains likely have multiple responsibilities
- **File Length**: Files > 200 lines often indicate multiple responsibilities

#### Semantic Analysis Indicators
- **Multiple "and" in class/function names**: `UserManagerAndValidator` → SRP violation
- **Diverse method prefixes**: If a class has methods like `save_`, `validate_`, `send_`, `calculate_` → multiple responsibilities
- **Multiple reasons to change**: Track which methods change together in git history

### Implementation Tools

#### 1. AST-Based Analysis (Python)
```python
# Detect classes with multiple responsibility indicators
- Count distinct method prefixes (get_, set_, validate_, save_, etc.)
- Measure coupling between methods
- Analyze method parameter types for domain mixing
```

#### 2. Git History Analysis
```bash
# Find files that change for multiple reasons
git log --format="" --name-only | sort | uniq -c | sort -rn
```

#### 3. Dependency Analysis
- Classes depending on multiple unrelated modules
- Circular dependencies between modules
- Fan-out complexity > 5

## 2. Open/Closed Principle (OCP) Detection

### Violation Indicators
- **Frequent modifications**: Files changed > 10 times in 6 months
- **Switch/if-else chains**: Multiple conditional branches on type checking
- **Hardcoded values**: Magic numbers and strings instead of configuration
- **Missing abstraction layers**: Direct dependencies on concrete implementations

### Detection Methods
```python
# AST analysis for:
- isinstance() checks in multiple branches
- Type checking in conditionals
- Long if/elif chains (> 3 branches)
- Methods with > 3 boolean parameters
```

## 3. Liskov Substitution Principle (LSP) Detection

### Violation Indicators
- **Method signature changes**: Overridden methods with different parameters
- **Exception throwing**: Subclasses throwing exceptions base class doesn't
- **Precondition strengthening**: Subclasses with stricter input validation
- **Return type narrowing**: Returning None when base returns value

### Detection Tools
```python
# Check for:
- NotImplementedError in subclasses
- Different method signatures in inheritance chain
- Type hints inconsistency in overridden methods
```

## 4. Interface Segregation Principle (ISP) Detection

### Violation Indicators
- **Large interfaces**: > 5 methods in an interface/ABC
- **Unused interface methods**: Implementations that raise NotImplementedError
- **Fat interfaces**: Multiple unrelated method groups
- **Client-specific methods**: Methods used by only one client

### Metrics
- **Interface Utilization Rate**: % of interface methods actually used by each client
- **Method Grouping**: Cluster analysis of which methods are used together

## 5. Dependency Inversion Principle (DIP) Detection

### Violation Indicators
- **Direct instantiation**: Using `ClassName()` instead of dependency injection
- **Import from implementation**: Importing concrete classes instead of interfaces
- **Hardcoded dependencies**: No constructor parameters for dependencies
- **Framework coupling**: Business logic importing framework-specific modules

### Detection Methods
```python
# Check for:
- Direct instantiation patterns (Class() instead of injected)
- Imports from 'impl' or 'concrete' packages
- Missing abstract base classes
- Circular import detection
```

## 6. Custom Linting Rules Implementation

### Python Implementation Strategy

```python
# srp_linter.py
import ast
import collections
from typing import List, Dict

class SRPAnalyzer(ast.NodeVisitor):
    """Detects potential SRP violations."""
    
    def __init__(self):
        self.violations = []
        self.class_metrics = {}
    
    def visit_ClassDef(self, node):
        metrics = self.analyze_class(node)
        if self.violates_srp(metrics):
            self.violations.append({
                'class': node.name,
                'line': node.lineno,
                'reasons': self.get_violation_reasons(metrics)
            })
    
    def analyze_class(self, node):
        return {
            'method_count': len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
            'method_prefixes': self.get_method_prefixes(node),
            'dependencies': self.get_dependencies(node),
            'lines': node.end_lineno - node.lineno
        }
    
    def violates_srp(self, metrics):
        # Multiple indicators of SRP violation
        if metrics['method_count'] > 7:
            return True
        if len(metrics['method_prefixes']) > 3:
            return True
        if metrics['lines'] > 200:
            return True
        return False
```

### TypeScript/JavaScript Implementation

```typescript
// srp-analyzer.ts
interface ClassMetrics {
  methodCount: number;
  responsibilityGroups: string[];
  dependencies: string[];
  complexity: number;
}

class SRPAnalyzer {
  analyzeClass(node: ts.ClassDeclaration): ClassMetrics {
    // Analyze method names for responsibility patterns
    const methods = node.members.filter(ts.isMethodDeclaration);
    const responsibilityGroups = this.groupMethodsByResponsibility(methods);
    
    return {
      methodCount: methods.length,
      responsibilityGroups: Array.from(responsibilityGroups),
      dependencies: this.extractDependencies(node),
      complexity: this.calculateComplexity(node)
    };
  }
  
  private groupMethodsByResponsibility(methods: ts.MethodDeclaration[]): Set<string> {
    const groups = new Set<string>();
    methods.forEach(method => {
      const name = method.name?.getText() || '';
      // Group by prefix: get, set, validate, save, send, etc.
      const prefix = name.split(/(?=[A-Z])/)[0];
      groups.add(prefix);
    });
    return groups;
  }
}
```

## 7. AI-Assisted Review Configuration

### GPT-Based Analysis Prompt Template

```yaml
# .gpt-review.yml
review_prompts:
  srp_check: |
    Analyze this class for Single Responsibility Principle violations:
    - Does it have multiple reasons to change?
    - Are all methods cohesive around a single responsibility?
    - Could this be split into multiple classes?
    Rate: PASS/WARN/FAIL with explanation
    
  design_smell: |
    Check for design smells:
    - Feature envy (using another class's data excessively)
    - Inappropriate intimacy (classes knowing too much about each other)
    - Large class (too many responsibilities)
    - Data clumps (same parameters appearing together)
    Provide specific recommendations
```

## 8. Metrics Thresholds

### Configurable Limits
```yaml
# .design-lint.yml
srp:
  max_methods_per_class: 7
  max_method_prefixes: 3
  max_class_lines: 200
  max_dependencies: 5
  max_lcom: 1

ocp:
  max_modifications_per_month: 2
  max_conditional_branches: 3
  
dip:
  allow_direct_instantiation: false
  require_dependency_injection: true
  
coupling:
  max_afferent_coupling: 7
  max_efferent_coupling: 5
  
cohesion:
  min_cohesion_ratio: 0.7
```

## 9. Integration with CI/CD

### GitHub Actions Workflow

```yaml
name: Design Principles Check

on: [pull_request]

jobs:
  design-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Run SRP Analysis
        run: |
          python tools/srp_analyzer.py --threshold strict
          
      - name: Check SOLID Violations
        run: |
          python tools/solid_checker.py
          
      - name: Cohesion Metrics
        run: |
          radon hal . --min B  # Halstead complexity
          radon mi . --min B   # Maintainability index
          
      - name: Architecture Conformance
        run: |
          python tools/arch_checker.py --rules .architecture.yml
```

## 10. Gradual Enforcement Strategy

### Phase 1: Monitoring (Months 1-2)
- Run checks but don't fail builds
- Generate reports and track trends
- Identify hotspots

### Phase 2: Warnings (Months 3-4)
- Fail on severe violations only
- Require justification for overrides
- Track improvement metrics

### Phase 3: Enforcement (Month 5+)
- Strict enforcement of all rules
- Require architectural review for exceptions
- Automated refactoring suggestions

## 11. Example Violations and Fixes

### SRP Violation Example
```python
# BAD: Multiple responsibilities
class UserManager:
    def create_user(self): ...
    def validate_email(self): ...
    def send_notification(self): ...
    def generate_report(self): ...
    def encrypt_password(self): ...

# GOOD: Single responsibility
class UserRepository:
    def create_user(self): ...
    
class EmailValidator:
    def validate(self): ...
    
class NotificationService:
    def send(self): ...
```

### Tools Integration

1. **Prospector**: Python static analysis umbrella
2. **Wily**: Python complexity and maintainability tracking
3. **Dependency-cruiser**: JavaScript/TypeScript dependency analysis
4. **Pyreverse**: Generate UML diagrams for review
5. **Code Climate**: Automated code review for maintainability

## 12. Custom Metrics Dashboard

```python
# Generate design metrics report
metrics = {
    'srp_score': calculate_srp_compliance(),
    'coupling': measure_coupling(),
    'cohesion': measure_cohesion(),
    'stability': calculate_stability(),
    'abstractness': calculate_abstractness()
}

# Fail if below thresholds
assert metrics['srp_score'] > 0.8, "SRP compliance too low"
assert metrics['cohesion'] > 0.7, "Low cohesion detected"
```

## Conclusion

While SRP and other design principles are "less objective," we can create objective proxies through:
1. **Quantitative metrics** (method count, LCOM, coupling)
2. **Pattern detection** (naming conventions, change patterns)
3. **Historical analysis** (change frequency, co-change patterns)
4. **AI-assisted review** (GPT-based principle checking)
5. **Gradual enforcement** (monitor → warn → enforce)

The key is combining multiple indicators to reduce false positives while catching real violations.