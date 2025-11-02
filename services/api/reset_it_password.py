"""Reset IT admin password to fix bcrypt issues"""
from database import SessionLocal
from models.models import User
from passlib.context import CryptContext

# Use the same password context as the auth router
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

# Find IT admin
user = db.query(User).filter_by(email='it@pulseops.com').first()

if user:
    print(f'Found IT admin: {user.email}')
    
    # Create new password hash using passlib (same as auth router)
    password = 'itadmin123'
    hashed = pwd_context.hash(password)
    
    # Update user password
    user.hashed_password = hashed
    db.commit()
    
    print(f'✅ Password reset successfully!')
    print(f'\n📋 Login Credentials:')
    print(f'   Email: it@pulseops.com')
    print(f'   Password: itadmin123')
    
    # Test the new password
    is_valid = pwd_context.verify(password, user.hashed_password)
    
    if is_valid:
        print(f'\n✅ Password verification: SUCCESS')
    else:
        print(f'\n❌ Password verification: FAILED')
else:
    print(f'❌ IT admin user not found!')
    print(f'   Run seed_it_licenses.py first')

db.close()
