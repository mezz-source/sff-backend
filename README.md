# SFF Bot Backend

A FastAPI backend for user accounts and text logs.

## What This Project Uses

- FastAPI for the HTTP API surface
- SQLAlchemy ORM with SQLite storage
- Pydantic for request validation at the API boundary
- msgspec Structs for service/core contracts
- JWT bearer tokens for authentication

## Documentation Sources (Homework Citations)

- FastAPI: https://fastapi.tiangolo.com/
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI Security (OAuth2/JWT patterns): https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- SQLAlchemy ORM 2.0: https://docs.sqlalchemy.org/en/20/orm/
- SQLAlchemy Relationships: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- SQLAlchemy Typed Mappings (Mapped/mapped_column): https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
- Pydantic Fields: https://docs.pydantic.dev/latest/concepts/fields/
- msgspec Structs: https://jcristharif.com/msgspec/structs.html
- JWT Standard (RFC 7519): https://datatracker.ietf.org/doc/html/rfc7519

## Project Layout

- src/main.py: app entrypoint for Uvicorn
- src/app.py: FastAPI app factory and router registration
- src/db/session.py: engine/session/Base and DB dependency
- src/models/: SQLAlchemy models
- src/schemas/: API request schemas (Pydantic)
- src/schemas/core/: service/core contracts (msgspec)
- src/repo/: data access layer
- src/services/: business logic layer
- src/security/: password hashing and JWT helpers
- src/api/routers/: HTTP routes
- src/util/response.py: unified response pipeline

## Response Envelope

All endpoints return a consistent envelope:

- code: status code label, for example SUCCESS, NOT_FOUND, ALREADY_EXISTS
- detail: human-readable summary
- result: payload object/list/null

Example success:

```json
{
  "code": "SUCCESS",
  "detail": "User retrieved successfully",
  "result": {
    "id": 1,
    "username": "camey",
    "created_at": "2026-04-13T20:40:11.123456"
  }
}
```

Example error:

```json
{
  "code": "ALREADY_EXISTS",
  "detail": "Username camey already exists",
  "result": null
}
```

## Authentication Flow

1. Register a user with POST /api/users/ and header X-User-Creation-Token
2. Login with POST /api/users/login to receive access_token
3. Send token in Authorization header:

```http
Authorization: Bearer <access_token>
```

4. Access protected routes such as /api/logs/ and /api/users/{id}

## API Endpoints

### Users

- POST /api/users/ (requires X-User-Creation-Token): create account
- POST /api/users/login (public): login and receive bearer token
- GET /api/users/{user_id} (auth): get own user
- PATCH /api/users/{user_id} (auth): modify own user
- DELETE /api/users/{user_id} (auth): delete own user

### Logs

- GET /api/logs/ (auth): list own logs
- GET /api/logs/{log_id} (auth): get one owned log
- POST /api/logs/ (auth): create log
- PATCH /api/logs/{log_id} (auth): modify owned log

## Quick Start

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

## 2) Required environment variables

- JWT_SECRET
- USER_CREATION_TOKEN

## 3) Optional environment variables

- DATABASE_URL (default: sqlite:///./sff.db)
- JWT_EXPIRE_MINUTES (default: 60)

Codespaces note:
- Store JWT_SECRET and USER_CREATION_TOKEN as Codespaces secrets.
- They are exposed as environment variables at runtime, so no dotenv file is required.

PowerShell example:

```powershell
$env:JWT_SECRET = "super-secret-value"
$env:USER_CREATION_TOKEN = "long-random-create-token"
$env:JWT_EXPIRE_MINUTES = "120"
```

## 4) Run the API

```bash
uvicorn src.main:app --reload
```

## 5) Open docs

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Request Examples

Create user:

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "X-User-Creation-Token: YOUR_CREATE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"camey","password":"securePass123"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"camey","password":"securePass123"}'
```

Create log (replace TOKEN):

```bash
curl -X POST http://127.0.0.1:8000/api/logs/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"first log entry"}'
```

## Notes

- Tables are auto-created at startup through Base.metadata.create_all(...).
- This is good for learning/dev. For production schema evolution, use Alembic migrations.
- Passwords are stored as PBKDF2-SHA256 hashes, never plaintext.
