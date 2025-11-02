"""
Configuration settings for PulseOps AI
Environment variables and constants
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PulseOps AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "pulseops")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "true").lower() == "true"
    
    @property
    def DATABASE_URL(self) -> str:
        if self.USE_SQLITE:
            return "sqlite:///./pulseops.db"
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "pulseops-data")
    DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "pulseops-metrics")
    
    # ML Service
    ML_ENDPOINT: str = os.getenv("ML_ENDPOINT", "http://localhost:5000")
    
    # Monitoring thresholds
    CHURN_RISK_THRESHOLD: float = 0.6
    ANOMALY_THRESHOLD: float = 0.3
    UTILIZATION_LOW_THRESHOLD: float = 50.0
    
    class Config:
        case_sensitive = True

settings = Settings()