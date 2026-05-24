"""
tests/test_api.py — Agent-generated tests.
Run:  pytest day1/session3_agents/tests/test_api.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from day1.session3_agents.app import app
from day1.session3_agents.database import Base, get_db

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DB_URL = "sqlite://"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


client = TestClient(app)


def test_create_user_success():
    resp = client.post("/api/users", json={"name": "Alice", "email": "alice@acme.com", "role": "admin"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@acme.com"
    assert body["role"]  == "admin"
    assert "id" in body


def test_create_user_invalid_email():
    resp = client.post("/api/users", json={"name": "Bob", "email": "not-an-email", "role": "viewer"})
    assert resp.status_code == 422


def test_create_user_invalid_role():
    resp = client.post("/api/users", json={"name": "Carol", "email": "carol@x.com", "role": "superuser"})
    assert resp.status_code == 422


def test_create_user_duplicate_email():
    client.post("/api/users", json={"name": "Dave",  "email": "dave@x.com", "role": "viewer"})
    resp = client.post("/api/users", json={"name": "Dave2", "email": "dave@x.com", "role": "viewer"})
    assert resp.status_code == 409


def test_list_users_empty():
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_users_after_create():
    client.post("/api/users", json={"name": "Eve", "email": "eve@x.com", "role": "viewer"})
    resp = client.get("/api/users")
    assert len(resp.json()) == 1


def test_get_user_not_found():
    resp = client.get("/api/users/nonexistent-id")
    assert resp.status_code == 404


def test_get_user_success():
    created = client.post("/api/users", json={"name": "Frank", "email": "frank@x.com"}).json()
    resp = client.get(f"/api/users/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Frank"
