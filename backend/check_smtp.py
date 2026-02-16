"""
SMTP Configuration Checker
Verifies that email sending is properly configured
"""

from app.core.config import settings
import smtplib

def check_smtp_configuration():
    """Check if SMTP is properly configured and test connection"""
    
    print("=" * 60)
    print("SMTP Configuration Check")
    print("=" * 60)
    
    # Check if credentials are configured
    print("\n1. Checking SMTP Credentials:")
    print(f"   SMTP_HOST: {settings.SMTP_HOST}")
    print(f"   SMTP_PORT: {settings.SMTP_PORT}")
    print(f"   SMTP_USER: {'✅ Configured' if settings.SMTP_USER else '❌ NOT CONFIGURED'}")
    print(f"   SMTP_PASSWORD: {'✅ Configured' if settings.SMTP_PASSWORD else '❌ NOT CONFIGURED'}")
    print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
    print(f"   EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("\n❌ SMTP credentials are NOT configured!")
        print("\nTo enable email sending:")
        print("1. Edit backend/.env file")
        print("2. Add the following lines:")
        print()
        print("   SMTP_HOST=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SMTP_USER=your-email@gmail.com")
        print("   SMTP_PASSWORD=your-app-password")
        print("   EMAIL_FROM=your-email@gmail.com")
        print("   EMAIL_FROM_NAME=UniPass")
        print()
        print("For Gmail:")
        print("  - Enable 2-Factor Authentication")
        print("  - Generate App Password: https://myaccount.google.com/apppasswords")
        print("  - Use the 16-character app password (not your regular password)")
        print()
        return False
    
    # Test connection
    print("\n2. Testing SMTP Connection:")
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            print(f"   ✅ Connected to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            
            server.starttls()
            print("   ✅ TLS enabled")
            
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            print(f"   ✅ Authentication successful as {settings.SMTP_USER}")
            
        print("\n✅ SMTP Configuration is WORKING!")
        print("Certificates can be sent via email.")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\n❌ SMTP Authentication FAILED!")
        print("   Error: Invalid username or password")
        print()
        print("   If using Gmail:")
        print("   - Make sure 2FA is enabled")
        print("   - Use App Password, not your regular password")
        print("   - Generate new app password: https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        print("   Check your internet connection and firewall settings")
        return False

if __name__ == "__main__":
    check_smtp_configuration()
    print("\n" + "=" * 60)
