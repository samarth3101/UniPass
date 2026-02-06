## License

This project is licensed under the MIT License – see the LICENSE file for details.

#  UniPass - AI-Powered Event Attendance Management System

<div align="center">

**Modern QR-Based Attendance Tracking for University Events with Real-Time Analytics**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js_16.1-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

---

## 📋 Table of Contents
- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Setup Instructions](#-setup-instructions)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Security Features](#-security-features)
- [Future Roadmap](#-future-roadmap)
- [Team](#-team)

---

## 🎯 Problem Statement

Universities and educational institutions face significant challenges in managing event attendance:

- **Manual Attendance**: Traditional paper-based systems are time-consuming and error-prone
- **No Real-Time Insights**: Organizers can't monitor attendance during events
- **Security Issues**: Easy to forge paper tickets or share QR codes
- **Data Silos**: Attendance data scattered across multiple spreadsheets
- **Poor Analytics**: No insights into student participation patterns
- **Administrative Overhead**: Generating reports and certificates manually

**Impact**: Inefficient resource allocation, poor event planning, and lack of student engagement metrics.

---

## 💡 Solution Overview

**UniPass** is an intelligent, secure, and scalable event management platform that revolutionizes how educational institutions handle event attendance. Built with modern technologies and enterprise-grade security, UniPass combines:

 **JWT-Signed QR Tickets** - Each ticket is cryptographically signed and time-bound  
 **Real-Time Analytics** - Live attendance monitoring via Server-Sent Events (SSE)  
 **Role-Based Access Control** - Granular permissions for admins, organizers, and scanners  
 **Automated Email Ticketing** - Instant QR code delivery to registered students  
 **AI-Ready Architecture** - Predictive analytics and behavioral insights (in development)  
 **Complete Audit Trail** - Every action logged for compliance and accountability

---

## ✨ Key Features

###  **Smart Ticketing System**
- **JWT-Signed QR Codes**: Each ticket contains encrypted event data (event_id, student_id, timestamp)
- **Time-Bound Validation**: QR codes only work during event time window
- **One-Time Scan Protection**: Prevents ticket reuse and fraud
- **Email Delivery**: Automated ticket generation and email dispatch

###  **Multi-Role Dashboard**

####  Admin Dashboard
- Create and manage events with full CRUD operations
- Assign organizers to events
- View system-wide analytics and reports
- Manage user roles and permissions
- Export attendance data (CSV, Excel, PDF)

####  Organizer Dashboard
- Monitor assigned events in real-time
- View live attendance count with SSE streaming
- Access detailed student lists with attendance status
- Generate quick reports and certificates

####  Scanner Interface
- Camera-based QR code scanning
- Instant validation feedback (success/error states)
- Works on any device with camera
- Offline-capable validation (coming soon)

###  **Advanced Analytics**
- **Real-Time Monitoring**: Live attendance updates using Server-Sent Events
- **Attendance Dashboard**: Compare actual vs expected attendance across events
- **Student Insights**: Individual participation history and patterns
- **Visual Reports**: Charts and graphs for quick decision-making
- **Export Options**: Multiple formats for external analysis

###  **Enterprise Security**
- **JWT Authentication**: Stateless, scalable authentication
- **Password Hashing**: Bcrypt with configurable rounds
- **RBAC Implementation**: 4 roles (superadmin, admin, organizer, scanner)
- **Audit Logging**: Complete trail of all system actions
- **CORS Protection**: Environment-based origin whitelisting
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM

###  **AI/ML Integration (In Development)**
- Attendance prediction models
- Anomaly detection (duplicate scans, unusual patterns)
- Student engagement scoring
- Event success prediction
- Personalized event recommendations

---

## 🛠 Tech Stack

### **Backend**
- **Framework**: FastAPI (Python 3.12) - High-performance async API
- **ORM**: SQLAlchemy - Database abstraction and migrations
- **Validation**: Pydantic - Automatic request/response validation
- **Authentication**: JWT with bcrypt password hashing
- **Email**: SMTP integration (Gmail/SendGrid support)
- **QR Generation**: qrcode + Pillow for image generation

### **Frontend**
- **Framework**: Next.js 16.1 (React 19) with Turbopack
- **Language**: TypeScript for type safety
- **Styling**: SCSS modules for component-scoped styles
- **State Management**: React hooks and context
- **Routing**: Next.js App Router (file-based)
- **API Client**: Fetch API with custom service layer

### **Database**
- **RDBMS**: PostgreSQL 15+ (ACID compliance)
- **Schema**: Normalized design with foreign keys
- **Features**: JSON support, full-text search, indexes

### **DevOps & Tools**
- **Version Control**: Git + GitHub
- **API Testing**: Swagger UI (auto-generated)
- **Code Quality**: ESLint, Prettier
- **Package Management**: pip (Python), npm (Node.js)

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web App     │  │  Mobile Web  │  │  QR Scanner  │      │
│  │  (Next.js)   │  │  (Responsive)│  │  (Camera)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST API
┌────────────────────────▼────────────────────────────────────┐
│                   API GATEWAY LAYER                          │
│         FastAPI + JWT Auth + CORS + Validation              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│  [Auth] [Events] [Tickets] [QR Service] [Email] [AI/ML]    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                     DATA LAYER                               │
│  PostgreSQL: Users | Events | Tickets | Attendance | Logs  │
└─────────────────────────────────────────────────────────────┘
```

**Key Innovations:**
1. **JWT-Secured QR Tickets**: Not just authentication tokens, but QR codes themselves are JWT-signed
2. **Time-Bound Validation**: Event timeframe enforcement at QR scan
3. **Real-Time SSE Streaming**: Instant attendance updates without polling
4. **Multi-Layer Security**: Authentication, authorization, audit logging, and encryption

---

## 🚀 Setup Instructions

### **Prerequisites**
- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Git

### **Backend Setup**

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << EOL
DATABASE_URL=postgresql://username:password@localhost/unipass
SECRET_KEY=your-super-secret-key-min-32-chars
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOL

# 5. Initialize database (create tables)
python -c "from app.db.database import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"

# 6. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will run at**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/docs`

### **Frontend Setup**

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env.local file
cat > .env.local << EOL
NEXT_PUBLIC_API_URL=http://localhost:8000
EOL

# 4. Run development server
npm run dev
```

**Frontend will run at**: `http://localhost:3000`

### **Database Setup**

```sql
-- Create database
CREATE DATABASE unipass;

-- Connect to database
\c unipass

-- Tables will be auto-created by SQLAlchemy on first run
```

### **Create First Admin User**

```bash
# Option 1: Using the API (POST to /api/auth/signup)
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@university.edu",
    "password": "SecurePassword123",
    "full_name": "Admin User",
    "role": "admin"
  }'

# Option 2: Directly in database
# Run: python backend/app/create_admin.py
```

---

## 📁 Project Structure

```
UniPass/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── core/
│   │   │   ├── config.py           # Environment configuration
│   │   │   ├── security.py         # Password hashing utilities
│   │   │   └── permissions.py      # RBAC permission matrix
│   │   ├── db/
│   │   │   ├── database.py         # Database connection
│   │   │   └── base.py             # SQLAlchemy base class
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   ├── ticket.py
│   │   │   ├── attendance.py
│   │   │   ├── student.py
│   │   │   └── audit_log.py
│   │   ├── schemas/                # Pydantic schemas (validation)
│   │   │   ├── user.py
│   │   │   ├── event.py
│   │   │   └── ...
│   │   ├── routes/                 # API endpoints
│   │   │   ├── auth.py             # Login, signup, token refresh
│   │   │   ├── event.py            # CRUD operations for events
│   │   │   ├── scan.py             # QR code scanning & validation
│   │   │   ├── registration.py     # Student event registration
│   │   │   └── ...
│   │   ├── services/               # Business logic
│   │   │   ├── email_service.py    # Email & QR ticket generation
│   │   │   ├── qr_service.py       # QR generation & validation
│   │   │   └── audit_service.py    # Audit logging
│   │   └── security/
│   │       └── jwt.py              # JWT token generation/validation
│   ├── requirements.txt            # Python dependencies
│   └── migrate_*.py                # Database migration scripts
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/             # Login, signup pages
│   │   │   ├── (app)/              # Protected app routes
│   │   │   │   ├── dashboard/      # Main dashboard
│   │   │   │   ├── events/         # Event management
│   │   │   │   ├── scan/           # QR scanner interface
│   │   │   │   ├── attendance/     # Attendance dashboard
│   │   │   │   ├── students/       # Student management
│   │   │   │   └── organizers/     # Organizer management
│   │   │   └── (public)/           # Landing page, registration
│   │   ├── components/             # Reusable React components
│   │   │   ├── RoleGuard.tsx       # Route protection by role
│   │   │   └── Toast.tsx           # Notification component
│   │   ├── services/
│   │   │   └── api.ts              # API client service
│   │   └── lib/
│   │       └── auth.ts             # Authentication utilities
│   ├── package.json
│   └── next.config.ts
│
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── PROJECT_REPORT.md               # Detailed technical documentation
├── BUG_REPORT_AND_FIXES.md         # Known issues and fixes
└── DIAGRAMS.md                     # System architecture diagrams
```

---

## 📚 API Documentation

### **Authentication Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/signup` | Create new user | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| GET | `/api/auth/me` | Get current user info | Yes |

### **Event Management**
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/events` | Create event | Admin |
| GET | `/api/events` | List all events | All |
| GET | `/api/events/{id}` | Get event details | All |
| PUT | `/api/events/{id}` | Update event | Admin |
| DELETE | `/api/events/{id}` | Delete event | Admin |

### **Ticket & Registration**
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/events/{id}/register` | Register for event | Any |
| GET | `/api/tickets/my-tickets` | Get user's tickets | User |

### **QR Scanning**
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/scan/validate` | Validate QR code | Scanner |
| GET | `/api/scan/event/{id}/realtime` | SSE stream for live updates | Organizer |

### **Analytics & Reports**
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/api/attendance/dashboard` | Attendance overview | Admin/Organizer |
| GET | `/api/export/event/{id}/csv` | Export attendance CSV | Admin/Organizer |

**Full API Documentation**: Run backend and visit `http://localhost:8000/docs`

---

##  Security Features

### **Authentication & Authorization**
- ✅ JWT-based stateless authentication
- ✅ Bcrypt password hashing (12 rounds)
- ✅ Token expiration (30 days)
- ✅ Role-based access control (4 roles)
- ✅ Protected routes with middleware

### **QR Security**
- ✅ JWT-signed QR codes (can't be forged)
- ✅ Time-bound validation (only valid during event)
- ✅ One-time use enforcement
- ✅ Event ID + Student ID embedded
- ✅ Signature verification on scan

### **Data Protection**
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection (input sanitization)
- ✅ CORS policy enforcement
- ✅ HTTPS recommended for production
- ✅ Environment-based configuration

### **Audit & Compliance**
- ✅ Complete audit trail (who, what, when)
- ✅ Immutable log entries
- ✅ User action tracking
- ✅ Failed login attempt logging

---

##  Future Roadmap

### **AI/ML Integration**
- [ ] Attendance prediction models (Random Forest, XGBoost)
- [ ] Anomaly detection (isolation forests)
- [ ] Student engagement scoring
- [ ] Event success prediction

### **Advanced Features**
- [ ] Blockchain-based certificates
- [ ] Multi-tenancy (multiple universities)
- [ ] Advanced analytics dashboard
- [ ] Integration with university ERP systems


---

## 👥 Team Leader

**Developed by**: Samarth Patil  
**Institution**: PCET's Pimpri Chinchwad University, Pune
**Contact**: samarth.patil3101@gmail.com
**LinkedIn**: https://www.linkedin.com/in/samarth-patil-3101spp/
**GitHub**: https://github.com/samarth3101
**Portfolio**: https://samarthpatil.netlify.app/
---

## 📄 License

This project is developed for educational purposes as part of a hackathon, research and development. 

The system design, architecture, workflows, and research components associated with this project are the intellectual property of the author and are protected under applicable copyright laws.

Unauthorized use, reproduction, modification, or redistribution of the architecture, design documents, or core conceptual workflows—in whole or in part—without explicit written permission from the author may constitute a violation of intellectual property rights.

Source code is shared strictly for learning and evaluation purposes.

For permissions, collaborations, or authorized use, please contact the author.

---

##  Acknowledgments

- FastAPI documentation and community
- Next.js team for excellent developer experience
- PostgreSQL for robust database system
- All open-source contributors whose libraries made this possible

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

Made with ❤️ by Samarth Patil

</div>