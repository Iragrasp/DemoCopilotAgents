"""
DAY 1 · SESSION 3 — Copilot Agents
=====================================
This is the TARGET app the Copilot Agent builds from a single prompt.

▶ DEMO PROMPT (paste into Copilot Agent mode):
─────────────────────────────────────────────────────────────────────
Create a FastAPI REST API for user management:
1. POST /api/users  — accepts {name, email, role} JSON body
                      validates email format
                      saves to SQLite via SQLAlchemy
                      returns 201 with the created user or 422 on validation error
2. GET  /api/users  — returns all users as a JSON list
3. GET  /api/users/{id} — returns single user or 404
Include:
  - SQLAlchemy ORM model in models.py
  - Database setup in database.py
  - Routes in routes/users.py
  - Unit tests using pytest + httpx in tests/test_api.py
─────────────────────────────────────────────────────────────────────

The Agent creates ALL these files automatically. Below is the result.
Run it with:  uvicorn day1.session3_agents.app:app --reload --port 8000
"""
from fastapi import FastAPI
from day1.session3_agents.database import engine, Base
from day1.session3_agents.routes.users import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Management API", version="1.0.0")
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "User Management API — Copilot Agent Demo",
        "docs": "/docs",
        "endpoints": ["POST /api/users", "GET /api/users", "GET /api/users/{id}"],
    }
