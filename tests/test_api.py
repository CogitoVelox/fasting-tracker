import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_start_fast(client):
    response = client.post("/fasts")
    assert response.status_code == 201
    data = response.json()
    assert data["ended_at"] is None
    assert data["id"] == 1


def test_cannot_start_second_fast(client):
    client.post("/fasts")
    response = client.post("/fasts")
    assert response.status_code == 409


def test_end_fast(client):
    client.post("/fasts")
    response = client.patch("/fasts/1/end", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["ended_at"] is not None
    assert data["duration_seconds"] is not None


def test_cannot_end_already_ended_fast(client):
    client.post("/fasts")
    client.patch("/fasts/1/end", json={})
    response = client.patch("/fasts/1/end", json={})
    assert response.status_code == 409


def test_current_fast_when_none_open(client):
    response = client.get("/fasts/current")
    assert response.status_code == 404


def test_current_fast_when_one_open(client):
    client.post("/fasts")
    response = client.get("/fasts/current")
    assert response.status_code == 200
    assert response.json()["ended_at"] is None
