"""
Seed script to populate software licenses with categories
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models.models import Base, SoftwareLicense, User
from datetime import datetime, timedelta
import random

def seed_software_licenses():
    """Seed software licenses with categories"""
    db = SessionLocal()
    
    try:
        # Get or create IT admin user
        it_admin = db.query(User).filter(User.role == "it_admin").first()
        if not it_admin:
            print("Creating IT admin user...")
            # Simple hash for demo
            it_admin = User(
                username="itadmin",
                email="it@pulseops.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU/FdO8pMu1W",  # admin123
                company_name="PulseOps Inc",
                role="it_admin",
                is_active=True
            )
            db.add(it_admin)
            db.commit()
            db.refresh(it_admin)
            print(f"✅ Created IT admin user (id: {it_admin.id})")
        
        # Clear existing software licenses
        db.query(SoftwareLicense).filter(SoftwareLicense.owner_id == it_admin.id).delete()
        db.commit()
        
        # Software data with categories (no duplicates)
        software_data = [
            # Productivity (35%)
            {
                "software_name": "Microsoft 365 Suite",
                "vendor": "Microsoft",
                "category": "Productivity",
                "total_licenses": 150,
                "active_users": 142,
                "monthly_cost": 12750,
                "department": "Company-wide"
            },
            {
                "software_name": "Google Workspace",
                "vendor": "Google",
                "category": "Productivity",
                "total_licenses": 50,
                "active_users": 38,
                "monthly_cost": 2250,
                "department": "Marketing"
            },
            {
                "software_name": "Notion",
                "vendor": "Notion Labs",
                "category": "Productivity",
                "total_licenses": 75,
                "active_users": 68,
                "monthly_cost": 750,
                "department": "Product"
            },
            
            # Development (30%)
            {
                "software_name": "GitHub Enterprise",
                "vendor": "GitHub",
                "category": "Development",
                "total_licenses": 80,
                "active_users": 75,
                "monthly_cost": 6400,
                "department": "Engineering"
            },
            {
                "software_name": "JetBrains IntelliJ",
                "vendor": "JetBrains",
                "category": "Development",
                "total_licenses": 60,
                "active_users": 58,
                "monthly_cost": 3600,
                "department": "Engineering"
            },
            {
                "software_name": "AWS Services",
                "vendor": "Amazon",
                "category": "Development",
                "total_licenses": 1,
                "active_users": 1,
                "monthly_cost": 2400,
                "department": "Engineering"
            },
            
            # Communication (20%)
            {
                "software_name": "Slack Enterprise",
                "vendor": "Salesforce",
                "category": "Communication",
                "total_licenses": 180,
                "active_users": 157,
                "monthly_cost": 5400,
                "department": "Company-wide"
            },
            {
                "software_name": "Zoom Business",
                "vendor": "Zoom",
                "category": "Communication",
                "total_licenses": 100,
                "active_users": 92,
                "monthly_cost": 2000,
                "department": "Company-wide"
            },
            {
                "software_name": "Miro",
                "vendor": "Miro",
                "category": "Communication",
                "total_licenses": 50,
                "active_users": 41,
                "monthly_cost": 1500,
                "department": "Product"
            },
            
            # Security (12%)
            {
                "software_name": "Norton Antivirus",
                "vendor": "Norton",
                "category": "Security",
                "total_licenses": 200,
                "active_users": 200,
                "monthly_cost": 3000,
                "department": "IT"
            },
            {
                "software_name": "1Password Business",
                "vendor": "1Password",
                "category": "Security",
                "total_licenses": 150,
                "active_users": 138,
                "monthly_cost": 1800,
                "department": "IT"
            },
            {
                "software_name": "Cloudflare Enterprise",
                "vendor": "Cloudflare",
                "category": "Security",
                "total_licenses": 1,
                "active_users": 1,
                "monthly_cost": 800,
                "department": "IT"
            },
            
            # Other (3%)
            {
                "software_name": "Adobe Creative Cloud",
                "vendor": "Adobe",
                "category": "Other",
                "total_licenses": 25,
                "active_users": 23,
                "monthly_cost": 1250,
                "department": "Design"
            },
            {
                "software_name": "Figma Professional",
                "vendor": "Figma",
                "category": "Other",
                "total_licenses": 30,
                "active_users": 28,
                "monthly_cost": 900,
                "department": "Design"
            },
            {
                "software_name": "Salesforce CRM",
                "vendor": "Salesforce",
                "category": "Other",
                "total_licenses": 40,
                "active_users": 35,
                "monthly_cost": 6000,
                "department": "Sales"
            }
        ]
        
        # Create software licenses
        for data in software_data:
            utilization = (data["active_users"] / data["total_licenses"] * 100) if data["total_licenses"] > 0 else 0
            annual_cost = data["monthly_cost"] * 12
            
            renewal_date = datetime.utcnow() + timedelta(days=random.randint(30, 365))
            
            license = SoftwareLicense(
                software_name=data["software_name"],
                vendor=data["vendor"],
                category=data["category"],
                total_licenses=data["total_licenses"],
                active_users=data["active_users"],
                utilization_percent=round(utilization, 1),
                monthly_cost=data["monthly_cost"],
                annual_cost=annual_cost,
                department=data["department"],
                renewal_date=renewal_date,
                owner_id=it_admin.id
            )
            db.add(license)
        
        db.commit()
        
        # Calculate totals
        total_monthly = sum(s["monthly_cost"] for s in software_data)
        print(f"\n✅ Successfully seeded {len(software_data)} software licenses")
        print(f"📊 Total Monthly Cost: ${total_monthly:,.2f}")
        print("\n📈 Category Breakdown:")
        
        categories = {}
        for s in software_data:
            cat = s["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += s["monthly_cost"]
        
        for cat, cost in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / total_monthly * 100)
            print(f"   {cat}: ${cost:,.2f} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"Error seeding software: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding software licenses...")
    seed_software_licenses()
    print("\n✨ Seeding complete!")
