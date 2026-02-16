"""
Cortex Lecture Intelligence Engine - AI Service Layer
Handles audio-to-text conversion, keyword extraction, and AI summarization
Powered by Google Gemini AI
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models.lecture_report import LectureReport
from app.models.event import Event
from app.models.user import User
from app.services.gemini_service import GeminiService


# Configuration
AUDIO_STORAGE_DIR = "backend/storage/audio"
ALLOWED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a"}
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class LectureAIService:
    """Service for AI-powered lecture analysis using Google Gemini"""
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_storage_dir()
        try:
            self.gemini = GeminiService()
        except Exception as e:
            print(f"⚠️ Warning: Gemini AI not initialized: {e}")
            print("   Make sure GEMINI_API_KEY is set in your .env file")
            self.gemini = None
    
    def _ensure_storage_dir(self):
        """Create audio storage directory if it doesn't exist"""
        os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)
    
    async def validate_audio_file(self, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate audio file format and size
        Returns: (is_valid, error_message)
        """
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_AUDIO_FORMATS:
            return False, f"Invalid file format. Allowed: {', '.join(ALLOWED_AUDIO_FORMATS)}"
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE_BYTES:
            return False, f"File size exceeds {MAX_FILE_SIZE_MB}MB limit"
        
        return True, ""
    
    async def save_audio_file(self, file: UploadFile, event_id: int) -> str:
        """
        Save uploaded audio file to storage
        Returns: saved filename
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(file.filename)[1].lower()
        saved_filename = f"event_{event_id}_{timestamp}{file_ext}"
        file_path = os.path.join(AUDIO_STORAGE_DIR, saved_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return saved_filename
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Convert audio to text using Google Gemini AI
        
        Uses Gemini 1.5 Pro multimodal capabilities for high-quality transcription
        """
        if self.gemini:
            try:
                return await self.gemini.transcribe_audio(audio_path)
            except Exception as e:
                print(f"⚠️ Gemini transcription failed: {e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Audio transcription failed: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=503,
                detail="Gemini AI is not configured. Please set GEMINI_API_KEY in .env file"
            )
    
    def extract_keywords(self, transcript: str, top_n: int = 15) -> List[str]:
        """
        Extract keywords from transcript using Google Gemini AI
        
        Uses context-aware AI analysis to identify the most important concepts
        """
        if self.gemini:
            try:
                return self.gemini.extract_keywords(transcript, top_n)
            except Exception as e:
                print(f"⚠️ Keyword extraction failed: {e}")
                # Fallback to basic extraction
                return self._fallback_keywords(transcript, top_n)
        else:
            return self._fallback_keywords(transcript, top_n)
    
    def _fallback_keywords(self, transcript: str, top_n: int) -> List[str]:
        """Fallback keyword extraction using simple frequency analysis"""
        from collections import Counter
        import re
        
        # Simple tokenization
        words = re.findall(r'\b[a-zA-Z]{4,}\b', transcript.lower())
        # Remove common stop words
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'your', 'their', 'what', 'when', 'where', 'which', 'about', 'would', 'there', 'could', 'should'}
        words = [w for w in words if w not in stop_words]
        
        # Count frequency
        common = Counter(words).most_common(top_n)
        return [word for word, _ in common]
    
    async def generate_structured_summary(
        self,
        event_title: str,
        event_description: str,
        keywords: List[str],
        transcript: str
    ) -> Dict:
        """
        Generate AI-powered structured summary using Google Gemini
        
        Provides comprehensive analysis with insights and actionable recommendations
        """
        if self.gemini:
            try:
                return await self.gemini.generate_structured_summary(
                    event_title=event_title,
                    event_description=event_description,
                    keywords=keywords,
                    transcript=transcript
                )
            except Exception as e:
                print(f"⚠️ Summary generation failed: {e}")
                return self._fallback_summary(event_title, keywords)
        else:
            return self._fallback_summary(event_title, keywords)
    
    def _fallback_summary(self, event_title: str, keywords: List[str]) -> Dict:
        """Fallback summary when Gemini is unavailable"""
        return {
            "event_overview": f"{event_title} - Analysis pending. Please ensure Gemini AI is configured.",
            "key_topics_discussed": keywords[:8],
            "important_quotes": ["AI analysis unavailable - configure GEMINI_API_KEY"],
            "technical_highlights": "Detailed analysis requires Gemini AI configuration",
            "audience_engagement_summary": "Analysis pending",
            "recommended_followup_actions": [
                "Configure Gemini API key to enable full analysis",
                "Review the transcript manually"
            ]
        }
    
    async def process_lecture_audio(
        self,
        file: UploadFile,
        event_id: int,
        user_id: int
    ) -> LectureReport:
        """
        Main processing pipeline for lecture audio analysis
        
        Steps:
        1. Validate and save audio file
        2. Transcribe audio to text
        3. Extract keywords
        4. Generate structured summary
        5. Save to database
        """
        # Validate event exists
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Validate file
        is_valid, error_msg = await self.validate_audio_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create initial report record
        report = LectureReport(
            event_id=event_id,
            audio_filename=file.filename,
            generated_by=user_id,
            status="processing"
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        try:
            # Save audio file
            saved_filename = await self.save_audio_file(file, event_id)
            report.audio_filename = saved_filename
            
            # Step 1: Transcribe audio
            audio_path = os.path.join(AUDIO_STORAGE_DIR, saved_filename)
            transcript = await self.transcribe_audio(audio_path)
            report.transcript = transcript
            
            # Step 2: Extract keywords
            keywords = self.extract_keywords(transcript)
            report.keywords = keywords
            
            # Step 3: Generate structured summary
            summary_dict = await self.generate_structured_summary(
                event_title=event.title,
                event_description=event.description or "",
                keywords=keywords,
                transcript=transcript
            )
            report.summary = json.dumps(summary_dict, indent=2)
            
            # Mark as completed
            report.status = "completed"
            
        except Exception as e:
            # Handle processing errors
            report.status = "failed"
            report.error_message = str(e)
            
        finally:
            self.db.commit()
            self.db.refresh(report)
        
        return report
    
    def get_lecture_report(self, event_id: int) -> Optional[LectureReport]:
        """Retrieve lecture report for an event"""
        return self.db.query(LectureReport).filter(
            LectureReport.event_id == event_id
        ).order_by(LectureReport.generated_at.desc()).first()
    
    def get_all_reports(self, limit: int = 50) -> List[LectureReport]:
        """Get all lecture reports (admin view)"""
        return self.db.query(LectureReport).order_by(
            LectureReport.generated_at.desc()
        ).limit(limit).all()
