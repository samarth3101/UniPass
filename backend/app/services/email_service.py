"""
Email Service
Sends professional emails with QR code tickets to students
"""

import smtplib
import qrcode
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from typing import Optional

from app.core.config import settings


def generate_qr_code_image(data: str) -> bytes:
    """
    Generate QR code image as bytes
    Returns PNG image data
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#4f46e5", back_color="white")
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()


def create_ticket_email_html(
    student_name: str,
    event_title: str,
    event_location: str,
    event_start_time: datetime,
    event_end_time: datetime,
    ticket_token: str
) -> str:
    """
    Create beautiful HTML email template for event ticket
    """
    start_str = event_start_time.strftime('%B %d, %Y at %I:%M %p')
    end_str = event_end_time.strftime('%I:%M %p')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8fafb;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            .header p {{
                margin: 8px 0 0 0;
                font-size: 16px;
                opacity: 0.9;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                color: #1e293b;
                margin-bottom: 20px;
            }}
            .ticket-box {{
                background: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                text-align: center;
            }}
            .event-title {{
                font-size: 24px;
                font-weight: 700;
                color: #4f46e5;
                margin: 0 0 20px 0;
            }}
            .event-details {{
                text-align: left;
                margin: 20px 0;
            }}
            .event-row {{
                display: flex;
                align-items: flex-start;
                margin: 12px 0;
                font-size: 15px;
            }}
            .event-icon {{
                width: 24px;
                margin-right: 12px;
                color: #64748b;
            }}
            .event-label {{
                font-weight: 600;
                color: #475569;
                margin-right: 8px;
            }}
            .event-value {{
                color: #1e293b;
            }}
            .qr-section {{
                margin: 30px 0;
                padding: 20px;
                background: white;
                border-radius: 12px;
                border: 2px solid #e0e7ff;
            }}
            .qr-title {{
                font-size: 16px;
                font-weight: 600;
                color: #4f46e5;
                margin-bottom: 15px;
            }}
            .qr-image {{
                max-width: 250px;
                height: auto;
                margin: 0 auto;
                display: block;
            }}
            .qr-hint {{
                font-size: 13px;
                color: #64748b;
                margin-top: 15px;
            }}
            .instructions {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 16px 20px;
                margin: 25px 0;
                border-radius: 8px;
            }}
            .instructions-title {{
                font-weight: 600;
                color: #92400e;
                margin-bottom: 8px;
                font-size: 15px;
            }}
            .instructions-text {{
                color: #78350f;
                font-size: 14px;
                line-height: 1.6;
                margin: 0;
            }}
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e5e9f2;
            }}
            .footer-text {{
                color: #64748b;
                font-size: 13px;
                margin: 8px 0;
            }}
            .support-link {{
                color: #4f46e5;
                text-decoration: none;
                font-weight: 600;
            }}
            .divider {{
                height: 1px;
                background: #e5e9f2;
                margin: 25px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎟️ Your Event Ticket</h1>
                <p>UniPass Event Management</p>
            </div>
            
            <div class="content">
                <div class="greeting">
                    Hi <strong>{student_name}</strong>,
                </div>
                
                <p style="color: #475569; line-height: 1.6; font-size: 15px;">
                    Great news! Your registration has been confirmed. Here's your ticket for the upcoming event:
                </p>
                
                <div class="ticket-box">
                    <h2 class="event-title">{event_title}</h2>
                    
                    <div class="event-details">
                        <div class="event-row">
                            <span class="event-icon">📍</span>
                            <span class="event-label">Location:</span>
                            <span class="event-value">{event_location}</span>
                        </div>
                        <div class="event-row">
                            <span class="event-icon">📅</span>
                            <span class="event-label">Date & Time:</span>
                            <span class="event-value">{start_str}</span>
                        </div>
                        <div class="event-row">
                            <span class="event-icon">⏰</span>
                            <span class="event-label">Ends:</span>
                            <span class="event-value">{end_str}</span>
                        </div>
                    </div>
                    
                    <div class="qr-section">
                        <div class="qr-title">Your QR Code Ticket</div>
                        <img src="cid:qr_code" alt="QR Code" class="qr-image" />
                        <p class="qr-hint">Show this code at the event entrance</p>
                    </div>
                </div>
                
                <div class="instructions">
                    <div class="instructions-title">📱 How to Use Your Ticket</div>
                    <p class="instructions-text">
                        1. Save this email or take a screenshot of the QR code<br>
                        2. Arrive at the venue on time<br>
                        3. Show your QR code at the entrance for scanning<br>
                        4. Your attendance will be recorded automatically
                    </p>
                </div>
                
                <div class="divider"></div>
                
                <p style="color: #64748b; font-size: 14px; line-height: 1.6;">
                    <strong>Important:</strong> Please keep this email safe. You'll need to present the QR code to mark your attendance at the event.
                </p>
            </div>
            
            <div class="footer">
                <p class="footer-text">
                    <strong>UniPass</strong> - University Attendance Management System
                </p>
                <p class="footer-text">
                    Need help? Contact your event organizer
                </p>
                <p class="footer-text" style="margin-top: 15px; color: #94a3b8; font-size: 12px;">
                    This is an automated email. Please do not reply to this message.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_ticket_email(
    to_email: str,
    student_name: str,
    event_title: str,
    event_location: str,
    event_start_time: datetime,
    event_end_time: datetime,
    ticket_token: str
) -> bool:
    """
    Send ticket email with QR code to student
    Returns True if successful, False otherwise
    """
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("Warning: SMTP not configured. Email sending skipped.")
        print(f"Would send ticket to: {to_email}")
        return False
    
    try:
        # Generate QR code image
        qr_image_data = generate_qr_code_image(ticket_token)
        
        # Create email
        msg = MIMEMultipart('related')
        msg['Subject'] = f"🎟️ Your Ticket: {event_title}"
        msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg['To'] = to_email
        
        # Create HTML body
        html_body = create_ticket_email_html(
            student_name=student_name,
            event_title=event_title,
            event_location=event_location,
            event_start_time=event_start_time,
            event_end_time=event_end_time,
            ticket_token=ticket_token
        )
        
        # Attach HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Attach QR code image
        qr_image = MIMEImage(qr_image_data, name='qr_code.png')
        qr_image.add_header('Content-ID', '<qr_code>')
        qr_image.add_header('Content-Disposition', 'inline', filename='qr_code.png')
        msg.attach(qr_image)
        
        # Send email with timeout - support both SSL (port 465) and TLS (port 587)
        if settings.SMTP_PORT == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"✅ Ticket email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        # Silently log email failures (network/SMTP issues are common)
        print(f"ℹ️  Email delivery skipped for {to_email} (SMTP unavailable)")
        return False


def create_teacher_email_html(
    teacher_name: str,
    event_title: str,
    event_location: str,
    event_date: str,
    total_registered: int,
    total_present: int,
    attendance_list: list
) -> str:
    """
    Create professional HTML email template for teacher attendance report
    """
    
    # Calculate attendance percentage
    attendance_percentage = (total_present / total_registered * 100) if total_registered > 0 else 0
    
    # Build attendance rows HTML
    attendance_rows = ""
    for idx, record in enumerate(attendance_list, 1):
        scanned_at = record['scanned_at'].strftime('%I:%M %p') if isinstance(record['scanned_at'], datetime) else record['scanned_at']
        attendance_rows += f"""
        <tr style="border-bottom: 1px solid #e2e8f0;">
            <td style="padding: 12px; text-align: center; color: #64748b; font-size: 14px;">{idx}</td>
            <td style="padding: 12px; color: #1e293b; font-size: 14px; font-weight: 500;">{record['student_prn']}</td>
            <td style="padding: 12px; color: #475569; font-size: 14px;">{record.get('student_name', 'N/A')}</td>
            <td style="padding: 12px; color: #64748b; font-size: 14px; text-align: center;">{scanned_at}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Attendance Report - {event_title}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="max-width: 700px; margin: 40px auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 40px 30px; text-align: center;">
                <div style="display: inline-block; background: white; padding: 12px 24px; border-radius: 50px; margin-bottom: 20px;">
                    <span style="color: #6366f1; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">📊 Attendance Report</span>
                </div>
                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 800; line-height: 1.3;">{event_title}</h1>
                <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">Event Attendance Summary</p>
            </div>
            
            <!-- Greeting -->
            <div style="padding: 30px;">
                <p style="margin: 0 0 20px; color: #1e293b; font-size: 16px; line-height: 1.6;">
                    Dear <strong>{teacher_name}</strong>,
                </p>
                <p style="margin: 0 0 30px; color: #475569; font-size: 15px; line-height: 1.6;">
                    Please find below the attendance report for the event conducted on <strong>{event_date}</strong>.
                </p>
                
                <!-- Event Details -->
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); border-left: 4px solid #6366f1; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                    <div style="margin-bottom: 12px;">
                        <span style="color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Event</span>
                        <p style="margin: 5px 0 0; color: #1e293b; font-size: 16px; font-weight: 600;">{event_title}</p>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <span style="color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Location</span>
                        <p style="margin: 5px 0 0; color: #475569; font-size: 15px;">{event_location}</p>
                    </div>
                    <div>
                        <span style="color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Date</span>
                        <p style="margin: 5px 0 0; color: #475569; font-size: 15px;">{event_date}</p>
                    </div>
                </div>
                
                <!-- Statistics -->
                <div style="display: flex; gap: 15px; margin-bottom: 30px;">
                    <div style="flex: 1; background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);">
                        <div style="color: white; font-size: 32px; font-weight: 800; margin-bottom: 5px;">{total_present}</div>
                        <div style="color: rgba(255,255,255,0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Present</div>
                    </div>
                    <div style="flex: 1; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);">
                        <div style="color: white; font-size: 32px; font-weight: 800; margin-bottom: 5px;">{total_registered}</div>
                        <div style="color: rgba(255,255,255,0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Registered</div>
                    </div>
                    <div style="flex: 1; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);">
                        <div style="color: white; font-size: 32px; font-weight: 800; margin-bottom: 5px;">{attendance_percentage:.1f}%</div>
                        <div style="color: rgba(255,255,255,0.9); font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Attendance</div>
                    </div>
                </div>
                
                <!-- Attendance List -->
                <div style="margin-bottom: 30px;">
                    <h2 style="color: #1e293b; font-size: 18px; font-weight: 700; margin: 0 0 15px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;">Attendance List</h2>
                    <div style="overflow-x: auto; border-radius: 10px; border: 1px solid #e2e8f0;">
                        <table style="width: 100%; border-collapse: collapse; background: white;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%);">
                                    <th style="padding: 12px; text-align: center; color: #475569; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">#</th>
                                    <th style="padding: 12px; text-align: left; color: #475569; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">PRN</th>
                                    <th style="padding: 12px; text-align: left; color: #475569; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Student Name</th>
                                    <th style="padding: 12px; text-align: center; color: #475569; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                {attendance_rows}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Footer Message -->
                <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border-left: 4px solid #6366f1;">
                    <p style="margin: 0; color: #475569; font-size: 14px; line-height: 1.6;">
                        <strong>Note:</strong> This is an automated attendance report generated by UniPass. All timestamps are recorded at the moment of QR code scanning.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8fafc; padding: 25px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0 0 8px; color: #1e293b; font-size: 15px; font-weight: 600;">UniPass - Smart Attendance System</p>
                <p style="margin: 0; color: #94a3b8; font-size: 12px;">This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_teacher_email(
    to_email: str,
    teacher_name: str,
    event_title: str,
    event_location: str,
    event_date: str,
    total_registered: int,
    total_present: int,
    attendance_list: list
) -> bool:
    """
    Send attendance report email to teacher
    Returns True if successful, False otherwise
    """
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("Warning: SMTP not configured. Email sending skipped.")
        print(f"Would send attendance report to: {to_email}")
        return False
    
    try:
        # Create email
        msg = MIMEMultipart('related')
        msg['Subject'] = f"📊 Attendance Report: {event_title}"
        msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg['To'] = to_email
        
        # Create HTML body
        html_body = create_teacher_email_html(
            teacher_name=teacher_name,
            event_title=event_title,
            event_location=event_location,
            event_date=event_date,
            total_registered=total_registered,
            total_present=total_present,
            attendance_list=attendance_list
        )
        
        # Attach HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email with timeout - support both SSL (port 465) and TLS (port 587)
        if settings.SMTP_PORT == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"✅ Teacher attendance report sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send teacher report to {to_email}: {str(e)}")
        return False


