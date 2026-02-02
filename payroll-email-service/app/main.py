from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import email, templates, health
from app.services.event_subscriber import start_event_subscriber
from app.config import settings
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Payroll Email Service",
    version="1.0.0",
    description="Email microservice for the Payroll System",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(templates.router, prefix="/templates", tags=["templates"])


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    logger.info("Starting Email Service...")

    # Start Redis subscriber in background
    asyncio.create_task(start_event_subscriber())

    logger.info("Email Service started successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "email-service", "version": "1.0.0", "status": "running"}
