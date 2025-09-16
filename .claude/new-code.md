# New Code Command

## Purpose

This command ensures all new code adheres to the established development standards before implementation.

## Pre-Implementation Checklist

Before writing any new code, I will:

### 1. Review Documentation

- Read all documents in the `/docs/` folder to understand:
  - Development standards and best practices (`STANDARDS.md`)
  - Design principles and linting requirements (`DESIGN_PRINCIPLES_LINTING.md`)
  - File header standards (`FILE_HEADER_STANDARDS.md`)
  - CSS layout guidelines (`CSS_LAYOUT_STABILITY.md`)
  - Branch protection requirements (`BRANCH_PROTECTION.md`)
- Identify relevant sections for the current task
- Note specific requirements for the language/framework being used

### 2. Analyze Existing Codebase

- Check existing code patterns in similar files
- Identify naming conventions in use
- Review import structures and dependencies
- Understand the current testing approach

### 3. Plan Implementation

- Define the component/module structure
- Identify required types/interfaces
- Plan error handling approach
- Determine testing strategy

## Implementation Process

### For Python Backend Code:

1. **Structure Check**
   - Verify proper module placement according to project structure
   - Ensure **init**.py files exist where needed

2. **Code Standards**
   - Apply Black formatting (88 char line length)
   - Follow snake_case naming conventions
   - Add Google-style docstrings
   - Implement type hints

3. **API Endpoints**
   - Use proper RESTful conventions
   - Add Pydantic models for validation
   - Include error handling
   - Document with OpenAPI annotations

4. **Testing**
   - Write pytest tests first (TDD)
   - Use fixtures for test data
   - Mock external dependencies
   - Aim for >80% coverage

5. **Security**
   - No hardcoded secrets
   - Validate all inputs
   - Use parameterized queries

### For React Frontend Code:

1. **Component Creation**
   - Place in appropriate directory (components/pages/hooks)
   - Use functional components with hooks
   - Define TypeScript interfaces for props

2. **Code Standards**
   - Apply Prettier formatting (2 spaces)
   - Follow PascalCase for components
   - Organize imports properly
   - Add proper TypeScript types

3. **State Management**
   - Use appropriate state solution (local/context)
   - Implement loading and error states
   - Create custom hooks for reusable logic

4. **Testing**
   - Write React Testing Library tests
   - Test user interactions
   - Mock API calls
   - Aim for >70% coverage

5. **Performance & Accessibility**
   - Use React.memo where appropriate
   - Implement lazy loading
   - Add ARIA labels
   - Ensure keyboard navigation

## Validation Steps

After writing code, verify:

### Code Quality

- [ ] Runs without errors
- [ ] Passes all linting checks
- [ ] Formatted correctly
- [ ] Type checking passes
- [ ] No console.logs or debugging code

### Testing

- [ ] All tests pass
- [ ] Coverage meets requirements
- [ ] Edge cases handled
- [ ] Error scenarios tested

### Documentation

- [ ] Functions/components documented
- [ ] Complex logic explained
- [ ] API endpoints documented
- [ ] README updated if needed

### Security

- [ ] No exposed secrets
- [ ] Input validation present
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies are secure

## Command Execution

When this command is invoked, I will:

1. **First Step - Documentation Review**

   ```
   Read all files in /docs/ folder
   Focus on standards, principles, and requirements relevant to task
   ```

2. **Second Step - Context Analysis**

   ```
   Analyze existing code in the target directory
   Check for patterns and conventions
   ```

3. **Third Step - Implementation**

   ```
   Write code following all identified standards
   Include proper error handling
   Add comprehensive documentation
   ```

4. **Fourth Step - Testing**

   ```
   Write and run tests
   Verify coverage requirements
   Fix any issues found
   ```

5. **Final Step - Validation**
   ```
   Run linters and formatters
   Check type safety
   Ensure all standards are met
   ```

## Error Handling

If standards are not met:

- Identify specific violations
- Fix issues before proceeding
- Re-run validation checks
- Document any exceptions with justification

## Continuous Improvement

After each use:

- Note any missing standards
- Update STANDARDS.md if needed
- Refine this command based on experience
- Share learnings with team

## Usage Example

```
User: Create a new API endpoint for user authentication

Claude will:
1. Read all docs (standards, design principles, file headers, etc.)
2. Check existing auth code patterns
3. Create endpoint with:
   - Proper file structure
   - Pydantic models
   - Error handling
   - Security measures
   - Tests
   - Documentation
4. Validate all standards are met
```

## Notes

- This command prioritizes code quality over speed
- All code must be production-ready
- Standards are non-negotiable unless explicitly overridden
- Focus on maintainability and durability
