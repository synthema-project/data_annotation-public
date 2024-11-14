import os
import json
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session
from models import Schema

# Set up an SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for testing
engine = create_engine(TEST_DATABASE_URL, echo=True)

# Path for example data
current_dir = Path(__file__).resolve().parent

# Create a new SQLite session for testing
def override_get_session():
    with Session(engine) as session:
        yield session

# Override the session dependency to use the SQLite database instead of PostgreSQL
app.dependency_overrides[get_session] = override_get_session

# Create database and tables for the test
def create_test_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Test client for FastAPI
client = TestClient(app)

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_schema():
    create_test_db_and_tables()  # Ensure the database is set up before running the test
    schema_path = current_dir / "Example_data" / "AML_schema.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            "/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert response.json() == {"message": "Schema for AML created successfully"}
    print('SCHEMA CREATED SUCCESSFULLY')

def test_get_schema():
    response = client.get("/schema/AML")
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "AML"
    assert isinstance(data["schema"], dict)
    print('SCHEMA GOT SUCCESSFULLY')

def test_update_schema():
    schema_path = current_dir / "Example_data" / "AML_schema_updated.json"
    with open(schema_path, "rb") as schema_file:
        response = client.put(
            "/schema?disease=AML",
            files={"file": ("AML_schema_updated.json", schema_file, "application/json")},
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for AML updated successfully"}
    print('SCHEMA UPDATED SUCCESSFULLY')

def test_delete_schema():
    response = client.delete("/schema/AML")
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for disease 'AML' deleted successfully"}
    print('SCHEMA DELETED SUCCESSFULLY')
