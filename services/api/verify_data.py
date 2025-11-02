"""Quick verification script to check seeded data"""
from database import SessionLocal
from models.models import SoftwareLicense

db = SessionLocal()
licenses = db.query(SoftwareLicense).filter_by(owner_id=2).all()

print(f'\n✅ Found {len(licenses)} licenses\n')

total_monthly = 0
total_annual = 0
total_count = 0
categories = {}

for l in licenses:
    print(f'{l.software_name}:')
    print(f'  Monthly: ${l.monthly_cost:,.2f}')
    print(f'  Annual: ${l.annual_cost:,.2f}')
    print(f'  Licenses: {l.total_licenses}')
    print(f'  Category: {l.category}')
    print()
    
    total_monthly += l.monthly_cost or 0
    total_annual += l.annual_cost or 0
    total_count += l.total_licenses or 0
    
    if l.category:
        categories[l.category] = categories.get(l.category, 0) + (l.monthly_cost or 0)

print(f'\n📊 TOTALS:')
print(f'Total Monthly Cost: ${total_monthly:,.2f}')
print(f'Total Annual Cost: ${total_annual:,.2f}')
print(f'Total Licenses: {total_count}')
print(f'\nCategories: {len(categories)}')
for cat, cost in sorted(categories.items(), key=lambda x: x[1], reverse=True):
    print(f'  {cat}: ${cost:,.2f}')

db.close()
