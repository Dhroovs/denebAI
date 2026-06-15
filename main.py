import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import chatbot_router, kb_router
from app.config import settings

# Automatically create the SQLite database tables on application start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend APIs for Project Deneb, an enterprise-grade AI chatbot platform."
)

# CORS Middleware configurations to allow client requests from any host
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to capture unhandled exceptions and format them nicely
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

# Register API routes with proper prefixing
app.include_router(chatbot_router, prefix="/api/v1")
app.include_router(kb_router, prefix="/api/v1")

# Clean API metadata landing response
@app.get("/", tags=["System"])
async def get_system_root():
    """
    Root endpoint returning system info and documentation endpoints.
    """
    return {
        "message": "Welcome to the Deneb AI REST API Command Center",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "chatbots": "/api/v1/chatbots/",
            "knowledge_bases": "/api/v1/knowledge-bases/"
        }
    }


if __name__ == "__main__":
    # Runs the uvicorn development server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
