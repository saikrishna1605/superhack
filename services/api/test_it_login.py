"""Test IT admin login through API"""
import requests

# Test login endpoint
login_url = "http://localhost:8000/api/auth/login"
params = {
    "email": "it@pulseops.com",
    "password": "itadmin123"
}

try:
    response = requests.post(login_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f'✅ Login SUCCESSFUL!')
        print(f'\n📋 Response:')
        print(f'   Token: {data.get("access_token", "")[:50]}...')
        print(f'   User: {data.get("user", {})}')
        print(f'\n✅ IT Admin can login with:')
        print(f'   Email: it@pulseops.com')
        print(f'   Password: itadmin123')
    else:
        print(f'❌ Login FAILED!')
        print(f'   Status: {response.status_code}')
        print(f'   Error: {response.text}')
        
except requests.exceptions.ConnectionError:
    print(f'❌ Cannot connect to API server!')
    print(f'   Make sure backend is running on port 8000')
except Exception as e:
    print(f'❌ Error: {e}')
