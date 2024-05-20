from fastapi import FastAPI, Depends, HTTPException, Body, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, List, Union
import uvicorn
from data_annotation_utils import create_connection, get_current_user, save_schema_to_database, update_schema_in_database, get_schema_from_database, delete_schema_from_db
from data_annotation_utils import User, UserInDB, TokenData, authenticate_user, create_access_token, fake_users_db, central_node_schemas
from datetime import datetime, timedelta
import sqlite3
import os
import json
import csv
import io
import uuid
import pandas as pd
import numpy as np

# FastAPI app
app = FastAPI()

# Endpoint to generate JWT token
@app.post("/token", tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

############################
# SCHEMA FASTAPI FUNCTIONS #
############################

# save schema in the postgres database
@app.post("/schema", tags=["data-annotation"])
async def create_schema(disease: str,  file: UploadFile = File(...), current_user: User = Depends(get_current_user)): #schema: DatasetSchema,
    #carico lo schema come file json
    if file.filename.endswith(".json"):
        dataframe = await file.read()
        data = json.loads(dataframe)

        # save schema in central node
        central_node_schemas[disease] = data#schema
        print(central_node_schemas)

        # save the schema in SQL database table
        await save_schema_to_database(disease, data, current_user)

    else:
        raise HTTPException(status_code=400, detail="Only json files are accepted")
    return {"message": f"Schema for {disease} created successfully"}, central_node_schemas

# update schema in the postgres database
@app.put("/schema", tags=["data-annotation"])
async def update_schema(disease: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if file.filename.endswith(".json"):
        try:
            # read the uploaded JSON file
            schema_data = await file.read()
            updated_schema = json.loads(schema_data)

            # update the schema in the database
            await update_schema_in_database(disease, updated_schema, current_user)

            return {"message": f"Schema for {disease} updated successfully"}

        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(status_code=400, detail="Only JSON files are accepted")

# retrieve schema from the postgres database
#@app.get("/upload-schema/{disease}", tags=["data-annotation"])
#async def retrieve_schema(disease: str):
#    try:
#        schema = await get_schema_from_database(disease)
#        if schema is None:
#            raise HTTPException(status_code=404, detail=f"No schema found in the database for the disease: {disease}")

#        return {"disease": disease, "schema": schema}

#    except Exception as e:
#        raise HTTPException(status_code=500, detail=f"Error retrieving schema: {str(e)}")

@app.get("/schema/{disease}", tags=["data-annotation"])
async def get_schema(disease: str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT schema FROM schemas WHERE disease=?", (disease,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": disease, "schema": eval(row[0])}  # Ensure schema is returned as dict
    else:
        raise HTTPException(status_code=404, detail="Schema not found")

@app.delete("/schema/{disease}", tags=["data-annotation"])
async def delete_schema(disease: str):
    # Delete the schema from the database based on the disease name
    result = await delete_schema_from_db(disease)
    if result:
        return {"message": f"Schema for disease '{disease}' deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail=f"Schema for disease '{disease}' not found.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)