def create_certificate_email_html(
    student_name: str,
    event_title: str,
    event_location: str,
    event_date: str,
    certificate_id: str,
    role_type: str = "attendee"
) -> str:
    """
    Create beautiful HTML email template for event certificate
    Role-aware: attendee, organizer, scanner, volunteer
    """
    
    # Role-specific content
    role_config = {
        "attendee": {
            "badge": "🎓 CERTIFICATE",
            "title": "Certificate of Participation",
            "greeting": "Congratulations!",
            "message": "We are pleased to inform you that you have successfully completed your participation in:",
            "achievement": "🌟 Thank you for your active participation! This certificate recognizes your attendance and engagement in the event.",
            "gradient": "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)"
        },
        "organizer": {
            "badge": "🏆 APPRECIATION",
            "title": "Certificate of Appreciation - Event Organizer",
            "greeting": "Outstanding Leadership!",
            "message": "This certificate recognizes your exceptional contribution as an organizer for:",
            "achievement": "👏 Thank you for your dedicated service in organizing this event! Your leadership and commitment made this event a success.",
            "gradient": "linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)"
        },
        "scanner": {
            "badge": "✅ APPRECIATION",
            "title": "Certificate of Appreciation - Event Scanner",
            "greeting": "Excellent Service!",
            "message": "This certificate recognizes your valuable contribution as a scanner for:",
            "achievement": "🙌 Thank you for your dedicated service! Your efficient attendance management ensured smooth event operations.",
            "gradient": "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        },
        "volunteer": {
            "badge": "❤️ APPRECIATION",
            "title": "Certificate of Appreciation - Volunteer",
            "greeting": "Heartfelt Thanks!",
            "message": "This certificate recognizes your generous volunteercontribution for:",
            "achievement": "💝 Thank you for volunteering your time and effort! Your selfless service made a meaningful difference to this event's success.",
            "gradient": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        }
    }
    
    config = role_config.get(role_type, role_config["attendee"])
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Certificate of Participation - {event_title}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div style="max-width: 700px; margin: 40px auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);">
            
            <!-- Header -->
            <div style="background: {config['gradient']}; padding: 40px 30px; text-align: center;">
                <div style="display: inline-block; background: white; padding: 12px 24px; border-radius: 50px; margin-bottom: 20px;">
                    <span style="color: #4f46e5; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">{config['badge']}</span>
                </div>
                <h1 style="margin: 0; color: white; font-size: 32px; font-weight: 800; line-height: 1.3;">{config['greeting']}</h1>
                <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">{config['title']}</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="margin: 0 0 20px; color: #1e293b; font-size: 16px; line-height: 1.6;">
                    Dear <strong>{student_name}</strong>,
                </p>
                <p style="margin: 0 0 30px; color: #475569; font-size: 15px; line-height: 1.6;">
                    {config['message']}
                </p>
                
                <!-- Certificate Box -->
                <div style="background: linear-gradient(135deg, #fef3c7 0%, #fce7f3 100%); border: 3px solid #f59e0b; border-radius: 16px; padding: 30px; margin: 30px 0; text-align: center; position: relative; box-shadow: 0 10px 30px rgba(245, 158, 11, 0.2);">
                    <div style="position: absolute; top: -15px; left: 50%; transform: translateX(-50%); background: white; padding: 8px 20px; border-radius: 20px; border: 2px solid #f59e0b;">
                        <span style="color: #f59e0b; font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Official Certificate</span>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h2 style="margin: 0 0 20px; color: #92400e; font-size: 28px; font-weight: 800; line-height: 1.3;">{event_title}</h2>
                        
                        <div style="margin: 20px 0;">
                            <div style="display: inline-block; margin: 8px 12px;">
                                <span style="color: #78350f; font-size: 14px; font-weight: 600;">📍 Location: </span>
                                <span style="color: #92400e; font-size: 14px; font-weight: 500;">{event_location}</span>
                            </div>
                            <div style="display: inline-block; margin: 8px 12px;">
                                <span style="color: #78350f; font-size: 14px; font-weight: 600;">📅 Date: </span>
                                <span style="color: #92400e; font-size: 14px; font-weight: 500;">{event_date}</span>
                            </div>
                        </div>
                        
                        <div style="margin-top: 25px; padding-top: 20px; border-top: 2px dashed #f59e0b;">
                            <p style="margin: 0; color: #78350f; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Certificate ID</p>
                            <p style="margin: 5px 0 0; color: #92400e; font-size: 16px; font-weight: 700; font-family: monospace;">{certificate_id}</p>
                        </div>
                    </div>
                </div>
                
                <!-- Achievement Message -->
                <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                    <p style="margin: 0; color: #065f46; font-size: 15px; line-height: 1.6; font-weight: 500;">
                        {config['achievement']}
                    </p>
                </div>
                
                <!-- Verification Info -->
                <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                    <p style="margin: 0 0 12px; color: #1e293b; font-size: 14px; font-weight: 700;">📋 Certificate Details:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.8;">
                        <li>This is an official certificate issued by UniPass Event Management</li>
                        <li>Certificate ID can be used for verification purposes</li>
                        <li>Keep this email for your records</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.6;">
                        We appreciate your participation and hope to see you at future events!
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8fafc; padding: 25px 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="margin: 0 0 8px; color: #1e293b; font-size: 15px; font-weight: 600;">UniPass - Smart Event Management</p>
                <p style="margin: 0; color: #94a3b8; font-size: 12px;">This is an automated email. Please do not reply to this message.</p>
                <p style="margin: 15px 0 0; color: #cbd5e1; font-size: 11px;">© 2026 UniPass. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_certificate_email(
    to_email: str,
    student_name: str,
    event_title: str,
    event_location: str,
    event_date: str,
    certificate_id: str,
    role_type: str = "attendee"
) -> bool:
    """
    Send certificate email to student
    Returns True if successful, False otherwise
    """
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("Warning: SMTP not configured. Email sending skipped.")
        print(f"Would send certificate to: {to_email}")
        return False
    
    try:
        # Create email
        msg = MIMEMultipart('related')
        msg['Subject'] = f"🎓 Certificate of Participation: {event_title}"
        msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg['To'] = to_email
        
        # Create HTML body
        html_body = create_certificate_email_html(
            student_name=student_name,
            event_title=event_title,
            event_location=event_location,
            event_date=event_date,
            certificate_id=certificate_id,
            role_type=role_type
        )
        
        # Attach HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email with timeout - support both SSL (port 465) and TLS (port 587)
        if settings.SMTP_PORT == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"✅ Certificate email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send certificate email to {to_email}: {str(e)}")
        return False


