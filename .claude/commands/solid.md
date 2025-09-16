---
description: Check code for SOLID principle violations using AI agents that work in parallel
argument-hint: [optional: "all code" for full codebase analysis]
---

Check code for SOLID principle violations using AI agents that work in parallel to analyze each principle independently.

## Command Overview
The `/solid` command performs comprehensive SOLID principle analysis using specialized AI agents. It can operate in two modes:
- **Current branch**: Analyzes only files changed in the current branch (default)
- **All code**: Comprehensive analysis of the entire codebase (when "all code" is specified)

## AI Agent Architecture
This command launches 5 specialized AI agents in parallel, each focusing on one SOLID principle:

### 1. Single Responsibility Principle (SRP) Agent
- **Focus**: Classes/modules with multiple responsibilities
- **Detection**: Functions/classes doing unrelated tasks
- **Tools**: Code analysis, pattern detection
- **Output**: List of violations with refactoring suggestions

### 2. Open/Closed Principle (OCP) Agent
- **Focus**: Code that violates open for extension, closed for modification
- **Detection**: Hard-coded conditionals, type checking, direct instantiation
- **Tools**: Pattern analysis, abstraction detection
- **Output**: Areas needing abstraction or polymorphism

### 3. Liskov Substitution Principle (LSP) Agent
- **Focus**: Inheritance violations where subtypes aren't substitutable
- **Detection**: Overridden methods that change behavior contracts
- **Tools**: Inheritance analysis, contract verification
- **Output**: Inheritance issues and interface problems

### 4. Interface Segregation Principle (ISP) Agent
- **Focus**: Fat interfaces that force unnecessary dependencies
- **Detection**: Large interfaces, unused interface methods
- **Tools**: Interface analysis, dependency tracking
- **Output**: Interface splitting recommendations

### 5. Dependency Inversion Principle (DIP) Agent
- **Focus**: High-level modules depending on low-level modules
- **Detection**: Direct instantiation, concrete dependencies
- **Tools**: Dependency analysis, abstraction detection
- **Output**: Dependency injection opportunities

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

Focus on:
- Classes with multiple unrelated methods
- Functions doing multiple unrelated tasks
- Modules mixing different concerns
- Methods with multiple reasons to change

For each violation found:
1. Identify the specific class/function
2. List the different responsibilities
3. Suggest how to split the responsibilities
4. Provide refactoring recommendations

Return a structured report with file paths, line numbers, and specific recommendations.
```

### OCP Agent Task
```
Analyze the provided code files for Open/Closed Principle violations.

Focus on:
- Hard-coded if/else or switch statements based on type
- Direct type checking with isinstance() or typeof
- Methods that need modification when new types are added
- Missing abstraction layers

For each violation found:
1. Identify the violation pattern
2. Explain why it violates OCP
3. Suggest abstraction strategies (interfaces, polymorphism)
4. Provide refactoring examples

Return a structured report with specific extension points and abstraction recommendations.
```

### LSP Agent Task
```
Analyze the provided code files for Liskov Substitution Principle violations.

Focus on:
- Subclasses that strengthen preconditions
- Subclasses that weaken postconditions
- Overridden methods that change expected behavior
- Inheritance hierarchies that break substitutability

For each violation found:
1. Identify the inheritance relationship
2. Explain the substitution problem
3. Suggest interface or composition alternatives
4. Provide corrected implementation examples

Return a structured report with inheritance issues and design alternatives.
```

### ISP Agent Task
```
Analyze the provided code files for Interface Segregation Principle violations.

Focus on:
- Large interfaces with many unrelated methods
- Classes forced to implement unused interface methods
- Clients depending on methods they don't use
- Fat interfaces that could be split

For each violation found:
1. Identify the oversized interface
2. Group related methods together
3. Suggest how to split the interface
4. Show how clients would use smaller interfaces

Return a structured report with interface splitting recommendations.
```

### DIP Agent Task
```
Analyze the provided code files for Dependency Inversion Principle violations.

Focus on:
- High-level modules importing low-level modules directly
- Direct instantiation of concrete classes
- Hardcoded dependencies
- Missing abstraction layers

For each violation found:
1. Identify the dependency relationship
2. Explain the inversion needed
3. Suggest abstract interfaces
4. Provide dependency injection examples

Return a structured report with dependency inversion opportunities.
```

## Report Generation

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
"Code quality grade: B+ (significant improvement from last scan)"
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

## Notes
- Agents run in parallel for maximum speed
- Results are cached for 1 hour to avoid redundant analysis
- Command respects existing design linting configuration
- Integrates with make design-lint and existing tooling
