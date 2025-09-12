# Development Standards and Best Practices

## Python Backend Standards

### 1. Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/   # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings and configuration
│   │   └── security.py      # Security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py        # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── business.py      # Business logic
│   └── db/
│       ├── __init__.py
│       └── session.py       # Database connection
├── tests/
├── pyproject.toml
└── .env
```

### 2. Code Style and Formatting
- **Formatter**: Black with line length 88
- **Linter**: Ruff with default configuration
- **Type Checker**: MyPy with strict mode
- **Docstrings**: Google style docstrings for all public functions/classes
- **Naming Conventions**:
  - Classes: PascalCase
  - Functions/Variables: snake_case
  - Constants: UPPER_SNAKE_CASE
  - Private methods: _leading_underscore

### 3. API Design Principles
- RESTful conventions with proper HTTP methods
- Version API endpoints (/api/v1/)
- Use Pydantic models for request/response validation
- Implement proper error handling with meaningful status codes
- Document all endpoints with OpenAPI/Swagger

### 4. Testing Requirements
- Minimum 80% code coverage
- Use pytest for all tests
- Test file naming: test_*.py
- Use fixtures for common test data
- Mock external dependencies

### 5. Security Best Practices
- Never hardcode secrets
- Use environment variables for configuration
- Implement proper authentication/authorization
- Validate all inputs with Pydantic
- Use parameterized queries for database operations
- Enable CORS with specific origins only

### 6. Error Handling
- Use custom exception classes
- Implement global exception handlers
- Return consistent error response format:
  ```python
  {
      "error": {
          "code": "ERROR_CODE",
          "message": "Human readable message",
          "details": {}
      }
  }
  ```

### 7. Dependency Management
- Use Poetry for dependency management
- Pin exact versions in pyproject.toml
- Separate dev dependencies
- Regular security updates

## React Frontend Standards

### 1. Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable components
│   │   └── features/        # Feature-specific components
│   ├── pages/               # Page components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API services
│   ├── store/               # State management
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── styles/              # Global styles
│   ├── App.tsx
│   └── main.tsx
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env
```

### 2. Code Style and Formatting
- **Formatter**: Prettier with 2 space indentation
- **Linter**: ESLint with recommended rules
- **TypeScript**: Strict mode enabled
- **Import Order**:
  1. React imports
  2. Third-party libraries
  3. Internal absolute imports
  4. Relative imports
  5. Style imports

### 3. Component Guidelines
- **Functional Components Only**: Use hooks instead of class components
- **Component Structure**:
  ```typescript
  // 1. Imports
  // 2. Type definitions
  // 3. Component definition
  // 4. Styled components (if using CSS-in-JS)
  ```
- **Naming Conventions**:
  - Components: PascalCase
  - Props interfaces: ComponentNameProps
  - Hooks: use prefix (useCustomHook)
  - Event handlers: handle prefix (handleClick)
  - Boolean props: is/has/should prefix

### 4. TypeScript Best Practices
- Define explicit types for all props
- Avoid using `any` type
- Use interfaces for object types
- Use type for unions and primitives
- Export types from their usage location

### 5. State Management
- Use React Context for global state
- Use local state for component-specific data
- Use custom hooks for reusable stateful logic
- Implement proper loading and error states

### 6. API Integration
- Centralize API calls in services directory
- Use environment variables for API URLs
- Implement proper error handling
- Add request/response interceptors
- Type all API responses

### 7. Performance Optimization
- Use React.memo for expensive components
- Implement lazy loading for routes
- Use useMemo and useCallback appropriately
- Optimize bundle size with code splitting
- Minimize re-renders

### 8. Testing Requirements
- Unit tests for utilities and hooks
- Component testing with React Testing Library
- Integration tests for critical user flows
- Maintain 70% code coverage minimum

### 9. Accessibility Standards
- Use semantic HTML elements
- Provide proper ARIA labels
- Ensure keyboard navigation
- Maintain proper heading hierarchy
- Test with screen readers

### 10. CSS Guidelines
- Use CSS Modules or styled-components
- Follow BEM naming for class names
- Use CSS variables for theming
- Mobile-first responsive design
- Avoid inline styles

## File Placement and Organization Standards

### 1. Root-Level Files
**Allowed files only:**
- Configuration files: `.gitignore`, `.env.example`, `docker-compose.yml`, `Makefile`, `README.md`
- Project setup files: `pyproject.toml`, `package.json` (for monorepo package managers)
- CI/CD files: `.pre-commit-config.yaml`, `.github/` directory contents
- IDE configurations: `.vscode/`, `.idea/` (optional)

**Prohibited at root:**
- Source code files (`.py`, `.js`, `.ts`, `.tsx`, `.html`, `.css`)
- Test files (`test_*.py`, `*.test.js`, `*.spec.ts`)
- Build artifacts (`dist/`, `build/`, compiled files)

### 2. Python Files Placement
```
├── durable-code-app/backend/
│   ├── app/                    # Application source code
│   │   ├── *.py               # Python modules
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Data models
│   │   ├── services/          # Business logic
│   │   └── core/              # Core functionality
│   └── docs/                  # Module-specific documentation
├── tools/                     # Development and build tools
│   └── *.py                   # Python utility scripts
└── test/                      # ALL project tests (unified location)
    ├── unit_test/             # Unit tests for all components
    │   ├── tools/             # Tests for tools/ directory
    │   ├── backend/           # Tests for backend components
    │   └── frontend/          # Tests for frontend components
    └── integration_test/      # Integration tests
```

**Important**: All test files should be in the root `test/` directory, organized by component being tested. This provides a unified testing structure across the entire project.

