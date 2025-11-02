"""
Seed script for IT Dashboard Software Licenses
Creates software license data matching the original hardcoded values:
- Total Monthly Cost: $45,200
- Total Licenses: 287
"""

import sys
from datetime import datetime, timedelta
from database import SessionLocal
from models.models import User, SoftwareLicense
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_it_licenses():
    db = SessionLocal()
    
    try:
        # Create or get IT admin user
        it_admin = db.query(User).filter(User.email == "it@pulseops.com").first()
        if not it_admin:
            it_admin = User(
                email="it@pulseops.com",
                username="itadmin",
                hashed_password=pwd_context.hash("itadmin123"),
                role="it_admin",
                company_name="PulseOps IT"
            )
            db.add(it_admin)
            db.commit()
            db.refresh(it_admin)
            print(f"Created IT admin user with ID: {it_admin.id}")
        else:
            print(f"Using existing IT admin user with ID: {it_admin.id}")
        
        # Delete existing licenses for this user
        db.query(SoftwareLicense).filter(SoftwareLicense.owner_id == it_admin.id).delete()
        db.commit()
        
        # Software licenses data matching original hardcoded data
        # Total: $45,200/month, 287 licenses
        licenses_data = [
            # Productivity Tools - $16,100/month, 75 licenses
            {
                "software_name": "Microsoft 365 E5",
                "vendor": "Microsoft",
                "category": "Productivity",
                "total_licenses": 50,
                "active_users": 48,
                "monthly_cost": 12500.00,
                "department": "Organization-wide",
                "renewal_date": datetime.now() + timedelta(days=180)
            },
            {
                "software_name": "Google Workspace Business",
                "vendor": "Google",
                "category": "Productivity",
                "total_licenses": 25,
                "active_users": 23,
                "monthly_cost": 3600.00,
                "department": "Marketing",
                "renewal_date": datetime.now() + timedelta(days=90)
            },
            
            # Development Tools - $9,200/month, 47 licenses
            {
                "software_name": "GitHub Enterprise",
                "vendor": "GitHub",
                "category": "Development",
                "total_licenses": 32,
                "active_users": 30,
                "monthly_cost": 6400.00,
                "department": "Engineering",
                "renewal_date": datetime.now() + timedelta(days=365)
            },
            {
                "software_name": "JetBrains All Products",
                "vendor": "JetBrains",
                "category": "Development",
                "total_licenses": 15,
                "active_users": 14,
                "monthly_cost": 2800.00,
                "department": "Engineering",
                "renewal_date": datetime.now() + timedelta(days=270)
            },
            
            # Communication - $7,800/month, 85 licenses
            {
                "software_name": "Slack Enterprise Grid",
                "vendor": "Slack",
                "category": "Communication",
                "total_licenses": 50,
                "active_users": 47,
                "monthly_cost": 4200.00,
                "department": "Organization-wide",
                "renewal_date": datetime.now() + timedelta(days=120)
            },
            {
                "software_name": "Zoom Business Plus",
                "vendor": "Zoom",
                "category": "Communication",
                "total_licenses": 28,
                "active_users": 27,
                "monthly_cost": 2600.00,
                "department": "Sales",
                "renewal_date": datetime.now() + timedelta(days=150)
            },
            {
                "software_name": "Microsoft Teams Phone",
                "vendor": "Microsoft",
                "category": "Communication",
                "total_licenses": 7,
                "active_users": 7,
                "monthly_cost": 1000.00,
                "department": "Support",
                "renewal_date": datetime.now() + timedelta(days=200)
            },
            
            # Security - $5,100/month, 32 licenses
            {
                "software_name": "CrowdStrike Falcon",
                "vendor": "CrowdStrike",
                "category": "Security",
                "total_licenses": 15,
                "active_users": 15,
                "monthly_cost": 2600.00,
                "department": "IT Security",
                "renewal_date": datetime.now() + timedelta(days=240)
            },
            {
                "software_name": "LastPass Enterprise",
                "vendor": "LastPass",
                "category": "Security",
                "total_licenses": 12,
                "active_users": 11,
                "monthly_cost": 1500.00,
                "department": "Organization-wide",
                "renewal_date": datetime.now() + timedelta(days=180)
            },
            {
                "software_name": "Okta Workforce Identity",
                "vendor": "Okta",
                "category": "Security",
                "total_licenses": 5,
                "active_users": 5,
                "monthly_cost": 1000.00,
                "department": "IT Security",
                "renewal_date": datetime.now() + timedelta(days=300)
            },
            
            # Cloud Services - $3,200/month, 23 licenses
            {
                "software_name": "AWS Business Support",
                "vendor": "Amazon",
                "category": "Cloud Services",
                "total_licenses": 10,
                "active_users": 10,
                "monthly_cost": 1600.00,
                "department": "Engineering",
                "renewal_date": datetime.now() + timedelta(days=365)
            },
            {
                "software_name": "Azure DevOps",
                "vendor": "Microsoft",
                "category": "Cloud Services",
                "total_licenses": 8,
                "active_users": 8,
                "monthly_cost": 1000.00,
                "department": "Engineering",
                "renewal_date": datetime.now() + timedelta(days=180)
            },
            {
                "software_name": "Dropbox Business Advanced",
                "vendor": "Dropbox",
                "category": "Cloud Services",
                "total_licenses": 5,
                "active_users": 4,
                "monthly_cost": 600.00,
                "department": "Design",
                "renewal_date": datetime.now() + timedelta(days=90)
            },
            
            # Other - $3,800/month, 25 licenses
            {
                "software_name": "Adobe Creative Cloud All Apps",
                "vendor": "Adobe",
                "category": "Other",
                "total_licenses": 10,
                "active_users": 9,
                "monthly_cost": 1800.00,
                "department": "Marketing",
                "renewal_date": datetime.now() + timedelta(days=270)
            },
            {
                "software_name": "Figma Professional",
                "vendor": "Figma",
                "category": "Other",
                "total_licenses": 8,
                "active_users": 8,
                "monthly_cost": 1200.00,
                "department": "Design",
                "renewal_date": datetime.now() + timedelta(days=210)
            },
            {
                "software_name": "Miro Team Plan",
                "vendor": "Miro",
                "category": "Other",
                "total_licenses": 7,
                "active_users": 7,
                "monthly_cost": 800.00,
                "department": "Product",
                "renewal_date": datetime.now() + timedelta(days=120)
            },
        ]
        
        # Create license records
        total_monthly = 0
        total_annual = 0
        total_licenses = 0
        total_active = 0
        
        for license_data in licenses_data:
            utilization = (license_data["active_users"] / license_data["total_licenses"]) * 100
            annual_cost = license_data["monthly_cost"] * 12
            
            license_obj = SoftwareLicense(
                software_name=license_data["software_name"],
                vendor=license_data["vendor"],
                category=license_data["category"],
                total_licenses=license_data["total_licenses"],
                active_users=license_data["active_users"],
                utilization_percent=round(utilization, 1),
                monthly_cost=license_data["monthly_cost"],
                annual_cost=annual_cost,
                department=license_data["department"],
                renewal_date=license_data["renewal_date"],
                owner_id=it_admin.id
            )
            db.add(license_obj)
            
            total_monthly += license_data["monthly_cost"]
            total_annual += annual_cost
            total_licenses += license_data["total_licenses"]
            total_active += license_data["active_users"]
        
        db.commit()
        
        print(f"\n✅ Successfully created {len(licenses_data)} software licenses")
        print(f"\n📊 Summary:")
        print(f"Total Monthly Cost: ${total_monthly:,.2f}")
        print(f"Total Annual Cost: ${total_annual:,.2f}")
        print(f"Total Licenses: {total_licenses}")
        print(f"Active Users: {total_active}")
        print(f"Overall Utilization: {(total_active/total_licenses*100):.1f}%")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_it_licenses()
