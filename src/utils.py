from sqlmodel import Session, select
from fastapi import HTTPException
from models import Schema
import json
import logging

async def save_schema_to_database(session: Session, disease: str, schemas: dict):
    try:
        logging.info(f"Saving schema for disease: {disease}")
        schema = Schema(disease=disease, features=json.dumps(schemas)) #schema
        session.add(schema)
        session.commit()
        logging.info("Schema saved successfully")
    except Exception as e:
        print("Error saving schema to database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def update_schema_in_database(session: Session, disease: str, updated_schema: dict):
    try:
        statement = select(Schema).where(Schema.disease == disease)
        schema = session.exec(statement).first()
        if schema:
            schema.features = json.dumps(updated_schema) #schema
            session.add(schema)
            session.commit()
        else:
            raise HTTPException(status_code=404, detail=f"No schema found for disease: {disease}")
    except Exception as e:
        print("Error updating schema in database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_schema_from_database(session: Session, disease: str):
    try:
        statement = select(Schema).where(Schema.disease == disease)
        schema = session.exec(statement).first()
        if schema:
            return schema.features #schema
        else:
            raise HTTPException(status_code=404, detail=f"No schema found for disease: {disease}")
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error retrieving schema from database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_schema_from_db(session: Session, disease: str):
    try:
        statement = select(Schema).where(Schema.disease == disease)
        schema = session.exec(statement).first()
        if schema:
            session.delete(schema)
            session.commit()
            return True
        else:
            raise HTTPException(status_code=404, detail=f"No schema found for disease: {disease}")
    except Exception as e:
        print("Error deleting schema from database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_all_schemas_from_db(session: Session):
    try:
        statement = select(Schema)
        schemas = session.exec(statement).all()
        return schemas
    except Exception as e:
        print("Error retrieving all schemas from database:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
