"""
Test script to verify IT dashboard API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing IT Dashboard API Endpoints")
print("=" * 60)

# 1. Login
print("\n1. Logging in as IT admin...")
params = {
    "email": "it@pulseops.com",
    "password": "itadmin123"
}
response = requests.post(f"{BASE_URL}/api/auth/login", params=params)
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
    exit(1)

# 2. Test spending trend endpoint
print("\n2. Testing spending trend endpoint...")
params = {"year": 2024, "from_month": 1, "to_month": 12}
response = requests.get(f"{BASE_URL}/api/it/spending-trend", headers=headers, params=params)
if response.status_code == 200:
    trend_data = response.json()
    print(f"✅ Spending trend data received: {len(trend_data)} months")
    print(f"   First month: {trend_data[0]}")
    print(f"   Last month: {trend_data[-1]}")
else:
    print(f"❌ Spending trend failed: {response.status_code}")
    print(response.text)

# 3. Test cost breakdown endpoint
print("\n3. Testing cost breakdown endpoint...")
response = requests.get(f"{BASE_URL}/api/it/cost-breakdown", headers=headers)
if response.status_code == 200:
    breakdown_data = response.json()
    print(f"✅ Cost breakdown data received: {len(breakdown_data)} categories")
    
    total_monthly = sum(item['monthly'] for item in breakdown_data)
    total_annual = sum(item['annual'] for item in breakdown_data)
    total_licenses = sum(item['licenses'] for item in breakdown_data)
    
    print(f"\n   📊 Summary:")
    print(f"   Total Monthly Cost: ${total_monthly:,.2f}")
    print(f"   Total Annual Cost: ${total_annual:,.2f}")
    print(f"   Total Licenses: {total_licenses}")
    
    print(f"\n   📋 Categories:")
    for item in breakdown_data:
        print(f"   - {item['category']}: ${item['monthly']:,.2f}/month ({item['licenses']} licenses)")
else:
    print(f"❌ Cost breakdown failed: {response.status_code}")
    print(response.text)

# 4. Test software by category endpoint
print("\n4. Testing software by category endpoint...")
response = requests.get(f"{BASE_URL}/api/it/software/category/Productivity", headers=headers)
if response.status_code == 200:
    software_data = response.json()
    print(f"✅ Software data received: {len(software_data)} items in Productivity")
    for sw in software_data[:3]:  # Show first 3
        print(f"   - {sw['software_name']}: ${sw['monthly_cost']}/month")
else:
    print(f"❌ Software by category failed: {response.status_code}")
    print(response.text)

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
