import os
import json
from pathlib import Path
import requests
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from main import app
from database import get_session
from models import Schema

# Set up an SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for testing
engine = create_engine(TEST_DATABASE_URL, echo=True)

# Path for example data
current_dir = Path(__file__).resolve().parent
example_data_dir = current_dir / "Example_data"

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

# Base URL for the API
#BASE_URL = "http://49.13.149.57:80" #"http://localhost:8000"  # Adjust the port if needed
BASE_URL = "http://data-annotation.k8s.synthema.rid-intrasoft.eu:80"

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_schema():
    create_test_db_and_tables()  # Ensure the database is set up before running the test
    schema_path = example_data_dir / "AML_schema.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            f"{BASE_URL}/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert response.json() == {"message": "Schema for AML created successfully"}

def test_get_schema():
    response = client.get(f"{BASE_URL}/schema/AML")
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "AML"
    assert isinstance(data["schema"], dict)

def test_update_schema():
    schema_path = example_data_dir / "AML_schema_updated.json"
    with open(schema_path, "rb") as schema_file:
        response = client.put(
            f"{BASE_URL}/schema?disease=AML",
            files={"file": ("AML_schema_updated.json", schema_file, "application/json")},
        )
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for AML updated successfully"}

def test_delete_schema():
    response = client.delete(f"{BASE_URL}/schema/AML")
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for disease 'AML' deleted successfully"}

if __name__ == "__main__":
    # Run the tests sequentially
    test_healthcheck()
    test_create_schema()
    test_get_schema()
    test_update_schema()
    test_delete_schema()
