---
description: Create a new code file with proper structure and error handling
argument-hint: filename and description
---

Before creating any code, please:

1. **Review the AI Index**: Consult `.ai/index.json` for quick navigation, then `.ai/index_expanded.md` for detailed understanding
2. **Check Standards**: Reference `.ai/docs/STANDARDS.md` for development guidelines
3. **Select Template**: Choose appropriate template from `.ai/templates/` based on file type:
   - `linting-rule.py.template` - For design linting rules
   - `react-component.tsx.template` - For React components
   - `web-tab.tsx.template` - For new web application tabs
   - `fastapi-endpoint.py.template` - For API endpoints
   - `test-suite.py.template` - For comprehensive testing
   - `workflow.html.template` - For documentation workflows

4. **Understand Features**: Review relevant feature documentation in `.ai/features/`:
   - `design-linters.md` - For linting framework extensions
   - `web-application.md` - For frontend/backend development
   - `development-tooling.md` - For build system integration
   - `claude-integration.md` - For AI workflow enhancement
   - `testing-framework.md` - For test development

Create a new code file named $ARGUMENTS with:

1. **Template-Based Generation**: Use appropriate template from `.ai/templates/`
2. **Standards Compliance**: Follow `.ai/docs/STANDARDS.md` requirements
3. **File Header**: Include comprehensive header per `.ai/docs/FILE_HEADER_STANDARDS.md`
4. **Error Handling**: Implement robust error handling patterns
5. **Type Safety**: Use TypeScript for frontend, type hints for Python
6. **Testing**: Consider corresponding test file creation
7. **Documentation**: Include inline documentation and usage examples
8. **Integration**: Ensure proper integration with existing project architecture

**Template Variables**: Replace all `{{PLACEHOLDER}}` variables with project-specific values based on:
- Project context from `.ai/index.md`
- Existing code patterns in relevant directories
- Feature requirements from `.ai/features/`
- Standards from `.ai/docs/`

Make the code production-ready with proper structure, comprehensive error handling, and full compliance with project standards.
