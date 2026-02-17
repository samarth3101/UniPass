# Role-Based Certificate System - Implementation Plan

## Overview
Implement a comprehensive role-based certificate system where users can receive multiple certificates based on their roles (Attendee, Organizer, Scanner, Volunteer) with unique, visually appealing designs for each role.

## Architecture

### 1. Certificate Roles
- **Attendee/Participant**: Default role for students who attended the event
- **Organizer**: Users who organized the event  
- **Scanner**: Users who scanned attendees
- **Volunteer**: External volunteers (not login users, managed via email)

### 2. Database Changes

#### Update `certificates` Table:
```sql
ALTER TABLE certificates ADD COLUMN role_type VARCHAR(50) NOT NULL DEFAULT 'ATTENDEE';
ALTER TABLE certificates ADD COLUMN recipient_name VARCHAR(255);
ALTER TABLE certificates ADD COLUMN recipient_email VARCHAR(255);
-- For volunteers who don't have student_prn
ALTER TABLE certificates MODIFY COLUMN student_prn VARCHAR NULL;
```

#### New `volunteers` Table:
```sql
CREATE TABLE volunteers (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    added_by INTEGER REFERENCES users(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    certificate_sent BOOLEAN DEFAULT FALSE,
    UNIQUE(event_id, email)
);
```

### 3. Backend Implementation

#### Files to Create/Update:

1. **`backend/app/models/volunteer.py`** (NEW)
   - Volunteer model with event association

2. **`backend/app/models/certificate.py`** (UPDATE)
   - Add `role_type` field (ENUM: ATTENDEE, ORGANIZER, SCANNER, VOLUNTEER)
   - Add `recipient_name` and `recipient_email` for non-student certificates
   - Make `student_prn` nullable for volunteer certificates

3. **`backend/app/routes/volunteers.py`** (NEW)
   - POST `/volunteers/{event_id}` - Add volunteer
   - GET `/volunteers/{event_id}` - List event volunteers
   - DELETE `/volunteers/{volunteer_id}` - Remove volunteer
   - POST `/volunteers/{volunteer_id}/resend-certificate` - Resend certificate

4. **`backend/app/routes/certificates.py`** (UPDATE)
   - POST `/certificates/event/{event_id}/push` - Update to accept role filters
   ```json
   {
     "roles": ["ATTENDEE", "ORGANIZER", "SCANNER", "VOLUNTEER"],
     "dry_run": false
   }
   ```

5. **`backend/app/services/certificate_service.py`** (UPDATE)
   - `generate_certificate_pdf()` - Add role_type parameter
   - Create 4 distinct template functions:
     - `_generate_attendee_certificate()`
     - `_generate_organizer_certificate()`
     - `_generate_scanner_certificate()`
     - `_generate_volunteer_certificate()`

6. **`backend/migrate_role_based_certificates.py`** (NEW)
   - Migration script to add new fields and table

### 4. Frontend Implementation

#### Files to Create/Update:

1. **`frontend/src/components/CertificatePushModal.tsx`** (NEW)
   - Modal with role checkboxes
   - Preview counts for each role
   - Push certificates button

2. **`frontend/src/app/(app)/volunteers/page.tsx`** (NEW)
   - Volunteer management page
   - Add volunteer form (name + email)
   - List of volunteers with delete/resend options

3. **`frontend/src/app/(app)/volunteers/volunteers.scss`** (NEW)
   - Styling for volunteer page

4. **`frontend/src/app/(app)/sidebar.tsx`** (UPDATE)
   - Add "Volunteers" link after "Scanners"

5. **`frontend/src/app/(app)/events/event-modal.tsx`** (UPDATE)
   - Replace `pushCertificates()` button click to open modal
   - Import and use CertificatePushModal

### 5. Certificate Design Specifications

