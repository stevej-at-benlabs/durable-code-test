---
description: Generate a pragmatic SOLID principles report focusing on essential violations - no code changes, read-only analysis
argument-hint: [optional: "all code" for full codebase analysis]
---

Generate a **pragmatic SOLID principles compliance report** that focuses on violations that actually matter. This command uses AI agents working in parallel to identify genuine maintainability issues while filtering out theoretical violations that don't impact real-world development.

## 🎯 Pragmatic Philosophy: Focus on What Matters

This command has been designed to **avoid pedantic violations** and focus on **real maintainability issues**:

- **Higher Thresholds**: 20+ methods for SRP (not 15), 5+ branches for OCP (not 3)
- **Modern Patterns**: Recognizes that React components, service coordinators, and config objects follow different rules
- **Language Awareness**: Python duck typing, TypeScript discriminated unions, and framework patterns are respected
- **Practical Impact**: Only flags violations that would actually cause problems in production or testing
- **No Over-Engineering**: Avoids suggesting abstractions for simple cases

## 🔒 HEADLESS MODE - NO PERMISSIONS REQUIRED

**This command runs in read-only report mode:**
- ✅ **No code modifications** - Only generates analysis reports
- ✅ **No permissions needed** - Runs completely autonomously
- ✅ **Safe to run unattended** - User can start and walk away
- ✅ **No interactive prompts** - Fully automated execution
- ✅ **Report-only output** - Results saved to `.reports/` directory

## Command Overview
The `/solid` command performs comprehensive SOLID principle analysis using specialized AI agents. It operates in **report-only mode** and can analyze code in two scopes:
- **Current branch**: Analyzes only files changed in the current branch (default)
- **All code**: Comprehensive analysis of the entire codebase (when "all code" is specified)

**Important**: This is a diagnostic tool only. It will:
1. Read and analyze your code
2. Generate detailed violation reports
3. Save reports to the `.reports/` directory
4. Never modify any source files
5. Never require user interaction or permissions

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
This command launches 5 specialized AI agents in parallel, each focusing on one SOLID principle with **pragmatic, real-world thresholds** to avoid false positives.

### 1. Single Responsibility Principle (SRP) Agent
- **Focus**: Classes/modules with multiple unrelated responsibilities
- **Detection Thresholds**:
  - Classes with 20+ public methods (not 15)
  - Components handling 4+ completely unrelated domains
  - Mixing business logic with infrastructure in the same class
- **What We DON'T Flag**:
  - React components managing their own state, effects, and rendering
  - Service classes coordinating related operations
  - Test classes with setup/teardown methods
  - CLI commands that parse and execute
- **Output**: Only significant SRP violations that genuinely impact maintainability

### 2. Open/Closed Principle (OCP) Agent
- **Focus**: Code requiring modification for common extensions
- **Detection Thresholds**:
  - If/elif chains with 5+ branches for type dispatch
  - Frequently modified switch statements for new cases
  - Hard-coded production URLs or endpoints
- **What We DON'T Flag**:
  - UI configuration objects (tabs, routes, menus)
  - Enum/string switches under 5 cases
  - Type guards and runtime type checking
  - Factory methods with type selection
- **Output**: Only OCP violations that actually impede extensibility

### 3. Liskov Substitution Principle (LSP) Agent
- **Focus**: Actual behavioral contract violations
- **Detection**:
  - Methods that completely change expected behavior
  - Required parameters with different meanings
  - Fundamentally different side effects
- **What We DON'T Flag**:
  - Minor return type extensions with optional fields
  - Empty vs undefined return differences
  - Additional optional parameters
  - Interface extensions that maintain base behavior
- **Output**: Only true behavioral incompatibilities

### 4. Interface Segregation Principle (ISP) Agent
- **Focus**: Genuinely oversized interfaces forcing unused dependencies
- **Detection Thresholds**:
  - Interfaces with 10+ unrelated methods
  - Clients forced to depend on 5+ unused methods
  - Clear method groupings serving different client types
- **What We DON'T Flag**:
  - React component props with up to 10 properties
  - Service interfaces with related methods
  - State interfaces combining related concerns
  - Configuration interfaces
- **Output**: Only interfaces that truly need segregation

### 5. Dependency Inversion Principle (DIP) Agent
- **Focus**: Dependencies that actually impair testing and flexibility
- **Detection**:
  - Business logic directly instantiating infrastructure
  - Hard-coded production URLs/endpoints
  - Circular dependencies between modules
  - Missing DI where testing is impaired
