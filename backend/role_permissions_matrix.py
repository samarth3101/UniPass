"""
Role Permissions Matrix - Visual Guide
This file documents the complete permission structure
"""

PERMISSIONS_MATRIX = {
    "Feature": {
        "Scanner": "Access Level",
        "Organizer": "Access Level", 
        "Admin": "Access Level"
    },
    
    # Navigation & UI
    "Dashboard": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Full Access",
        "Admin": "✅ Full Access"
    },
    
    # Event Management
    "Create Events": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Can Create",
        "Admin": "✅ Can Create"
    },
    "Edit Events": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Can Edit Own",
        "Admin": "✅ Can Edit All"
    },
    "Delete Events": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Can Delete Own",
        "Admin": "✅ Can Delete All"
    },
    "View Events": {
        "Scanner": "✅ Read Only",
        "Organizer": "✅ Full Access",
        "Admin": "✅ Full Access"
    },
    
    # Attendance Management
    "Scan QR Codes": {
        "Scanner": "✅ Full Access",
        "Organizer": "✅ Full Access",
        "Admin": "✅ Full Access"
    },
    "View Attendance Dashboard": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Full Access",
        "Admin": "✅ Full Access"
    },
    "Export Attendance": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Can Export",
        "Admin": "✅ Can Export"
    },
    
    # Student Analytics
    "View Student Analytics": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Can View",
        "Admin": "✅ Can View"
    },
    "Student Details": {
        "Scanner": "❌ No Access",
        "Organizer": "✅ Read Only",
        "Admin": "✅ Full Access"
    },
    
    # System Administration
    "Manage Users": {
        "Scanner": "❌ No Access",
        "Organizer": "❌ No Access",
        "Admin": "✅ Full Access"
    },
    "System Settings": {
        "Scanner": "❌ No Access",
        "Organizer": "❌ No Access",
        "Admin": "✅ Full Access"
    },
    "Audit Logs": {
        "Scanner": "❌ No Access",
        "Organizer": "❌ No Access",
        "Admin": "✅ Full Access"
    }
}


def print_permissions_matrix():
    """Print formatted permissions matrix"""
    print("\n" + "="*80)
    print("UNIPASS ROLE-BASED ACCESS CONTROL MATRIX")
    print("="*80 + "\n")
    
    # Print header
    print(f"{'Feature':<30} {'Scanner':<20} {'Organizer':<20} {'Admin':<20}")
    print("-" * 90)
    
    # Print each feature
    for feature, roles in PERMISSIONS_MATRIX.items():
        if feature == "Feature":
            continue
        
        print(f"{feature:<30} {roles['Scanner']:<20} {roles['Organizer']:<20} {roles['Admin']:<20}")
    
    print("\n" + "="*80)
    print("Legend: ✅ = Has Access | ❌ = No Access")
    print("="*80 + "\n")


# Backend Route Protection Reference
BACKEND_ROUTES = {
    "Public Routes (No Auth)": [
        "POST /auth/signup",
        "POST /auth/login",
        "GET /health",
        "POST /register/public/{slug}",
    ],
    
    "Scanner Level (Any Authenticated User)": [
        "POST /scan",
        "GET /events (Read-Only)",
    ],
    
    "Organizer Level (Organizer + Admin)": [
        "POST /events",
        "PUT /events/{id}",
        "DELETE /events/{id}",
        "GET /attendance/event/{id}",
        "GET /students/{prn}/analytics",
        "GET /attendance/summary",
    ],
    
    "Admin Level (Admin Only)": [
        "Future: User management routes",
        "Future: System configuration",
        "Future: Audit log access",
    ]
}


def print_backend_routes():
    """Print backend route protection info"""
    print("\n" + "="*80)
    print("BACKEND API ROUTE PROTECTION")
    print("="*80 + "\n")
    
    for category, routes in BACKEND_ROUTES.items():
        print(f"\n{category}:")
        print("-" * 50)
        for route in routes:
            print(f"  • {route}")
    
    print("\n" + "="*80 + "\n")


# Frontend Route Protection Reference
FRONTEND_ROUTES = {
    "/": "Public - Landing Page",
    "/login": "Public - Authentication",
    "/signup": "Public - Registration",
    "/register/{slug}": "Public - Event Registration",
    
    "/dashboard": "Protected - Organizer + Admin",
    "/events": "Protected - Organizer + Admin",
    "/attendance": "Protected - Organizer + Admin",
    "/scan": "Protected - All Roles (Scanner, Organizer, Admin)",
}


def print_frontend_routes():
    """Print frontend route protection info"""
    print("\n" + "="*80)
    print("FRONTEND ROUTE PROTECTION")
    print("="*80 + "\n")
    
    print("Public Routes:")
    print("-" * 50)
    for route, access in FRONTEND_ROUTES.items():
        if "Public" in access:
            print(f"  • {route:<25} → {access}")
    
    print("\nProtected Routes:")
    print("-" * 50)
    for route, access in FRONTEND_ROUTES.items():
        if "Protected" in access:
            print(f"  • {route:<25} → {access}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print_permissions_matrix()
    print_backend_routes()
    print_frontend_routes()
    
    print("\n🎯 Quick Reference:")
    print("  Scanner    → Can only scan QR codes")
    print("  Organizer  → Can manage events + view analytics + scan")
    print("  Admin      → Full system access\n")