### 3. Frontend Files Placement
```
├── durable-code-app/frontend/
│   ├── src/                   # Source code
│   │   ├── *.tsx, *.ts        # TypeScript/React files
│   │   ├── *.css              # Stylesheets
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API services
│   │   ├── types/             # Type definitions
│   │   └── utils/             # Utility functions
│   ├── public/                # Static assets
│   │   ├── *.html             # HTML templates (index.html only)
│   │   ├── *.svg, *.png       # Static images
│   │   └── *.ico              # Favicons
│   ├── tests/                 # Test files
│   │   ├── *.test.tsx         # Component tests
│   │   ├── *.spec.ts          # Unit tests
│   │   └── __tests__/         # Test directories
│   └── dist/                  # Build output (generated)
```

### 4. HTML Files Placement Rules
- **Main Template**: `frontend/index.html` (Vite entry point - required in frontend root)
- **Static HTML**: `frontend/public/` for additional static pages
- **Documentation HTML**: `docs/` directory only
- **Build Output**: `frontend/dist/` (auto-generated)
- **Component HTML**: Should be React/JSX components in `frontend/src/components/`

**Prohibited locations:**
- Root directory
- Backend directories
- Direct in `src/` without component structure

**Note**: `index.html` must be in the frontend root directory as required by Vite.

### 5. Test Files Organization
```
├── test/                      # ALL project tests (unified structure)
│   ├── unit_test/            # Unit tests organized by component
│   │   ├── tools/            # Tests for tools/ directory
│   │   │   ├── test_magic_number_detector.py
│   │   │   └── test_srp_analyzer.py
│   │   ├── backend/          # Tests for backend components
│   │   │   ├── app/          # Tests for backend app
│   │   │   ├── api/          # API endpoint tests
│   │   │   └── models/       # Model tests
│   │   └── frontend/         # Tests for frontend components
│   │       ├── components/   # Component tests
│   │       └── utils/        # Utility function tests
│   ├── integration_test/     # Integration tests
│   │   ├── backend/          # Backend integration tests
│   │   └── frontend/         # Frontend integration tests
│   └── fixtures/             # Test data and fixtures
└── durable-code-app/frontend/tests/ # Frontend-specific tests (if needed)
    └── e2e/                  # End-to-end tests only
```

**Key Principles:**
- **Unified Structure**: All tests in root `test/` directory
- **Component Organization**: Tests organized by what they test, not where they run
- **Clear Separation**: Unit tests, integration tests, and fixtures clearly separated
- **Frontend Exception**: Only E2E tests can remain in frontend/tests/ if needed for tooling

### 6. Documentation Files
- **Project docs**: `docs/` directory
- **Component docs**: Next to source files or in module `docs/` subdirectory
- **API docs**: Auto-generated in `durable-code-app/backend/docs/`
- **README files**: Each major directory can have one README.md

### 7. Configuration Files Hierarchy
```
├── .env.example               # Global environment template
├── .pre-commit-config.yaml    # Global pre-commit
├── durable-code-app/
│   ├── backend/
│   │   ├── pyproject.toml     # Python dependencies
│   │   ├── .flake8           # Python linting config
│   │   └── .env              # Backend-specific env (gitignored)
│   └── frontend/
│       ├── package.json       # Node dependencies
│       ├── tsconfig.json      # TypeScript config
│       ├── vite.config.ts     # Build tool config
│       └── .env              # Frontend-specific env (gitignored)
```

### 8. File Placement Validation Rules
The custom file placement linter enforces these rules:
- **Python files**: Must be in `app/`, `tools/`, or root `test/` directories
- **HTML files**: Must be in `frontend/`, `frontend/public/`, `frontend/dist/`, or `docs/`
- **TypeScript/React**: Must be in `frontend/src/` or `frontend/tests/` (E2E only)
- **CSS files**: Must be in `frontend/src/` or `frontend/public/`
- **Test files**: Must be in root `test/` directory with proper organization
- **Config files**: Must be in designated locations based on scope and purpose

**Critical Rule**: All test files must be in the root `test/` directory, organized by component being tested, not by technology stack.

## General Development Practices

### 1. Version Control
- Commit messages: type(scope): description
- Types: feat, fix, docs, style, refactor, test, chore
- Keep commits atomic and focused
- Write descriptive PR descriptions

### 2. Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No hardcoded values
- [ ] Error handling is implemented
- [ ] Security considerations addressed
- [ ] Performance impact considered

### 3. Documentation Requirements
- README with setup instructions
- API documentation
- Component documentation
- Architecture decision records
- Deployment guides

### 4. Development Workflow
1. Create feature branch from main
2. Write tests first (TDD approach)
3. Implement feature
4. Run linters and formatters
5. Ensure all tests pass
6. Update documentation
7. Create pull request
8. Address review feedback
9. Merge after approval

### 5. Performance Monitoring
- Implement logging for errors
- Monitor API response times
- Track frontend performance metrics
- Set up alerts for critical issues

### 6. Security Checklist
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] Authentication required where needed
- [ ] HTTPS enforced
- [ ] Dependencies updated
- [ ] Security headers configured
- [ ] Rate limiting implemented

## Continuous Integration/Deployment

### 1. Pre-commit Hooks
- Format code automatically
- Run linters
- Check for secrets
- Verify commit message format

### 2. CI Pipeline
- Run tests on every PR
- Check code coverage
- Run security scans
- Build validation
- Deploy to staging

### 3. Production Deployment
- Require PR approval
- Run full test suite
- Deploy with rollback capability
- Monitor after deployment
- Update documentation

## Code Quality Metrics
- Code coverage: >75%
- Cyclomatic complexity: <10
- Duplication: <3%
- Technical debt ratio: <5%
- Bundle size limits enforced