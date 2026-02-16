"""
PS1 Transcript Service
Generates comprehensive participation transcripts for students
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.user import User
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.participation_role import ParticipationRole


class TranscriptService:
    """Service for generating student participation transcripts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_student_participations(self, prn: str) -> Dict[str, Any]:
        """
        Get all participation data for a student
        Returns structured data for transcript generation
        """
        # Get all registrations
        registrations = (
            self.db.query(Ticket, Event)
            .join(Event, Ticket.event_id == Event.id)
            .filter(Ticket.student_prn == prn)
            .order_by(Event.start_time.desc())
            .all()
        )
        
        # Get all attendance records
        attendances = (
            self.db.query(Attendance, Event)
            .join(Event, Attendance.event_id == Event.id)
            .filter(Attendance.student_prn == prn)
            .order_by(Event.start_time.desc())
            .all()
        )
        
        # Get all certificates
        certificates = (
            self.db.query(Certificate, Event)
            .join(Event, Certificate.event_id == Event.id)
            .filter(Certificate.student_prn == prn)
            .filter(Certificate.revoked == False)
            .order_by(Certificate.issued_at.desc())
            .all()
        )
        
        # Get all roles
        roles = (
            self.db.query(ParticipationRole, Event)
            .join(Event, ParticipationRole.event_id == Event.id)
            .filter(ParticipationRole.student_prn == prn)
            .order_by(ParticipationRole.assigned_at.desc())
            .all()
        )
        
        # Compile comprehensive participation list
        participations = []
        event_ids_seen = set()
        
        for ticket, event in registrations:
            if event.id not in event_ids_seen:
                # Find matching attendance
                attendance_record = next(
                    (a for a, e in attendances if e.id == event.id),
                    None
                )
                
                # Find matching certificate
                cert_record = next(
                    (c for c, e in certificates if e.id == event.id),
                    None
                )
                
                # Find roles for this event
                event_roles = [
                    r.role for r, e in roles if e.id == event.id
                ]
                
                participations.append({
                    'event_id': event.id,
                    'event_name': event.title,
                    'event_date': event.start_time,
                    'event_type': event.event_type if hasattr(event, 'event_type') else 'event',
                    'registered': True,
                    'registration_date': ticket.issued_at,
                    'attended': attendance_record is not None,
                    'attendance_time': attendance_record.scanned_at if attendance_record else None,
                    'certified': cert_record is not None,
                    'certificate_id': cert_record.certificate_id if cert_record else None,
                    'roles': event_roles,
                    'status': 'registered'
                })
                
                event_ids_seen.add(event.id)
        
        # Calculate statistics
        total_registered = len(participations)
        total_attended = sum(1 for p in participations if p['attended'])
        total_certified = sum(1 for p in participations if p['certified'])
        attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0
        
        # Get unique roles
        all_roles = set()
        for p in participations:
            all_roles.update(p['roles'])
        
        return {
            'prn': prn,
            'participations': participations,
            'statistics': {
                'total_registered': total_registered,
                'total_attended': total_attended,
                'total_certified': total_certified,
                'attendance_rate': round(attendance_rate, 1),
                'unique_roles': list(all_roles),
                'total_roles': len(all_roles)
            },
            'generated_at': datetime.now()
        }
    
    def generate_transcript_pdf(self, prn: str) -> BytesIO:
        """
        Generate PDF transcript for student
        Returns BytesIO object containing PDF
        """
        data = self.get_student_participations(prn)
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            spaceBefore=20
        )
        
        # Title
        story.append(Paragraph("Campus Participation Transcript", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Student info
        info_data = [
            ['Student PRN:', data['prn']],
            ['Generated:', data['generated_at'].strftime('%B %d, %Y at %I:%M %p')],
            ['Total Events:', str(data['statistics']['total_registered'])]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Statistics section
        story.append(Paragraph("Participation Summary", heading_style))
        
        stats = data['statistics']
        stats_data = [
            ['Registered', 'Attended', 'Certified', 'Attendance Rate'],
            [
                str(stats['total_registered']),
                str(stats['total_attended']),
                str(stats['total_certified']),
                f"{stats['attendance_rate']}%"
            ]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch]*4)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe'))
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Roles section
        if stats['unique_roles']:
            roles_text = f"<b>Roles Held:</b> {', '.join(stats['unique_roles'])}"
            story.append(Paragraph(roles_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Participations section
        story.append(Paragraph("Detailed Participation History", heading_style))
        
        if data['participations']:
            # Table headers
            participation_data = [
                ['Event', 'Date', 'Registered', 'Attended', 'Certified', 'Roles']
            ]
            
            # Add each participation
            for p in data['participations']:
                participation_data.append([
                    Paragraph(p['event_name'][:40], styles['Normal']),
                    p['event_date'].strftime('%Y-%m-%d') if p['event_date'] else 'N/A',
                    '✓' if p['registered'] else '✗',
                    '✓' if p['attended'] else '✗',
                    '✓' if p['certified'] else '✗',
                    ', '.join(p['roles'][:2]) if p['roles'] else '-'
                ])
            
            participation_table = Table(
                participation_data,
                colWidths=[2.5*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch]
            )
            
            participation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (4, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1'))
            ]))
            
            story.append(participation_table)
        else:
            story.append(Paragraph("No participation records found.", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            "This transcript is generated automatically from the UniPass participation database.<br/>"
            "For verification, visit https://unipass.example.com/verify",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
