# Role-Based Certificate System - Implementation Guide

## ✅ Completed Components

### 1. Database Layer
- ✅ **Volunteer Model** (`backend/app/models/volunteer.py`)
  - Tracks volunteers with name, email, event association
  - Certificate tracking fields
  
- ✅ **Certificate Model** Updated (`backend/app/models/certificate.py`)
  - Added `role_type` field (attendee, organizer, scanner, volunteer)
  - Added `recipient_name` and `recipient_email` for non-students
  - Made `student_prn` nullable for volunteer certificates
  
- ✅ **Migration Script** (`backend/migrate_role_based_certificates.py`)
  - Creates volunteers table
  - Adds new certificate fields
  - Populates existing data

### 2. Backend API
- ✅ **Volunteer Routes** (`backend/app/routes/volunteers.py`)
  - `POST /volunteers/{event_id}` - Add volunteer
  - `GET /volunteers/{event_id}` - List volunteers
  - `DELETE /volunteers/{volunteer_id}` - Remove volunteer
  - `POST /volunteers/{volunteer_id}/resend-certificate` - Resend certificate
  
- ✅ **Router Registration** (`backend/app/main.py`)
  - Volunteers router added to FastAPI app

### 3. Frontend UI
- ✅ **Certificate Push Modal** (`frontend/src/components/CertificatePushModal/`)
  - Beautiful role selection UI with checkboxes
  - Live count display for each role
  - Color-coded role cards
  
- ✅ **Volunteers Page** (`frontend/src/app/(app)/volunteers/`)
  - Add/remove volunteers
  - View certificate status
  - Resend certificates
  - Event selector
  
- ✅ **Sidebar Update** (`frontend/src/app/(app)/sidebar.tsx`)
  - Added "Volunteers" link with heart icon
  - Accessible to Admin and Organizer roles

---

## 🚧 Components To Complete

### 1. Backend Certificate Service Updates

#### File: `backend/app/routes/certificates.py`

Add new endpoint for role-based stats:

```python
@router.get("/event/{event_id}/role-stats")
def get_certificate_role_stats(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Get eligible recipient counts for each role"""
    from app.models.attendance import Attendance
    from app.models.volunteer import Volunteer
    from app.models.user import User
    
    # Attendees: Students who attended but no certificate
    attendees_query = db.query(Attendance.student_prn).filter(
        Attendance.event_id == event_id
    ).distinct()
    existing_attendee_certs = db.query(Certificate.student_prn).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'attendee'
    ).all()
    existing_prns = {cert[0] for cert in existing_attendee_certs}
    attendees = attendees_query.count() - len(existing_prns)
    
    # Organizers: Event creator + ?
    event = db.query(Event).filter(Event.id == event_id).first()
    organizers = 1 if event else 0  # Event creator
    existing_org_certs = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'organizer'
    ).count()
    organizers = max(0, organizers - existing_org_certs)
    
    # Scanners: Users who scanned for this event
    scanner_ids = db.query(Attendance.scanner_id).filter(
        Attendance.event_id == event_id,
        Attendance.scanner_id.isnot(None)
    ).distinct().all()
    scanners = len(scanner_ids)
    existing_scanner_certs = db.query(Certificate).filter(
        Certificate.event_id == event_id,
        Certificate.role_type == 'scanner'
    ).count()
    scanners = max(0, scanners - existing_scanner_certs)
    
    # Volunteers: From volunteers table without certificates
    volunteers_query = db.query(Volunteer).filter(
        Volunteer.event_id == event_id,
        Volunteer.certificate_sent == False
    )
    volunteers = volunteers_query.count()
    
    return {
        "attendees": attendees,
        "organizers": organizers,
        "scanners": scanners,
        "volunteers": volunteers
    }


@router.post("/event/{event_id}/push-by-roles")
def push_certificates_by_roles(
    event_id: int,
    request: Request,
    roles: List[str] = Body(...),  # ["ATTENDEE", "ORGANIZER", etc.]
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Push certificates to selected roles
    Calls appropriate certificate generation for each role
    """
    from app.services.certificate_service import (
        issue_attendee_certificates,
        issue_organizer_certificates,
        issue_scanner_certificates,
        issue_volunteer_certificates
    )
    
    results = {}
    
    if "ATTENDEE" in roles:
        results["attendee"] = issue_attendee_certificates(db, event_id)
    
    if "ORGANIZER" in roles:
        results["organizer"] = issue_organizer_certificates(db, event_id)
    
    if "SCANNER" in roles:
        results["scanner"] = issue_scanner_certificates(db, event_id)
    
    if "VOLUNTEER" in roles:
        results["volunteer"] = issue_volunteer_certificates(db, event_id)
    
    # Create audit log
    create_audit_log(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
        action_type="certificates_pushed_multi_role",
        details={"roles": roles, "results": results},
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "success": True,
        "roles_processed": roles,
        "results": results
    }
```

