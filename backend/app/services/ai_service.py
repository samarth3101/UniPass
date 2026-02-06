"""
AI Service for Backend (Python/FastAPI)
Provides AI-powered features for event management
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from functools import wraps
import time

# Initialize OpenAI client
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Rate limiting decorator
def rate_limit(calls_per_minute: int = 10):
    """Decorator to limit API calls"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator


class AIService:
    """AI Service for generating content and insights"""

    def __init__(self):
        self.client = client
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

    def is_enabled(self) -> bool:
        """Check if AI service is properly configured"""
        return self.client is not None

    @rate_limit(calls_per_minute=10)
    def _generate(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict:
        """Internal method to generate AI content"""
        if not self.is_enabled():
            return {
                "success": False,
                "content": "",
                "error": "AI service not configured. Please set OPENAI_API_KEY."
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            }
        except Exception as e:
            return {
                "success": False,
                "content": "",
                "error": str(e)
            }

    def generate_event_description(
        self,
        title: str,
        location: str,
        date: str,
        target_audience: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> Dict:
        """Generate compelling event description"""
        prompt = f"""Generate a compelling and professional event description for:
Event Title: {title}
Location: {location}
Date: {date}
{f'Target Audience: {target_audience}' if target_audience else ''}
{f'Event Type: {event_type}' if event_type else ''}

The description should be engaging, informative, and suitable for promoting the event.
Keep it between 150-300 words."""

        return self._generate(
            prompt=prompt,
            system_message="You are a professional event organizer helping to create engaging event descriptions.",
            max_tokens=500,
        )

    def generate_email_content(
        self,
        event_title: str,
        event_date: str,
        recipient_type: str,
        additional_info: Optional[str] = None,
    ) -> Dict:
        """Generate email content for event notifications"""
        prompts = {
            "registered": f"""Generate a professional confirmation email for someone who just registered for:
Event: {event_title}
Date: {event_date}
{f'Additional Info: {additional_info}' if additional_info else ''}

Include: Welcome message, event details, what to bring, and next steps.""",

            "attended": f"""Generate a thank you email for someone who attended:
Event: {event_title}
Date: {event_date}

Include: Gratitude, event recap, feedback request, and information about upcoming events.""",

            "reminder": f"""Generate a reminder email for an upcoming event:
Event: {event_title}
Date: {event_date}

Include: Friendly reminder, event details, what to expect, and contact information.""",
        }

        prompt = prompts.get(recipient_type, prompts["registered"])

        return self._generate(
            prompt=prompt,
            system_message="You are a professional email copywriter creating engaging emails for event management.",
            max_tokens=800,
        )

    def generate_attendance_insights(
        self,
        event_title: str,
        total_registrations: int,
        total_attended: int,
        attendance_rate: float,
    ) -> Dict:
        """Generate insights and recommendations based on attendance data"""
        prompt = f"""Analyze this event attendance data and provide insights:
Event: {event_title}
Total Registrations: {total_registrations}
Total Attended: {total_attended}
Attendance Rate: {attendance_rate}%

Provide:
1. Performance assessment (is this good/average/needs improvement?)
2. Possible reasons for the attendance rate
3. 3-5 actionable recommendations to improve attendance in future events
4. Any patterns or trends you notice

Keep the insights practical and specific."""

        return self._generate(
            prompt=prompt,
            system_message="You are a data analyst providing insights on event attendance patterns.",
            max_tokens=800,
        )

    def generate_certificate_content(
        self,
        student_name: str,
        event_title: str,
        event_date: str,
        event_type: str = "participation",
    ) -> Dict:
        """Generate personalized certificate content"""
        prompt = f"""Generate a formal and professional certificate text for:
Student Name: {student_name}
Event: {event_title}
Date: {event_date}
Certificate Type: {event_type}

Include: Formal acknowledgment, skills/topics covered, and a motivational closing statement.
Keep it professional and brief (2-3 sentences)."""

        return self._generate(
            prompt=prompt,
            system_message="You are a professional certificate designer creating formal recognition documents.",
            max_tokens=200,
        )

    def suggest_event_improvements(
        self,
        event_title: str,
        event_description: str,
        feedback_points: List[str],
    ) -> Dict:
        """Suggest improvements based on feedback"""
        feedback_text = "\n".join([f"- {point}" for point in feedback_points])
        
        prompt = f"""Analyze this event and its feedback to suggest improvements:
Event: {event_title}
Description: {event_description}

Feedback received:
{feedback_text}

Provide 5-7 specific, actionable improvements for future iterations of this event."""

        return self._generate(
            prompt=prompt,
            system_message="You are an event planning consultant providing actionable improvement suggestions.",
            max_tokens=800,
        )


# Create singleton instance
ai_service = AIService()


# Utility functions for easy access
def generate_event_description(**kwargs) -> Dict:
    """Convenience function to generate event description"""
    return ai_service.generate_event_description(**kwargs)


def generate_email_content(**kwargs) -> Dict:
    """Convenience function to generate email content"""
    return ai_service.generate_email_content(**kwargs)


def generate_attendance_insights(**kwargs) -> Dict:
    """Convenience function to generate attendance insights"""
    return ai_service.generate_attendance_insights(**kwargs)


def generate_certificate_content(**kwargs) -> Dict:
    """Convenience function to generate certificate content"""
    return ai_service.generate_certificate_content(**kwargs)
