# apps/schemas/summarize_schema.py

from pydantic import BaseModel, Field


class SummarizeInput(BaseModel):
    text: str = Field(
        ..., min_length=10, max_length=100000, description="Text to be summarized"
    )
