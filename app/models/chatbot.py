from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(250), nullable=True)
    system_prompt = Column(Text, default="You are a helpful AI assistant.", nullable=True)
    model = Column(String(50), default="deneb-core-v1", nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to KnowledgeBase. If a chatbot is deleted, delete its knowledge bases.
    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="chatbot",
        cascade="all, delete-orphan"
    )
