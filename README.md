# Durable Code Test

A demonstration project showcasing AI-assisted development with strong coding standards and best practices.

## Project Structure

```
.
├── durable-code-app/
│   ├── frontend/          # React + TypeScript + Vite
│   └── backend/           # Python + FastAPI + Poetry
├── docs/
│   └── STANDARDS.md       # Comprehensive development standards
└── .claude/
    └── new-code.md        # Claude command for enforcing standards
```

## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- CSS Modules

### Backend
- Python 3.11+
- FastAPI
- Poetry
- Pydantic

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Poetry

### Backend Setup
```bash
cd durable-code-app/backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd durable-code-app/frontend
npm install
npm run dev
```

## Development Standards

All code in this project follows strict standards defined in `/docs/STANDARDS.md`. These standards ensure:
- Consistent code style
- Comprehensive testing
- Security best practices
- Performance optimization
- Maintainability

## Claude Integration

This project includes a custom Claude command (`.claude/new-code.md`) that ensures all new code adheres to established standards. When writing new code, Claude will:

1. Review the standards document
2. Analyze existing code patterns
3. Implement with proper structure and style
4. Include comprehensive tests
5. Validate all requirements are met

## License

MIT