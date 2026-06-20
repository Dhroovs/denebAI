# Deneb AI -—- Backend REST API (Phase 1)

Welcome to Phase 1 of the **Deneb AI** backend API. This repository houses a production-ready REST API designed using the **FastAPI** framework and backed by **SQLite** and **SQLAlchemy ORM**.

This phase establishes the structural, database, validation, and endpoint foundations for managing chatbot configurations and their associated knowledge-base documentation. It strictly isolates the core backend engineering and CRUD fundamentals, serving as a clean, scalable starting point before layer integration in future phases (LLMs, RAG, and Agents).

---

## 📂 Project Structure

The project follows a modular, clean, and scalable architecture, strictly separating database concerns, schemas, routing, and CRUD/service layers:

```text
denebAI/
│
├── app/
│   ├── database/
│   │   ├── __init__.py          # Database package connection interfaces
│   │   └── connection.py        # SQLite engine, SessionLocal, and get_db dependency
│   │
│   ├── models/
│   │   ├── __init__.py          # Models loading and registry exports
│   │   ├── chatbot.py           # Chatbot database model
│   │   └── knowledge_base.py    # KnowledgeBase database model
│   │
│   ├── schemas/
│   │   ├── __init__.py          # Schemas bundling and exports
│   │   ├── chatbot.py           # Pydantic schemas for Chatbots
│   │   └── knowledge_base.py    # Pydantic schemas for KnowledgeBases
│   │
│   ├── services/
│   │   ├── __init__.py          # Services bundling and exports
│   │   ├── chatbot.py           # Chatbots database CRUD/services
│   │   └── knowledge_base.py    # KnowledgeBases database CRUD/services
│   │
│   ├── routes/
│   │   ├── __init__.py          # Routes bundling and exports
│   │   ├── chatbot.py           # API route controller for Chatbots
│   │   └── knowledge_base.py    # API route controller for KnowledgeBases
│   │
│   ├── config.py                # Base configuration and environment settings
│   └── utils/
│       └── __init__.py          # Global helper functions and utility hooks
│
├── main.py                      # FastAPI app entry point and configuration loading
├── requirements.txt             # Project requirements and dependencies
├── seed_data.py                 # SQLite database initial seeding script
├── test_api.py                  # Pytest test suite covering 100% of CRUD, filtering & validation
└── README.md                    # Setup, execution, and documentation manual (This file)
```

---

## 🛠️ Requirements & Prerequisites

The application requires **Python 3.8+** (developed and tested on Python 3.13).

Dependencies:
* `fastapi` — High-performance ASGI framework
* `uvicorn` — ASGI web server implementation
* `sqlalchemy` — Python SQL Toolkit and Object Relational Mapper
* `pydantic` — Data validation and settings management
* `pytest` — Testing framework
* `httpx` — Test Client HTTP requests engine

---

## 🚀 Setup & Installation Instructions

Follow these steps to run the REST API locally:

### 1. Navigate to the Directory
Open your terminal and navigate to the project root directory:
```bash
cd d:\denebAI
```

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
# Create the environment
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (Mac/Linux Bash)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Seed the Database
Initialize the SQLite database (`deneb.db`) and seed it with pre-built developer chatbot configs and training roadmap documentation:
```bash
python seed_data.py
```

---

## 🖥️ Running the Server

Start the FastAPI application server using:
```bash
python main.py
```
*Alternatively, run with uvicorn directly:*
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The application will launch on **`http://127.0.0.1:8000/`**.

---

## 🌐 Navigating the REST API

1. **System Root Metadata**:
   Accessing `http://127.0.0.1:8000/` returns a JSON metadata block summarizing the API status and exposing Swagger links.

2. **FastAPI Swagger API Documentation**:
   Navigate to **`http://127.0.0.1:8000/docs`** to view automatic OpenAPI specifications, schemas description, validation inputs, and test API endpoints directly.

3. **ReDoc Alternative Documentation**:
   Navigate to **`http://127.0.0.1:8000/redoc`** for a alternative clean documentation layout.

---

## 🧪 Running Unit Tests

Run the automated test suite to verify the application constraints:
```bash
python -m pytest test_api.py
```

All 10 test cases will execute against a temporary SQLite test database (`test.db`) verifying:
* Chatbot creation, read, update, delete operations.
* Knowledge base insertion, search, filtering, and model constraints..
* Active status filters and offset-limit pagination logic.
* Database cascades (deleting a chatbot automatically cascade-deletes linked knowledge documents).