- **What We DON'T Flag**:
  - Browser APIs in frontend components
  - Standard library imports
  - Framework-specific imports
  - Test utilities and fixtures
  - Development/demo code dependencies
- **Output**: Only DIP violations that matter for testing and deployment

## Command Execution Flow - Fully Autonomous

### 🤖 Headless Execution Characteristics
- **Zero User Interaction**: Command runs start-to-finish without prompts
- **No Permission Dialogs**: All operations are read-only
- **Background-Safe**: Can be run in CI/CD or scheduled tasks
- **Walk-Away Operation**: Start the command and leave - it will complete autonomously
- **Report Generation Only**: Results written to files, no code changes

### Mode 1: Current Branch Analysis (Default)
```bash
# Usage: /solid
# Generates report for files changed in current branch
# NO PERMISSIONS REQUIRED - READ-ONLY OPERATION
```

1. **Git Analysis**: Identify changed files in current branch vs main (read-only)
2. **Agent Deployment**: Launch 5 SOLID agents in parallel (autonomous)
3. **Focused Analysis**: Each agent analyzes only the changed files (read-only)
4. **Report Generation**: Combine findings into unified report file
5. **Save Results**: Write report to `.reports/` directory (creates dir if needed)
6. **Complete**: Exit with summary of report location

### Mode 2: Comprehensive Analysis
```bash
# Usage: /solid all code
# Generates report for entire codebase
# NO PERMISSIONS REQUIRED - READ-ONLY OPERATION
```

1. **Codebase Scan**: Identify all relevant source files (read-only)
2. **Agent Deployment**: Launch 5 SOLID agents in parallel (autonomous)
3. **Full Analysis**: Each agent analyzes entire codebase (read-only)
4. **Comprehensive Report**: Complete SOLID compliance assessment
5. **Save Results**: Write reports to `.reports/` directory
6. **Complete**: Exit with summary of report locations

## Agent Prompts and Tasks

### SRP Agent Task
```
Analyze the provided code files for Single Responsibility Principle violations using PRAGMATIC thresholds.

CRITICAL: Only flag SIGNIFICANT violations that genuinely impact maintainability.

VIOLATION THRESHOLDS:
- Classes with 20+ public methods (not just many methods)
- Components handling 4+ completely unrelated domains
- Clear mixing of business logic with infrastructure/persistence
- Files over 500 lines handling multiple unrelated concerns

ACCEPTABLE PATTERNS (DO NOT FLAG):
- UI components managing their own state, effects, and rendering
- Service classes coordinating related operations (e.g., WebSocket + processing)
- Test classes with setup/teardown/assertion methods together
- CLI commands that parse arguments and execute
- Data classes with validation and transformation methods
- Utility modules with related helper functions

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Focus on modules with unrelated function groups (not just many functions)
- Don't flag classes that could be functions unless they're overly complex
- Simple data classes with methods are fine
- Consider that Python modules are valid organizational units

For JavaScript/TypeScript:
- React components under 200 lines are generally acceptable
- Hooks combining related logic are single responsibility
- Don't flag components for having render + event handlers + effects

For each SIGNIFICANT violation:
1. Explain why this specifically impacts maintainability
2. Count the number of truly unrelated responsibilities
3. Only suggest splitting if responsibilities are genuinely unrelated
4. Provide practical, not theoretical, refactoring suggestions

Return only violations that would provide real value if fixed.
```

### OCP Agent Task
```
Analyze the provided code files for Open/Closed Principle violations using PRAGMATIC thresholds.

CRITICAL: Focus on code that FREQUENTLY requires modification, not just any conditional logic.

VIOLATION THRESHOLDS:
- If/elif chains with 5+ branches for type/behavior dispatch
- Switch statements modified 3+ times in recent history for new cases
- Hard-coded production URLs, API endpoints, or external service configurations
- Type checking that forces code modification for every new type

ACCEPTABLE PATTERNS (DO NOT FLAG):
- UI configuration objects (tabs, routes, navigation menus)
- Enum/string switches with fewer than 5 cases
- Type guards and discriminated unions in TypeScript
- Factory methods with type selection
- Configuration-driven behavior (where config is external)
- isinstance() checks for validation or error handling
- Strategy selection based on user input or configuration

LANGUAGE-SPECIFIC FOCUS:

For Python:
- If/elif chains are acceptable for 3-4 cases (Pythonic simplicity)
- Duck typing often makes OCP less relevant - don't over-engineer
- Simple string/enum checking is fine for small sets

For JavaScript/TypeScript:
- Discriminated unions with switch statements are good patterns
- Type guards are necessary and acceptable
- Configuration objects for UI are meant to be modified

For each SIGNIFICANT violation:
1. Verify this code actually changes frequently (not just theoretically)
2. Count how many branches/cases exist
3. Only suggest abstraction if it would genuinely improve maintainability
4. Avoid suggesting over-engineering for simple cases

Return only violations where abstraction would provide clear value.
```

