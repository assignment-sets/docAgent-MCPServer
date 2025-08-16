# app/schemas/extract_schema.py

from pydantic import BaseModel, Field, HttpUrl


class FileExtractInput(BaseModel):
    file_url: HttpUrl = Field(..., description="Public or signed URL to the file")
    file_type: str = Field(..., description="File extension or MIME subtype (e.g., 'pdf', 'png', 'docx')")
