# app/schemas/zipper_schema.py

from pydantic import BaseModel, Field, HttpUrl


class FileZipperInput(BaseModel):
    file_url: HttpUrl = Field(
        ..., description="Public or signed URL to the file to be archived"
    )
