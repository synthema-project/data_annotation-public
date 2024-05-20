from fastapi import FastAPI, Depends, HTTPException, Body, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Dict, List, Union
from datetime import datetime, timedelta
import sqlite3
import os
import json
import csv
import io
import uuid
import pandas as pd
import numpy as np

# dict to save schemas in the central node
central_node_schemas = {}
# Path al database SQLite
DATABASE_FILE = "/mnt/c/users/lenovo/desktop/fastapi/SYNTHEMA/central_node.db"
#DATABASE_FILE = "./central_node.db"

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "francesco.casadei20@unibo.it",
        "hashed_password": "$2b$12$6sKsO/QlT2FYO2GpFvPwaOaC3HpTfB0YVVnZjF7g8Kx8/W2OH5M2a",  # hashed version of "password"
        "disabled": False,
        "role": "admin"
    },
    "user": {
        "username": "user",
        "full_name": "Regular User",
        "email": "francesco.casadei16@studio.unibo.it",
        "hashed_password": "def456",  # hashed version of "password"
        "disabled": False,
        "role": "user"
    },
}

# Secret key for signing JWT tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Password hashing parameters
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool = None
    role: str


class UserInDB(User):
    hashed_password: str


class TokenData(BaseModel):
    username: str
    role: str


# Functions for password verification and token generation

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password):
    hashed_password = get_password_hash(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password):#, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    return token_data

###########################################
# CONNECTION BETWEEN FASTAPI AND SQLITE #
###########################################

# Funzione per creare la connessione al database SQLite
#def create_connection():
#    conn = None
#    try:
#        conn = sqlite3.connect(DATABASE_FILE)
#        print(f"Connected to SQLite database '{DATABASE_FILE}'")
#        return conn
#    except Exception as e:
#        print(e)


def create_connection():
    try:
        if not os.path.exists(DATABASE_FILE):
            print(f"Database file {DATABASE_FILE} does not exist.")

        conn = sqlite3.connect(DATABASE_FILE)
        print(f"Connected to SQLite database '{DATABASE_FILE}'")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

##################
# DISEASE SCHEMA #
##################

# Save the schema in a SQL database table
async def save_schema_to_database(disease: str, schemas: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    try:
        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()

        # create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schemas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease TEXT NOT NULL,
                schema TEXT NOT NULL
            )
        """)
        conn.commit()

        # Insert schema into database
        cursor.execute("""
            INSERT INTO schemas (disease, schema)
            VALUES (?, ?)
        """, (disease, json.dumps(schemas)))

        print('SCHEMA successfully saved into the database')

        # Commit and close connection
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error saving schema to database:", e)

# Update a schema in the database
async def update_schema_in_database(disease: str, updated_schema: dict, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    try:
        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()

        # Update the schema in the database
        cursor.execute("""
            UPDATE schemas
            SET schema = ?
            WHERE disease = ?
        """, (json.dumps(updated_schema), disease))

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error updating schema in database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Retrieve a schema from the database
async def get_schema_from_database(disease: str):
    try:
        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()

        # Query to retrieve the schema
        cursor.execute("""
            SELECT schema FROM schemas WHERE disease = ?
        """, (disease,))

        # Fetching the result
        schema = cursor.fetchone()
        cursor.close()
        conn.close()

        # If schema is found, return it
        if schema:
            print("Schema found in the database:")
            print(schema[0])
            return schema[0]
        else:
            print(f"No schema found in the database for the given {disease}.")
            return None

    except Exception as e:
        print("Error retrieving schema from database:", e)
        return None

async def delete_schema_from_db(disease: str):
    # Function to delete a schema from SQLite database based on disease name
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schemas WHERE disease = ?", (disease,))
    conn.commit()
    affected_rows = cursor.rowcount
    conn.close()
    return affected_rows > 0