### LSP Agent Task
```
Analyze the provided code files for Liskov Substitution Principle violations focusing on ACTUAL behavioral problems.

CRITICAL: Only flag violations that would cause runtime errors or unexpected behavior in production.

VIOLATION CRITERIA:
- Methods that completely change or ignore expected behavior
- Required parameters that have fundamentally different meanings
- Return values that break calling code expectations
- Side effects that are completely different (not just additional)
- Throwing exceptions where parent class doesn't

ACCEPTABLE PATTERNS (DO NOT FLAG):
- Extending return types with additional optional fields
- Empty vs null vs undefined differences (unless they break callers)
- Additional optional parameters in overrides
- Subclasses that add extra functionality while preserving base behavior
- NotImplementedError for genuinely optional methods
- Covariant return types that maintain compatibility
- Additional logging or metrics (non-functional additions)

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Duck typing means behavioral compatibility matters more than inheritance
- Focus on protocol violations that would cause AttributeError
- Don't flag if the substitution works in practice
- Consider that Python is dynamic - runtime behavior matters most

For JavaScript/TypeScript:
- Prototype chains and mixins have different rules than classical inheritance
- Optional chaining and null coalescing handle many potential issues
- Focus on actual breaking changes, not type system warnings

For each TRUE violation:
1. Demonstrate how this would break existing code
2. Show the specific scenario where substitution fails
3. Only suggest changes if they prevent actual runtime issues
4. Consider if composition would be more appropriate than inheritance

Return only violations that could cause actual bugs in production.
```

### ISP Agent Task
```
Analyze the provided code files for Interface Segregation Principle violations using PRACTICAL thresholds.

CRITICAL: Only flag interfaces that force significant unused dependencies on clients.

VIOLATION THRESHOLDS:
- Interfaces/protocols with 10+ unrelated methods
- Clients forced to depend on 5+ methods they never use
- Clear clusters of methods serving completely different client types
- Interfaces mixing multiple unrelated domains (e.g., auth + data + UI)

ACCEPTABLE PATTERNS (DO NOT FLAG):
- Component props interfaces with up to 10 properties
- Service interfaces where methods are cohesive
- State/context interfaces that group related data
- Configuration interfaces (these are meant to be comprehensive)
- Builder/fluent interfaces with many methods
- Test fixtures and mocks
- Framework-required interfaces (e.g., React component interfaces)

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Protocols with 3-6 methods are usually fine
- Duck typing means clients naturally use only what they need
- Don't flag ABCs unless they're genuinely bloated (10+ unrelated methods)
- Consider that Python's dynamic nature already provides ISP benefits

For JavaScript/TypeScript:
- Props interfaces for components are naturally large - this is fine
- Optional properties don't violate ISP
- Intersection types and extends are good patterns
- Don't flag unless implementation is forced to handle unused methods

For each SIGNIFICANT violation:
1. Count how many unrelated method groups exist
2. Show which clients use which subset of methods
3. Only suggest splitting if it would reduce coupling significantly
4. Consider if the interface is intentionally comprehensive (e.g., facades)

Return only violations where interface splitting would measurably improve the design.
```

### DIP Agent Task
```
Analyze the provided code files for Dependency Inversion Principle violations that ACTUALLY impair testing or deployment flexibility.

CRITICAL: Focus on dependencies that genuinely need to be configurable, not all direct imports.

VIOLATION CRITERIA:
- Business logic directly instantiating infrastructure services
- Hard-coded production URLs, API endpoints, or database connections
- Circular dependencies between modules
- Service instantiation without factories where multiple implementations exist
- Tight coupling that prevents unit testing

ACCEPTABLE PATTERNS (DO NOT FLAG):
- Browser APIs in frontend components (WebSocket, fetch, localStorage)
- Standard library imports in any language
- Framework imports (React, FastAPI, Express, etc.)
- Utility/helper function imports
- Type/interface/protocol imports
- Development tools and test utilities
- Single-implementation services (no need for abstraction)
- Constructor injection that's already in place

LANGUAGE-SPECIFIC FOCUS:

For Python:
- Module-level imports of standard library are fine
- Consider existing dependency injection (constructor parameters)
- Don't flag if testability isn't actually impaired
- Simple scripts don't need DI

For JavaScript/TypeScript:
- Direct use of browser APIs is normal and acceptable
- Node.js built-in modules are fine to import directly
- Consider that frontend apps often use module bundlers for DI
- React context and hooks are forms of dependency injection

For each TRUE violation:
1. Explain specifically how this impairs testing or deployment
2. Verify that multiple implementations would actually be useful
3. Only suggest DI if it provides real benefits
4. Avoid over-engineering for hypothetical flexibility

Return only violations that demonstrably impact testing or deployment.
```

