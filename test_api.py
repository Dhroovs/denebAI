import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from main import app

# Use a separate test database file.
TEST_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture to build and tear down database tables.
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up the file test.db after testing completes.
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except PermissionError:
            pass


# Fixture to provide a clean database session per test.
@pytest.fixture
def db():
    # Clear tables to start with a fresh state.
    db = TestingSessionLocal()
    db.query(models.KnowledgeBase).delete()
    db.query(models.Chatbot).delete()
    db.commit()
    try:
        yield db
    finally:
        db.close()


# Fixture to override FastAPI's get_db dependency.
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- TEST CASES ---

def test_create_chatbot(client):
    payload = {
        "name": "Deneb Navigator",
        "description": "Guides systems",
        "system_prompt": "Persona test",
        "model": "deneb-core-v1",
        "temperature": 0.5,
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Deneb Navigator"
    assert data["id"] is not None
    assert "created_at" in data


def test_create_chatbot_invalid_temp(client):
    payload = {
        "name": "Invalid Temp Bot",
        "model": "deneb-core-v1",
        "temperature": 1.2,  # Must be between 0.0 and 1.0
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 422  # Validation Error


def test_create_chatbot_invalid_model(client):
    payload = {
        "name": "Invalid Model Bot",
        "model": "gpt-99",  # Not supported model type
        "temperature": 0.5,
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 422  # Validation Error


def test_get_chatbot_details(client):
    # Setup test bot
    payload = {
        "name": "Search Target",
        "model": "deneb-core-v1",
        "temperature": 0.7
    }
    create_resp = client.post("/api/v1/chatbots/", json=payload)
    bot_id = create_resp.json()["id"]

    # Test GET
    response = client.get(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Search Target"

    # Test GET non-existent
    response = client.get("/api/v1/chatbots/99999")
    assert response.status_code == 404


def test_update_chatbot_details(client):
    # Setup
    payload = {"name": "Old Name", "model": "deneb-core-v1", "temperature": 0.5}
    bot_id = client.post("/api/v1/chatbots/", json=payload).json()["id"]

    # Test update
    update_payload = {"name": "New Name", "temperature": 0.9}
    response = client.put(f"/api/v1/chatbots/{bot_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["temperature"] == 0.9
    assert data["model"] == "deneb-core-v1"  # Retains old value


def test_delete_chatbot(client):
    # Setup
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Delete Me"}).json()["id"]

    # Test DELETE
    response = client.delete(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 204

    # Confirm it is gone
    response = client.get(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 404


def test_list_chatbots_pagination_and_search(client):
    # Seed 3 chatbots
    client.post("/api/v1/chatbots/", json={"name": "Alpha Coder", "model": "stellar-ultra", "is_active": True})
    client.post("/api/v1/chatbots/", json={"name": "Beta Creative", "model": "nebula-mini", "is_active": True})
    client.post("/api/v1/chatbots/", json={"name": "Gamma Helper", "model": "deneb-light-v1", "is_active": False})

    # Test List Pagination (page=1, size=2)
    response = client.get("/api/v1/chatbots/?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 3
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2
    assert data["page"] == 1
    assert data["size"] == 2

    # Test List Search
    response = client.get("/api/v1/chatbots/?search=Coder")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["name"] == "Alpha Coder"

    # Test List Filter status
    response = client.get("/api/v1/chatbots/?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["name"] == "Gamma Helper"


def test_create_knowledge_base(client):
    # Setup chatbot first
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Owner Bot"}).json()["id"]

    # Create KB
    kb_payload = {
        "name": "System Handbook",
        "description": "Rules of engagement",
        "data_source": "text",
        "content": "Line 1. Line 2.",
        "chatbot_id": bot_id
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "System Handbook"
    assert data["chatbot_id"] == bot_id


def test_create_kb_invalid_chatbot(client):
    kb_payload = {
        "name": "Orphan KB",
        "data_source": "text",
        "content": "No parent",
        "chatbot_id": 99999  # Non-existent ID
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_delete_chatbot_cascades_kb(client):
    # Setup bot and attach KB
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Target Bot"}).json()["id"]
    kb_id = client.post("/api/v1/knowledge-bases/", json={
        "name": "Linked Doc",
        "data_source": "text",
        "content": "Will be deleted",
        "chatbot_id": bot_id
    }).json()["id"]

    # Assert KB is reachable
    assert client.get(f"/api/v1/knowledge-bases/{kb_id}").status_code == 200

    # Delete Chatbot
    assert client.delete(f"/api/v1/chatbots/{bot_id}").status_code == 204

    # Assert KB is deleted automatically via DB cascade
    assert client.get(f"/api/v1/knowledge-bases/{kb_id}").status_code == 404
