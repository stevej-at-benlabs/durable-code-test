---
description: AI-powered Q&A system for project knowledge and guidance
argument-hint: your question about the project
---

I'll answer your question about the Durable Code Test project using comprehensive project knowledge.

**CRITICAL: I will ALWAYS follow this exact order:**

1. **FIRST - Read Project Index**: I MUST read `.ai/index.json` BEFORE doing anything else. This provides the navigation map for the entire project.

2. **SECOND - Use Index to Navigate**: Based on the index, I'll identify which specific files or sections are relevant to your question, then navigate to those specific locations.

3. **THIRD - Check Relevant Features**: Reference appropriate documentation in `.ai/features/` as identified by the index:
   - `design-linters.md` - Linting framework and rule system
   - `web-application.md` - Frontend/backend architecture
   - `development-tooling.md` - Build system and automation
   - `claude-integration.md` - AI workflow integration
   - `testing-framework.md` - Quality assurance infrastructure

4. **Reference Standards**: Check `.ai/docs/` for relevant guidelines as indicated by the index:
   - `STANDARDS.md` - Development standards and best practices
   - `FILE_HEADER_STANDARDS.md` - Documentation requirements
   - `CSS_LAYOUT_STABILITY.md` - Frontend guidelines
   - `BRANCH_PROTECTION.md` - Git workflow standards

5. **Examine Implementation**: ONLY after checking the index, look at actual code files for accurate, current information
6. **Consider Templates**: Reference `.ai/templates/` for implementation patterns as directed by the index

**Important**: I will NOT perform generic searches or grep operations before consulting the index. The `.ai/index.json` file is the authoritative navigation guide and MUST be consulted first.

**Your Question**: $ARGUMENTS

**My Answer**: [I'll provide a comprehensive answer based on project documentation, implementation files, and current codebase state]

**What I can help with:**

🔧 **Development Questions**
- How to implement new features using existing patterns
- Code generation guidance using project templates
- Build system usage and Make target explanations
- Docker environment setup and troubleshooting

🏗️ **Architecture Questions**
- Project structure and component relationships
- Integration points between frontend and backend
- Database and service architecture decisions
- Scalability and performance considerations

🧪 **Testing and Quality**
- Test suite organization and execution
- Linting rule configuration and usage
- CI/CD pipeline setup and troubleshooting
- Code quality standards and enforcement

🤖 **AI Integration**
- Claude command usage and customization
- Template selection and customization
- Workflow automation opportunities
- Standards enforcement automation

📋 **Standards and Best Practices**
- Project coding standards interpretation
- File organization and naming conventions
- Documentation requirements and patterns
- Git workflow and branch management

🔍 **Code Understanding**
- Existing feature functionality and usage
- Component interaction and data flow
- Configuration system usage
- Extension and customization points

**Response Format**: I will provide:
- Direct answer to your specific question
- Relevant code examples and file references
- Links to documentation sections
- Step-by-step guidance when appropriate
- Alternative approaches or considerations
- Related topics you might find helpful

**Note**: All answers are based on current project state and documentation. If you need information about external dependencies or general programming concepts, I'll clarify when answering beyond project scope.
