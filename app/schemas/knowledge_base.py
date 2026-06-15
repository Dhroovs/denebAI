from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

ALLOWED_SOURCES = ["text", "file", "url", "database"]

class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="The name of the knowledge source")
    description: Optional[str] = Field(None, max_length=250, description="Brief description of the content")
    data_source: str = Field("text", description="Source type (text, file, url, database)")
    content: str = Field(..., min_length=1, description="The knowledge content text")
    chatbot_id: int = Field(..., description="The ID of the chatbot linked to this knowledge")

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, value: str) -> str:
        if value not in ALLOWED_SOURCES:
            raise ValueError(f"Data source must be one of: {', '.join(ALLOWED_SOURCES)}")
        return value


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    data_source: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    chatbot_id: Optional[int] = Field(None)

    @field_validator("data_source")
    @classmethod
    def validate_data_source(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and value not in ALLOWED_SOURCES:
            raise ValueError(f"Data source must be one of: {', '.join(ALLOWED_SOURCES)}")
        return value


class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedKnowledgeBaseResponse(BaseModel):
    total_items: int = Field(..., description="Total count of matching knowledge bases")
    page: int = Field(..., description="Current page index")
    size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total pages available")
    items: List[KnowledgeBaseResponse] = Field(..., description="List of knowledge bases for the current page")
