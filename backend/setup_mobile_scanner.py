#!/usr/bin/env python3
"""
Quick setup script to help configure mobile access for UniPass Scanner
"""

import socket
import os
import sys
from pathlib import Path

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket to find IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def update_env_file(ip_address):
    """Update .env file with network settings"""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found. Please create one first.")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update or add CORS_ORIGINS
    cors_found = False
    new_lines = []
    
    for line in lines:
        if line.startswith("CORS_ORIGINS="):
            new_lines.append(f"CORS_ORIGINS=*\n")
            cors_found = True
        else:
            new_lines.append(line)
    
    if not cors_found:
        new_lines.append("CORS_ORIGINS=*\n")
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    return True

def create_frontend_env(ip_address):
    """Create/update frontend .env.local file"""
    frontend_dir = Path(__file__).parent.parent / "frontend"
    env_file = frontend_dir / ".env.local"
    
    content = f"NEXT_PUBLIC_API_URL=http://{ip_address}:8000\n"
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    return True

def main():
    print("=" * 60)
    print("🚀 UniPass Mobile Scanner Setup")
    print("=" * 60)
    print()
    
    # Get IP address
    ip = get_local_ip()
    
    if not ip:
        print("❌ Could not detect IP address automatically.")
        print()
        print("Please find your IP manually:")
        print("  macOS/Linux: ifconfig | grep 'inet ' | grep -v 127.0.0.1")
        print("  Windows: ipconfig")
        return
    
    print(f"✅ Detected IP Address: {ip}")
    print()
    
    # Update backend .env
    print("📝 Configuring backend CORS...")
    if update_env_file(ip):
        print("   ✅ Backend .env updated (CORS_ORIGINS=*)")
    else:
        print("   ⚠️  Could not update backend .env")
    
    print()
    
    # Create frontend .env.local
    print("📝 Configuring frontend API URL...")
    if create_frontend_env(ip):
        print(f"   ✅ Frontend .env.local created (API_URL=http://{ip}:8000)")
    else:
        print("   ⚠️  Could not create frontend .env.local")
    
    print()
    print("=" * 60)
    print("🎯 Next Steps:")
    print("=" * 60)
    print()
    print("1. Start Backend:")
    print(f"   cd {Path(__file__).parent}")
    print("   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("2. Start Frontend (in new terminal):")
    print(f"   cd {Path(__file__).parent.parent}/frontend")
    print("   npm run dev -- -H 0.0.0.0")
    print()
    print("3. On your phone, navigate to:")
    print(f"   📱 http://{ip}:3000/scanner-login")
    print()
    print("4. Login with scanner credentials and start scanning!")
    print()
    print("=" * 60)
    print("📚 For detailed guide, see: MOBILE_SCANNER_SETUP.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
