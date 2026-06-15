import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import services, schemas, database

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"]
)


@router.post("/", response_model=schemas.KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_new_knowledge_base(
    kb: schemas.KnowledgeBaseCreate,
    db: Session = Depends(database.get_db)
):
    """
    Create a new Knowledge Base document and link it to a Chatbot agent.
    
    Verifies that the target chatbot ID exists.
    Returns HTTP 201 Created on success.
    """
    # Verify the target chatbot exists before linking
    chatbot = services.get_chatbot(db=db, chatbot_id=kb.chatbot_id)
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot create Knowledge Base: Chatbot with ID {kb.chatbot_id} does not exist"
        )
        
    return services.create_knowledge_base(db=db, kb=kb)


@router.get("/", response_model=schemas.PaginatedKnowledgeBaseResponse)
def list_knowledge_bases(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search term for name/content"),
    data_source: Optional[str] = Query(None, description="Filter by data source type"),
    chatbot_id: Optional[int] = Query(None, description="Filter by owner chatbot ID"),
    db: Session = Depends(database.get_db)
):
    """
    List Knowledge Base documents with filtering, searching, and pagination.
    """
    skip = (page - 1) * size
    
    items, total_items = services.get_knowledge_bases(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        data_source=data_source,
        chatbot_id=chatbot_id
    )
    
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    
    return schemas.PaginatedKnowledgeBaseResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=items
    )


@router.get("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
def get_knowledge_base_details(kb_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve details for a single knowledge base by ID.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
    return db_kb


@router.put("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
def update_knowledge_base_details(
    kb_id: int,
    kb_update: schemas.KnowledgeBaseUpdate,
    db: Session = Depends(database.get_db)
):
    """
    Update an existing knowledge base (partial updates allowed).
    
    If updating the chatbot link, verifies that the new chatbot ID exists first.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
        
    # If the user is trying to change which chatbot this knowledge base is attached to,
    # verify that the new chatbot exists first.
    if kb_update.chatbot_id is not None:
        new_chatbot = services.get_chatbot(db=db, chatbot_id=kb_update.chatbot_id)
        if not new_chatbot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update Knowledge Base: Chatbot with ID {kb_update.chatbot_id} does not exist"
            )
            
    return services.update_knowledge_base(db=db, db_kb=db_kb, kb_update=kb_update)


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base_record(kb_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a knowledge base record by ID.
    
    Returns HTTP 204 No Content upon success.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
    services.delete_knowledge_base(db=db, db_kb=db_kb)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
