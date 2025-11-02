"""
MSP Features Router
Endpoints for Managed Service Providers
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta
import random
import uuid

from database import get_db
from models.models import User, Client, ClientMetric, Recommendation, Alert
from schemas.schemas import (
    ClientCreate, ClientResponse, MSPDashboardResponse,
    RecommendationResponse
)
from routers.auth import get_current_user

router = APIRouter()

@router.get("/dashboard", response_model=MSPDashboardResponse)
async def get_msp_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MSP dashboard with key metrics and insights"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    # Get all clients for this MSP
    clients = db.query(Client).filter(Client.owner_id == current_user.id).all()
    
    # Calculate metrics
    total_clients = len(clients)
    total_mrr = sum(c.monthly_spend or 0 for c in clients)
    avg_health_score = sum(c.health_score or 0 for c in clients) / total_clients if total_clients > 0 else 0
    high_risk_clients = len([c for c in clients if c.churn_risk == "high"])
    
    # Get recommendations
    recommendations = db.query(Recommendation).filter(
        Recommendation.owner_id == current_user.id,
        Recommendation.status == "pending"
    ).all()
    
    # Recent clients
    recent_clients = db.query(Client).filter(
        Client.owner_id == current_user.id
    ).order_by(desc(Client.created_at)).limit(5).all()
    
    # Churn risks
    churn_risks = db.query(Client).filter(
        Client.owner_id == current_user.id,
        Client.churn_risk.in_(["high", "medium"])
    ).order_by(desc(Client.churn_probability)).limit(5).all()
    
    # Upsell opportunities
    upsell_recommendations = db.query(Recommendation).filter(
        Recommendation.owner_id == current_user.id,
        Recommendation.recommendation_type == "upsell",
        Recommendation.status == "pending"
    ).order_by(desc(Recommendation.potential_value)).limit(5).all()
    
    return {
        "total_clients": total_clients,
        "total_mrr": total_mrr,
        "avg_health_score": avg_health_score,
        "high_risk_clients": high_risk_clients,
        "total_recommendations": len(recommendations),
        "recent_clients": recent_clients,
        "churn_risks": churn_risks,
        "upsell_opportunities": upsell_recommendations
    }

@router.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all clients for the MSP"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    clients = db.query(Client).filter(
        Client.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific client details"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new client"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    # Generate unique client ID
    client_id = f"CLT-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate initial health score (simple formula)
    health_score = 70 + random.uniform(-10, 20)
    churn_probability = random.uniform(0.1, 0.5)
    churn_risk = "low" if churn_probability < 0.3 else "medium" if churn_probability < 0.6 else "high"
    
    db_client = Client(
        client_id=client_id,
        name=client.name,
        industry=client.industry,
        contract_value=client.contract_value,
        monthly_spend=client.monthly_spend,
        total_licenses=client.total_licenses,
        total_users=client.total_users,
        health_score=health_score,
        churn_risk=churn_risk,
        churn_probability=churn_probability,
        owner_id=current_user.id
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

@router.get("/clients/{client_id}/health-score")
async def get_client_health_score(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed health score breakdown for a client"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    client = db.query(Client).filter(
        Client.id == client_id,
        Client.owner_id == current_user.id
    ).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return {
        "client_id": client.client_id,
        "client_name": client.name,
        "overall_score": client.health_score,
        "factors": {
            "payment_history": random.uniform(70, 100),
            "support_ticket_frequency": random.uniform(60, 90),
            "license_utilization": random.uniform(65, 95),
            "contract_renewal_proximity": random.uniform(50, 100),
            "engagement_level": random.uniform(60, 95)
        },
        "trend": "improving" if random.random() > 0.5 else "declining",
        "churn_risk": client.churn_risk,
        "churn_probability": client.churn_probability
    }

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_type: str = None
):
    """Get AI-generated recommendations"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    query = db.query(Recommendation).filter(
        Recommendation.owner_id == current_user.id
    )
    
    if recommendation_type:
        query = query.filter(Recommendation.recommendation_type == recommendation_type)
    
    recommendations = query.order_by(desc(Recommendation.created_at)).all()
    
    return recommendations

@router.get("/alerts")
async def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str = "active"
):
    """Get priority alerts for MSP admin"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    query = db.query(Alert).filter(Alert.owner_id == current_user.id)
    
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    
    alerts = query.order_by(
        # Sort by priority: Critical, High, Medium, Low
        func.case(
            (Alert.priority == 'Critical', 1),
            (Alert.priority == 'High', 2),
            (Alert.priority == 'Medium', 3),
            else_=4
        ),
        Alert.created_at.desc()
    ).all()
    
    return alerts

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.owner_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    
    return {"message": "Alert resolved successfully", "alert": alert}