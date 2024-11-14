import os
import time
from pathlib import Path 
from fastapi import Depends
from fastapi.testclient import TestClient
from database import create_db_and_tables, get_session
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker
from main import app
import pytest

# Configure PostgreSQL database for testing
TEST_DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/test_db"
engine = create_engine(TEST_DATABASE_URL)

# Create a FastAPI test client
client = TestClient(app)

# Get the directory path of the current script
current_dir = Path(__file__).resolve().parent


# Override the get_session dependency for testing
def override_get_session():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        yield session


# Apply the dependency override
app.dependency_overrides[get_session] = override_get_session


# Wait for the database to be ready before tests
def wait_for_db():
    for _ in range(10):  # Retry 10 times
        try:
            response = client.get("/healthcheck")  # Assuming there's a health check endpoint
            if response.status_code == 200:
                print('The database is up and running')
                return True
        except Exception as e:
            print(f"Database connection failed, retrying... ({e})")
            time.sleep(2)
    raise Exception("Database not ready")


#@pytest.fixture(scope="module", autouse=True)
#def setup_database():
#    """Set up the database schema before running tests."""
#    create_db_and_tables()
#    wait_for_db()


def test_healthcheck():
    response = client.get("/healthcheck")
    print('HEALTHCHECK OK')
    assert response.status_code == 200


def test_create_schema():
    # Test the endpoint for creating a schema
    wait_for_db()  # Ensure the database is up and running
    schema_path = current_dir / "Example_data" / "AML_schema.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            f"/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert response.json() == {"message": "Schema for AML created successfully"}
    print("Create Schema Test Passed")


def test_update_schema():
    # Test the endpoint for updating a schema
    schema_path = current_dir / "Example_data" / "AML_schema_updated.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            f"/schema?disease=AML",
            files={"file": ("AML_schema_updated.json", schema_file, "application/json")},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    print("Update Schema Test Passed")


def test_get_schema():
    # Test the endpoint for retrieving a schema
    response = client.get("/schema/AML")
    assert response.status_code == 200
    print("Get Schema Test Passed")


def test_delete_schema():
    # Test the endpoint for deleting a schema
    response = client.delete("/schema/AML")
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for disease 'AML' deleted successfully."}
    print("Delete Schema Test Passed")

