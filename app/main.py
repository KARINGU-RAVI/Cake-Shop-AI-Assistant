from fastapi import FastAPI, Depends, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database.db import engine, Base, get_db
from app.whatsapp.webhook import router as whatsapp_router
from app.agent.conversation_manager import ConversationManager
from app.core.logger import logger

# Initialize Database Tables automatically on startup
logger.info("Initializing database schemas...")
Base.metadata.create_all(bind=engine)
logger.info("Database schemas initialized successfully.")

app = FastAPI(
    title="Sweet Cheeks Bakery AI Sales Agent",
    description="Production-grade AI WhatsApp Sales Agent for autonomous ordering, customization, and mock checkout workflows for Sweet Cheeks Bakery.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Standard CORS Config for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(whatsapp_router, prefix="/api/v1")


@app.get("/")
def home():
    """
    Service health check endpoint.
    """
    return {
        "status": "running",
        "app_name": settings.HOST,
        "database": "connected",
        "meta_whatsapp_sender": "configured" if settings.PHONE_NUMBER_ID else "missing"
    }


@app.post("/api/v1/chat", tags=["Agent Simulator"])
def chat_simulator(
    phone_number: str = Body(..., example="1234567890"),
    name: str = Body(..., example="Arjun"),
    message: str = Body(..., example="I want to buy a Chocolate Cake"),
    db: Session = Depends(get_db)
):
    """
    Local testing chat simulator. Use this to chat directly with the AI agent 
    in your browser using Swagger UI (/docs) without Meta developer configuration.
    """
    logger.info(f"Local chat simulation request from {phone_number} ({name}): '{message}'")
    try:
        response = ConversationManager.process_message(
            db=db,
            phone_number=phone_number,
            user_name=name,
            message_content=message
        )
        return {
            "phone_number": phone_number,
            "name": name,
            "response": response
        }
    except Exception as e:
        logger.error(f"Simulator error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal agent reasoning error: {str(e)}"
        )
