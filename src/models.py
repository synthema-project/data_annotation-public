from sqlmodel import SQLModel, Field

class Schema(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    disease: str
    features: str 
    #schema_name: str = Field(alias='schema')