## Report Generation

### Severity Classification
The agents use pragmatic severity levels focused on actual impact:

#### 🔴 High Severity (Must Fix)
- **SRP**: Classes with 20+ methods or 500+ lines mixing unrelated domains
- **OCP**: If/elif chains with 5+ branches that change frequently
- **LSP**: Behavioral violations that would cause runtime errors
- **ISP**: Interfaces forcing 5+ unused methods on clients
- **DIP**: Hard-coded production URLs/endpoints or circular dependencies

#### 🟡 Medium Severity (Should Consider)
- **SRP**: Classes with 15-19 methods or components doing 3 related-but-distinct tasks
- **OCP**: 4-5 branch conditionals that might need extension
- **LSP**: Behavioral differences that could surprise users
- **ISP**: Interfaces with 7-9 methods where some clients use subsets
- **DIP**: Direct instantiation where DI would improve testing

#### 🟢 Low Severity (Nice to Have)
- **SRP**: Minor cohesion issues within related functionality
- **OCP**: 3-branch conditionals that rarely change
- **LSP**: Minor contract differences that don't break functionality
- **ISP**: Slightly large but cohesive interfaces
- **DIP**: Direct imports that don't impact testing

#### ℹ️ Informational (Not Violations)
- Pattern observations that might be intentional
- Framework-specific conventions
- Trade-offs made for simplicity
- Performance optimizations

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

### Pragmatic vs Over-Zealous Analysis

#### Example 1: React Component (SRP)
```typescript
// ❌ OVER-ZEALOUS: "Component has 8 methods - violates SRP!"
// ✅ PRAGMATIC: This is a normal React component pattern
export const DashboardComponent: React.FC = () => {
    const [data, setData] = useState();
    const handleClick = () => { /* ... */ };
    const handleSubmit = () => { /* ... */ };
    const renderHeader = () => { /* ... */ };
    const renderContent = () => { /* ... */ };

    useEffect(() => { /* fetch data */ }, []);

    return <div>{/* Component JSX */}</div>;
};
```

#### Example 2: Configuration Object (OCP)
```typescript
// ❌ OVER-ZEALOUS: "Hard-coded configuration violates OCP!"
// ✅ PRAGMATIC: UI configuration is meant to be explicit
const tabs = [
    { id: 'home', label: 'Home', component: HomeTab },
    { id: 'settings', label: 'Settings', component: SettingsTab },
    { id: 'profile', label: 'Profile', component: ProfileTab }
];
```

#### Example 3: Service with Multiple Operations (SRP)
```python
# ❌ OVER-ZEALOUS: "Class handles WebSocket AND data processing!"
# ✅ PRAGMATIC: These are related concerns in a cohesive service
class RealtimeDataService:
    def connect_websocket(self): ...
    def process_message(self, msg): ...
    def transform_data(self, data): ...
    def emit_update(self, update): ...
```

