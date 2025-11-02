"""
Seed script for software licenses
"""

from database import SessionLocal
from models.models import User, SoftwareLicense
from datetime import datetime, timedelta

def seed_software_licenses():
    db = SessionLocal()
    
    try:
        # Get or create IT admin user
        it_admin = db.query(User).filter(User.email == "it@pulseops.com").first()
        
        if not it_admin:
            print("IT admin user not found. Creating...")
            it_admin = User(
                email="it@pulseops.com",
                username="itadmin",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5XkBvz7EZX.hK",  # password: itadmin123
                role="it_admin"
            )
            db.add(it_admin)
            db.commit()
            db.refresh(it_admin)
            print(f"Created IT admin user with ID: {it_admin.id}")
        
        # Clear existing software licenses for this user
        db.query(SoftwareLicense).filter(SoftwareLicense.owner_id == it_admin.id).delete()
        db.commit()
        
        # Software license data
        software_data = [
            # Productivity Suite
            {"name": "Microsoft 365 Suite", "vendor": "Microsoft", "category": "Productivity", "total": 120, "active": 115, "monthly": 12750, "dept": "All"},
            {"name": "Google Workspace", "vendor": "Google", "category": "Productivity", "total": 50, "active": 48, "monthly": 3050, "dept": "Marketing"},
            
            # Development Tools
            {"name": "GitHub Enterprise", "vendor": "GitHub", "category": "Development", "total": 45, "active": 42, "monthly": 8900, "dept": "Engineering"},
            {"name": "JetBrains Suite", "vendor": "JetBrains", "category": "Development", "total": 30, "active": 28, "monthly": 3500, "dept": "Engineering"},
            
            # Communication
            {"name": "Slack Enterprise", "vendor": "Slack", "category": "Communication", "total": 150, "active": 127, "monthly": 4500, "dept": "All"},
            {"name": "Zoom Business", "vendor": "Zoom", "category": "Communication", "total": 100, "active": 85, "monthly": 2400, "dept": "All"},
            {"name": "Microsoft Teams Phone", "vendor": "Microsoft", "category": "Communication", "total": 75, "active": 70, "monthly": 2000, "dept": "Sales"},
            
            # Security Software
            {"name": "Norton Security", "vendor": "Norton", "category": "Security", "total": 200, "active": 200, "monthly": 2800, "dept": "All"},
            {"name": "LastPass Enterprise", "vendor": "LastPass", "category": "Security", "total": 150, "active": 145, "monthly": 1500, "dept": "All"},
            {"name": "VPN Pro", "vendor": "ExpressVPN", "category": "Security", "total": 100, "active": 92, "monthly": 1300, "dept": "All"},
            
            # Cloud Services
            {"name": "AWS Services", "vendor": "Amazon", "category": "Cloud Services", "total": 20, "active": 18, "monthly": 1200, "dept": "Engineering"},
            {"name": "Azure Cloud", "vendor": "Microsoft", "category": "Cloud Services", "total": 15, "active": 14, "monthly": 900, "dept": "Engineering"},
            {"name": "Dropbox Business", "vendor": "Dropbox", "category": "Cloud Services", "total": 50, "active": 45, "monthly": 400, "dept": "All"},
            
            # Design & Media
            {"name": "Adobe Creative Cloud", "vendor": "Adobe", "category": "Other", "total": 25, "active": 22, "monthly": 1250, "dept": "Design"},
            {"name": "Figma Professional", "vendor": "Figma", "category": "Other", "total": 20, "active": 19, "monthly": 600, "dept": "Design"},
            
            # Project Management
            {"name": "Jira Software", "vendor": "Atlassian", "category": "Other", "total": 80, "active": 75, "monthly": 1600, "dept": "All"},
            {"name": "Monday.com", "vendor": "Monday", "category": "Other", "total": 40, "active": 35, "monthly": 800, "dept": "Operations"},
            
            # CRM & Sales
            {"name": "Salesforce CRM", "vendor": "Salesforce", "category": "Other", "total": 60, "active": 58, "monthly": 6000, "dept": "Sales"},
            {"name": "HubSpot Marketing", "vendor": "HubSpot", "category": "Other", "total": 30, "active": 28, "monthly": 2400, "dept": "Marketing"},
        ]
        
        licenses_created = 0
        for data in software_data:
            utilization = (data["active"] / data["total"]) * 100 if data["total"] > 0 else 0
            annual = data["monthly"] * 12
            renewal_date = datetime.utcnow() + timedelta(days=random.choice([30, 60, 90, 180, 365]))
            
            license = SoftwareLicense(
                software_name=data["name"],
                vendor=data["vendor"],
                category=data["category"],
                total_licenses=data["total"],
                active_users=data["active"],
                utilization_percent=round(utilization, 2),
                monthly_cost=data["monthly"],
                annual_cost=annual,
                department=data["dept"],
                renewal_date=renewal_date,
                owner_id=it_admin.id
            )
            db.add(license)
            licenses_created += 1
        
        db.commit()
        print(f"✅ Successfully created {licenses_created} software licenses")
        
        # Calculate total costs
        total_monthly = sum(d["monthly"] for d in software_data)
        total_annual = total_monthly * 12
        total_licenses = sum(d["total"] for d in software_data)
        active_users = sum(d["active"] for d in software_data)
        
        print(f"\n📊 Summary:")
        print(f"Total Monthly Cost: ${total_monthly:,.2f}")
        print(f"Total Annual Cost: ${total_annual:,.2f}")
        print(f"Total Licenses: {total_licenses}")
        print(f"Active Users: {active_users}")
        print(f"Overall Utilization: {(active_users/total_licenses*100):.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import random
    seed_software_licenses()
