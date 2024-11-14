# test_functional.py
import os
import pytest
from fastapi.testclient import TestClient
from data_annotation_utils import DATABASE_FILE
from main import app

@pytest.fixture(scope="module")
def client():
    # Set up
    os.environ["DATABASE_PATH"] = ":memory:"  # Use in-memory database for testing
    with TestClient(app) as test_client:
        yield test_client
    # Tear down
    os.unlink(DATABASE_FILE)  # Remove the in-memory database file after tests

def test_create_schema(client):
    # Test the endpoint for creating a schema
    schema_path = "tests/Example_data/AML_schema.json"  # Adjust the path as needed
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            "/schema?disease=AML",
            files={"file": schema_file},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert any("AML" in item for item in response.json()), "Failed to create schema for AML"

def test_update_schema(client):
    # Test the endpoint for updating a schema
    schema_path = "tests/Example_data/AML_schema_updated.json"  # Adjust the path as needed
    with open(schema_path, "rb") as schema_file:
        response = client.put(
            "/schema?disease=AML",
            files={"file": schema_file},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert response.json().get("message") == "Schema for AML updated successfully", "Failed to update schema for AML"

def test_retrieve_schema(client):
    # Test the endpoint for retrieving a schema
    response = client.get("/schema/AML")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert response.json().get("name") == "AML", "Retrieved schema does not match expected disease"

def test_delete_schema(client):
    # Test the endpoint for deleting a schema
    response = client.delete("/schema/AML")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert response.json().get("message") == "Schema for disease 'AML' deleted successfully.", "Failed to delete schema for AML"

# Add more tests for other functionalities as needed
