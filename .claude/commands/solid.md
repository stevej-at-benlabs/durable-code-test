---
description: Check code for SOLID principle violations using AI agents that work in parallel
argument-hint: [optional: "all code" for full codebase analysis]
---

Check code for SOLID principle violations using AI agents that work in parallel to analyze each principle independently, with language-aware adaptations for dynamically typed languages like Python.

## Command Overview
The `/solid` command performs comprehensive SOLID principle analysis using specialized AI agents. It can operate in two modes:
- **Current branch**: Analyzes only files changed in the current branch (default)
- **All code**: Comprehensive analysis of the entire codebase (when "all code" is specified)

## Language-Specific Adaptations
The command automatically adapts its analysis based on the programming language:
- **Python**: Focuses on duck typing, protocols, and runtime behavior rather than strict type hierarchies
- **JavaScript/TypeScript**: Considers prototype-based inheritance and dynamic nature
- **Statically Typed Languages**: Full traditional SOLID analysis with strict type checking

### Python-Specific Considerations

#### What We DON'T Enforce in Python:
1. **Strict Type Hierarchies**: Python's duck typing means we focus on behavior, not inheritance trees
2. **Interface Implementation**: Python doesn't have interfaces - we look at protocols and ABCs instead
3. **Compile-Time Type Safety**: Runtime behavior matters more than static type declarations
4. **Everything as Classes**: Python supports multiple paradigms - functional solutions are often cleaner

#### What We DO Enforce in Python:
1. **Behavioral Contracts**: Objects should behave consistently when used in similar contexts
2. **Module Organization**: Python modules should have clear, single purposes
3. **Dependency Management**: Even without types, dependencies should flow correctly
4. **Protocol Compliance**: When using protocols/ABCs, implementations should be complete
5. **Testability**: Code should be easily testable through dependency injection

#### Pragmatic Adaptations:
- **SRP**: Focus on module and function cohesion, not just classes
- **OCP**: Emphasize extensibility through duck typing and protocols
- **LSP**: Check behavioral compatibility, not type substitution
- **ISP**: Consider how objects are actually used, not formal interfaces
- **DIP**: Focus on import structure and configuration, not type abstractions

## AI Agent Architecture
This command launches 5 specialized AI agents in parallel, each focusing on one SOLID principle:

### 1. Single Responsibility Principle (SRP) Agent
- **Focus**: Classes/modules with multiple responsibilities
- **Detection**: Functions/classes doing unrelated tasks
- **Tools**: Code analysis, pattern detection
- **Output**: List of violations with refactoring suggestions

### 2. Open/Closed Principle (OCP) Agent
- **Focus**: Code that violates open for extension, closed for modification
- **Detection**:
  - **Python**: Focuses on if/elif chains based on attributes, missing use of protocols/ABCs
  - **Other**: Hard-coded conditionals, type checking, direct instantiation
- **Tools**: Pattern analysis, abstraction detection
- **Output**: Areas needing abstraction or polymorphism (respecting duck typing in Python)

### 3. Liskov Substitution Principle (LSP) Agent
- **Focus**: Behavioral substitutability rather than strict type substitutability
- **Detection**:
  - **Python**: Focus on behavioral contracts and duck typing compatibility
  - **Other**: Overridden methods that change behavior contracts
- **Tools**: Behavioral analysis, protocol verification
- **Output**: Behavioral incompatibilities and protocol violations
- **Note**: In Python, emphasizes "if it walks like a duck" principle

### 4. Interface Segregation Principle (ISP) Agent
- **Focus**: Method dependencies and protocol segregation
- **Detection**:
  - **Python**: Large protocols/ABCs, objects with many unrelated methods
  - **Other**: Large interfaces, unused interface methods
- **Tools**: Protocol analysis, method grouping
- **Output**: Protocol/interface splitting recommendations
- **Note**: In Python, focuses on protocols and ABC usage rather than strict interfaces

### 5. Dependency Inversion Principle (DIP) Agent
- **Focus**: Dependencies on abstractions rather than concretions
- **Detection**:
  - **Python**: Hard-coded imports, missing dependency injection, tight coupling
  - **Other**: Direct instantiation, concrete dependencies
