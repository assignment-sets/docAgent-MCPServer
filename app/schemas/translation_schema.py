from pydantic import BaseModel, Field

class TranslationInput(BaseModel):
    text: str = Field(
        ..., min_length=5, max_length=100000, description="Text to be translated"
    )
    input_language: str = Field(
        ..., min_length=2, max_length=10, description="Source language code (e.g., 'en', 'fr')"
    )
    output_language: str = Field(
        ..., min_length=2, max_length=10, description="Target language code (e.g., 'es', 'de')"
    )
