# test_unit.py
import os
from pathlib import Path
from fastapi import Depends
from fastapi.testclient import TestClient
from database import create_db_and_tables, get_session
from sqlmodel import SQLModel, Session, create_engine 
from sqlalchemy.orm import sessionmaker
from main import app

client = TestClient(app)

# Get the directory path of the current script
current_dir = Path(__file__).resolve().parent

#TEST_DATABASE_URL = "postgresql://fcasadei:7IGc540zOTX04ET@mstorage-svc:5432/dataset_schema"
TEST_DATABASE_URL = "postgresql://fcasadei:mypassword@mydatabase:5432/dataset_schema"
engine = create_engine(TEST_DATABASE_URL)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to wait for database to be ready
def wait_for_db():
    for _ in range(10):  # Retry 10 times
        try:
            # Attempt a simple database connection (assuming SQLAlchemy or similar)
            response = client.get("/healthcheck")  # Assuming there's a health check endpoint
            if response.status_code == 200:
                print('the database is up and running')
                return True
        except Exception:
            time.sleep(2)
    raise Exception("Database not ready")

def test_healthcheck():
    response = client.get("/healthcheck")
    print('HEALTHCHECK OK')
    assert response.status_code == 200

#def test_create_schema1():
#    """Test for creating a schema."""
#    wait_for_db()  # Ensure the database is up and running
#    schema_path = current_dir / "Example_data" / "AML_schema.json"
#    files = {"file": ("AML_schema.json", open(schema_path, "rb"), "application/json")}
#    response = requests.post(f"{BASE_URL}/schema?disease=AML", files=files)
    
#    assert response.status_code == 200, f"Failed to create schema. Status: {response.status_code}, Response: {response.json()}"
#    print("Create Schema Test Passed")

def test_create_schema():
    # Test the endpoint for creating a schema
    wait_for_db()  # Ensure the database is up and running
    schema_path = current_dir / "Example_data" / "AML_schema.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            f"/schema?disease=AML",
            files={"file": ("AML_schema.json", schema_file, "application/json")},
            #files={"file": schema_file},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert response.json() == {"message": "Schema for AML created successfully"}
    assert any("AML" in item for item in response.json()), "Failed to create schema for AML"

    # Additional assertions for schema validation or database checks can be added here


def test_update_schema():
    # Test the endpoint for updating a schema
    schema_path = current_dir / "Example_data" / "AML_schema_updated.json"
    with open(schema_path, "rb") as schema_file:
        response = client.post(
            f"/schema?disease=AML",
            files={"file": schema_file},
        )
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response content: {response.content.decode()}"
    assert any("AML" in item for item in response.json()), "Failed to update schema for AML"

    # Additional assertions for schema validation or database checks can be added here


def test_get_schema():
    # Test the endpoint for retrieving a schema
    response = client.get("/schema/AML")
    assert response.status_code == 200

    # Additional assertions for schema validation or expected schema content can be added here


def test_delete_schema():
    # Test the endpoint for deleting a schema
    response = client.delete("/schema/AML")
    assert response.status_code == 200
    assert response.json() == {"message": "Schema for disease 'AML' deleted successfully."}

    # Additional assertions for database checks or verifying schema deletion can be added here


# Add more test cases as needed
