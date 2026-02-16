"""
Gemini AI Integration Service
Handles audio transcription and content analysis using Google Gemini API
"""

import os
import json
import google.generativeai as genai
from typing import Dict, List, Optional
from pathlib import Path


class GeminiService:
    """Service for Google Gemini AI integration"""
    
    def __init__(self):
        """Initialize Gemini AI with API key from environment"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file"
            )
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 1.5 Pro for best results
        # Gemini 1.5 Pro supports audio, video, and multimodal input
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Gemini's multimodal capabilities
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            # Upload the audio file to Gemini
            audio_file = genai.upload_file(path=audio_path)
            
            # Wait for file processing
            import time
            while audio_file.state.name == "PROCESSING":
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                raise ValueError("Audio file processing failed")
            
            # Create transcription prompt
            prompt = """
            Please transcribe this audio recording completely and accurately.
            Provide the full transcript of everything said in the audio.
            Format it as continuous text with proper paragraphs.
            Do not add any commentary, just provide the pure transcription.
            """
            
            # Generate transcription
            response = self.model.generate_content([audio_file, prompt])
            
            # Clean up uploaded file
            genai.delete_file(audio_file.name)
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini transcription failed: {str(e)}")
    
    def extract_keywords(self, transcript: str, top_n: int = 15) -> List[str]:
        """
        Extract key topics and keywords from transcript using Gemini
        
        Args:
            transcript: The transcribed text
            top_n: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        try:
            prompt = f"""
            Analyze the following lecture transcript and extract the {top_n} most important 
            keywords and key phrases. Focus on technical terms, main concepts, and important topics.
            
            Transcript:
            {transcript}
            
            Return ONLY a JSON array of strings with the keywords, nothing else.
            Example format: ["keyword1", "keyword2", "keyword3"]
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            keywords_text = response.text.strip()
            # Remove markdown code blocks if present
            if keywords_text.startswith("```json"):
                keywords_text = keywords_text.split("```json")[1].split("```")[0].strip()
            elif keywords_text.startswith("```"):
                keywords_text = keywords_text.split("```")[1].split("```")[0].strip()
            
            keywords = json.loads(keywords_text)
            return keywords[:top_n]
            
        except Exception as e:
            # Fallback: simple keyword extraction
            print(f"Gemini keyword extraction failed: {e}")
            # Return basic word frequency analysis
            words = transcript.lower().split()
            from collections import Counter
            common = Counter(words).most_common(top_n)
            return [word for word, _ in common if len(word) > 4]
    
    async def generate_structured_summary(
        self,
        event_title: str,
        event_description: str,
        keywords: List[str],
        transcript: str
    ) -> Dict:
        """
        Generate comprehensive structured analysis using Gemini
        
        Args:
            event_title: Title of the event
            event_description: Description of the event
            keywords: Extracted keywords
            transcript: Full transcript
            
        Returns:
            Structured summary dictionary
        """
        try:
            prompt = f"""
            Analyze the following lecture transcript and generate a comprehensive structured report.
            
            Event Title: {event_title}
            Event Description: {event_description}
            Key Topics Identified: {', '.join(keywords)}
            
            Full Transcript:
            {transcript}
            
            Generate a detailed JSON response with the following structure:
            {{
                "event_overview": "Brief 2-3 sentence summary of the lecture",
                "key_topics_discussed": ["array", "of", "main", "topics"],
                "important_quotes": ["array", "of", "2-3", "notable", "quotes"],
                "technical_highlights": "Detailed description of technical concepts covered",
                "audience_engagement_summary": "Analysis of engagement, Q&A, participation",
                "recommended_followup_actions": ["array", "of", "suggested", "next", "steps"]
            }}
            
            Provide ONLY the JSON object, no additional text or markdown formatting.
            Make the analysis thorough and insightful based on the actual transcript content.
            """
            
            response = self.model.generate_content(prompt)
            summary_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if summary_text.startswith("```json"):
                summary_text = summary_text.split("```json")[1].split("```")[0].strip()
            elif summary_text.startswith("```"):
                summary_text = summary_text.split("```")[1].split("```")[0].strip()
            
            # Parse and return JSON
            summary_dict = json.loads(summary_text)
            return summary_dict
            
        except Exception as e:
            # Fallback summary
            print(f"Gemini summary generation failed: {e}")
            return {
                "event_overview": f"{event_title} - Lecture analysis in progress",
                "key_topics_discussed": keywords[:8],
                "important_quotes": ["Analysis pending - please retry"],
                "technical_highlights": "Detailed analysis will be available shortly",
                "audience_engagement_summary": "Engagement analysis in progress",
                "recommended_followup_actions": [
                    "Review the full transcript",
                    "Follow up with participants"
                ]
            }
    
    def analyze_sentiment(self, transcript: str) -> Dict:
        """
        Analyze sentiment and tone of the lecture
        
        Args:
            transcript: The transcribed text
            
        Returns:
            Sentiment analysis results
        """
        try:
            prompt = f"""
            Analyze the sentiment and tone of this lecture transcript.
            
            Transcript:
            {transcript}
            
            Provide a JSON response with:
            {{
                "overall_sentiment": "positive/neutral/negative",
                "tone": "description of speaking tone",
                "energy_level": "high/medium/low",
                "clarity": "high/medium/low"
            }}
            
            Return ONLY the JSON object.
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean JSON
            if result_text.startswith("```json"):
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif result_text.startswith("```"):
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return {
                "overall_sentiment": "neutral",
                "tone": "conversational",
                "energy_level": "medium",
                "clarity": "medium"
            }