#### Example 4: Type Checking (OCP)
```python
# ❌ OVER-ZEALOUS: "If/elif chain violates OCP!"
# ✅ PRAGMATIC: 3 cases is fine - don't over-engineer
if record_type == "user":
    return process_user(data)
elif record_type == "product":
    return process_product(data)
elif record_type == "order":
    return process_order(data)

# Only flag if 5+ cases that change frequently
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

## Usage Examples - Headless Report Generation

### Example 1: Quick Branch Check (Walk-Away Mode)
```bash
# User runs: /solid
# Then walks away - no interaction needed
# System Response (fully autonomous):
"🔒 Starting HEADLESS SOLID analysis (report-only mode)..."
"📊 No permissions required - running autonomously"
"Analyzing current branch for SOLID violations..."
"Launching 5 AI agents in parallel (read-only analysis)..."
"✓ SRP Agent: 3 violations found"
"✓ OCP Agent: 1 violation found"
"✓ LSP Agent: 0 violations found"
"✓ ISP Agent: 2 violations found"
"✓ DIP Agent: 1 violation found"
"📁 Report saved: .reports/solid-analysis-2024-01-15-143022.md"
"✅ Analysis complete - 7 violations documented (no code modified)"
"View report: cat .reports/solid-analysis-2024-01-15-143022.md"
```

### Example 2: Comprehensive Analysis (Unattended Execution)
```bash
# User runs: /solid all code
# Can immediately leave - runs without supervision
# System Response (fully autonomous):
"🔒 Starting HEADLESS SOLID analysis (report-only mode)..."
"📊 No permissions required - running autonomously"
"Analyzing entire codebase for SOLID violations..."
"Scanning 247 files across all modules (read-only)..."
"Launching 5 AI agents for comprehensive analysis..."
"✓ SRP Agent: Analyzed 247 files, 23 violations"
"✓ OCP Agent: Analyzed 247 files, 8 violations"
"✓ LSP Agent: Analyzed 247 files, 2 violations"
"✓ ISP Agent: Analyzed 247 files, 12 violations"
"✓ DIP Agent: Analyzed 247 files, 15 violations"
"📁 Reports generated (no code modified):"
"  - Main: .reports/solid-analysis-2024-01-15-143022.md"
"  - Individual principle reports saved to .reports/"
"✅ Analysis complete - Code quality grade: B+"
"View report: cat .reports/solid-analysis-2024-01-15-143022.md"
```

### Example 3: Large Report Handling (Background Safe)
```bash
# User runs: /solid all code (on large codebase)
# Perfect for CI/CD or scheduled tasks
# System Response (fully autonomous):
"🔒 Starting HEADLESS SOLID analysis (report-only mode)..."
"📊 No permissions required - running autonomously"
"Analyzing entire codebase for SOLID violations..."
"Scanning 1,247 files across all modules (read-only)..."
"Launching 5 AI agents for comprehensive analysis..."
"Processing... (safe to run in background)"
"✓ SRP Agent: Analyzed 1,247 files, 156 violations"
"✓ OCP Agent: Analyzed 1,247 files, 89 violations"
"✓ LSP Agent: Analyzed 1,247 files, 23 violations"
"✓ ISP Agent: Analyzed 1,247 files, 67 violations"
"✓ DIP Agent: Analyzed 1,247 files, 112 violations"
"📁 Reports generated (no code modified):"
"  - solid-analysis-2024-01-15-143022.md (main report)"
"  - solid-srp-2024-01-15-143022.md (156 violations)"
"  - solid-ocp-2024-01-15-143022.md (89 violations)"
"  - solid-lsp-2024-01-15-143022.md (23 violations)"
"  - solid-isp-2024-01-15-143022.md (67 violations)"
"  - solid-dip-2024-01-15-143022.md (112 violations)"
"✅ Analysis complete - 447 violations documented"
"📊 Summary: Grade C+ | Top priority: SRP (156)"
"View: cat .reports/solid-analysis-2024-01-15-143022.md"
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

## Safety and Autonomy Guarantees

### 🔒 This Command is Completely Safe
- **Read-Only Operation**: Never modifies source code
- **No Permissions Required**: No dialogs or confirmations needed
- **No User Interaction**: Runs start-to-finish autonomously
- **Report Generation Only**: Only creates report files in `.reports/`
- **Background Safe**: Can run in CI/CD pipelines or cron jobs
- **Walk-Away Execution**: Start it and leave - it handles everything

### Ideal Use Cases for Headless Mode
1. **Pre-meeting Reports**: Run before code reviews to have violations ready
2. **Scheduled Audits**: Set up weekly/monthly SOLID compliance checks
3. **CI/CD Integration**: Add to build pipelines for automatic reporting
4. **Background Analysis**: Run while working on other tasks
5. **Remote Execution**: SSH in, start command, disconnect safely

### What Happens When You Run /solid
1. Command starts immediately (no permission prompts)
2. Agents analyze code in parallel (read-only)
3. Reports are generated automatically
4. Files saved to `.reports/` directory
5. Summary displayed with file locations
6. Command exits cleanly
7. You read reports at your convenience

## Notes
- Agents run in parallel for maximum speed
- Results are cached for 1 hour to avoid redundant analysis
- Command respects existing design linting configuration
- Integrates with make design-lint and existing tooling
- Reports directory (`.reports/`) is automatically created and gitignored
- Large reports (≥50 violations) are automatically saved to files
- Individual principle reports saved when violations exceed 20 per principle
- **HEADLESS MODE**: No permissions, no interactions, no code changes - just reports
