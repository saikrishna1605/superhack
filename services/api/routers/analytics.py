"""
Analytics Router
General analytics and reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from database import get_db
from models.models import User, Client, SoftwareLicense, ClientMetric
from routers.auth import get_current_user

router = APIRouter()

@router.get("/trends/revenue")
async def get_revenue_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get revenue trends over time (MSP only)"""
    if current_user.role != "msp":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. MSP role required."
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Simulate trend data (in production, query from ClientMetric)
    trends = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "revenue": 15000 + (i * 100),
            "new_clients": 1 if i % 7 == 0 else 0,
            "churned_clients": 1 if i % 15 == 0 else 0
        })
    
    return {
        "period": f"Last {days} days",
        "trends": trends,
        "total_revenue": sum(t["revenue"] for t in trends),
        "avg_daily_revenue": sum(t["revenue"] for t in trends) / days
    }

@router.get("/trends/cost")
async def get_cost_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get cost trends over time (IT Admin only)"""
    if current_user.role != "it_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. IT Admin role required."
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Simulate trend data
    trends = []
    base_cost = 25000
    for i in range(days):
        date = start_date + timedelta(days=i)
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "total_cost": base_cost + (i * 50),
            "optimization_savings": i * 20,
            "new_licenses": 2 if i % 5 == 0 else 0
        })
    
    return {
        "period": f"Last {days} days",
        "trends": trends,
        "total_cost": sum(t["total_cost"] for t in trends),
        "total_savings": sum(t["optimization_savings"] for t in trends)
    }

@router.get("/reports/executive-summary")
async def get_executive_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get executive summary report"""
    
    if current_user.role == "msp":
        # MSP executive summary
        clients = db.query(Client).filter(Client.owner_id == current_user.id).all()
        
        return {
            "role": "MSP",
            "period": "Current Month",
            "key_metrics": {
                "total_clients": len(clients),
                "monthly_recurring_revenue": sum(c.monthly_spend or 0 for c in clients),
                "average_health_score": sum(c.health_score or 0 for c in clients) / len(clients) if clients else 0,
                "at_risk_clients": len([c for c in clients if c.churn_risk == "high"]),
                "growth_rate": 8.5
            },
            "top_clients": sorted(
                [{"name": c.name, "revenue": c.monthly_spend} for c in clients],
                key=lambda x: x["revenue"] or 0,
                reverse=True
            )[:5],
            "action_items": [
                "Review 3 high-risk clients for retention strategies",
                "Follow up on 5 upsell opportunities worth $15,000",
                "Investigate 2 clients with declining health scores"
            ]
        }
    
    elif current_user.role == "it_admin":
        # IT Admin executive summary
        licenses = db.query(SoftwareLicense).filter(
            SoftwareLicense.owner_id == current_user.id
        ).all()
        
        total_cost = sum(l.monthly_cost or 0 for l in licenses)
        low_utilization = [l for l in licenses if l.utilization_percent and l.utilization_percent < 50]
        
        return {
            "role": "IT Admin",
            "period": "Current Month",
            "key_metrics": {
                "total_software_count": len(licenses),
                "monthly_spend": total_cost,
                "average_utilization": sum(l.utilization_percent or 0 for l in licenses) / len(licenses) if licenses else 0,
                "cost_savings_potential": sum(
                    l.monthly_cost * (1 - l.utilization_percent / 100)
                    for l in low_utilization
                ),
                "licenses_managed": sum(l.total_licenses or 0 for l in licenses)
            },
            "top_expenses": sorted(
                [{"software": l.software_name, "cost": l.monthly_cost} for l in licenses],
                key=lambda x: x["cost"] or 0,
                reverse=True
            )[:5],
            "action_items": [
                f"Deactivate {len(low_utilization)} unused licenses to save ${sum(l.monthly_cost * 0.3 for l in low_utilization):.2f}",
                "Review 2 cost anomalies detected this week",
                "Negotiate renewal for 3 software licenses expiring next month"
            ]
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role"
        )