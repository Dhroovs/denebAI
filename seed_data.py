from app import models, database
from app.database import engine

def seed_database():
    db = database.SessionLocal()
    
    try:
        # Clear old database records for a clean reload
        db.query(models.KnowledgeBase).delete()
        db.query(models.Chatbot).delete()
        db.commit()

        print("Seeding database with DENEB AI Learning Platform configurations...")

        # 1. Create Athena AI Tutor & Stellar Code Reviewer Chatbots
        athena = models.Chatbot(
            name="Athena AI Tutor",
            description="Your virtual instructor for the Enterprise AI engineering roadmap, guiding you through FastAPI, RAG, and Agents.",
            system_prompt=(
                "You are Athena, the AI Engineering Tutor for the DENEB AI platform. "
                "You help interns learn backend engineering, FastAPI development, REST API design, "
                "LLM prompt engineering, vector databases, Retrieval-Augmented Generation (RAG), "
                "and AI agent orchestration. Explain technical concepts clearly, provide simple python examples, "
                "and reference our platform's learning milestones in your responses."
            ),
            model="deneb-core-v1",
            temperature=0.4,
            is_active=True
        )

        stellar_coder = models.Chatbot(
            name="Stellar Code Reviewer",
            description="An AI reviewer optimized for evaluating Python syntax, Pydantic validation schemas, and database ORMs.",
            system_prompt=(
                "You are the Stellar Code Reviewer. Analyze Python script snippets, suggest "
                "performance optimizations, verify Pydantic validator compliance, and ensure "
                "appropriate FastAPI status codes are used."
            ),
            model="stellar-ultra",
            temperature=0.2,
            is_active=True
        )

        db.add_all([athena, stellar_coder])
        db.commit()

        # Refresh database session to get auto-generated IDs
        db.refresh(athena)
        db.refresh(stellar_coder)

        print(f"Chatbots seeded successfully! Athena Tutor ID: {athena.id}")

        # 2. Create Knowledge Base articles linked to Athena AI Tutor
        kb1 = models.KnowledgeBase(
            name="FastAPI & REST API Guidelines",
            description="Reference study guide for building compliant REST APIs in FastAPI.",
            data_source="text",
            content=(
                "FastAPI is a modern web framework for building APIs with Python 3.8+. "
                "Key learning topics: 1. Request body validation using Pydantic models. "
                "2. Standard REST status codes: 201 Created (POST success), 200 OK (GET/PUT success), "
                "204 No Content (DELETE success), 422 Unprocessable Entity (input validation errors). "
                "3. Query-based list controls: always implement limit-based pagination and search/filtering."
            ),
            chatbot_id=athena.id
        )

        kb2 = models.KnowledgeBase(
            name="Retrieval-Augmented Generation (RAG)",
            description="Introduction to RAG architecture, vector databases, and semantic search.",
            data_source="text",
            content=(
                "Retrieval-Augmented Generation (RAG) is a technique that references external knowledge "
                "sources before an LLM synthesizes a response. The workflow includes: "
                "- Parsing & Chunking: Dividing long text documents into smaller semantically cohesive segments. "
                "- Vector Embeddings: Converting text segments into numeric vectors. "
                "- Indexing: Storing vectors in databases like Chroma or pgvector. "
                "- Semantic Search: Finding the top matching document chunks to inject into the system prompt."
            ),
            chatbot_id=athena.id
        )

        kb3 = models.KnowledgeBase(
            name="AI Agents & Tool Calling Workflows",
            description="Guide to orchestrating LLM agents with external function capabilities.",
            data_source="text",
            content=(
                "An AI Agent is an autonomous loop that uses an LLM to plan tasks, reflect on inputs, "
                "and execute tools. Tool Calling (Function Calling) allows the model to output a structured "
                "JSON block representing a function call. The runtime environment executes the function, "
                "collects the string output, and passes it back to the model. This is the core foundation "
                "for building complex multi-step workflows."
            ),
            chatbot_id=athena.id
        )

        kb4 = models.KnowledgeBase(
            name="DENEB AI Internship Roadmap",
            description="The four structured phases of our enterprise AI chatbot developer internship.",
            data_source="text",
            content=(
                "Deneb AI Internship Milestones:\n"
                "- Phase 1: API Development (FastAPI REST endpoints, SQLite ORM database integration, search/filter, and paginated lists).\n"
                "- Phase 2: LLMs & Prompt Engineering (Cloud-hosted and self-hosted models, system instructions, temperature, and context windows).\n"
                "- Phase 3: RAG & Vector Databases (Chunking engines, semantic index searches, and knowledge injections).\n"
                "- Phase 4: AI Agents & Tool Calling (Integrating external APIs, function mappings, and multi-agent loops)."
            ),
            chatbot_id=athena.id
        )

        db.add_all([kb1, kb2, kb3, kb4])
        db.commit()
        print("Knowledge bases for Athena Tutor seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    database.Base.metadata.create_all(bind=engine)
    seed_database()
