from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# For SQLite, check_same_thread=False is needed to allow FastAPI
# to process database requests across different threads in a single connection.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative database models.
Base = declarative_base()

# FastAPI Dependency to get a database session for each request.
# The session is closed automatically after the request completes.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
