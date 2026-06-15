from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

# List of allowed LLM models in our platform.
ALLOWED_MODELS = ["deneb-core-v1", "deneb-light-v1", "stellar-ultra", "nebula-mini"]

class ChatbotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="The chatbot agent name")
    description: Optional[str] = Field(None, max_length=250, description="Brief description of purpose")
    system_prompt: Optional[str] = Field("You are a helpful AI assistant.", description="The primary instructions for the LLM")
    model: str = Field("deneb-core-v1", description="LLM model engine name")
    temperature: float = Field(0.7, description="Creativity temperature (0.0 to 1.0)")
    is_active: bool = Field(True, description="Active status of the chatbot")

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {', '.join(ALLOWED_MODELS)}")
        return value

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0 inclusive")
        return value


class ChatbotCreate(ChatbotBase):
    pass


class ChatbotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    system_prompt: Optional[str] = Field(None)
    model: Optional[str] = Field(None)
    temperature: Optional[float] = Field(None)
    is_active: Optional[bool] = Field(None)

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ALLOWED_MODELS:
            raise ValueError(f"Model must be one of: {', '.join(ALLOWED_MODELS)}")
        return value

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and not (0.0 <= value <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0 inclusive")
        return value


class ChatbotResponse(ChatbotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedChatbotResponse(BaseModel):
    total_items: int = Field(..., description="Total count of matching chatbots")
    page: int = Field(..., description="Current page index")
    size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total pages available")
    items: List[ChatbotResponse] = Field(..., description="List of chatbots for the current page")
