# app/schemas/fallback_schema.py

from pydantic import BaseModel, Field

class FallbackInput(BaseModel):
    prompt: str = Field(
        ...,
        description=(
            "user task statement which is to be done"
        ),
        min_length=10,
        max_length=8000
    )
