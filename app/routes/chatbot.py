import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import services, schemas, database

router = APIRouter(
    prefix="/chatbots",
    tags=["Chatbots"]
)


@router.post("/", response_model=schemas.ChatbotResponse, status_code=status.HTTP_201_CREATED)
def create_new_chatbot(chatbot: schemas.ChatbotCreate, db: Session = Depends(database.get_db)):
    """
    Create a new Chatbot Agent.
    
    Validates fields like name, temperature, and model engine.
    Returns the created chatbot with its DB-generated ID and timestamps.
    """
    return services.create_chatbot(db=db, chatbot=chatbot)


@router.get("/", response_model=schemas.PaginatedChatbotResponse)
def list_chatbots(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    model: Optional[str] = Query(None, description="Filter by model engine type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(database.get_db)
):
    """
    List Chatbot Agents with filtering, searching, and pagination.
    
    Calculates offsets automatically and returns paginated metadata alongside the item list.
    """
    skip = (page - 1) * size
    
    items, total_items = services.get_chatbots(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        model=model,
        is_active=is_active
    )
    
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    
    return schemas.PaginatedChatbotResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=items
    )


@router.get("/{chatbot_id}", response_model=schemas.ChatbotResponse)
def get_chatbot_details(chatbot_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve details for a single chatbot agent by its unique ID.
    
    Raises a 404 error if the chatbot does not exist.
    """
    db_chatbot = services.get_chatbot(db=db, chatbot_id=chatbot_id)
    if not db_chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chatbot with ID {chatbot_id} not found"
        )
    return db_chatbot


@router.put("/{chatbot_id}", response_model=schemas.ChatbotResponse)
def update_chatbot_details(
    chatbot_id: int,
    chatbot_update: schemas.ChatbotUpdate,
    db: Session = Depends(database.get_db)
):
    """
    Update an existing chatbot agent's details (partial updates allowed).
    
    Raises a 404 error if the chatbot does not exist.
    """
    db_chatbot = services.get_chatbot(db=db, chatbot_id=chatbot_id)
    if not db_chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chatbot with ID {chatbot_id} not found"
        )
    return services.update_chatbot(db=db, db_chatbot=db_chatbot, chatbot_update=chatbot_update)


@router.delete("/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chatbot_record(chatbot_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a chatbot agent by ID.
    
    Cascades deletion to any associated knowledge bases.
    Returns HTTP 204 No Content upon success.
    """
    db_chatbot = services.get_chatbot(db=db, chatbot_id=chatbot_id)
    if not db_chatbot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chatbot with ID {chatbot_id} not found"
        )
    services.delete_chatbot(db=db, db_chatbot=db_chatbot)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
