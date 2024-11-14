import os
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from main import app, get_session

# Test Database URL (make sure this points to your test database)
TEST_DATABASE_URL = "postgresql://fcasadei:7IGc540zOTX04ET@mstorage-svc:5432/dataset_schema"

# Set up a test client
client = TestClient(app)

# Create the test database engine
engine = create_engine(TEST_DATABASE_URL)

# Directory where example test files are located
current_dir = Path(__file__).resolve().parent

# Override the get_session to use the real test database
def get_test_session():
    with Session(engine) as session:
        yield session

# Apply the test session override
app.dependency_overrides[get_session] = get_test_session

# Set up and tear down for the test database
@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Create tables in the test database
    SQLModel.metadata.create_all(engine)
    yield
    # Drop all tables after tests
    SQLModel.metadata.drop_all(engine)

def test_create_schema_success():
    """Test uploading a valid JSON schema file."""
    schema_path = current_dir / "Example_data" / "AML_schema.json"
    
    assert schema_path.exists(), f"Test file not found: {schema_path}"

    with open(schema_path, "rb") as schema_file:
        response = client.post(
            "/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")}
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Schema for AML created successfully"}

def test_update_schema_success():
    """Test updating an existing schema."""
    schema_path = current_dir / "Example_data" / "AML_schema.json"
    
    assert schema_path.exists(), f"Test file not found: {schema_path}"

    with open(schema_path, "rb") as schema_file:
        response = client.put(
            "/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")}
        )

    assert response.status_code == 200
    assert response.json() == {"message": "Schema for AML updated successfully"}

def test_get_schema_success():
    """Test retrieving an existing schema."""
    response = client.get("/schema/AML")
    
    assert response.status_code == 200
    assert "schema" in response.json()
    assert response.json()["disease"] == "AML"

#def test_get_schema_not_found():
#    """Test retrieving a schema that does not exist."""
#    response = client.get("/schema/NonExistentDisease")

#    assert response.status_code == 404
#    assert response.json() == {"detail": "No schema found for disease: NonExistentDisease"}

#def test_get_all_schemas_success():
#    """Test retrieving all schemas."""
#    response = client.get("/schemas")

#    assert response.status_code == 200
#    assert isinstance(response.json(), list)

def test_delete_schema_success():
    """Test deleting an existing schema."""
    response = client.delete("/schema/AML")

    assert response.status_code == 200
    assert response.json() == {"message": "Schema for disease 'AML' deleted successfully"}

#def test_delete_schema_not_found():
#    """Test deleting a schema that doesn't exist."""
#    response = client.delete("/schema/NonExistentDisease")

#    assert response.status_code == 404
#    assert response.json() == {"detail": "Schema for disease 'NonExistentDisease' not found"}
