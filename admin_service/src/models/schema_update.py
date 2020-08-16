from pydantic import BaseModel



class SchemaUpdate(BaseModel):
	template: str
	schema_update: dict