#### Attendee Certificate
- **Color Scheme**: Blue gradient (#3b82f6 to #1e40af)
- **Style**: Modern, clean, professional
- **Elements**: 
  - Large "Certificate of Attendance"
  - Student name in cursive font
  - Event details
  - Date and signature
  - QR code for verification

#### Organizer Certificate
- **Color Scheme**: Purple gradient (#8b5cf6 to #6d28d9)
- **Style**: Leadership-focused, prestigious
- **Elements**:
  - "Certificate of Event Organization"
  - Gold/bronze accents
  - Leadership badge icon
  - Event details  
  - Signature with "Event Lead" designation

#### Scanner Certificate
- **Color Scheme**: Green gradient (#10b981 to #059669)
- **Style**: Technical, operational
- **Elements**:
  - "Certificate of Service - Scanner Team"
  - Scanner icon/badge
  - Number of scans performed
  - Event details
  - Tech-themed border

#### Volunteer Certificate  
- **Color Scheme**: Orange/Pink gradient (#f59e0b to #ec4899)
- **Style**: Appreciation-focused, warm
- **Elements**:
  - "Certificate of Appreciation - Volunteer"
  - Heart/hands icon
  - "In recognition of your valuable contribution"
  - Event details
  - Special thank you message

### 6. Certificate Logic Flow

```
When "Push Certificates" is clicked:
1. Open CertificatePushModal
2. Show checkboxes: [x] Attendee [x] Organizer [x] Scanner [x] Volunteer
3. For each selected role, show count of eligible recipients:
   - Attendee: Count of attended students without certificates
   - Organizer: Event creator + assigned organizers
   - Scanner: Users who scanned for this event
   - Volunteer: Volunteers added to this event
4. On "Send Certificates" click:
   - Backend generates role-specific PDFs
   - Sends emails with appropriate certificate
   - Creates certificate records with role_type
5. Show success/failure counts per role
```

### 7. Migration Strategy

1. Run database migration to add new fields/table
2. Default existing certificates to `role_type='ATTENDEE'`
3. Populate `recipient_name` and `recipient_email` for existing certificates
4. Deploy backend changes
5. Deploy frontend changes
6. Test with sample event

### 8. API Endpoints Summary

#### New Endpoints:
```
POST   /volunteers/{event_id}                    - Add volunteer
GET    /volunteers/{event_id}                    - List volunteers
DELETE /volunteers/{volunteer_id}                - Remove volunteer
POST   /volunteers/{volunteer_id}/resend         - Resend certificate
```

#### Updated Endpoints:
```
POST /certificates/event/{event_id}/push
Body: {
  "roles": ["ATTENDEE", "ORGANIZER", "SCANNER", "VOLUNTEER"],
  "dry_run": false
}

Response: {
  "success": true,
  "results": {
    "ATTENDEE": {
      "issued": 45,
      "emailed": 43,
      "failed": 2
    },
    "ORGANIZER": {
      "issued": 3,
      "emailed": 3,
      "failed": 0
    },
    ...
  }
}
```

### 9. Testing Checklist

- [ ] Create volunteers table and run migration
- [ ] Add volunteers to an event via UI
- [ ] Open certificate push modal
- [ ] Select multiple roles and push certificates
- [ ] Verify each role receives correct template
- [ ] Test email delivery for all roles
- [ ] Verify certificate verification works for all types
- [ ] Test resend functionality
- [ ] Check audit logs

### 10. Security Considerations

- Only ADMIN and ORGANIZER can add volunteers
- Only event creator or ADMIN can push certificates
- Email validation for volunteers
- Rate limiting on certificate push
- Audit logging for all certificate operations

## Implementation Priority

1. **Phase 1**: Database migration + Models (30 min)
2. **Phase 2**: Backend volunteers management (45 min)
3. **Phase 3**: Backend certificate role logic (60 min)
4. **Phase 4**: Certificate template designs (90 min)
5. **Phase 5**: Frontend volunteer page (45 min)
6. **Phase 6**: Frontend certificate modal (60 min)
7. **Phase 7**: Testing and refinement (60 min)

**Total Estimated Time: ~6 hours**

## Next Steps

Execute implementation in order, testing each phase before moving forward.
