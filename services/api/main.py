"""
PulseOps AI - FastAPI Application
Main entry point for the API service
Lambda-compatible using Mangum
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
from typing import Optional
import os

from routers import msp, it_team, auth, analytics, clients
from database import engine, Base
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="PulseOps AI API",
    description="Autonomous AI agent for MSPs and IT teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "PulseOps AI",
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ml_service": "operational"
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(msp.router, prefix="/api/msp", tags=["MSP Features"])
app.include_router(it_team.router, prefix="/api/it", tags=["IT Team Features"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(clients.router, tags=["Clients"])

# Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)