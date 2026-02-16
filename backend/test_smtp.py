"""
Quick SMTP connection test
"""
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

print(f"Testing SMTP connection...")
print(f"Host: {SMTP_HOST}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
print()

if not SMTP_USER or not SMTP_PASSWORD:
    print("❌ ERROR: SMTP credentials not configured in .env file")
    exit(1)

try:
    print("Attempting to connect...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        print("✅ Connected to SMTP server")
        
        print("Starting TLS...")
        server.starttls()
        print("✅ TLS started")
        
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✅ Login successful")
        
    print("\n🎉 SMTP configuration is working correctly!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("\nPossible solutions:")
    print("1. Enable 2-Step Verification in Google Account")
    print("2. Generate a new App Password at: https://myaccount.google.com/apppasswords")
    print("3. Use the App Password (not your regular Gmail password)")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP error: {e}")
    
except TimeoutError:
    print(f"\n❌ Connection timed out")
    print("Possible solutions:")
    print("1. Check your internet connection")
    print("2. Verify SMTP_HOST and SMTP_PORT are correct")
    print("3. Check if Gmail SMTP is blocked by firewall")
    
except Exception as e:
    print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
