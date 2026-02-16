# PS1 Integration: 3-Phase Strategy for UniPass

**Document Date:** February 16, 2026  
**Project:** UniPass - Unified Campus Participation Intelligence System  
**Status:** Phase 1 Complete ✅ | Phase 2 & 3 Planned  

---

## 📊 Executive Summary

This document outlines a **strategic 3-phase approach** to fully integrate the **Unified Campus Participation Intelligence System (PS1)** into UniPass. Each phase is designed to be independently deployable, demo-ready, and progressively builds towards 100% PS1 compliance.

**Phase Completion:**
- ✅ **Phase 1:** COMPLETE (58% PS1 coverage) - **~2 hours**
- 📅 **Phase 2:** Planned (85% PS1 coverage) - **~4 hours**
- 📅 **Phase 3:** Planned (100% PS1 coverage) - **~3 hours**

Total estimated time: **~9 hours** for complete PS1 implementation

---

## 🎯 Phase 1: Foundation & Quick Wins ✅ COMPLETE

**Duration:** 2 hours  
**Coverage:** 58% of PS1 requirements  
**Status:** ✅ **DEPLOYED**

### What Was Built:

#### **Feature 1: Participation Reconciliation (70% complete)**
✅ Canonical status computation  
✅ Five conflict types detected  
✅ Trust scoring (0-100)  
✅ API endpoints for status & conflicts  
❌ Conflict resolution UI (Phase 2)  

#### **Feature 3: Verification System (75% complete)**
✅ SHA-256 verification hashing  
✅ Public verification endpoint  
✅ Beautiful verification UI at `/verify`  
✅ Certificate revocation support  
❌ Participation transcript (Phase 2)  

#### **Feature 4: Retroactive Changes (60% complete)**
✅ Certificate revocation with reason  
✅ Audit trail integration  
✅ User attribution  
❌ Attendance invalidation (Phase 2)  
❌ Versioned records (Phase 3)  

#### **Feature 5: Multi-Role Participation (85% complete)**
✅ Six role types supported  
✅ Multiple roles per student  
✅ Time segment support  
✅ Complete role management API  
❌ Role-based certificate templates (Phase 2)  

### Database Changes:
- ✅ `participation_roles` table created
- ✅ Certificate verification fields added
- ✅ Certificate revocation fields added

### API Endpoints Added:
- `GET /ps1/participation/status/{event_id}/{prn}` - Canonical status
- `GET /ps1/participation/conflicts/{event_id}` - Conflict detection
- `GET /ps1/verify/certificate/{cert_id}` - Public verification
- `POST /ps1/certificate/{cert_id}/revoke` - Revoke with reason
- `POST /ps1/roles/{event_id}/assign` - Assign role
- `GET /ps1/roles/{event_id}` - Get event roles
- `GET /ps1/roles/student/{prn}` - Get student roles
- `DELETE /ps1/roles/{role_id}` - Remove role

### Demo-Ready Features:
✅ Conflict detection finds data inconsistencies  
✅ Public certificate verification  
✅ Certificate revocation with reason tracking  
✅ Multi-role student participation  

---

## 📋 Phase 2: Advanced Features & UI Integration

**Duration:** 4 hours  
**Coverage:** 85% of PS1 requirements  
**Status:** 📅 **PLANNED**

### Objectives:
1. Complete remaining PS1 features
2. Build admin dashboards
3. Implement transcript generation
4. Add temporal snapshots

### Implementation Plan:

#### **2.1 Participation Transcript Generator** (1.5 hours)

**Feature 3 Completion: 95%**

##### Backend Implementation:
```python
# /backend/app/services/transcript_service.py

class TranscriptService:
    def generate_transcript(self, student_prn: str, format: str = "json"):
        """Generate participation transcript"""
        - Get all attendance records
        - Get all certificates
        - Get all roles assigned
        - Calculate engagement score
        - Return/generate PDF
    
    def generate_pdf_transcript(self, data: dict):
        """Generate PDF using ReportLab"""
        - Professional header with logo
        - Student information
        - Events attended (grouped by role)
        - Certificates earned
        - Engagement metrics
```

