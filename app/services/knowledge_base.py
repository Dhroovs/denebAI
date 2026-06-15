from sqlalchemy.orm import Session
from app import models, schemas

def get_knowledge_base(db: Session, kb_id: int) -> models.KnowledgeBase:
    """Retrieve a single knowledge base document by its ID."""
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()


def get_knowledge_bases(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    data_source: str = None,
    chatbot_id: int = None
):
    """
    Retrieve knowledge bases with searching (by name/content),
    filtering (by data source or owner chatbot ID), and pagination.
    Returns a tuple of (items, total_count).
    """
    query = db.query(models.KnowledgeBase)

    # Search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.KnowledgeBase.name.ilike(search_filter)) |
            (models.KnowledgeBase.content.ilike(search_filter))
        )

    # Data source filter (text, file, url, database)
    if data_source:
        query = query.filter(models.KnowledgeBase.data_source == data_source)

    # Chatbot owner filter
    if chatbot_id is not None:
        query = query.filter(models.KnowledgeBase.chatbot_id == chatbot_id)

    total_count = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return items, total_count


def create_knowledge_base(db: Session, kb: schemas.KnowledgeBaseCreate) -> models.KnowledgeBase:
    """Create a new knowledge base item and attach it to a chatbot."""
    db_kb = models.KnowledgeBase(**kb.model_dump())
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)
    return db_kb


def update_knowledge_base(
    db: Session,
    db_kb: models.KnowledgeBase,
    kb_update: schemas.KnowledgeBaseUpdate
) -> models.KnowledgeBase:
    """Perform a partial update on a knowledge base document."""
    update_data = kb_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_kb, key, value)
        
    db.commit()
    db.refresh(db_kb)
    return db_kb


def delete_knowledge_base(db: Session, db_kb: models.KnowledgeBase) -> None:
    """Delete a knowledge base document."""
    db.delete(db_kb)
    db.commit()
