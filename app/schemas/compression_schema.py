# app/schemas/compression_schema.py

from pydantic import BaseModel, Field, HttpUrl


class FileCompressionInput(BaseModel):
    file_url: HttpUrl = Field(..., description="Public or signed URL to the file")