##### API Endpoints:
```
GET /ps1/transcript/{prn}?format=json|pdf
GET /ps1/transcript/{prn}/email - Email transcript to student
```

##### Frontend:
- Student profile: "Download Transcript" button
- Admin view: Bulk transcript generation
- Public transcript with verification link

**Deliverables:**
- ✅ TranscriptService class
- ✅ PDF generator with ReportLab
- ✅ API endpoints
- ✅ UI integration

---

#### **2.2 Temporal Student Snapshots** (1.5 hours)

**Feature 2 Implementation: 75%**

##### Database Schema:
```python
# /backend/app/models/student_snapshot.py

class StudentSnapshot(Base):
    __tablename__ = "student_snapshots"
    
    id = Column(Integer, primary_key=True)
    student_prn = Column(String, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    snapshot_at = Column(DateTime)
    
    # Historical student data at time of event
    name = Column(String)
    branch = Column(String)
    year = Column(Integer)
    division = Column(String)
    email = Column(String)
    
    # Additional historical data
    club_role = Column(String, nullable=True)
    department = Column(String, nullable=True)
```

##### Logic Updates:
1. **Capture snapshot on registration:**
   ```python
   def register_student(event_id, student_prn):
       snapshot = create_student_snapshot(student_prn, event_id)
       # Continue with registration
   ```

2. **Query "as-of" data:**
   ```python
   def get_student_as_of_event(student_prn, event_id):
       return db.query(StudentSnapshot).filter_by(
           student_prn=student_prn,
           event_id=event_id
       ).first()
   ```

##### API Endpoints:
```
GET /ps1/student/{prn}/snapshot/{event_id} - Get historical profile
GET /ps1/student/{prn}/history - Timeline of all changes
```

**Deliverables:**
- ✅ StudentSnapshot model
- ✅ Snapshot capture logic
- ✅ Migration script
- ✅ API endpoints
- ✅ UI to show historical data

---

#### **2.3 Conflict Resolution Dashboard** (1 hour)

**Feature 1 Completion: 90%**

##### Frontend Dashboard:
```
/app/(app)/ps1/conflicts/page.tsx

Features:
- List all conflicts by event
- Filter by severity (HIGH/MEDIUM/LOW)
- One-click resolution actions
- Bulk resolution
- Resolution history
```

##### Resolution Actions:
1. **Mark as resolved** - Add note, no changes
2. **Fix attendance** - Add missing attendance record
3. **Revoke certificate** - Revoke with reason
4. **Add registration** - Create missing ticket

##### UI Components:
- Conflict card with severity badge
- Resolution dropdown menu
- Reason input modal
- Confirmation dialog
- Success/failure toast

**Deliverables:**
- ✅ Conflict dashboard UI
- ✅ Resolution action handlers
- ✅ Backend resolution endpoints
- ✅ Audit trail integration

---

### Phase 2 Summary:

**New Tables:**
- `student_snapshots` - Historical student profiles

**New API Endpoints:**
- `/ps1/transcript/{prn}` - Generate transcript
- `/ps1/student/{prn}/snapshot/{event_id}` - Get snapshot
- `/ps1/conflicts/resolve` - Resolve conflict

**New UI Pages:**
- `/verify` - Already complete ✅
- `/app/ps1/conflicts` - Conflict dashboard
- `/app/ps1/transcript/{prn}` - Transcript viewer

**Phase 2 Coverage:** 85% of PS1 requirements

---

## 🚀 Phase 3: Polish & Advanced Features

**Duration:** 3 hours  
**Coverage:** 100% of PS1 requirements  
**Status:** 📅 **PLANNED**

### Objectives:
1. Complete all remaining features
2. Add advanced UI integrations
3. Performance optimizations
4. Comprehensive testing

### Implementation Plan:

#### **3.1 Role-Based Features** (1 hour)

