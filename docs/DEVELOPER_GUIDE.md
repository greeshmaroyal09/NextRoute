# Developer Guide

## Architecture
NextRoute follows strict **Clean Architecture** patterns.
- Backend: Domain -> Application (Use Cases) -> Infrastructure -> Presentation.
- Frontend: Core -> Shared -> Features (Feature-First architecture).

## Workflow
1. Make changes to an Engine in `backend/app/engines`.
2. Run `pytest` to ensure no routing algorithms break.
3. Use `ruff check --fix .` before committing Python code.
