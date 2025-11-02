"""
Sample data seeding script for development and testing
Run this to populate the database with sample data
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models.models import User, Client, SoftwareLicense, LicenseUsage, CostAnomaly, Recommendation
from routers.auth import get_password_hash

def seed_database():
    """Seed database with sample data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding users...")
        # Create MSP user
        msp_user = User(
            email="msp@pulseops.com",
            username="msp_admin",
            hashed_password=get_password_hash("password123"),
            role="msp",
            company_name="PulseOps MSP Services"
        )
        db.add(msp_user)
        
        # Create IT Admin user
        it_user = User(
            email="it@pulseops.com",
            username="it_admin",
            hashed_password=get_password_hash("password123"),
            role="it_admin",
            company_name="TechCorp Inc"
        )
        db.add(it_user)
        db.commit()
        
        print("Seeding MSP clients...")
        # Sample clients for MSP
        clients_data = [
            {"name": "TechCorp Solutions", "industry": "Technology", "contract_value": 15000, "monthly_spend": 2500, "licenses": 45, "users": 120},
            {"name": "MedLife Healthcare", "industry": "Healthcare", "contract_value": 25000, "monthly_spend": 4200, "licenses": 78, "users": 200},
            {"name": "EduPrime Academy", "industry": "Education", "contract_value": 8000, "monthly_spend": 1200, "licenses": 25, "users": 80},
            {"name": "FinServe Bank", "industry": "Finance", "contract_value": 35000, "monthly_spend": 5800, "licenses": 120, "users": 350},
            {"name": "RetailMax Corp", "industry": "Retail", "contract_value": 12000, "monthly_spend": 2000, "licenses": 60, "users": 150}
        ]
        
        for idx, client_data in enumerate(clients_data):
            health_score = 70 + random.uniform(-10, 25)
            churn_prob = random.uniform(0.1, 0.7)
            churn_risk = "low" if churn_prob < 0.3 else "medium" if churn_prob < 0.6 else "high"
            
            client = Client(
                client_id=f"CLT-{str(idx+1).zfill(3)}",
                name=client_data["name"],
                industry=client_data["industry"],
                contract_value=client_data["contract_value"],
                monthly_spend=client_data["monthly_spend"],
                total_licenses=client_data["licenses"],
                total_users=client_data["users"],
                health_score=health_score,
                churn_risk=churn_risk,
                churn_probability=churn_prob,
                last_support_ticket=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                owner_id=msp_user.id
            )
            db.add(client)
        
        db.commit()
        
        print("Seeding software licenses for IT team...")
        # Sample software licenses
        software_data = [
            {"name": "Microsoft 365", "vendor": "Microsoft", "licenses": 500, "active": 380, "cost": 7500, "dept": "All"},
            {"name": "Slack Premium", "vendor": "Slack", "licenses": 200, "active": 145, "cost": 1600, "dept": "Engineering"},
            {"name": "Adobe Creative Suite", "vendor": "Adobe", "licenses": 50, "active": 25, "cost": 2500, "dept": "Marketing"},
            {"name": "Salesforce", "vendor": "Salesforce", "licenses": 75, "active": 68, "cost": 5625, "dept": "Sales"},
            {"name": "Zoom Pro", "vendor": "Zoom", "licenses": 300, "active": 220, "cost": 4500, "dept": "All"},
            {"name": "Jira Software", "vendor": "Atlassian", "licenses": 100, "active": 85, "cost": 1500, "dept": "Engineering"},
            {"name": "Tableau", "vendor": "Tableau", "licenses": 30, "active": 15, "cost": 2100, "dept": "Analytics"}
        ]
        
        for sw_data in software_data:
            utilization = (sw_data["active"] / sw_data["licenses"] * 100) if sw_data["licenses"] > 0 else 0
            
            license = SoftwareLicense(
                software_name=sw_data["name"],
                vendor=sw_data["vendor"],
                total_licenses=sw_data["licenses"],
                active_users=sw_data["active"],
                utilization_percent=utilization,
                monthly_cost=sw_data["cost"],
                annual_cost=sw_data["cost"] * 12,
                department=sw_data["dept"],
                renewal_date=datetime.utcnow() + timedelta(days=random.randint(30, 365)),
                owner_id=it_user.id
            )
            db.add(license)
        
        db.commit()
        
        print("Seeding cost anomalies...")
        # Sample anomalies
        anomalies = [
            {"software": "AWS Services", "expected": 2500, "actual": 4200, "severity": "high", "cause": "Unexpected EC2 instance scaling"},
            {"software": "Zoom Pro", "expected": 800, "actual": 1200, "severity": "medium", "cause": "Additional webinar licenses purchased"},
            {"software": "Salesforce", "expected": 5625, "actual": 7000, "severity": "medium", "cause": "New API usage charges"}
        ]
        
        for anom in anomalies:
            variance = ((anom["actual"] - anom["expected"]) / anom["expected"] * 100)
            anomaly = CostAnomaly(
                software_name=anom["software"],
                expected_cost=anom["expected"],
                actual_cost=anom["actual"],
                variance_percent=variance,
                severity=anom["severity"],
                cause=anom["cause"],
                detected_at=datetime.utcnow() - timedelta(days=random.randint(1, 7)),
                resolved=random.choice([True, False]),
                owner_id=it_user.id
            )
            db.add(anomaly)
        
        db.commit()
        
        print("Seeding recommendations...")
        # MSP recommendations
        msp_recommendations = [
            {
                "type": "upsell",
                "title": "Upsell Cloud Backup to MedLife Healthcare",
                "desc": "Client has shown interest in disaster recovery. Recommend cloud backup solution worth $1,500/month.",
                "value": 18000,
                "priority": "high"
            },
            {
                "type": "churn_prevention",
                "title": "Risk: TechCorp Solutions showing declining engagement",
                "desc": "Health score dropped 15 points. Schedule check-in call and review service quality.",
                "value": 30000,
                "priority": "high"
            },
            {
                "type": "upsell",
                "title": "Security Assessment for FinServe Bank",
                "desc": "Compliance requirements increasing. Offer security audit and implementation package.",
                "value": 25000,
                "priority": "medium"
            }
        ]
        
        for rec in msp_recommendations:
            recommendation = Recommendation(
                recommendation_type=rec["type"],
                title=rec["title"],
                description=rec["desc"],
                potential_value=rec["value"],
                priority=rec["priority"],
                status="pending",
                owner_id=msp_user.id
            )
            db.add(recommendation)
        
        # IT recommendations
        it_recommendations = [
            {
                "type": "cost_saving",
                "title": "Deactivate 25 unused Adobe Creative Suite licenses",
                "desc": "25 licenses haven't been used in 60+ days. Potential monthly savings: $1,250",
                "value": 15000,
                "priority": "high"
            },
            {
                "type": "cost_saving",
                "title": "Consolidate Zoom and Microsoft Teams",
                "desc": "90% overlap in users. Consider consolidating to Teams to save $3,000/month.",
                "value": 36000,
                "priority": "medium"
            },
            {
                "type": "cost_saving",
                "title": "Negotiate Salesforce renewal",
                "desc": "Contract up for renewal in 60 days. Historical 15% discount available.",
                "value": 10125,
                "priority": "medium"
            }
        ]
        
        for rec in it_recommendations:
            recommendation = Recommendation(
                recommendation_type=rec["type"],
                title=rec["title"],
                description=rec["desc"],
                potential_value=rec["value"],
                priority=rec["priority"],
                status="pending",
                owner_id=it_user.id
            )
            db.add(recommendation)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print("\nTest Users:")
        print("  MSP User: msp@pulseops.com / password123")
        print("  IT Admin: it@pulseops.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()