##### Role-Based Certificate Templates:
```python
# Different certificate templates per role
def generate_certificate(student_prn, event_id):
    role = get_student_role(student_prn, event_id)
    
    if role == RoleType.SPEAKER:
        template = "certificate_speaker.html"
    elif role == RoleType.VOLUNTEER:
        template = "certificate_volunteer.html"
    else:
        template = "certificate_participant.html"
    
    return render_certificate(template, data)
```

##### UI Enhancements:
- Role badges in attendance list
- Filter events by role
- Role statistics in dashboard
- Role timeline view

**Deliverables:**
- ✅ Role-specific certificate templates (3 designs)
- ✅ Role filter in event lists
- ✅ Role badges UI component
- ✅ Role statistics cards

---

#### **3.2 Attendance Invalidation Workflow** (1 hour)

**Feature 4 Completion: 100%**

##### Backend:
```python
# /backend/app/routes/ps1.py

@router.post("/attendance/{attendance_id}/invalidate")
async def invalidate_attendance(
    attendance_id: int,
    reason: str,
    current_user: User
):
    """Mark attendance as invalid with reason"""
    attendance.invalidated = True
    attendance.invalidated_at = datetime.utcnow()
    attendance.invalidated_by = current_user.id
    attendance.invalidation_reason = reason
    
    # Log audit trail
    # Trigger certificate revocation if applicable
```

##### Database Changes:
```sql
ALTER TABLE attendance 
ADD COLUMN invalidated BOOLEAN DEFAULT FALSE,
ADD COLUMN invalidated_at TIMESTAMP,
ADD COLUMN invalidated_by INTEGER REFERENCES users(id),
ADD COLUMN invalidation_reason TEXT;
```

##### UI:
- "Invalidate" button in attendance modal
- Reason input form
- Confirmation dialog
- Show invalid attendances with strikethrough

**Deliverables:**
- ✅ Attendance invalidation fields
- ✅ API endpoints
- ✅ UI for invalidation
- ✅ Cascade to certificate revocation

---

#### **3.3 Advanced Reconciliation** (1 hour)

##### Priority Rules Configuration:
```python
# /backend/app/services/reconciliation_service.py

class ReconciliationConfig:
    # Define trust priority
    TRUST_PRIORITY = {
        "qr_scan": 100,      # Highest trust
        "admin_override": 80,
        "bulk_upload": 60,
        "api_integration": 70
    }
    
    # Auto-resolution rules
    AUTO_RESOLVE_RULES = {
        "certificate_without_attendance": "revoke_certificate",
        "duplicate_scans_same_day": "keep_first_scan"
    }
```

##### Smart Conflict Resolution:
- Auto-apply rules based on trust score
- Suggest resolution actions
- ML-based anomaly integration
- Batch resolution API

**Deliverables:**
- ✅ Configurable priority rules
- ✅ Auto-resolution engine
- ✅ Batch resolution API
- ✅ Admin configuration UI

---

### Phase 3 Summary:

**New Features:**
- ✅ Role-based certificate templates
- ✅ Attendance invalidation
- ✅ Smart conflict resolution
- ✅ Advanced reconciliation rules

**New Database Fields:**
- `attendance.invalidated`, `invalidated_at`, `invalidated_by`, `invalidation_reason`

**New API Endpoints:**
- `/ps1/attendance/{id}/invalidate` - Invalidate attendance
- `/ps1/reconciliation/config` - Get/set rules
- `/ps1/conflicts/auto-resolve` - Batch auto-resolution

**Phase 3 Coverage:** 100% of PS1 requirements ✅

---

## 📊 Feature Completion Roadmap

| Feature | Phase 1 | Phase 2 | Phase 3 | Final |
|---------|---------|---------|---------|-------|
| **Feature 1: Reconciliation** | 70% | 90% | 100% | ✅ |
| **Feature 2: Timeline** | 0% | 75% | 90% | ✅ |
| **Feature 3: Verification** | 75% | 95% | 100% | ✅ |
| **Feature 4: Retroactive** | 60% | 80% | 100% | ✅ |
| **Feature 5: Multi-Role** | 85% | 85% | 100% | ✅ |
| **Overall PS1** | **58%** | **85%** | **100%** | ✅ |

