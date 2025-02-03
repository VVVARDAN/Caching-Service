import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from fast_api import app, get_session, CachedResult, Payload

# Test database setup
test_database_url = "sqlite:///./test_cache.db"
test_engine = create_engine(test_database_url, echo=True)
SQLModel.metadata.create_all(test_engine)

def get_test_session():
    """
    Provides a session connected to the test database.
    """
    with Session(test_engine) as session:
        yield session

# Override the dependency in FastAPI app
app.dependency_overrides[get_session] = get_test_session

# Create a test client
client = TestClient(app)

def test_create_payload_success():
    """
    Tests successful creation of a payload with valid input lists.
    """
    payload_data = {
        "list_1": ["hello", "world"],
        "list_2": ["fastapi", "test"]
    }
    response = client.post("/payload", json=payload_data)
    assert response.status_code == 200
    assert "identifier" in response.json()

def test_create_payload_mismatched_lists():
    """
    Tests failure case where input lists have different lengths.
    """
    payload_data = {
        "list_1": ["hello", "world"],
        "list_2": ["fastapi"]
    }
    response = client.post("/payload", json=payload_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Lists must be of the same length."

def test_read_existing_payload():
    """
    Tests retrieval of an existing payload.
    """
    payload_data = {
        "list_1": ["test1", "test2"],
        "list_2": ["test3", "test4"]
    }
    create_response = client.post("/payload", json=payload_data)
    identifier = create_response.json()["identifier"]
    
    response = client.get(f"/payload/{identifier}")
    assert response.status_code == 200
    assert "output" in response.json()

def test_read_nonexistent_payload():
    """
    Tests retrieval of a non-existent payload.
    """
    response = client.get("/payload/nonexistent_identifier")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payload not found."

if __name__ == "__main__":
    pytest.main()
