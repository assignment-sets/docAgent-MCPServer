# app/schemas/extract_schema.py

from pydantic import BaseModel, Field, HttpUrl


class FileExtractInput(BaseModel):
    file_url: HttpUrl = Field(..., description="Public or signed URL to the file")