#### File: `backend/app/services/certificate_service.py`

Create role-specific certificate functions:

```python
def issue_attendee_certificates(db: Session, event_id: int):
    """Issue certificates to attendees"""
    # Get students who attended
    eligible = get_students_without_certificates(db, event_id)
    
    issued = 0
    emailed = 0
    failed = 0
    
    for student in eligible:
        cert_id = generate_certificate_id()
        
        # Create certificate record
        cert = Certificate(
            event_id=event_id,
            student_prn=student['prn'],
            certificate_id=cert_id,
            role_type='attendee',
            recipient_name=student['name'],
            recipient_email=student['email']
        )
        
        # Generate hash
        cert.verification_hash = cert.generate_verification_hash()
        
        db.add(cert)
        db.commit()
        db.refresh(cert)
        issued += 1
        
        # Send email with ATTENDEE template
        success = send_certificate_email_with_role(
            db, cert_id, student['email'], student['name'], 
            event_id, role='attendee'
        )
        
        if success:
            cert.email_sent = True
            cert.email_sent_at = datetime.now(timezone.utc)
            emailed += 1
        else:
            failed += 1
        
        db.commit()
    
    return {
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }


def issue_volunteer_certificates(db: Session, event_id: int):
    """Issue certificates to volunteers"""
    from app.models.volunteer import Volunteer
    
    volunteers = db.query(Volunteer).filter(
        Volunteer.event_id == event_id,
        Volunteer.certificate_sent == False
    ).all()
    
    issued = 0
    emailed = 0
    failed = 0
    
    for volunteer in volunteers:
        cert_id = generate_certificate_id()
        
        # Create certificate (no student_prn for volunteers)
        cert = Certificate(
            event_id=event_id,
            student_prn=None,  # Volunteers don't have PRN
            certificate_id=cert_id,
            role_type='volunteer',
            recipient_name=volunteer.name,
            recipient_email=volunteer.email
        )
        
        cert.verification_hash = cert.generate_verification_hash()
        
        db.add(cert)
        db.commit()
        db.refresh(cert)
        issued += 1
        
        # Send email with VOLUNTEER template
        success = send_certificate_email_with_role(
            db, cert_id, volunteer.email, volunteer.name,
            event_id, role='volunteer'
        )
        
        if success:
            cert.email_sent = True
            cert.email_sent_at = datetime.now(timezone.utc)
            volunteer.certificate_sent = True
            volunteer.certificate_sent_at = datetime.now(timezone.utc)
            emailed += 1
        else:
            failed += 1
        
        db.commit()
    
    return {
        "issued": issued,
        "emailed": emailed,
        "failed": failed
    }


# Similar functions for:
# - issue_organizer_certificates()
# - issue_scanner_certificates()
```

### 2. Certificate Template Designs

#### Create: `backend/app/services/certificate_templates.py`

This file should contain 4 beautiful PDF templates using ReportLab:

1. **Attendee Template** - Blue gradient, modern design
2. **Organizer Template** - Purple gradient, leadership focused
3. **Scanner Template** - Green gradient, technical design
4. **Volunteer Template** - Orange/pink gradient, appreciation focused

Each template should include:
- Header with event logo/branding
- Certificate title specific to role
- Recipient name in elegant font
- Event details (name, date, location)
- Certificate ID and QR code
- Signature section
- Decorative borders matching role color scheme

Example structure:

```python
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO

def generate_attendee_certificate_pdf(cert_id, student_name, event_title, event_date):
    """Generate beautiful blue attendee certificate"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    
    story = []
    
    # Header
    header_style = ParagraphStyle(
        'Header',
        fontSize=36,
        textColor=colors.HexColor('#1e40af'),
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("CERTIFICATE OF ATTENDANCE", header_style))
    story.append(Spacer(1, 30))
    
    # Body
    body_style = ParagraphStyle(
        'Body',
        fontSize=20,
        textColor=colors.HexColor('#1f2937'),
        alignment=1
    )
    story.append(Paragraph(f"This is to certify that", body_style))
    story.append(Spacer(1, 20))
    
    # Student name in large, elegant font
    name_style = ParagraphStyle(
        'Name',
        fontSize=42,
        textColor=colors.HexColor('#3b82f6'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(student_name, name_style))
    story.append(Spacer(1, 30))
    
    # Event details
    story.append(Paragraph(f"has successfully attended", body_style))
    story.append(Spacer(1, 15))
    
    event_style = ParagraphStyle(
        'Event',
        fontSize=28,
        textColor=colors.HexColor('#1e40af'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph(event_title, event_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"held on {event_date}", body_style))
    story.append(Spacer(1, 40))
    
    # Footer with QR and cert ID
    footer_style = ParagraphStyle(
        'Footer',
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        alignment=1
    )
    story.append(Paragraph(f"Certificate ID: {cert_id}", footer_style))
    story.append(Paragraph("Verify at: unipass.example.com/verify", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# Create similar functions for:
# - generate_organizer_certificate_pdf()
# - generate_scanner_certificate_pdf()
# - generate_volunteer_certificate_pdf()
```

### 3. Event Modal Update

#### File: `frontend/src/app/(app)/events/event-modal.tsx`

Update to open CertificatePushModal:

```tsx
import CertificatePushModal from '@/components/CertificatePushModal/CertificatePushModal';

// Add state
const [showCertificateModal, setShowCertificateModal] = useState(false);

// Replace pushCertificates button click:
<button 
  type="button" 
  onClick={() => setShowCertificateModal(true)}
  className="control-btn certificate-btn"
>
  🎓 Push Certificates
</button>

// Add modal at end of component:
{showCertificateModal && (
  <CertificatePushModal
    eventId={event.id}
    eventTitle={event.title}
    onClose={() => setShowCertificateModal(false)}
    onSuccess={() => {
      loadCertificateStats();
      setShowCertificateModal(false);
    }}
  />
)}
```

---

## 📋 Step-by-Step Implementation Checklist

### Database Setup
- [ ] Run migration: `cd backend && python migrate_role_based_certificates.py`
- [ ] Verify volunteers table created
- [ ] Verify certificate fields added

### Backend Testing
- [ ] Test adding a volunteer via API
- [ ] Test volunteer list endpoint
- [ ] Test removing volunteer
- [ ] Implement role-stats endpoint
- [ ] Implement push-by-roles endpoint
- [ ] Create certificate template functions
- [ ] Test each certificate template PDF generation

### Frontend Integration
- [ ] Verify Volunteers link appears in sidebar
- [ ] Test Volunteers page - add/remove volunteers
- [ ] Test Certificate Push Modal opens
- [ ] Test role selection in modal
- [ ] Test certificate push with multiple roles selected

