"""
Event Report Service
Generates professional PDF reports for events with attendance statistics
"""

from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.event import Event
from app.models.ticket import Ticket
from app.models.attendance import Attendance
from app.models.student import Student


def calculate_event_statistics(db: Session, event_id: int):
    """
    Calculate event statistics:
    - Total registered
    - Total attended
    - Attendance percentage
    - List of absentees with student details
    """
    # Get total registered (tickets issued)
    total_registered = db.query(Ticket).filter(Ticket.event_id == event_id).count()
    
    # Get total attended (attendance records)
    total_attended = db.query(Attendance).filter(Attendance.event_id == event_id).count()
    
    # Calculate attendance percentage
    attendance_percentage = (total_attended / total_registered * 100) if total_registered > 0 else 0
    
    # Get absentees: students with tickets but no attendance record
    tickets = db.query(Ticket).filter(Ticket.event_id == event_id).all()
    attended_prns = {att.student_prn for att in db.query(Attendance.student_prn).filter(Attendance.event_id == event_id).all()}
    
    absentees = []
    for ticket in tickets:
        if ticket.student_prn not in attended_prns:
            student = db.query(Student).filter(Student.prn == ticket.student_prn).first()
            absentees.append({
                "prn": ticket.student_prn,
                "name": student.name if student else "Unknown",
                "email": student.email if student else "N/A"
            })
    
    return {
        "total_registered": total_registered,
        "total_attended": total_attended,
        "attendance_percentage": round(attendance_percentage, 2),
        "absentees": absentees
    }


def generate_event_report_pdf(db: Session, event_id: int) -> BytesIO:
    """
    Generate a professional PDF report for an event
    Returns BytesIO buffer containing the PDF
    """
    # Get event details
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise ValueError(f"Event with ID {event_id} not found")
    
    # Calculate statistics
    stats = calculate_event_statistics(db, event_id)
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Header
    elements.append(Paragraph("UniPass Event Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Event Details Section
    elements.append(Paragraph("Event Details", heading_style))
    
    # Format datetime objects directly
    start_time_str = event.start_time.strftime('%B %d, %Y at %I:%M %p') if hasattr(event.start_time, 'strftime') else str(event.start_time)
    end_time_str = event.end_time.strftime('%B %d, %Y at %I:%M %p') if hasattr(event.end_time, 'strftime') else str(event.end_time)
    
    event_data = [
        ["Event Title:", event.title],
        ["Location:", event.location],
        ["Start Time:", start_time_str],
        ["End Time:", end_time_str],
    ]
    
    if event.description:
        event_data.append(["Description:", event.description[:100] + "..." if len(event.description) > 100 else event.description])
    
    event_table = Table(event_data, colWidths=[2*inch, 4.5*inch])
    event_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e9f2')),
    ]))
    
    elements.append(event_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Statistics Section
    elements.append(Paragraph("Attendance Statistics", heading_style))
    
    stats_data = [
        ["Metric", "Value"],
        ["Total Registered", str(stats["total_registered"])],
        ["Total Attended", str(stats["total_attended"])],
        ["Absentees", str(stats["total_registered"] - stats["total_attended"])],
        ["Attendance Rate", f"{stats['attendance_percentage']}%"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3.25*inch, 3.25*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e9f2')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Absentees Section (if any)
    if stats["absentees"]:
        elements.append(Paragraph(f"Absentees List ({len(stats['absentees'])} students)", heading_style))
        
        absentee_data = [["#", "PRN", "Name", "Email"]]
        for idx, absentee in enumerate(stats["absentees"], 1):
            absentee_data.append([
                str(idx),
                absentee["prn"],
                absentee["name"],
                absentee["email"]
            ])
        
        absentee_table = Table(absentee_data, colWidths=[0.5*inch, 1.5*inch, 2.5*inch, 2*inch])
        absentee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e9f2')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        
        elements.append(absentee_table)
    else:
        elements.append(Paragraph("Absentees List", heading_style))
        no_absentees_style = ParagraphStyle(
            'NoAbsentees',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#10b981'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("🎉 Perfect Attendance! All registered students attended.", no_absentees_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Generated by UniPass - University Attendance Management System", footer_style))
    elements.append(Paragraph("This is an official attendance report", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position
    buffer.seek(0)
    return buffer
