"""
Client management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.models import Client
from pydantic import BaseModel

router = APIRouter(prefix="/api/clients", tags=["clients"])

# Pydantic models for request/response
class ClientBase(BaseModel):
    name: str
    industry: str | None = None
    contract_value: float | None = None
    monthly_spend: float | None = None
    total_licenses: int | None = None
    total_users: int | None = None
    health_score: float | None = None
    churn_risk: str | None = None
    churn_probability: float | None = None
    contact: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None

class ClientCreate(ClientBase):
    client_id: str  # Accept client_id from frontend
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    contract_value: float | None = None
    monthly_spend: float | None = None
    total_licenses: int | None = None
    total_users: int | None = None
    health_score: float | None = None
    churn_risk: str | None = None
    churn_probability: float | None = None
    contact: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None
    health_score: float | None = None
    churn_risk: str | None = None
    churn_probability: float | None = None

class ClientResponse(ClientBase):
    id: int
    client_id: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ClientResponse])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all clients"""
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/", response_model=ClientResponse)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Use the client_id provided from frontend
    db_client = Client(
        client_id=client.client_id,
        name=client.name,
        industry=client.industry,
        contract_value=client.contract_value,
        monthly_spend=client.monthly_spend,
        total_licenses=client.total_licenses,
        total_users=client.total_users,
        health_score=client.health_score,
        churn_risk=client.churn_risk,
        churn_probability=client.churn_probability,
        contact=client.contact,
        email=client.email,
        phone=client.phone,
        status=client.status or 'Active'
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: int, client_update: ClientUpdate, db: Session = Depends(get_db)):
    """Update a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update only provided fields
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client"""
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return {"message": "Client deleted successfully"}
