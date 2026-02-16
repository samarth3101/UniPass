"""
Role-Based Certificate Templates - PS1 Feature 5
Generate role-specific certificate content and styling

Part of PS1 Feature 5: Multi-Role Participation Engine
"""

from typing import Dict, List, Optional


class RoleBasedCertificateTemplate:
    """
    Generate role-specific certificate templates with customized 
    styling, titles, and descriptions based on participation role
    """
    
    # Role-specific colors and styling
    ROLE_COLORS = {
        "PARTICIPANT": {
            "primary": "#3b82f6",  # Blue
            "secondary": "#93c5fd",
            "icon": "🎓",
            "title_suffix": "Participant",
            "achievement_text": "for active participation in"
        },
        "VOLUNTEER": {
            "primary": "#10b981",  # Green
            "secondary": "#6ee7b7",
            "icon": "🤝",
            "title_suffix": "Volunteer",
            "achievement_text": "for dedicated volunteer service at"
        },
        "SPEAKER": {
            "primary": "#f59e0b",  # Amber
            "secondary": "#fcd34d",
            "icon": "🎤",
            "title_suffix": "Speaker",
            "achievement_text": "for delivering an impactful presentation at"
        },
        "ORGANIZER": {
            "primary": "#8b5cf6",  # Purple
            "secondary": "#c4b5fd",
            "icon": "👑",
            "title_suffix": "Organizer",
            "achievement_text": "for exceptional organization and leadership at"
        },
        "JUDGE": {
            "primary": "#dc2626",  # Red
            "secondary": "#fca5a5",
            "icon": "⚖️",
            "title_suffix": "Judge",
            "achievement_text": "for expert evaluation and judging at"
        },
        "MENTOR": {
            "primary": "#0891b2",  # Cyan
            "secondary": "#67e8f9",
            "icon": "🌟",
            "title_suffix": "Mentor",
            "achievement_text": "for guiding and mentoring participants at"
        }
    }
    
    @classmethod
    def get_role_template(cls, role: str) -> Dict[str, str]:
        """
        Get template configuration for a specific role
        
        Args:
            role: Role type (PARTICIPANT, VOLUNTEER, SPEAKER, etc.)
            
        Returns:
            Dictionary with role-specific styling and content
        """
        role = role.upper()
        return cls.ROLE_COLORS.get(role, cls.ROLE_COLORS["PARTICIPANT"])
    
    @classmethod
    def generate_certificate_title(cls, student_name: str, role: str) -> str:
        """
        Generate role-specific certificate title
        
        Example: "Certificate of Participation" or "Certificate of Speaker Excellence"
        """
        template = cls.get_role_template(role)
        if role.upper() in ["SPEAKER", "ORGANIZER", "MENTOR"]:
            return f"Certificate of {template['title_suffix']} Excellence"
        else:
            return f"Certificate of {template['title_suffix']}"
    
    @classmethod
    def generate_achievement_text(cls, role: str, event_title: str) -> str:
        """
        Generate role-specific achievement text for certificate body
        """
        template = cls.get_role_template(role)
        return f"{template['achievement_text']} {event_title}"
    
    @classmethod
    def generate_role_badge_html(cls, role: str) -> str:
        """
        Generate HTML badge for role display in certificate email
        """
        template = cls.get_role_template(role)
        return f"""
        <div style="display: inline-block; background: {template['primary']}; color: white; 
                    padding: 8px 16px; border-radius: 20px; font-size: 14px; 
                    font-weight: 600; margin: 10px 0;">
            {template['icon']} {template['title_suffix'].upper()}
        </div>
        """
    
    @classmethod
    def generate_role_description(cls, role: str) -> str:
        """
        Generate description of what the role entails
        """
        descriptions = {
            "PARTICIPANT": "Actively engaged in all event activities and contributed to the learning experience.",
            "VOLUNTEER": "Provided essential support and assistance to ensure the event's smooth operation.",
            "SPEAKER": "Shared expertise and knowledge through an engaging presentation, inspiring the audience.",
            "ORGANIZER": "Led the planning and execution of the event, ensuring its success through dedicated leadership.",
            "JUDGE": "Applied expert knowledge and fair judgment in evaluating participants and determining outcomes.",
            "MENTOR": "Provided valuable guidance, mentorship, and support to participants throughout the event."
        }
        return descriptions.get(role.upper(), descriptions["PARTICIPANT"])
    
    @classmethod
    def generate_stylized_certificate_email(
        cls,
        student_name: str,
        event_title: str,
        event_location: str,
        event_date: str,
        certificate_id: str,
        role: str = "PARTICIPANT",
        time_segment: Optional[str] = None
    ) -> str:
        """
        Generate complete HTML email with role-based certificate styling
        
        Args:
            student_name: Student's full name
            event_title: Event title
            event_location: Event location
            event_date: Event date string
            certificate_id: Unique certificate ID
            role: Participation role (PARTICIPANT, SPEAKER, etc.)
            time_segment: Optional time segment (e.g., "Day 1: 9AM-12PM")
            
        Returns:
            Complete HTML string for email
        """
        template = cls.get_role_template(role)
        cert_title = cls.generate_certificate_title(student_name, role)
        achievement = cls.generate_achievement_text(role, event_title)
        role_badge = cls.generate_role_badge_html(role)
        description = cls.generate_role_description(role)
        
        time_segment_html = f"""
        <p style="color: #64748b; margin: 5px 0;">
            <strong>Time Segment:</strong> {time_segment}
        </p>
        """ if time_segment else ""
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{cert_title} - {event_title}</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                     background: linear-gradient(135deg, {template['primary']} 0%, {template['secondary']} 100%); min-height: 100vh;">
            
            <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; 
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2); overflow: hidden;">
                
                <!-- Header with role-specific color -->
                <div style="background: linear-gradient(135deg, {template['primary']}, {template['secondary']}); 
                           padding: 40px 20px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        {template['icon']} {cert_title}
                    </h1>
                </div>
                
                <!-- Body -->
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <p style="font-size: 16px; color: #64748b; margin: 0 0 10px 0;">
                            This certifies that
                        </p>
                        <h2 style="font-size: 32px; color: {template['primary']}; margin: 10px 0; font-weight: 700;">
                            {student_name}
                        </h2>
                        <p style="font-size: 16px; color: #64748b; margin: 10px 0;">
                            has been recognized {achievement}
                        </p>
                        {role_badge}
                    </div>
                    
                    <!-- Event Details -->
                    <div style="background: #f8fafc; border-left: 4px solid {template['primary']}; 
                               padding: 20px; margin: 30px 0; border-radius: 8px;">
                        <h3 style="color: {template['primary']}; margin: 0 0 15px 0; font-size: 18px;">
                            Event Details
                        </h3>
                        <p style="color: #475569; margin: 5px 0;">
                            <strong>Event:</strong> {event_title}
                        </p>
                        <p style="color: #475569; margin: 5px 0;">
                            <strong>Location:</strong> {event_location}
                        </p>
                        <p style="color: #475569; margin: 5px 0;">
                            <strong>Date:</strong> {event_date}
                        </p>
                        {time_segment_html}
                        <p style="color: #64748b; margin: 15px 0 5px 0; font-size: 14px; font-style: italic;">
                            {description}
                        </p>
                    </div>
                    
                    <!-- Certificate ID -->
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; 
                               border-top: 2px dashed #e2e8f0;">
                        <p style="color: #94a3b8; font-size: 12px; margin: 5px 0;">
                            Certificate ID
                        </p>
                        <p style="color: {template['primary']}; font-family: 'Courier New', monospace; 
                                  font-size: 14px; font-weight: 600; margin: 5px 0;">
                            {certificate_id}
                        </p>
                        <p style="color: #94a3b8; font-size: 11px; margin: 15px 0 0 0;">
                            Verify at: unipass.example.com/verify/{certificate_id}
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                    <p style="color: #94a3b8; font-size: 12px; margin: 0;">
                        This is an automated email from UniPass Event Management System.
                    </p>
                    <p style="color: #cbd5e1; font-size: 11px; margin: 10px 0 0 0;">
                        © 2026 UniPass. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @classmethod
    def get_all_role_templates(cls) -> Dict[str, Dict]:
        """Get all available role templates"""
        return cls.ROLE_COLORS
    
    @classmethod
    def supports_role(cls, role: str) -> bool:
        """Check if a role has a specific template"""
        return role.upper() in cls.ROLE_COLORS
