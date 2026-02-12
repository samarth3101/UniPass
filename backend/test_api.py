#!/usr/bin/env python3
"""Quick test to verify API is working after migration"""
import requests

BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("🔍 Testing health endpoint...")
response = requests.get(f"{BASE_URL}/health")
print(f"✅ Health: {response.json()}")

# Test 2: Login
print("\n🔍 Testing login...")
login_data = {"email": "admin@test.com", "password": "admin"}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Login successful")
    
    # Test 3: Get events
    print("\n🔍 Testing events endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/events/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Events endpoint working!")
        print(f"   Total events: {data.get('total', 0)}")
        if data.get('events'):
            first_event = data['events'][0]
            print(f"   First event has total_days: {first_event.get('total_days', 'N/A')}")
    else:
        print(f"❌ Events endpoint failed: {response.status_code}")
        print(f"   Error: {response.text}")
else:
    print(f"❌ Login failed: {response.status_code}")
    print(f"   Error: {response.text}")
    print("\n💡 Try with organizer@test.com if admin@test.com doesn't work")
