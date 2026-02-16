"""
Cortex Lecture Intelligence Engine - AI Service Layer
Handles audio-to-text conversion, keyword extraction, and AI summarization
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


# Configuration
AUDIO_STORAGE_DIR = "backend/storage/audio"
ALLOWED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a"}
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class LectureAIService:
    """Service for AI-powered lecture analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_storage_dir()
    
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
        Convert audio to text using speech-to-text
        
        PRODUCTION NOTE:
        - Option 1: Use OpenAI Whisper API (requires OPENAI_API_KEY)
        - Option 2: Use local Whisper model (slower but free)
        
        For MVP, returns simulated transcript
        """
        # TODO: Implement actual transcription
        # Example with OpenAI Whisper API:
        # import openai
        # with open(audio_path, "rb") as audio_file:
        #     transcript = openai.Audio.transcribe("whisper-1", audio_file)
        #     return transcript["text"]
        
        # MVP Simulation
        return """
        [SIMULATED TRANSCRIPT]
        Welcome everyone to today's workshop on Advanced Machine Learning techniques.
        Today we'll be covering neural networks, deep learning architectures, and practical
        applications in computer vision. Let's start with the fundamentals of backpropagation
        and gradient descent. These concepts are crucial for understanding how neural networks
        learn from data. We'll also discuss regularization techniques like dropout and batch
        normalization that help prevent overfitting. Finally, we'll explore transfer learning
        and how pre-trained models can accelerate your development process.
        """
    
    def extract_keywords(self, transcript: str, top_n: int = 15) -> List[str]:
        """
        Extract keywords from transcript
        
        PRODUCTION NOTE:
        - Option 1: Use KeyBERT for context-aware extraction
        - Option 2: Use TF-IDF for simple frequency-based extraction
        
        For MVP, returns simulated keywords
        """
        # TODO: Implement actual keyword extraction
        # Example with KeyBERT:
        # from keybert import KeyBERT
        # kw_model = KeyBERT()
        # keywords = kw_model.extract_keywords(transcript, top_n=top_n)
        # return [kw[0] for kw in keywords]
        
        # MVP Simulation
        return [
            "machine learning",
            "neural networks",
            "deep learning",
            "computer vision",
            "backpropagation",
            "gradient descent",
            "dropout",
            "batch normalization",
            "overfitting",
            "transfer learning",
            "pre-trained models",
            "regularization",
            "optimization",
            "architecture",
            "algorithms"
        ]
    
    async def generate_structured_summary(
        self,
        event_title: str,
        event_description: str,
        keywords: List[str],
        transcript: str
    ) -> Dict:
        """
        Generate AI-powered structured summary using LLM
        
        PRODUCTION NOTE:
        - Use OpenAI GPT-4 or GPT-3.5-turbo
        - Requires OPENAI_API_KEY in environment
        
        For MVP, returns structured template
        """
        # TODO: Implement actual LLM-based summarization
        # Example prompt structure:
        prompt = f"""
        Analyze the following lecture transcript and generate a structured report.
        
        Event: {event_title}
        Description: {event_description}
        Key Topics: {', '.join(keywords)}
        
        Transcript:
        {transcript[:2000]}  # Truncate if too long
        
        Generate a JSON response with:
        - event_overview: Brief 2-3 sentence summary
        - key_topics_discussed: Array of main topics
        - important_quotes: Array of notable statements
        - technical_highlights: Technical concepts covered
        - audience_engagement_summary: Engagement indicators
        - recommended_followup_actions: Suggested next steps
        """
        
        # TODO: Call LLM API
        # import openai
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     temperature=0.7
        # )
        # return json.loads(response.choices[0].message.content)
        
        # MVP Simulation
        return {
            "event_overview": f"{event_title} covered fundamental and advanced concepts in the field, with strong emphasis on practical applications and hands-on learning.",
            "key_topics_discussed": keywords[:8],
            "important_quotes": [
                "Understanding the fundamentals is crucial before diving into advanced topics",
                "Transfer learning can significantly accelerate your development process",
                "Always validate your models with proper test data"
            ],
            "technical_highlights": "Deep dive into neural network architectures, backpropagation algorithms, regularization techniques including dropout and batch normalization, and practical transfer learning applications.",
            "audience_engagement_summary": "High engagement observed with multiple questions during Q&A session. Participants showed strong interest in practical implementation details.",
            "recommended_followup_actions": [
                "Share code examples and notebooks used in the workshop",
                "Schedule follow-up session on advanced topics",
                "Create practice assignments for hands-on learning",
                "Provide additional resources for self-study"
            ]
        }
    
    async def process_lecture_audio(
        self,
        event_id: int,
        user_id: int,
        file: UploadFile
    ) -> LectureReport:
        """
        Main pipeline: Process audio file and generate lecture report
        
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
