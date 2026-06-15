from sqlalchemy.orm import Session
from app import models, schemas

def get_chatbot(db: Session, chatbot_id: int) -> models.Chatbot:
    """Retrieve a single chatbot by its ID."""
    return db.query(models.Chatbot).filter(models.Chatbot.id == chatbot_id).first()


def get_chatbots(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    model: str = None,
    is_active: bool = None
):
    """
    Retrieve chatbots with optional searching (by name/description), 
    filtering (by model engine or active status), and pagination.
    Returns a tuple of (items, total_count).
    """
    query = db.query(models.Chatbot)

    # Search filter (case-insensitive substring matching on name/description)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Chatbot.name.ilike(search_filter)) |
            (models.Chatbot.description.ilike(search_filter))
        )

    # Model engine filter
    if model:
        query = query.filter(models.Chatbot.model == model)

    # Status filter
    if is_active is not None:
        query = query.filter(models.Chatbot.is_active == is_active)

    # Calculate total count of matching records (before pagination)
    total_count = query.count()

    # Apply pagination and fetch items
    items = query.offset(skip).limit(limit).all()
    
    return items, total_count


def create_chatbot(db: Session, chatbot: schemas.ChatbotCreate) -> models.Chatbot:
    """Create a new chatbot agent."""
    db_chatbot = models.Chatbot(**chatbot.model_dump())
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def update_chatbot(db: Session, db_chatbot: models.Chatbot, chatbot_update: schemas.ChatbotUpdate) -> models.Chatbot:
    """Perform a partial update on an existing chatbot."""
    update_data = chatbot_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chatbot, key, value)
    
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def delete_chatbot(db: Session, db_chatbot: models.Chatbot) -> None:
    """Delete a chatbot. Cascade deletes linked knowledge bases."""
    db.delete(db_chatbot)
    db.commit()
