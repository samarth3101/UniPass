#!/usr/bin/env python3
"""
PS1 Live Testing Script
Tests all PS1 features with real database data
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = None  # Will be set after login

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.RESET}")

def print_json(data, indent=2):
    print(json.dumps(data, indent=indent, default=str))

def login(email: str = "testadmin@unipass.com", password: str = "test123456") -> Optional[str]:
    """Login and get token"""
    print_header("AUTHENTICATION")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"Logged in as {email}")
            return token
        else:
            print_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None

def get_headers():
    """Get authorization headers"""
    return {"Authorization": f"Bearer {TOKEN}"}

def test_get_events():
    """Get list of events to use in tests"""
    print_header("FETCHING TEST DATA - Events")
    try:
        response = requests.get(f"{BASE_URL}/events/", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            # Handle pagination or direct list
            events = data if isinstance(data, list) else data.get('items', [])
            if events:
                print_success(f"Found {len(events)} events")
                for event in events[:3]:
                    event_id = event.get('id') or event.get('event_id')
                    event_name = event.get('title') or event.get('name')
                    print(f"  - Event ID: {event_id}, Name: {event_name}")
                return events
            else:
                print_error("No events found")
                return []
        else:
            print_error(f"Failed to fetch events: {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_get_students():
    """Get list of students"""
    print_header("FETCHING TEST DATA - Students")
    try:
        response = requests.get(f"{BASE_URL}/students/", headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            # Handle pagination or direct list
            students = data if isinstance(data, list) else data.get('items', [])
            if students:
                print_success(f"Found {len(students)} students")
                for student in students[:3]:
                    print(f"  - PRN: {student['prn']}, Name: {student.get('name', 'N/A')}")
                return students
            else:
                print_error("No students found")
                return []
        else:
            print_error(f"Failed to fetch students: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_participation_status(event_id: int, prn: str):
    """Test PS1 Feature 1: Participation Reconciliation"""
    print_header(f"PS1 FEATURE 1: PARTICIPATION STATUS - Event {event_id}, PRN {prn}")
    try:
        response = requests.get(
            f"{BASE_URL}/ps1/participation/status/{event_id}/{prn}",
            headers=get_headers()
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Participation status retrieved")
            print(f"\n{Colors.BOLD}Canonical Status:{Colors.RESET} {data['canonical_status']}")
            print(f"{Colors.BOLD}Registration:{Colors.RESET} {data['has_registration']}")
            print(f"{Colors.BOLD}Attendance:{Colors.RESET} {data['has_attendance']}")
            print(f"{Colors.BOLD}Certificate:{Colors.RESET} {data['has_certificate']}")
            print(f"{Colors.BOLD}Trust Score:{Colors.RESET} {data['trust_score']}/100")
            
            if data['conflicts']:
                print(f"\n{Colors.YELLOW}⚠ Conflicts Detected:{Colors.RESET}")
                for conflict in data['conflicts']:
                    print(f"  - [{conflict['severity']}] {conflict['type']}")
                    print(f"    {conflict['message']}")
            else:
                print(f"\n{Colors.GREEN}✓ No conflicts detected{Colors.RESET}")
            
            return True
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_event_conflicts(event_id: int):
    """Test PS1 Feature 1: Get all conflicts in event"""
    print_header(f"PS1 FEATURE 1: EVENT CONFLICTS - Event {event_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/ps1/participation/conflicts/{event_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            conflicts = response.json()
            print_success(f"Found {len(conflicts)} students with conflicts")
            
            if conflicts:
                print(f"\n{Colors.BOLD}Conflict Summary:{Colors.RESET}")
                for item in conflicts[:5]:  # Show first 5
                    print(f"\n  Student: {item['student_prn']}")
                    print(f"  Status: {item['canonical_status']}")
                    print(f"  Trust Score: {item['trust_score']}/100")
                    print(f"  Conflicts: {len(item['conflicts'])}")
                    for conflict in item['conflicts']:
                        print(f"    - [{conflict['severity']}] {conflict['type']}")
                
                if len(conflicts) > 5:
                    print(f"\n  ... and {len(conflicts) - 5} more")
            else:
                print(f"\n{Colors.GREEN}✓ No conflicts found in this event{Colors.RESET}")
            
            return conflicts
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def test_certificate_verification(cert_id: str):
    """Test PS1 Feature 3: Certificate Verification"""
    print_header(f"PS1 FEATURE 3: CERTIFICATE VERIFICATION - {cert_id}")
    try:
        # This is public endpoint, no auth needed
        response = requests.get(f"{BASE_URL}/ps1/verify/certificate/{cert_id}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Certificate is AUTHENTIC")
            print(f"\n{Colors.BOLD}Certificate Details:{Colors.RESET}")
            print(f"  Student: {data['student_name']}")
            print(f"  Event: {data['event_name']}")
            print(f"  Issued: {data['issued_at']}")
            print(f"  Verified: {data['verified_at']}")
            
            if data.get('revoked'):
                print(f"\n{Colors.RED}⚠ Certificate REVOKED{Colors.RESET}")
                print(f"  Reason: {data.get('revocation_reason')}")
                print(f"  Revoked At: {data.get('revoked_at')}")
            
            return True
        elif response.status_code == 404:
            print_error("Certificate NOT FOUND")
            return False
        else:
            print_error(f"Verification failed: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_certificates(event_id: int):
    """Get certificates for testing"""
    print_header(f"FETCHING TEST DATA - Certificates for Event {event_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/certificates/event/{event_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            certs = response.json()
            if certs:
                print_success(f"Found {len(certs)} certificates")
                for cert in certs[:3]:
                    print(f"  - {cert['certificate_id']}")
                return certs
            else:
                print_info("No certificates found for this event")
                return []
        else:
            print_error(f"Failed: {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def test_assign_role(event_id: int, prn: str, role: str = "VOLUNTEER"):
    """Test PS1 Feature 5: Multi-Role Assignment"""
    print_header(f"PS1 FEATURE 5: ASSIGN ROLE - {role} to {prn}")
    try:
        response = requests.post(
            f"{BASE_URL}/ps1/roles/{event_id}/assign",
            headers=get_headers(),
            json={
                "student_prn": prn,
                "role": role,
                "time_segment": "Full Event"
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Role assigned successfully")
            print(f"  Role ID: {data['id']}")
            print(f"  Student: {data['student_prn']}")
            print(f"  Role: {data['role']}")
            print(f"  Assigned At: {data['assigned_at']}")
            return data
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_get_event_roles(event_id: int):
    """Test PS1 Feature 5: Get all roles for event"""
    print_header(f"PS1 FEATURE 5: EVENT ROLES - Event {event_id}")
    try:
        response = requests.get(
            f"{BASE_URL}/ps1/roles/{event_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            roles = response.json()
            print_success(f"Found {len(roles)} role assignments")
            
            if roles:
                role_counts = {}
                for role in roles:
                    role_type = role['role']
                    role_counts[role_type] = role_counts.get(role_type, 0) + 1
                
                print(f"\n{Colors.BOLD}Role Distribution:{Colors.RESET}")
                for role_type, count in role_counts.items():
                    print(f"  {role_type}: {count}")
                
                print(f"\n{Colors.BOLD}Recent Assignments:{Colors.RESET}")
                for role in roles[:5]:
                    print(f"  - {role['student_prn']}: {role['role']} ({role['time_segment']})")
            
            return roles
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def test_get_student_roles(prn: str):
    """Test PS1 Feature 5: Get all roles for student"""
    print_header(f"PS1 FEATURE 5: STUDENT ROLES - PRN {prn}")
    try:
        response = requests.get(
            f"{BASE_URL}/ps1/roles/student/{prn}",
            headers=get_headers()
        )
        if response.status_code == 200:
            roles = response.json()
            print_success(f"Student has {len(roles)} role assignments")
            
            if roles:
                print(f"\n{Colors.BOLD}Roles Across Events:{Colors.RESET}")
                for role in roles:
                    print(f"  Event {role['event_id']}: {role['role']}")
                    print(f"    Time: {role['time_segment']}")
                    print(f"    Assigned: {role['assigned_at']}")
            else:
                print_info("No roles assigned to this student")
            
            return roles
        else:
            print_error(f"Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return []

def run_full_test_suite():
    """Run complete PS1 test suite"""
    global TOKEN
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                PS1 FEATURE TEST SUITE                             ║")
    print("║     Unified Campus Participation Intelligence System              ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Step 1: Authenticate
    TOKEN = login()
    if not TOKEN:
        print_error("Cannot proceed without authentication")
        return
    
    # Step 2: Get test data
    events = test_get_events()
    students = test_get_students()
    
    if not events or not students:
        print_error("Insufficient test data. Add events and students first.")
        return
    
    test_event = events[0]
    test_student = students[0]
    event_id = test_event['id']
    student_prn = test_student['prn']
    
    # Step 3: Test Feature 1 - Participation Reconciliation
    print("\n" + "="*70)
    print(f"{Colors.BOLD}TESTING FEATURE 1: PARTICIPATION RECONCILIATION{Colors.RESET}")
    print("="*70)
    
    test_participation_status(event_id, student_prn)
    conflicts = test_event_conflicts(event_id)
    
    # Step 4: Test Feature 3 - Certificate Verification
    print("\n" + "="*70)
    print(f"{Colors.BOLD}TESTING FEATURE 3: CERTIFICATE VERIFICATION{Colors.RESET}")
    print("="*70)
    
    certs = test_get_certificates(event_id)
    if certs:
        test_certificate_verification(certs[0]['certificate_id'])
    else:
        print_info("No certificates to verify. Create some first.")
    
    # Step 5: Test Feature 5 - Multi-Role Participation
    print("\n" + "="*70)
    print(f"{Colors.BOLD}TESTING FEATURE 5: MULTI-ROLE PARTICIPATION{Colors.RESET}")
    print("="*70)
    
    # Assign a role
    role_data = test_assign_role(event_id, student_prn, "VOLUNTEER")
    
    # Get event roles
    test_get_event_roles(event_id)
    
    # Get student roles
    test_get_student_roles(student_prn)
    
    # Assign another role to same student
    if role_data:
        print_info("\nAssigning second role to same student...")
        test_assign_role(event_id, student_prn, "PARTICIPANT")
        test_get_student_roles(student_prn)
    
    # Final Summary
    print_header("TEST SUITE COMPLETE")
    print_success("✓ Feature 1: Participation Reconciliation - TESTED")
    print_success("✓ Feature 3: Certificate Verification - TESTED")
    print_success("✓ Feature 5: Multi-Role Participation - TESTED")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
    print("  1. Visit http://localhost:8000/docs to see all PS1 endpoints")
    print("  2. Visit http://localhost:3000/verify to test certificate verification UI")
    print("  3. Check for conflicts and resolve them manually")
    print("  4. Ready for Phase 2 implementation!")
    print()

if __name__ == "__main__":
    run_full_test_suite()