def create_feedback_request_email_html(
    student_name: str,
    event_title: str,
    event_id: int,
    student_prn: str
) -> str:
    """
    Create beautiful HTML email template for feedback request
    """
    feedback_url = f"{settings.FRONTEND_URL}/feedback/{event_id}/{student_prn}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8fafb;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            .header h1 {{
                margin: 0;
                font-size: 32px;
                font-weight: 700;
            }}
            .header p {{
                margin: 12px 0 0 0;
                font-size: 16px;
                opacity: 0.95;
            }}
            .content {{
                padding: 40px 30px;
            }}
            .greeting {{
                font-size: 18px;
                color: #1e293b;
                margin-bottom: 20px;
                font-weight: 500;
            }}
            .message {{
                font-size: 16px;
                color: #475569;
                line-height: 1.6;
                margin-bottom: 30px;
            }}
            .event-box {{
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                border-left: 4px solid #10b981;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            .event-box h3 {{
                margin: 0 0 8px 0;
                color: #065f46;
                font-size: 20px;
            }}
            .event-box p {{
                margin: 0;
                color: #047857;
                font-size: 14px;
            }}
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                text-decoration: none;
                padding: 16px 48px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 600;
                text-align: center;
                margin: 20px 0;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                transition: all 0.3s ease;
            }}
            .cta-button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
            }}
            .button-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .benefits {{
                background: #f8fafc;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
            }}
            .benefits h3 {{
                margin: 0 0 15px 0;
                color: #1e293b;
                font-size: 18px;
            }}
            .benefit-item {{
                display: flex;
                align-items: start;
                margin-bottom: 12px;
            }}
            .benefit-icon {{
                background: #10b981;
                color: white;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                flex-shrink: 0;
                font-size: 14px;
                font-weight: bold;
            }}
            .benefit-text {{
                color: #475569;
                font-size: 15px;
                line-height: 1.5;
            }}
            .time-estimate {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            .time-estimate p {{
                margin: 0;
                color: #92400e;
                font-size: 15px;
            }}
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                color: #64748b;
                font-size: 14px;
                margin: 5px 0;
            }}
            .footer a {{
                color: #4f46e5;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 Your Feedback Matters!</h1>
                <p>Help us improve future events</p>
            </div>
            
            <div class="content">
                <p class="greeting">Hello {student_name},</p>
                
                <p class="message">
                    Thank you for attending our event! We hope you had a great experience. 
                    Your feedback is invaluable in helping us create even better events in the future.
                </p>
                
                <div class="event-box">
                    <h3>📌 {event_title}</h3>
                    <p>Share your thoughts about this event</p>
                </div>
                
                <div class="time-estimate">
                    <p>⏱️ <strong>Takes only 2-3 minutes</strong> to complete</p>
                </div>
                
                <div class="benefits">
                    <h3>Why your feedback matters:</h3>
                    <div class="benefit-item">
                        <div class="benefit-icon">✓</div>
                        <div class="benefit-text">Helps us improve content quality and organization</div>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-icon">✓</div>
                        <div class="benefit-text">Influences future event topics and speakers</div>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-icon">✓</div>
                        <div class="benefit-text">Ensures better experience for all students</div>
                    </div>
                    <div class="benefit-item">
                        <div class="benefit-icon">✓</div>
                        <div class="benefit-text">Your honest opinion helps event organizers grow</div>
                    </div>
                </div>
                
                <div class="button-container">
                    <a href="{feedback_url}" class="cta-button">
                        Submit Feedback
                    </a>
                </div>
                
                <p class="message" style="font-size: 14px; color: #64748b; text-align: center;">
                    This feedback form is anonymous and will only take a few minutes of your time.<br>
                    Your responses will be used to improve future events.
                </p>
            </div>
            
            <div class="footer">
                <p><strong>UniPass Event Management System</strong></p>
                <p>Secure AI-Powered Attendance & Feedback</p>
                <p style="margin-top: 15px;">
                    <a href="{settings.FRONTEND_URL}">Visit Dashboard</a> | 
                    <a href="mailto:{settings.EMAIL_FROM}">Contact Support</a>
                </p>
                <p style="margin-top: 15px; font-size: 12px;">
                    © 2026 UniPass. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def send_feedback_request_email(
    to_email: str,
    student_name: str,
    event_title: str,
    event_id: int,
    student_prn: str
) -> bool:
    """
    Send feedback request email to student who attended event
    Returns True if email sent successfully
    """
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("⚠️ SMTP not configured. Skipping feedback request email.")
        print(f"Would send feedback request to: {to_email}")
        return False
    
    try:
        # Create email
        msg = MIMEMultipart('related')
        msg['Subject'] = f"📝 We'd love your feedback on {event_title}"
        msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        msg['To'] = to_email
        
        # Create HTML body
        html_body = create_feedback_request_email_html(
            student_name=student_name,
            event_title=event_title,
            event_id=event_id,
            student_prn=student_prn
        )
        
        # Attach HTML
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email with timeout - support both SSL (port 465) and TLS (port 587)
        if settings.SMTP_PORT == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use STARTTLS for port 587
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        
        print(f"✅ Feedback request email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send feedback request email to {to_email}: {str(e)}")
        return False
