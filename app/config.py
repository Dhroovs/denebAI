import os

class Settings:
    PROJECT_NAME: str = "Deneb AI Chatbot Platform"
    PROJECT_VERSION: str = "1.0.0"
    
    # SQLite Database connection URL.
    # sqlite:///deneb.db will create the file in the project's root folder.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///deneb.db")

settings = Settings()
