from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "email-service"
    SERVICE_PORT: int = 8001
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Email Provider
    EMAIL_PROVIDER: str = "smtp"  # smtp or sendgrid

    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # SendGrid
    SENDGRID_API_KEY: str = ""

    # Email Defaults
    FROM_EMAIL: str
    FROM_NAME: str = "Payroll System"

    # Frontend
    FRONTEND_URL: str

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ]

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
