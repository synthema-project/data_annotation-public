from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Dict
from models import Schema
from utils import save_schema_to_database, update_schema_in_database, get_schema_from_database, delete_schema_from_db, get_all_schemas_from_db
from database import create_db_and_tables, get_session
import uvicorn
import json

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/schema", tags=["data-annotation"])
async def create_schema(disease: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    if file.filename.endswith(".json"):
        try:
            schema_data = await file.read()
            schema_dict = json.loads(schema_data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        await save_schema_to_database(session, disease, schema_dict)
        return {"message": f"Schema for {disease} created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Only JSON files are accepted")

@app.put("/schema", tags=["data-annotation"])
async def update_schema(disease: str, file: UploadFile = File(...), session: Session = Depends(get_session)):
    if file.filename.endswith(".json"):
        schema_data = await file.read()
        updated_schema = json.loads(schema_data)

        await update_schema_in_database(session, disease, updated_schema)
        return {"message": f"Schema for {disease} updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Only JSON files are accepted")

#@app.get("/schema/{disease}", tags=["data-annotation"])
#async def get_schema(disease: str, session: Session = Depends(get_session)):
#    try:
##        schema = await get_schema_from_database(session, disease)
#        return {"disease": disease, "schema": json.loads(schema)}
#    except HTTPException as e:
#        if e.status_code == 404:
#            return {"error": f"No schema found for disease: {disease}"}
#        raise e

@app.get("/schema/{disease}", tags=["data-annotation"])
async def get_schema(disease: str, session: Session = Depends(get_session)):
    schema = await get_schema_from_database(session, disease)
    return {"disease": disease, "schema": json.loads(schema)} #return {"disease": disease, "schema": json.loads(schema)}
    if not schema:
        raise HTTPException(status_code=404, detail=f"No schema found for disease: {disease}")

@app.get("/schemas", tags=["data-annotation"])
async def get_all_schemas(session: Session = Depends(get_session)):
    schemas = await get_all_schemas_from_db(session)
    return [{"disease": schema.disease, "schema": json.loads(schema.features)} for schema in schemas] #schema

@app.delete("/schema/{disease}", tags=["data-annotation"])
async def delete_schema(disease: str, session: Session = Depends(get_session)):
    result = await delete_schema_from_db(session, disease)
    if result:
        return {"message": f"Schema for disease '{disease}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Schema for disease '{disease}' not found")

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
