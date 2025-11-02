"""
Seed database with sample client data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models.models import Client
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

# Sample clients matching localStorage data
sample_clients = [
    # LOW RISK CLIENTS (churn_probability < 25)
    {"client_id": "CL0001", "name": "TechCorp Inc", "industry": "Technology", "total_licenses": 45, "monthly_spend": 12500, "health_score": 92, "churn_risk": "low", "churn_probability": 15, "total_users": 150, "contact": "John Smith", "email": "john.smith@techcorp.com", "phone": "+1 (555) 123-4567", "status": "Active"},
    {"client_id": "CL0003", "name": "Global Systems", "industry": "Finance", "total_licenses": 75, "monthly_spend": 18000, "health_score": 95, "churn_risk": "low", "churn_probability": 8, "total_users": 200, "contact": "Michael Chen", "email": "michael.chen@globalsystems.com", "phone": "+1 (555) 345-6789", "status": "Active"},
    {"client_id": "CL0005", "name": "MegaSoft Corp", "industry": "Software", "total_licenses": 90, "monthly_spend": 22000, "health_score": 88, "churn_risk": "low", "churn_probability": 12, "total_users": 250, "contact": "David Park", "email": "david.park@megasoft.com", "phone": "+1 (555) 567-8901", "status": "Active"},
    {"client_id": "CL0007", "name": "CloudPeak Inc", "industry": "Technology", "total_licenses": 55, "monthly_spend": 14500, "health_score": 91, "churn_risk": "low", "churn_probability": 10, "total_users": 165, "contact": "Robert Williams", "email": "robert.w@cloudpeak.com", "phone": "+1 (555) 789-0123", "status": "Active"},
    {"client_id": "CL0009", "name": "Velocity Partners", "industry": "Marketing", "total_licenses": 28, "monthly_spend": 7800, "health_score": 85, "churn_risk": "low", "churn_probability": 18, "total_users": 75, "contact": "James Anderson", "email": "james.anderson@velocity.com", "phone": "+1 (555) 901-2345", "status": "Active"},
    {"client_id": "CL0011", "name": "FusionEdge Ltd", "industry": "Technology", "total_licenses": 62, "monthly_spend": 15500, "health_score": 89, "churn_risk": "low", "churn_probability": 14, "total_users": 180, "contact": "Christopher Lee", "email": "chris.lee@fusionedge.com", "phone": "+1 (555) 123-7890", "status": "Active"},
    {"client_id": "CL0013", "name": "Quantum Group", "industry": "Research", "total_licenses": 42, "monthly_spend": 11500, "health_score": 87, "churn_risk": "low", "churn_probability": 16, "total_users": 125, "contact": "Daniel Kim", "email": "daniel.kim@quantum.com", "phone": "+1 (555) 345-9012", "status": "Active"},
    {"client_id": "CL0014", "name": "Sterling Global", "industry": "Finance", "total_licenses": 68, "monthly_spend": 17200, "health_score": 93, "churn_risk": "low", "churn_probability": 9, "total_users": 190, "contact": "Amanda White", "email": "amanda.white@sterling.com", "phone": "+1 (555) 456-0123", "status": "Active"},
    {"client_id": "CL0015", "name": "TitanSphere Corp", "industry": "Technology", "total_licenses": 52, "monthly_spend": 13800, "health_score": 84, "churn_risk": "low", "churn_probability": 20, "total_users": 155, "contact": "Thomas Wilson", "email": "thomas.wilson@titansphere.com", "phone": "+1 (555) 567-1234", "status": "Active"},
    {"client_id": "CL0018", "name": "WaveDriver Inc", "industry": "Technology", "total_licenses": 58, "monthly_spend": 15000, "health_score": 90, "churn_risk": "low", "churn_probability": 11, "total_users": 170, "contact": "Dr. Michelle Thompson", "email": "michelle.thompson@wavedriver.com", "phone": "+1 (555) 890-4567", "status": "Active"},
    {"client_id": "CL0019", "name": "Zenith Tech", "industry": "Software", "total_licenses": 50, "monthly_spend": 13200, "health_score": 86, "churn_risk": "low", "churn_probability": 17, "total_users": 145, "contact": "Brian Jackson", "email": "brian.jackson@zenithtech.com", "phone": "+1 (555) 901-5678", "status": "Active"},
    {"client_id": "CL0020", "name": "Apex Partners", "industry": "Finance", "total_licenses": 65, "monthly_spend": 16500, "health_score": 94, "churn_risk": "low", "churn_probability": 7, "total_users": 185, "contact": "Nicole Harris", "email": "nicole.harris@apexpartners.com", "phone": "+1 (555) 012-6789", "status": "Active"},
    
    # MEDIUM RISK CLIENTS (churn_probability 25-70)
    {"client_id": "CL0002", "name": "Blue Industries", "industry": "Manufacturing", "total_licenses": 30, "monthly_spend": 8500, "health_score": 78, "churn_risk": "medium", "churn_probability": 35, "total_users": 85, "contact": "Sarah Johnson", "email": "sarah.johnson@blueindustries.com", "phone": "+1 (555) 234-5678", "status": "Active"},
    {"client_id": "CL0006", "name": "DataEdge Partners", "industry": "Consulting", "total_licenses": 40, "monthly_spend": 11000, "health_score": 82, "churn_risk": "medium", "churn_probability": 28, "total_users": 120, "contact": "Dr. Lisa Martinez", "email": "lisa.martinez@dataedge.com", "phone": "+1 (555) 678-9012", "status": "Active"},
    {"client_id": "CL0008", "name": "SecureNet Systems", "industry": "Security", "total_licenses": 35, "monthly_spend": 9500, "health_score": 76, "churn_risk": "medium", "churn_probability": 38, "total_users": 95, "contact": "Jennifer Taylor", "email": "jen.taylor@securenet.com", "phone": "+1 (555) 890-1234", "status": "Active"},
    {"client_id": "CL0010", "name": "NextWave Digital", "industry": "Media", "total_licenses": 48, "monthly_spend": 12800, "health_score": 80, "churn_risk": "medium", "churn_probability": 32, "total_users": 135, "contact": "Maria Garcia", "email": "maria.garcia@nextwave.com", "phone": "+1 (555) 012-3456", "status": "Active"},
    {"client_id": "CL0012", "name": "Pinnacle Industries", "industry": "Manufacturing", "total_licenses": 38, "monthly_spend": 10200, "health_score": 73, "churn_risk": "medium", "churn_probability": 42, "total_users": 110, "contact": "Patricia Brown", "email": "patricia.brown@pinnacle.com", "phone": "+1 (555) 234-8901", "status": "Active"},
    {"client_id": "CL0016", "name": "Unity Analytics", "industry": "Data Science", "total_licenses": 45, "monthly_spend": 12200, "health_score": 79, "churn_risk": "medium", "churn_probability": 34, "total_users": 130, "contact": "Jessica Moore", "email": "jessica.moore@unityanalytics.com", "phone": "+1 (555) 678-2345", "status": "Active"},
    {"client_id": "CL0021", "name": "HorizonLink Corp", "industry": "Technology", "total_licenses": 36, "monthly_spend": 9800, "health_score": 75, "churn_risk": "medium", "churn_probability": 45, "total_users": 105, "contact": "Steven Roberts", "email": "steven.roberts@horizonlink.com", "phone": "+1 (555) 111-2222", "status": "Active"},
    {"client_id": "CL0022", "name": "PrimeEdge Solutions", "industry": "Consulting", "total_licenses": 33, "monthly_spend": 9100, "health_score": 77, "churn_risk": "medium", "churn_probability": 40, "total_users": 98, "contact": "Rachel Green", "email": "rachel.green@primeedge.com", "phone": "+1 (555) 222-3333", "status": "Active"},
    
    # HIGH RISK CLIENTS (churn_probability > 70)
    {"client_id": "CL0004", "name": "Acme Solutions", "industry": "Technology", "total_licenses": 22, "monthly_spend": 6500, "health_score": 65, "churn_risk": "high", "churn_probability": 78, "total_users": 60, "contact": "Emily Rodriguez", "email": "emily.r@acmesolutions.com", "phone": "+1 (555) 456-7890", "status": "Active"},
    {"client_id": "CL0017", "name": "Vertex Enterprises", "industry": "Consulting", "total_licenses": 32, "monthly_spend": 8900, "health_score": 70, "churn_risk": "high", "churn_probability": 72, "total_users": 88, "contact": "Kevin Davis", "email": "kevin.davis@vertex.com", "phone": "+1 (555) 789-3456", "status": "Active"},
    {"client_id": "CL0023", "name": "RetailMax Corp", "industry": "Retail", "total_licenses": 28, "monthly_spend": 7500, "health_score": 62, "churn_risk": "high", "churn_probability": 85, "total_users": 75, "contact": "Laura Mitchell", "email": "laura.mitchell@retailmax.com", "phone": "+1 (555) 333-4444", "status": "Active"},
    {"client_id": "CL0024", "name": "LegacyTech Inc", "industry": "Technology", "total_licenses": 25, "monthly_spend": 7000, "health_score": 58, "churn_risk": "high", "churn_probability": 82, "total_users": 68, "contact": "Mark Anderson", "email": "mark.anderson@legacytech.com", "phone": "+1 (555) 444-5555", "status": "Active"},
    {"client_id": "CL0025", "name": "OldGuard Systems", "industry": "Manufacturing", "total_licenses": 20, "monthly_spend": 6200, "health_score": 60, "churn_risk": "high", "churn_probability": 88, "total_users": 55, "contact": "Susan Miller", "email": "susan.miller@oldguard.com", "phone": "+1 (555) 555-6666", "status": "Active"}
]

def seed_clients():
    db = SessionLocal()
    try:
        # Check if we already have clients
        existing_count = db.query(Client).count()
        if existing_count > 0:
            print(f"Database has {existing_count} clients. Updating client IDs to new format...")
            # Delete all existing clients to reseed with new IDs
            db.query(Client).delete()
            db.commit()
            print("Cleared existing clients.")
        
        # Add sample clients
        for client_data in sample_clients:
            client = Client(**client_data)
            db.add(client)
        
        db.commit()
        print(f"Successfully seeded {len(sample_clients)} clients with new CL#### format!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding database with sample clients...")
    seed_clients()