### End-to-End Testing
- [ ] Create test event
- [ ]  Add test volunteers
- [ ] Record attendance with scanner
- [ ] Open Event Control Center
- [ ] Click "Push Certificates"
- [ ] Select multiple roles (Attendee, Volunteer, Scanner)
- [ ] Verify certificates sent
- [ ] Check each recipient received correct template
- [ ] Verify certificate verification works

### Visual Design Polish
- [ ] Customize attendee certificate colors/fonts
- [ ] Customize organizer certificate design
- [ ] Customize scanner certificate design
- [ ] Customize volunteer certificate design
- [ ] Add event logo to certificates
- [ ] Add decorative borders
- [ ] Test print quality of PDFs

---

## 🎨 Certificate Design Guidelines

### Color Palettes

**Attendee (Blue):**
- Primary: #3b82f6
- Dark: #1e40af
- Light: #dbeafe

**Organizer (Purple):**
- Primary: #8b5cf6
- Dark: #6d28d9
- Light: #ede9fe

**Scanner (Green):**
- Primary: #10b981
- Dark: #059669
- Light: #d1fae5

**Volunteer (Orange/Pink):**
- Primary gradient: #f59e0b to #ec4899
- Dark: #92400e
- Light: #fef3c7

### Fonts
- Headers: Helvetica-Bold or custom serif
- Body: Helvetica
- Names: 42pt Bold
- Titles: 28-36pt Bold
- Details: 16-20pt Regular

---

## 🚀 Quick Start Commands

```bash
# 1. Run migration
cd backend
python migrate_role_based_certificates.py

# 2. Start backend (with new routes)
python -m uvicorn app.main:app --reload

# 3. Start frontend
cd ../frontend
npm run dev

# 4. Test the flow
# - Login as admin
# - Navigate to Volunteers page
# - Add volunteers to an event
# - Go to Events page
# - Click event to open Control Center
# - Click "Push Certificates"
# - Select roles and send
```

---

## 📚 API Documentation

### Volunteers Endpoints

```
POST /volunteers/{event_id}
Body: { "name": "John Doe", "email": "john@example.com" }
Response: { "success": true, "volunteer": {...} }

GET /volunteers/{event_id}
Response: { "volunteers": [...], "total_volunteers": 5 }

DELETE /volunteers/{volunteer_id}
Response: { "success": true, "message": "..." }

POST /volunteers/{volunteer_id}/resend-certificate
Response: { "success": true, "message": "..." }
```

### Certificates Endpoints

```
GET /certificates/event/{event_id}/role-stats
Response: {
  "attendees": 50,
  "organizers": 2,
  "scanners": 3,
  "volunteers": 5
}

POST /certificates/event/{event_id}/push-by-roles
Body: { "roles": ["ATTENDEE", "VOLUNTEER"] }
Response: {
  "success": true,
  "results": {
    "attendee": { "issued": 50, "emailed": 48, "failed": 2 },
    "volunteer": { "issued": 5, "emailed": 5, "failed": 0 }
  }
}
```

---

## 🎯 Success Criteria

✅ Four distinct, beautiful certificate designs  
✅ Volunteers can be added without student accounts  
✅ Modal shows counts for all 4 roles  
✅ Certificates sent only to selected roles  
✅ Each role receives appropriate template  
✅ All certificates are verifiable  
✅ Audit trail for all operations  
✅ Email delivery tracking per role  
✅ Responsive UI across devices  

---

## 💡 Next Steps After Implementation

1. **Customize Templates**: Adjust colors, fonts, logos to match your brand
2. **Add Event Logo**: Include university/event logo in certificates
3. **Translation Support**: Add multi-language certificate templates
4. **Bulk Operations**: Add bulk volunteer import via CSV
5. **Analytics**: Track certificate distribution metrics
6. **Mobile App**: Create mobile app for certificate viewing
7. **Blockchain**: Store certificate hashes on blockchain for immutability

---

**Status**: Foundation complete, templates need implementation
**Priority**: Implement certificate templates and backend service methods
**Estimated Time Remaining**: 3-4 hours for complete implementation