---

## 🎬 Demo Strategy by Phase

### Phase 1 Demo (Current):
1. **Conflict Detection** - Show certificate without attendance
2. **Public Verification** - Verify certificate at /verify
3. **Certificate Revocation** - Revoke with reason
4. **Multi-Role Assignment** - Assign multiple roles

### Phase 2 Demo:
1. **Transcript Generation** - Download PDF transcript
2. **Historical Profile** - Show student as they were in past event
3. **Conflict Resolution** - One-click resolve conflicts
4. **Role Timeline** - Visual timeline of roles

### Phase 3 Demo:
1. **Role Certificates** - Different designs per role
2. **Attendance Invalidation** - Mark scan as invalid
3. **Auto-Resolution** - Smart conflict fixing
4. **Complete PS1** - Show 100% compliance

---

## 🛠 Technical Stack Requirements

### Additional Dependencies (Phase 2):
```bash
pip install reportlab  # PDF generation (already in requirements.txt)
```

### Database Migrations:
- ✅ Phase 1: participation_roles, certificate fields
- 📅 Phase 2: student_snapshots
- 📅 Phase 3: attendance invalidation fields

### Frontend Dependencies:
All dependencies already available, no new packages needed

---

## 📈 Performance Considerations

### Phase 2 Optimizations:
1. **Snapshot Caching** - Cache historical profiles
2. **Transcript Generation** - Async PDF generation
3. **Conflict Detection** - Indexed queries

### Phase 3 Optimizations:
1. **Batch Operations** - Bulk conflict resolution
2. **Query Optimization** - Minimize N+1 queries
3. **Caching Layer** - Redis for frequently accessed data

---

## ✅ Testing Strategy

### Phase 1 Testing (Complete):
- ✅ Migration script tested
- ✅ All endpoints verified
- ✅ Frontend verification page working

### Phase 2 Testing:
- Unit tests for transcript generation
- Integration tests for snapshots
- E2E tests for conflict resolution

### Phase 3 Testing:
- Load testing with 1000+ conflicts
- Performance benchmarks
- Security audit

---

## 📚 Documentation Deliverables

### Phase 1 (Complete):
- ✅ PS1_PHASE1_REPORT.md
- ✅ test_ps1_features.py
- ✅ API documentation in /docs

### Phase 2:
- PS1_PHASE2_REPORT.md
- Conflict resolution guide
- Transcript generator documentation

### Phase 3:
- PS1_COMPLETE_REPORT.md
- Deployment guide
- Performance tuning guide

---

## 🎯 Success Metrics

### Phase 1:
- ✅ 8 new API endpoints
- ✅ 1 new table
- ✅ 5 new certificate fields
- ✅ 1 public verification page

### Phase 2:
- 📅 5 new API endpoints
- 📅 1 new table (snapshots)
- 📅 1 conflict dashboard
- 📅 PDF transcript generation

### Phase 3:
- 📅 100% PS1 compliance
- 📅 3 certificate templates
- 📅 Auto-resolution engine
- 📅 Complete test coverage

---

## 🚀 Next Steps

### Immediate Actions (If continuing to Phase 2):
1. **Start with Transcript Generator** - High demo value
2. **Implement Student Snapshots** - Critical for Feature 2
3. **Build Conflict Dashboard** - Complete Feature 1

### Timeline:
- **Today:** Phase 1 complete ✅
- **Next Session:** Phase 2 (4 hours)
- **Final Session:** Phase 3 (3 hours)

### Team Coordination:
- Backend: Focus on services and API
- Frontend: Focus on UI components
- Testing: Verify each phase independently

---

## 📞 Support & Questions

**Documentation:**
- PS1_PHASE1_REPORT.md - Phase 1 details
- http://localhost:8000/docs - API documentation
- http://localhost:3000/verify - Verification demo

**Testing:**
```bash
python3 test_ps1_features.py
```

---

**Document Version:** 1.0  
**Last Updated:** February 16, 2026  
**Status:** Phase 1 Complete | Phase 2 & 3 Ready to Start
