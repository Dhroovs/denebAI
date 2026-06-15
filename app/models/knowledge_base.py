from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=True)
    data_source = Column(String(50), default="text", nullable=False)  # text, file, url, database
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Link to a specific chatbot
    chatbot_id = Column(Integer, ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=False)
    
    # Back relationship
    chatbot = relationship("Chatbot", back_populates="knowledge_bases")
