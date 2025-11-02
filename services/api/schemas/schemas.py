"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: str
    company_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Client schemas
class ClientBase(BaseModel):
    name: str
    industry: Optional[str] = None
    contract_value: Optional[float] = None
    monthly_spend: Optional[float] = None
    total_licenses: Optional[int] = None
    total_users: Optional[int] = None

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    client_id: str
    health_score: Optional[float] = None
    churn_risk: Optional[str] = None
    churn_probability: Optional[float] = None
    last_support_ticket: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Software License schemas
class SoftwareLicenseBase(BaseModel):
    software_name: str
    vendor: Optional[str] = None
    total_licenses: int
    active_users: Optional[int] = None
    monthly_cost: float
    department: Optional[str] = None

class SoftwareLicenseCreate(SoftwareLicenseBase):
    pass

class SoftwareLicenseResponse(SoftwareLicenseBase):
    id: int
    utilization_percent: Optional[float] = None
    annual_cost: Optional[float] = None
    renewal_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Anomaly schemas
class CostAnomalyResponse(BaseModel):
    id: int
    software_name: str
    expected_cost: float
    actual_cost: float
    variance_percent: float
    severity: str
    cause: Optional[str] = None
    detected_at: datetime
    resolved: bool
    
    class Config:
        from_attributes = True

# Recommendation schemas
class RecommendationResponse(BaseModel):
    id: int
    recommendation_type: str
    title: str
    description: str
    potential_value: Optional[float] = None
    priority: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class MSPDashboardResponse(BaseModel):
    total_clients: int
    total_mrr: float
    avg_health_score: float
    high_risk_clients: int
    total_recommendations: int
    recent_clients: List[ClientResponse]
    churn_risks: List[ClientResponse]
    upsell_opportunities: List[RecommendationResponse]

class ITDashboardResponse(BaseModel):
    total_software: int
    total_monthly_cost: float
    total_licenses: int
    active_licenses: int
    avg_utilization: float
    cost_savings_potential: float
    recent_anomalies: List[CostAnomalyResponse]
    low_utilization_software: List[SoftwareLicenseResponse]
    recommendations: List[RecommendationResponse]