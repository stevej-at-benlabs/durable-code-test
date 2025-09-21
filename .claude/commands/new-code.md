---
description: Create a new code file with proper structure and error handling
argument-hint: filename and description
---

**CRITICAL: Follow this EXACT order when creating new code:**

**Step 1 - ALWAYS FIRST**: Read `.ai/index.json` BEFORE doing anything else. This is mandatory. No searches, no file reads, no other actions until the index has been consulted.

**Step 2 - Consult Layout Rules**: Read `.ai/layout.json` to determine the correct location for the new file based on its type and purpose. This is MANDATORY before any file creation.

**Step 3 - Check Current Branch**: Ensure we are not on the main branch. If we are on main:
  - Ask the user for a description of the change they want to make
  - Create a new branch with a descriptive name based on that description
  - Switch to the new branch before proceeding

**Step 4 - Validate File Placement**: Based on `.ai/layout.json`:
  - Verify the target directory exists or should be created
  - Confirm the file type is allowed in the target directory
  - Check for any forbidden patterns or restrictions
  - If placement violates rules, suggest the correct location

**Step 5 - Use Index for Navigation**: Based on `.ai/index.json`, identify the relevant templates, standards, and existing patterns. Then consult `.ai/index_expanded.md` for detailed understanding of the specific areas identified.

**Step 6 - Check Standards**: Reference `.ai/docs/STANDARDS.md` for development guidelines (as indicated by the index).

**Step 7 - Select Template**: Choose appropriate template from `.ai/templates/` based on the index guidance and file type:
   - `linting-rule.py.template` - For design linting rules
   - `react-component.tsx.template` - For React components
   - `web-tab.tsx.template` - For new web application tabs
   - `fastapi-endpoint.py.template` - For API endpoints
   - `test-suite.py.template` - For comprehensive testing
   - `workflow.html.template` - For documentation workflows

**Step 8 - Understand Features**: Review relevant feature documentation in `.ai/features/` as directed by the index:
  - `design-linters.md` - For linting framework extensions
  - `web-application.md` - For frontend/backend development
  - `development-tooling.md` - For build system integration
  - `claude-integration.md` - For AI workflow enhancement
  - `testing-framework.md` - For test development

**Step 9 - Create Code**: After completing ALL above steps, create a new code file named $ARGUMENTS with:

- **Template-Based Generation**: Use appropriate template from `.ai/templates/`
- **Standards Compliance**: Follow `.ai/docs/STANDARDS.md` requirements
- **File Header**: Include comprehensive header per `.ai/docs/FILE_HEADER_STANDARDS.md`
- **Error Handling**: Implement robust error handling patterns
- **Type Safety**: Use TypeScript for frontend, type hints for Python
- **Testing**: Consider corresponding test file creation
- **Documentation**: Include inline documentation and usage examples
- **Integration**: Ensure proper integration with existing project architecture

**Template Variables**: Replace all `{{PLACEHOLDER}}` variables with project-specific values based on:
- Project context from `.ai/index.md`
- Existing code patterns in relevant directories
- Feature requirements from `.ai/features/`
- Standards from `.ai/docs/`

Make the code production-ready with proper structure, comprehensive error handling, and full compliance with project standards.

**REMEMBER**:
- The `.ai/index.json` file is your PRIMARY navigation tool. Always read it FIRST before any searches, grep operations, or file reads.
- The `.ai/layout.json` file is your AUTHORITATIVE source for file placement. MUST be consulted before creating any files.
- File placement rules in layout.json override any template location suggestions.
