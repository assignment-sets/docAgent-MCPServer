# app/schemas/compression_schema.py

from pydantic import BaseModel, Field, HttpUrl


class FileCompressionInput(BaseModel):
    file_url: HttpUrl = Field(..., description="Public or signed URL to the file")
    file_type: str = Field(..., description="File extension (e.g., 'pdf', 'png', 'jpg')")
