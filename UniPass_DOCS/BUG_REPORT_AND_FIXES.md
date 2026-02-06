# UniPass System Audit - Bug Report & Required Fixes

**Date**: February 5, 2026  
**Status**: Pre-AI Implementation Audit

---

## ✅ RECENTLY FIXED

### 1. **Timezone/DateTime Display Issues** ✓ FIXED
- **Issue**: Events showing wrong times (5.5 hour offset - IST/UTC mismatch)
- **Impact**: Users saw "07:52 PM" when they entered "02:22 PM"
- **Fix Applied**: Implemented proper timezone handling in backend schemas and routes
- **Files Modified**: 
  - `backend/app/schemas/event.py`
  - `backend/app/routes/event.py`
  - `frontend/src/app/(app)/events/event-card.tsx`

### 2. **Event Status Badge Logic** ✓ FIXED
- **Issue**: Live events showing as "Upcoming"
- **Impact**: Confusion about current event status
- **Fix Applied**: Corrected filtering logic and added "Live" filter tab
- **Files Modified**: 
  - `frontend/src/app/(app)/events/events-client.tsx`

---

## 🔴 CRITICAL ISSUES

### 1. **Hardcoded URLs/Endpoints (Production Blocker)**
**Severity**: HIGH  
**Impact**: App will fail in production/different environments

**Locations**:
```typescript
// Frontend - Multiple files
- frontend/src/services/api.ts: "http://localhost:8000"
- frontend/src/app/(app)/events/event-modal.tsx: "http://127.0.0.1:8000"
- frontend/src/app/(auth)/signup/page.tsx: "http://127.0.0.1:8000"
- frontend/src/app/(public)/page.tsx: "http://127.0.0.1:8000/docs"
- frontend/src/app/(app)/students/page.tsx: "http://localhost:8000"
- frontend/src/app/(app)/attendance/page.tsx: "http://127.0.0.1:8000"
- frontend/src/app/(app)/monitor/[eventId]/page.tsx: "http://localhost:8000"
- frontend/src/app/(app)/attendance/student-modal.tsx: "http://127.0.0.1:8000"
- frontend/src/app/(public)/register/[slug]/page.tsx: "http://127.0.0.1:8000"

// Backend
- backend/app/routes/event.py: "http://localhost:3000"
- backend/app/main.py: allow_origins=["http://localhost:3000"]
```

