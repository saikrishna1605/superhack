"""Verify IT admin user exists and test login"""
from database import SessionLocal
from models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

# Check if IT admin exists
user = db.query(User).filter_by(email='it@pulseops.com').first()

if user:
    print(f'✅ IT Admin user found:')
    print(f'   Email: {user.email}')
    print(f'   Role: {user.role}')
    print(f'   ID: {user.id}')
    
    # Test password verification
    test_password = 'itadmin123'
    is_valid = pwd_context.verify(test_password, user.hashed_password)
    
    if is_valid:
        print(f'\n✅ Password "itadmin123" is CORRECT')
        print(f'\n📋 Login Credentials:')
        print(f'   Email: it@pulseops.com')
        print(f'   Password: itadmin123')
    else:
        print(f'\n❌ Password "itadmin123" is INCORRECT')
        print(f'   Need to reset password!')
else:
    print(f'❌ IT Admin user NOT found!')
    print(f'   Need to run seed_it_licenses.py')

db.close()
