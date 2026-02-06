from dotenv import load_dotenv
import os
from pathlib import Path
import sys

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=backend_dir / ".env")

class Settings:
    PROJECT_NAME = "UniPass"
    
    # Required environment variables
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Validate required variables
    def __init__(self):
        required_vars = {
            'DATABASE_URL': self.DATABASE_URL,
            'SECRET_KEY': self.SECRET_KEY
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            print(f"❌ ERROR: Missing required environment variables: {', '.join(missing)}")
            print("Please create a .env file in the backend directory.")
            print("See .env.example for reference.")
            sys.exit(1)
    
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
    
    # Frontend Configuration
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    
    # Email Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@unipass.edu")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "UniPass")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))

settings = Settings()