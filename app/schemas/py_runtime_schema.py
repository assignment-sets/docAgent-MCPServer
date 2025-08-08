# app/schemas/py_runtime_schema.py

from pydantic import BaseModel, Field


class PyRuntimeInput(BaseModel):
    code: str = Field(..., description="Python code to execute")