**Fix Required**:
```typescript
// Create environment configuration files
// frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

// backend/.env
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### 2. **Missing Environment Variable Validation**
**Severity**: HIGH  
**Impact**: App crashes with cryptic errors if .env is misconfigured

**Issue**: No validation for required env vars like SECRET_KEY, DATABASE_URL

**Fix Required**:
```python
# backend/app/core/config.py
class Settings:
    def __init__(self):
        required_vars = ['DATABASE_URL', 'SECRET_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
```

### 3. **CORS Configuration Too Permissive**
**Severity**: MEDIUM  
**Impact**: Security vulnerability in production

**Current**:
```python
allow_origins=["http://localhost:3000"]  # Only one hardcoded origin
```

**Fix Required**:
```python
allow_origins=settings.CORS_ORIGINS.split(',')  # From env variable
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 4. **No Database Migration System**
**Severity**: MEDIUM  
**Impact**: Database schema changes will break production

**Issue**: Using `Base.metadata.create_all()` instead of migrations

**Fix Required**:
```bash
# Implement Alembic for migrations
pip install alembic
alembic init alembic
# Create migration scripts for existing schema
```

### 5. **Inconsistent Error Handling**
**Severity**: MEDIUM  
**Impact**: Poor user experience, difficult debugging

**Issues Found**:
- Multiple `alert()` calls in frontend (not user-friendly)
- `console.log` statements left in production code
- Generic error messages like "Failed to generate report"
- No centralized error handling/logging

**Fix Required**:
```typescript
// Create a toast notification system
// frontend/src/components/Toast.tsx
// Replace all alert() calls

// Centralized API error handler
// frontend/src/services/errorHandler.ts
```

### 6. **No Input Validation on Frontend**
**Severity**: MEDIUM  
**Impact**: Poor UX, unnecessary API calls

**Examples**:
- Event creation: No validation that end_time > start_time
- Email validation only checks for "@"
- No PRN format validation
- No file size/type validation for CSV uploads

**Fix Required**:
```typescript
// Add form validation library
npm install react-hook-form zod
// Implement comprehensive validation schemas
```

### 7. **Missing Loading States**
**Severity**: LOW-MEDIUM  
**Impact**: Users don't know if system is processing

**Issues**:
- Event list loads without skeleton/loading UI
- QR scan has no processing feedback
- File uploads don't show progress

### 8. **No Rate Limiting**
**Severity**: MEDIUM  
**Impact**: API abuse, DDoS vulnerability

**Fix Required**:
```python
# Install slowapi
pip install slowapi
# Add rate limiting to auth and scan endpoints
```

---

## 🟢 LOW PRIORITY / IMPROVEMENTS

### 9. **Memory Leaks Potential**
**Issue**: EventSource connections in monitor not properly cleaned up

**Fix**:
```typescript
useEffect(() => {
  const eventSource = new EventSource(/*...*/);
  return () => eventSource.close(); // Cleanup
}, []);
```

### 10. **No Database Connection Pooling**
**Issue**: May cause connection exhaustion under load

**Fix**:
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 11. **Security Headers Missing**
**Issue**: No security headers in responses

**Fix Required**:
```python
# Add security middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
```

### 12. **No Request/Response Logging**
**Issue**: Difficult to debug production issues

**Fix**:
```python
# Add logging middleware
import logging
logging.basicConfig(level=logging.INFO)
```

### 13. **Inconsistent Naming Conventions**
**Minor Issues**:
- Mix of camelCase and snake_case in some places
- Inconsistent file naming (some with hyphens, some without)

### 14. **No Database Indexes on Foreign Keys**
**Impact**: Slow queries as data grows

**Fix**: Add indexes to frequently queried columns:
```python
created_by = Column(Integer, ForeignKey("users.id"), index=True)
event_id = Column(Integer, ForeignKey("events.id"), index=True)
```

### 15. **No Soft Delete Implementation**
**Issue**: Hard deletes lose audit trail

**Fix**: Add `deleted_at` column and filter queries

### 16. **Missing Pagination**
**Issue**: Loading all events/students at once will slow down as data grows

**Fix**: Implement pagination in list endpoints:
```python
@router.get("/events/")
def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Event).offset(skip).limit(limit).all()
```

### 17. **No File Upload Validation**
**Issue**: CSV upload accepts any file without validation

**Fix**: Add file type, size, and content validation

### 18. **Duplicate Route Registration**
**Issue**: In `main.py` line 33-34: `event_router` included twice

---

## 🔒 SECURITY ISSUES

### 19. **JWT Token Storage**
**Issue**: Tokens in localStorage (vulnerable to XSS)

**Better**: Use httpOnly cookies with CSRF protection

### 20. **Password Requirements**
**Issue**: No password complexity requirements

**Fix**: Add validation for min length, special chars, etc.

### 21. **No SQL Injection Protection Verification**
**Status**: Using SQLAlchemy (should be safe), but needs security audit

### 22. **No CSRF Protection**
**Issue**: State-changing operations vulnerable to CSRF

**Fix**: Implement CSRF tokens for mutations

---

## 📊 PERFORMANCE ISSUES

### 23. **N+1 Query Problems**
**Issue**: Loading related data in loops

**Fix**: Use SQLAlchemy's `joinedload` or `selectinload`

### 24. **No Caching**
**Issue**: Frequently accessed data (events list) not cached

**Fix**: Implement Redis caching for read-heavy endpoints

### 25. **Large QR Code Generation**
**Issue**: Generating QR codes on every request

**Fix**: Cache generated QR codes

---

## 🧪 TESTING GAPS

### 26. **No Tests**
**Critical**: Zero unit tests, integration tests, or E2E tests

**Required**:
```bash
# Backend
pytest
pytest-cov
# Frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

---

## 📱 UI/UX ISSUES

### 27. **No Mobile Responsiveness Testing**
**Issue**: Many modals and tables may not work well on mobile

### 28. **No Dark Mode**
**Enhancement**: Add dark mode support

### 29. **Accessibility Issues**
- No ARIA labels
- No keyboard navigation support
- Poor color contrast in some areas
- Missing alt text on images

### 30. **No Offline Support**
**Enhancement**: Add service worker for offline functionality

---

## 🔄 CODE QUALITY

### 31. **No TypeScript Strict Mode**
**Fix**: Enable strict mode in tsconfig.json

### 32. **Unused Imports and Code**
**Issue**: Several console.log statements left in code

### 33. **No API Documentation**
**Fix**: Add OpenAPI/Swagger descriptions to all endpoints

### 34. **Magic Numbers/Strings**
**Issue**: Hardcoded values like "720" for token expiry

**Fix**: Use named constants:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12 hours
```

---

## 🎯 PRIORITY IMPLEMENTATION ORDER

### Phase 1 (Critical - Before Production):
1. Environment variable configuration
2. Database migrations setup
3. Proper error handling
4. Security headers
5. Rate limiting

### Phase 2 (Important):
6. Input validation
7. Pagination
8. Logging/monitoring
9. Tests (at least integration tests)
10. Database indexes

### Phase 3 (Enhancements):
11. Caching
12. Mobile responsiveness
13. Accessibility
14. Soft deletes
15. Performance optimizations

### Phase 4 (Nice to Have):
16. Dark mode
17. Offline support
18. Advanced analytics
19. Comprehensive test coverage
20. Documentation

---

## 🤖 AI IMPLEMENTATION READINESS

**System is NOT production-ready but suitable for AI feature development with caution.**

**Recommendations before AI integration**:
1. Fix all CRITICAL issues (environment configs, CORS, validation)
2. Implement proper error handling
3. Add comprehensive logging
4. Set up monitoring (consider Sentry, LogRocket)
5. Create staging environment
6. Implement feature flags for AI features

**Suggested AI Features** (in order of ease):
1. **Smart attendance insights** - Analyze patterns, suggest optimal times
2. **Auto-categorization** - Tag events by type, predict attendance
3. **Natural language event creation** - "Create event tomorrow 3pm at PCU"
4. **Anomaly detection** - Detect unusual attendance patterns
5. **Predictive analytics** - Forecast attendance based on historical data
6. **Chatbot assistant** - Help users navigate system, answer questions

---

## 📝 NOTES

- Most issues are typical for MVP/prototype stage
- Core functionality works well
- Architecture is solid and extensible
- Good separation of concerns (models, routes, schemas)
- No major architectural refactoring needed for AI features

**Overall Assessment**: 6.5/10 for production readiness, 8/10 for feature development readiness.
