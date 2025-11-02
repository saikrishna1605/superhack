#!/usr/bin/env python3
"""
Database Initialization and Migration Script
Sets up PostgreSQL database schema and seeds initial data
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'services' / 'api'))

from sqlalchemy import create_engine, text
from database import Base
from models.models import User, Client, ClientMetric, SoftwareLicense, LicenseUsage, CostAnomaly, Recommendation
from datetime import datetime, timedelta
import random

class DatabaseSetup:
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(db_url)
    
    def test_connection(self):
        """Test database connection"""
        print("🔌 Testing database connection...")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"  ✅ Connected to PostgreSQL")
                print(f"  Version: {version[:50]}...")
                return True
        except Exception as e:
            print(f"  ❌ Connection failed: {e}")
            return False
    
    def create_schema(self):
        """Create all tables"""
        print("\n🏗️  Creating database schema...")
        try:
            Base.metadata.create_all(self.engine)
            print("  ✅ Schema created successfully")
            
            # List created tables
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """))
                tables = [row[0] for row in result]
                print(f"\n  📋 Created tables:")
                for table in tables:
                    print(f"    - {table}")
            
            return True
        except Exception as e:
            print(f"  ❌ Schema creation failed: {e}")
            return False
    
    def drop_schema(self):
        """Drop all tables"""
        print("\n⚠️  Dropping database schema...")
        try:
            Base.metadata.drop_all(self.engine)
            print("  ✅ Schema dropped successfully")
            return True
        except Exception as e:
            print(f"  ❌ Schema drop failed: {e}")
            return False
    
    def seed_data(self):
        """Seed initial data"""
        print("\n🌱 Seeding initial data...")
        
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self.engine)
        session = Session()
        
        try:
            # Create MSP users
            print("  Creating users...")
            msp_user = User(
                email="msp@pulseops.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7TaA2Ec0m6",  # password: msp123
                full_name="MSP Admin",
                role="msp",
                is_active=True
            )
            
            it_user = User(
                email="it@pulseops.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7TaA2Ec0m6",  # password: it123
                full_name="IT Manager",
                role="it_team",
                is_active=True
            )
            
            session.add_all([msp_user, it_user])
            session.commit()
            print(f"    ✅ Created {2} users")
            
            # Create clients
            print("  Creating clients...")
            clients = [
                Client(
                    name="TechCorp Inc",
                    industry="Technology",
                    employee_count=250,
                    monthly_revenue=25000,
                    contract_start_date=datetime.now() - timedelta(days=730),
                    contract_end_date=datetime.now() + timedelta(days=365),
                    health_score=85.5,
                    is_active=True
                ),
                Client(
                    name="FinServe Ltd",
                    industry="Finance",
                    employee_count=150,
                    monthly_revenue=18000,
                    contract_start_date=datetime.now() - timedelta(days=365),
                    contract_end_date=datetime.now() + timedelta(days=365),
                    health_score=72.3,
                    is_active=True
                ),
                Client(
                    name="HealthPlus Medical",
                    industry="Healthcare",
                    employee_count=500,
                    monthly_revenue=45000,
                    contract_start_date=datetime.now() - timedelta(days=1095),
                    contract_end_date=datetime.now() + timedelta(days=365),
                    health_score=91.2,
                    is_active=True
                ),
                Client(
                    name="EduTech Academy",
                    industry="Education",
                    employee_count=100,
                    monthly_revenue=12000,
                    contract_start_date=datetime.now() - timedelta(days=180),
                    contract_end_date=datetime.now() + timedelta(days=545),
                    health_score=65.8,
                    is_active=True
                )
            ]
            
            session.add_all(clients)
            session.commit()
            print(f"    ✅ Created {len(clients)} clients")
            
            # Create client metrics
            print("  Creating client metrics...")
            metrics_count = 0
            for client in clients:
                for i in range(12):  # Last 12 months
                    date = datetime.now() - timedelta(days=30 * i)
                    metric = ClientMetric(
                        client_id=client.id,
                        metric_date=date,
                        ticket_count=random.randint(5, 25),
                        response_time_hours=random.uniform(1, 8),
                        resolution_time_hours=random.uniform(4, 48),
                        user_satisfaction=random.uniform(3.5, 5.0),
                        license_utilization=random.uniform(60, 95)
                    )
                    session.add(metric)
                    metrics_count += 1
            
            session.commit()
            print(f"    ✅ Created {metrics_count} client metrics")
            
            # Create software licenses
            print("  Creating software licenses...")
            licenses = [
                SoftwareLicense(
                    name="Microsoft 365 Business",
                    vendor="Microsoft",
                    category="Productivity",
                    total_licenses=250,
                    cost_per_license=12.50,
                    billing_cycle="monthly",
                    renewal_date=datetime.now() + timedelta(days=60)
                ),
                SoftwareLicense(
                    name="Salesforce Professional",
                    vendor="Salesforce",
                    category="CRM",
                    total_licenses=50,
                    cost_per_license=75.00,
                    billing_cycle="monthly",
                    renewal_date=datetime.now() + timedelta(days=90)
                ),
                SoftwareLicense(
                    name="Zoom Business",
                    vendor="Zoom",
                    category="Communication",
                    total_licenses=100,
                    cost_per_license=19.99,
                    billing_cycle="monthly",
                    renewal_date=datetime.now() + timedelta(days=45)
                ),
                SoftwareLicense(
                    name="Adobe Creative Cloud",
                    vendor="Adobe",
                    category="Design",
                    total_licenses=25,
                    cost_per_license=54.99,
                    billing_cycle="monthly",
                    renewal_date=datetime.now() + timedelta(days=120)
                ),
                SoftwareLicense(
                    name="Slack Business+",
                    vendor="Slack",
                    category="Communication",
                    total_licenses=150,
                    cost_per_license=12.50,
                    billing_cycle="monthly",
                    renewal_date=datetime.now() + timedelta(days=75)
                )
            ]
            
            session.add_all(licenses)
            session.commit()
            print(f"    ✅ Created {len(licenses)} software licenses")
            
            # Create license usage data
            print("  Creating license usage data...")
            usage_count = 0
            for license in licenses:
                for i in range(6):  # Last 6 months
                    date = datetime.now() - timedelta(days=30 * i)
                    usage = LicenseUsage(
                        license_id=license.id,
                        usage_date=date,
                        active_users=random.randint(
                            int(license.total_licenses * 0.5),
                            license.total_licenses
                        ),
                        total_usage_hours=random.randint(1000, 5000),
                        department="Engineering"
                    )
                    session.add(usage)
                    usage_count += 1
            
            session.commit()
            print(f"    ✅ Created {usage_count} license usage records")
            
            # Create some anomalies
            print("  Creating cost anomalies...")
            anomalies = [
                CostAnomaly(
                    license_id=licenses[0].id,
                    detected_date=datetime.now() - timedelta(days=5),
                    anomaly_type="spike",
                    severity="medium",
                    expected_value=3125.00,
                    actual_value=4500.00,
                    description="Unexpected increase in Microsoft 365 costs",
                    is_resolved=False
                ),
                CostAnomaly(
                    license_id=licenses[1].id,
                    detected_date=datetime.now() - timedelta(days=15),
                    anomaly_type="unusual_pattern",
                    severity="low",
                    expected_value=3750.00,
                    actual_value=3900.00,
                    description="Unusual Salesforce usage pattern detected",
                    is_resolved=True,
                    resolved_date=datetime.now() - timedelta(days=10)
                )
            ]
            
            session.add_all(anomalies)
            session.commit()
            print(f"    ✅ Created {len(anomalies)} anomalies")
            
            # Create recommendations
            print("  Creating recommendations...")
            recommendations = [
                Recommendation(
                    client_id=clients[3].id,
                    recommendation_type="upsell",
                    title="Upgrade to Premium Support",
                    description="Based on ticket volume, premium support would provide faster response times",
                    estimated_value=5000.00,
                    confidence_score=0.85,
                    priority="high",
                    status="pending"
                ),
                Recommendation(
                    license_id=licenses[0].id,
                    recommendation_type="cost_optimization",
                    title="Reduce Microsoft 365 Licenses",
                    description="25 licenses have been inactive for 90+ days",
                    estimated_value=3750.00,
                    confidence_score=0.92,
                    priority="medium",
                    status="pending"
                ),
                Recommendation(
                    client_id=clients[1].id,
                    recommendation_type="churn_prevention",
                    title="Schedule Business Review",
                    description="Client health score declining, recommend proactive engagement",
                    estimated_value=18000.00,
                    confidence_score=0.78,
                    priority="high",
                    status="pending"
                )
            ]
            
            session.add_all(recommendations)
            session.commit()
            print(f"    ✅ Created {len(recommendations)} recommendations")
            
            print("\n  ✅ Data seeding complete!")
            
            # Summary
            print("\n📊 Database Summary:")
            print(f"  Users: {session.query(User).count()}")
            print(f"  Clients: {session.query(Client).count()}")
            print(f"  Client Metrics: {session.query(ClientMetric).count()}")
            print(f"  Software Licenses: {session.query(SoftwareLicense).count()}")
            print(f"  License Usage: {session.query(LicenseUsage).count()}")
            print(f"  Anomalies: {session.query(CostAnomaly).count()}")
            print(f"  Recommendations: {session.query(Recommendation).count()}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Seeding failed: {e}")
            session.rollback()
            return False
        finally:
            session.close()

def main():
    parser = argparse.ArgumentParser(description='Setup PulseOps database')
    parser.add_argument('--db-url', 
                       required=True,
                       help='Database URL (postgresql://user:pass@host/db)')
    parser.add_argument('--action',
                       choices=['create', 'drop', 'reset', 'seed'],
                       default='create',
                       help='Action to perform')
    
    args = parser.parse_args()
    
    setup = DatabaseSetup(args.db_url)
    
    if not setup.test_connection():
        sys.exit(1)
    
    if args.action == 'drop':
        if setup.drop_schema():
            print("\n✅ Database dropped successfully")
        else:
            sys.exit(1)
    
    elif args.action == 'create':
        if setup.create_schema():
            print("\n✅ Database schema created successfully")
        else:
            sys.exit(1)
    
    elif args.action == 'reset':
        if setup.drop_schema() and setup.create_schema():
            print("\n✅ Database reset successfully")
        else:
            sys.exit(1)
    
    elif args.action == 'seed':
        if setup.seed_data():
            print("\n✅ Database seeded successfully")
        else:
            sys.exit(1)
    
    print("\n🎉 Done!")

if __name__ == '__main__':
    main()
