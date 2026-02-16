"""
QR Code Service - PS1 Feature 3
Generate QR codes for certificate verification links and general use

Part of PS1 Feature 3: Verifiable Certificate & Transcript System
"""

import qrcode
import io
import base64
from PIL import Image
from typing import Optional
import os


def generate_qr_code(data: str) -> str:
    """Legacy function - generates base64 encoded QR code"""
    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def generate_certificate_qr_code(
    certificate_id: str,
    base_url: Optional[str] = None,
    size: int = 300,
    return_base64: bool = False
) -> io.BytesIO:
    """
    Generate QR code for certificate verification (PS1 Feature 3)
    
    Args:
        certificate_id: Unique certificate ID (e.g., CERT-ABC123)
        base_url: Base URL for verification (defaults to environment variable)
        size: Size of QR code in pixels (default: 300x300)
        return_base64: If True, returns base64 string instead of BytesIO
    
    Returns:
        BytesIO or str: QR code image buffer (PNG format) or base64 string
    
    Example:
        >>> qr_buffer = generate_certificate_qr_code("CERT-ABC123")
        >>> # Save to file or attach to email
        >>> with open("certificate_qr.png", "wb") as f:
        >>>     f.write(qr_buffer.getvalue())
    """
    # Get base URL from environment or use default
    if not base_url:
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Construct verification URL
    verification_url = f"{base_url}/verify?cert={certificate_id}"
    
    # Create QR code with high error correction
    qr = qrcode.QRCode(
        version=1,  # Auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to requested size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    if return_base64:
        return base64.b64encode(buffer.getvalue()).decode()
    
    return buffer


def generate_transcript_qr_code(
    student_prn: str,
    base_url: Optional[str] = None,
    size: int = 200,
    return_base64: bool = False
) -> io.BytesIO:
    """
    Generate QR code for student transcript verification (PS1 Feature 3)
    
    Args:
        student_prn: Student PRN
        base_url: Base URL for transcript (defaults to environment variable)
        size: Size of QR code in pixels
        return_base64: If True, returns base64 string instead of BytesIO
    
    Returns:
        BytesIO or str: QR code image buffer (PNG format) or base64 string
    """
    if not base_url:
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # Construct transcript URL
    transcript_url = f"{base_url}/ps1/transcript/{student_prn}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    
    qr.add_data(transcript_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    if return_base64:
        return base64.b64encode(buffer.getvalue()).decode()
    
    return buffer


def embed_qr_in_certificate_pdf(
    certificate_id: str,
    pdf_canvas,
    x_position: float,
    y_position: float,
    qr_size: float = 100,
    base_url: Optional[str] = None
):
    """
    Embed QR code directly into a PDF canvas (for ReportLab)
    PS1 Feature 3: Add verification QR to certificates
    
    Args:
        certificate_id: Certificate ID to encode
        pdf_canvas: ReportLab canvas object
        x_position: X coordinate for QR code placement
        y_position: Y coordinate for QR code placement
        qr_size: Size of QR code in points
        base_url: Base URL for verification link
    
    Example:
        >>> from reportlab.pdfgen import canvas
        >>> c = canvas.Canvas("certificate.pdf")
        >>> embed_qr_in_certificate_pdf("CERT-123", c, 400, 100, qr_size=80)
        >>> c.save()
    """
    from reportlab.lib.utils import ImageReader
    
    # Generate QR code at 3x size for better quality
    qr_buffer = generate_certificate_qr_code(
        certificate_id, 
        base_url=base_url,
        size=int(qr_size * 3)
    )
    
    # Draw on PDF
    pdf_canvas.drawImage(
        ImageReader(qr_buffer),
        x_position,
        y_position,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask='auto'
    )
    
    # Add verification text below QR code
    pdf_canvas.setFont("Helvetica", 8)
    pdf_canvas.drawCentredString(
        x_position + (qr_size / 2),
        y_position - 12,
        "Scan to verify authenticity"
    )
    
    # Add certificate ID below
    pdf_canvas.setFont("Helvetica", 7)
    pdf_canvas.drawCentredString(
        x_position + (qr_size / 2),
        y_position - 24,
        certificate_id
    )