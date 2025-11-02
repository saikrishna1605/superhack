"""
Seed script to populate priority alerts in the database
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.models import Alert, User, Base
from datetime import datetime

def seed_alerts():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Get the first MSP user (assuming at least one exists)
        msp_user = db.query(User).filter(User.role == "msp").first()
        
        if not msp_user:
            # Create a default MSP user if none exists
            print("No MSP user found. Creating default MSP user...")
            
            # Use a simple hash for seeding purposes
            msp_user = User(
                email="msp@pulseops.ai",
                username="msp_admin",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU2xc3rBq/7W",  # "password"
                role="msp",
                company_name="PulseOps MSP",
                is_active=True
            )
            db.add(msp_user)
            db.commit()
            db.refresh(msp_user)
            print(f"✓ Created MSP user: {msp_user.email}")
        
        # Clear existing alerts for this user
        db.query(Alert).filter(Alert.owner_id == msp_user.id).delete()
        db.commit()
        
        # Create priority alerts
        alerts = [
            Alert(
                alert_type='critical',
                title='License Compliance Issue',
                description='Over-deployed licenses detected: 125 active users with only 100 licenses',
                client_id='TC001',
                client_name='TechCorp Inc',
                impact='Compliance Risk',
                priority='Critical',
                action_label='Review License Usage',
                action_route='/msp/licenses',
                details='Navigate to Active Licenses page to review license allocation and usage patterns',
                due_date='2 days',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='warning',
                title='Security Update Required',
                description='Critical security patches pending for 15+ workstations',
                client_id='AS004',
                client_name='DataSystems LLC',
                impact='Security Vulnerability',
                priority='High',
                action_label='Schedule Maintenance',
                action_route='/msp/clients/AS004',
                details='View client details to schedule maintenance window and apply security patches',
                due_date='5 days',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='action',
                title='Contract Renewal Due',
                description='Annual contract expires in 30 days - $182,400 ARR at risk',
                client_id='CP007',
                client_name='CloudNet Solutions',
                impact='$182K Revenue Risk',
                priority='High',
                action_label='Contact for Renewal',
                action_route='/msp/clients/CP007',
                details='Open client profile to review contract details and initiate renewal process',
                due_date='30 days',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='support',
                title='High Support Ticket Volume',
                description='12 open tickets (40% increase) - possible training gap or product issue',
                client_id='FS009',
                client_name='FinServ Partners',
                impact='Client Satisfaction Risk',
                priority='Medium',
                action_label='Schedule Review Call',
                action_route='/msp/clients/FS009',
                details='Access client dashboard to analyze ticket trends and schedule follow-up call',
                due_date='7 days',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='usage',
                title='Declining Usage Pattern',
                description='User activity down 45% over last 60 days - potential churn indicator',
                client_id='RH015',
                client_name='RetailHub Co',
                impact='Churn Risk',
                priority='Medium',
                action_label='Engagement Check-in',
                action_route='/msp/clients/RH015',
                details='Review client health metrics and usage analytics to identify engagement issues',
                due_date='14 days',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='critical',
                title='Payment Overdue',
                description='Invoice #3421 overdue by 15 days - $8,500 outstanding',
                client_id='MN012',
                client_name='ManufactureTech',
                impact='Cash Flow Risk',
                priority='Critical',
                action_label='Follow Up Payment',
                action_route='/msp/clients/MN012',
                details='Contact client for payment collection and review account status',
                due_date='Overdue',
                status='active',
                owner_id=msp_user.id
            ),
            Alert(
                alert_type='warning',
                title='License Expiration Pending',
                description='Microsoft 365 licenses expiring in 10 days for 45 users',
                client_id='HC018',
                client_name='HealthCare Systems',
                impact='Service Disruption Risk',
                priority='High',
                action_label='Renew Licenses',
                action_route='/msp/licenses',
                details='Process license renewal to avoid service interruption',
                due_date='10 days',
                status='active',
                owner_id=msp_user.id
            )
        ]
        
        # Add all alerts to database
        db.add_all(alerts)
        db.commit()
        
        print(f"✓ Successfully seeded {len(alerts)} alerts for user: {msp_user.email}")
        
    except Exception as e:
        print(f"Error seeding alerts: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_alerts()