- **Tools**: Import analysis, coupling detection
- **Output**: Dependency injection opportunities (considering Python's module system)
- **Note**: In Python, emphasizes dependency injection and configurable imports

## Command Execution Flow

### Mode 1: Current Branch Analysis (Default)
```bash
# Usage: /solid
# Analyzes only files changed in current branch
```

1. **Git Analysis**: Identify changed files in current branch vs main
2. **Agent Deployment**: Launch 5 SOLID agents in parallel
3. **Focused Analysis**: Each agent analyzes only the changed files
4. **Report Generation**: Combine findings into unified report
5. **Actionable Recommendations**: Specific fixes for violations found

### Mode 2: Comprehensive Analysis
```bash
# Usage: /solid all code
# Analyzes entire codebase
```

1. **Codebase Scan**: Identify all relevant source files
2. **Agent Deployment**: Launch 5 SOLID agents in parallel
3. **Full Analysis**: Each agent analyzes entire codebase
4. **Comprehensive Report**: Complete SOLID compliance assessment
5. **Priority Recommendations**: Ranked list of critical violations

## Agent Prompts and Tasks

### SRP Agent Task
```
Analyze the provided code files for Single Responsibility Principle violations.

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Modules doing too many things (Python modules are first-class organizational units)
- Classes that could be split into functions (not everything needs to be a class in Python)
- Functions with side effects mixed with calculations
- Consider Python's functional programming capabilities
- Note: Simple data classes with related methods are often acceptable

For Statically Typed Languages:
- Classes with multiple unrelated methods
- Functions doing multiple unrelated tasks
- Modules mixing different concerns
- Methods with multiple reasons to change

For each violation found:
1. Identify the specific class/function/module
2. List the different responsibilities
3. Suggest how to split (consider modules, functions, or classes as appropriate)
4. Provide language-idiomatic refactoring recommendations

Return a structured report with file paths, line numbers, and specific recommendations.
```

### OCP Agent Task
```
Analyze the provided code files for Open/Closed Principle violations.

LANGUAGE-SPECIFIC FOCUS:

For Python:
- If/elif chains that check object attributes or string values
- Missing use of protocols, ABCs, or duck typing patterns
- Functions that would need modification to handle new cases
- Consider that Python uses duck typing - focus on behavior rather than strict types
- Note: isinstance() checks are sometimes appropriate in Python (e.g., for runtime validation)

For Statically Typed Languages:
- Hard-coded if/else or switch statements based on type
- Direct type checking
- Methods that need modification when new types are added
- Missing abstraction layers

For each violation found:
1. Identify the violation pattern
2. Explain why it violates OCP in the context of the language
3. Suggest appropriate abstraction strategies (protocols/ABCs for Python, interfaces for others)
4. Provide language-idiomatic refactoring examples

Return a structured report with specific extension points and abstraction recommendations.
```

### LSP Agent Task
```
Analyze the provided code files for Liskov Substitution Principle violations.

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Focus on behavioral compatibility rather than strict type substitution
- Check if objects implementing the same protocol/interface behave consistently
- Look for duck-typed objects that don't fully implement expected behavior
- Consider that Python allows for more flexible substitution patterns
- NotImplementedError is often acceptable for optional protocol methods

For Statically Typed Languages:
- Subclasses that strengthen preconditions
- Subclasses that weaken postconditions
- Overridden methods that change expected behavior
- Inheritance hierarchies that break substitutability

For each violation found:
1. Identify the substitutability issue
2. Explain the behavioral incompatibility
3. Suggest protocol compliance or composition alternatives
4. Provide language-appropriate implementation examples

Return a structured report focusing on behavioral compatibility.
```

### ISP Agent Task
```
Analyze the provided code files for Interface Segregation Principle violations.

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Large Protocol or ABC definitions with many unrelated methods
- Classes with many public methods that different clients use differently
- Objects passed to functions where only a subset of methods is used
- Consider that Python's duck typing naturally supports ISP
- Focus on logical method grouping rather than strict interface enforcement

For Statically Typed Languages:
- Large interfaces with many unrelated methods
- Classes forced to implement unused interface methods
- Clients depending on methods they don't use
- Fat interfaces that could be split

For each violation found:
1. Identify the oversized interface/protocol/class
2. Group related methods by their cohesion
3. Suggest protocol/interface splitting strategies
4. Show how clients would use smaller, focused protocols

Return a structured report with segregation recommendations appropriate to the language.
```

### DIP Agent Task
```
Analyze the provided code files for Dependency Inversion Principle violations.

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Hard-coded imports of concrete implementations in high-level modules
- Missing use of dependency injection patterns
- Configuration that's tightly coupled to implementations
- Consider Python's module system and import mechanics
- Note: Some direct imports are acceptable in Python (e.g., standard library)
- Focus on configurable dependencies and testability

For Statically Typed Languages:
- High-level modules importing low-level modules directly
- Direct instantiation of concrete classes
- Hardcoded dependencies
- Missing abstraction layers

For each violation found:
1. Identify the problematic dependency
2. Explain how it limits flexibility and testing
3. Suggest dependency injection or configuration patterns
4. Provide language-idiomatic examples (e.g., Python's __init__ injection)

Return a structured report with practical dependency inversion strategies.
```

## Report Generation

### Report Storage
- **Small Reports** (< 50 violations): Displayed directly in the terminal
- **Large Reports** (≥ 50 violations): Saved to `.reports/` directory with timestamp
- **Report Files**: Named as `solid-analysis-YYYY-MM-DD-HHMMSS.md`
- **Individual Agent Reports**: Saved as separate files when violations exceed threshold

### Individual Agent Reports
Each agent produces a structured report:
```json
{
  "principle": "SRP|OCP|LSP|ISP|DIP",
  "violations": [
    {
      "file": "path/to/file.py",
      "line": 123,
      "severity": "high|medium|low",
      "description": "Specific violation description",
      "recommendation": "How to fix this violation",
      "example": "Code example showing the fix"
    }
  ],
  "summary": "Overall assessment for this principle"
}
```

### Unified Report
Combined report from all agents:
```markdown
# SOLID Principles Analysis Report

## Executive Summary
- **Total Violations**: X found across Y files
- **Critical Issues**: Z high-severity violations requiring immediate attention
- **Code Quality Score**: A-F grade based on violation density

## Analysis Scope
- **Mode**: Current branch / All code
- **Files Analyzed**: X files
- **Lines of Code**: Y total

## Principle-by-Principle Results

### Single Responsibility Principle (SRP)
- **Violations Found**: X
- **Severity Breakdown**: Y high, Z medium, W low
- **Top Issues**: [List of most critical violations]

### Open/Closed Principle (OCP)
- **Violations Found**: X
- **Extension Points Needed**: Y
- **Abstraction Opportunities**: Z

### Liskov Substitution Principle (LSP)
- **Violations Found**: X
- **Inheritance Issues**: Y
- **Substitution Problems**: Z

### Interface Segregation Principle (ISP)
- **Violations Found**: X
- **Interfaces to Split**: Y
- **Unused Dependencies**: Z

### Dependency Inversion Principle (DIP)
- **Violations Found**: X
- **Concrete Dependencies**: Y
- **Injection Opportunities**: Z

## Prioritized Action Items
1. **Critical (Fix Immediately)**
   - [List of high-priority violations]

2. **Important (Fix Soon)**
   - [List of medium-priority violations]

3. **Minor (Fix When Time Permits)**
   - [List of low-priority violations]

## Refactoring Recommendations
- **Extract Class**: [Files that need class splitting]
- **Introduce Interface**: [Places needing abstraction]
- **Dependency Injection**: [Hardcoded dependencies to fix]
- **Composition over Inheritance**: [Inheritance issues to address]
```

## Integration with Visualization

The results are automatically added to the Building tab visualization showing:
- SOLID compliance dashboard
- Real-time violation counts
- Progress tracking for fixes
- Before/after metrics

## Language-Specific Examples

### Python vs Java: Different Approaches to SOLID

#### Example: Open/Closed Principle
**Java (Traditional Approach):**
```java
// Violation - needs modification for new types
if (shape instanceof Circle) {
    return Math.PI * shape.radius * shape.radius;
} else if (shape instanceof Square) {
    return shape.side * shape.side;
}
```

**Python (Pragmatic Approach):**
```python
# Not necessarily a violation in Python - duck typing is idiomatic
if shape.shape_type == "circle":
    return math.pi * shape.radius ** 2
elif shape.shape_type == "square":
    return shape.side ** 2

# Better Python approach using duck typing:
return shape.calculate_area()  # Each shape knows how to calculate its area
```

#### Example: Liskov Substitution Principle
**Java (Strict Substitution):**
```java
// Violation - Rectangle/Square problem
class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        super.setWidth(width);
        super.setHeight(width);  // Violates LSP
    }
}
```

**Python (Behavioral Compatibility):**
```python
# Python focuses on behavioral compatibility
# Both shapes should behave correctly when area() is called
class Rectangle:
    def area(self):
        return self.width * self.height

class Square:
    def area(self):
        return self.side ** 2

# They're substitutable for area calculation even without inheritance
```

## Usage Examples

### Example 1: Quick Branch Check
```bash
# User runs: /solid
# System Response:
"Analyzing current branch for SOLID violations..."
"Launching 5 AI agents in parallel..."
"✓ SRP Agent: 3 violations found"
"✓ OCP Agent: 1 violation found"
"✓ LSP Agent: 0 violations found"
"✓ ISP Agent: 2 violations found"
"✓ DIP Agent: 1 violation found"
"Report generated with 7 total violations"
```

### Example 2: Comprehensive Analysis
```bash
# User runs: /solid all code
# System Response:
"Analyzing entire codebase for SOLID violations..."
"Scanning 247 files across all modules..."
"Launching 5 AI agents for comprehensive analysis..."
"✓ SRP Agent: Analyzed 247 files, 23 violations"
"✓ OCP Agent: Analyzed 247 files, 8 violations"
"✓ LSP Agent: Analyzed 247 files, 2 violations"
"✓ ISP Agent: Analyzed 247 files, 12 violations"
"✓ DIP Agent: Analyzed 247 files, 15 violations"
"Comprehensive report generated with 60 total violations"
"📁 Full report saved to: .reports/solid-analysis-2024-01-15-143022.md"
"📊 Individual principle reports also saved to .reports/"
"Code quality grade: B+ (significant improvement from last scan)"
```

### Example 3: Large Report Handling
```bash
# User runs: /solid all code (on large codebase)
# System Response:
"Analyzing entire codebase for SOLID violations..."
"Scanning 1,247 files across all modules..."
"Launching 5 AI agents for comprehensive analysis..."
"✓ SRP Agent: Analyzed 1,247 files, 156 violations"
"✓ OCP Agent: Analyzed 1,247 files, 89 violations"
"✓ LSP Agent: Analyzed 1,247 files, 23 violations"
"✓ ISP Agent: Analyzed 1,247 files, 67 violations"
"✓ DIP Agent: Analyzed 1,247 files, 112 violations"
"⚠️ Large report detected (447 total violations)"
"📁 Reports saved to .reports/ directory:"
"  - solid-analysis-2024-01-15-143022.md (main report)"
"  - solid-srp-2024-01-15-143022.md (156 violations)"
"  - solid-ocp-2024-01-15-143022.md (89 violations)"
"  - solid-lsp-2024-01-15-143022.md (23 violations)"
"  - solid-isp-2024-01-15-143022.md (67 violations)"
"  - solid-dip-2024-01-15-143022.md (112 violations)"
"📊 Summary: 447 violations | Grade: C+ | Top priority: SRP (156)"
"Run 'cat .reports/solid-analysis-2024-01-15-143022.md' to view full report"
```

## Error Handling

### Agent Failures
- If an agent fails, continue with remaining agents
- Report which agents completed successfully
- Provide partial results with warnings

### No Violations Found
- Celebrate clean code with positive feedback
- Provide code quality metrics
- Suggest proactive improvements

### Large Codebase Handling
- Implement chunking for very large codebases
- Progress indicators for long-running analysis
- Ability to cancel long-running operations

## Continuous Improvement

### Learning from Results
- Track violation trends over time
- Learn from user feedback on recommendations
- Improve agent prompts based on false positives

### Integration with CI/CD
- Can be run automatically on pull requests
- Configurable violation thresholds for build failures
- Integration with existing design linting pipeline

## Report Management

### .reports Directory Structure
```
.reports/
├── solid-analysis-YYYY-MM-DD-HHMMSS.md    # Main unified report
├── solid-srp-YYYY-MM-DD-HHMMSS.md         # SRP violations detail
├── solid-ocp-YYYY-MM-DD-HHMMSS.md         # OCP violations detail
├── solid-lsp-YYYY-MM-DD-HHMMSS.md         # LSP violations detail
├── solid-isp-YYYY-MM-DD-HHMMSS.md         # ISP violations detail
├── solid-dip-YYYY-MM-DD-HHMMSS.md         # DIP violations detail
└── solid-summary-latest.md                 # Symlink to latest report
```

### Report Features
- **Automatic Creation**: `.reports/` directory created if it doesn't exist
- **Timestamped Files**: Each analysis gets unique timestamp
- **Latest Symlink**: `solid-summary-latest.md` always points to most recent
- **Git Ignored**: `.reports/` directory is in .gitignore by default
- **Markdown Format**: All reports in readable markdown format
- **Threshold-Based**: Only creates files when violations exceed thresholds

### Viewing Reports
```bash
# View latest summary
cat .reports/solid-summary-latest.md

# View specific principle violations
cat .reports/solid-srp-*.md

# Open in editor
code .reports/solid-analysis-*.md

# Search for specific patterns
grep -n "high" .reports/solid-*.md
```

## Notes
- Agents run in parallel for maximum speed
- Results are cached for 1 hour to avoid redundant analysis
- Command respects existing design linting configuration
- Integrates with make design-lint and existing tooling
- Reports directory (`.reports/`) is automatically created and gitignored
- Large reports (≥50 violations) are automatically saved to files
- Individual principle reports saved when violations exceed 20 per principle
