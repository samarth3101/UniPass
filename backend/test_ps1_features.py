"""
Quick Test Script for PS1 Features
Run this to verify all PS1 endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# You'll need a valid token - get from login
TOKEN = ""  # Add your token here after logging in

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_participation_status():
    """Test Feature 1: Get canonical participation status"""
    print("\n🧪 Testing Feature 1: Participation Status...")
    event_id = 1  # Change to your event ID
    student_prn = "PRN001"  # Change to your student PRN
    
    response = requests.get(
        f"{BASE_URL}/ps1/participation/status/{event_id}/{student_prn}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_conflict_detection():
    """Test Feature 1: Detect event conflicts"""
    print("\n🧪 Testing Feature 1: Conflict Detection...")
    event_id = 1  # Change to your event ID
    
    response = requests.get(
        f"{BASE_URL}/ps1/participation/conflicts/{event_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Conflicts found: {len(response.json())}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_certificate_verification():
    """Test Feature 3: Public certificate verification"""
    print("\n🧪 Testing Feature 3: Certificate Verification...")
    cert_id = "CERT-XXXXXXXXXXXX"  # Change to your certificate ID
    
    # Note: This endpoint doesn't require authentication
    response = requests.get(
        f"{BASE_URL}/ps1/verify/certificate/{cert_id}"
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_role_assignment():
    """Test Feature 5: Assign event role"""
    print("\n🧪 Testing Feature 5: Role Assignment...")
    event_id = 1  # Change to your event ID
    
    data = {
        "student_prn": "PRN001",
        "role": "SPEAKER",
        "time_segment": "Day 1: 9AM-12PM"
    }
    
    response = requests.post(
        f"{BASE_URL}/ps1/roles/{event_id}/assign",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_get_event_roles():
    """Test Feature 5: Get all roles for event"""
    print("\n🧪 Testing Feature 5: Get Event Roles...")
    event_id = 1  # Change to your event ID
    
    response = requests.get(
        f"{BASE_URL}/ps1/roles/{event_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Roles found: {len(response.json())}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_certificate_revocation():
    """Test Feature 4: Revoke certificate"""
    print("\n🧪 Testing Feature 4: Certificate Revocation...")
    cert_id = "CERT-XXXXXXXXXXXX"  # Change to your certificate ID
    
    data = {
        "reason": "Test revocation - certificate issued in error"
    }
    
    response = requests.post(
        f"{BASE_URL}/ps1/certificate/{cert_id}/revoke",
        headers=headers,
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def main():
    """Run all tests"""
    print("="*70)
    print("🚀 PS1 Features Test Suite")
    print("="*70)
    
    if not TOKEN:
        print("\n❌ ERROR: Please set TOKEN variable after logging in")
        print("   1. Login at: POST /auth/login")
        print("   2. Copy the access_token from response")
        print("   3. Set TOKEN = 'your-token-here' in this script")
        return
    
    print(f"\nBase URL: {BASE_URL}")
    print(f"Token: {TOKEN[:20]}..." if len(TOKEN) > 20 else f"Token: {TOKEN}")
    
    # Run tests
    try:
        # test_participation_status()
        # test_conflict_detection()
        test_certificate_verification()  # No auth required
        # test_role_assignment()
        # test_get_event_roles()
        # test_certificate_revocation()
        
        print("\n" + "="*70)
        print("✅ Tests completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
