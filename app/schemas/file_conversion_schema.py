from pydantic import BaseModel, HttpUrl, Field

class FileConvertInput(BaseModel):
    file_url: HttpUrl = Field(..., description="Public or signed URL to the source file")
    input_format: str = Field(..., description="The current file format, e.g. 'docx'")
    output_format: str = Field(..., description="The desired output format, e.g. 'pdf'")
