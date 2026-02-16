from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

# Load models
import app.models  

# Routers (ALL from app.routes)
from app.routes.health import router as health_router
from app.routes.event import router as event_router
from app.routes.registration import router as registration_router
from app.routes.ticket_qr import router as ticket_qr_router
from app.routes.scan import router as scan_router
from app.routes.attendance_dashboard import router as attendance_router
from app.routes.export import router as export_router
from app.routes.public_registration import router as public_registration_router
from app.routes.auth import router as auth_router
from app.routes.student_details import router as student_details_router
from app.routes.admin import router as admin_router
from app.routes.monitor import router as monitor_router
from app.routes.students import router as students_router
from app.routes.organizers import router as organizers_router
from app.routes.certificates import router as certificates_router
from app.routes.volunteers import router as volunteers_router
from app.routes.feedback import router as feedback_router
from app.routes.analytics import router as analytics_router
from app.routes.anomaly import router as anomaly_router
from app.routes.ps1 import router as ps1_router

Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(title=settings.PROJECT_NAME)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(event_router)
app.include_router(registration_router)
app.include_router(ticket_qr_router)
app.include_router(scan_router)
app.include_router(attendance_router)
app.include_router(export_router)
app.include_router(public_registration_router)
app.include_router(auth_router)
app.include_router(student_details_router)
app.include_router(admin_router)
app.include_router(monitor_router)
app.include_router(students_router)
app.include_router(organizers_router)
app.include_router(certificates_router)
app.include_router(volunteers_router)
app.include_router(feedback_router)
app.include_router(analytics_router)
app.include_router(anomaly_router)
app.include_router(ps1_router)

@app.get("/")
def root():
    return {"message": "Welcome to UniPass API"}

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)