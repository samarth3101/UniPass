from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    event_id: int
    student_prn: str
    overall_rating: int = Field(..., ge=1, le=5, description="Overall rating 1-5")
    content_quality: int = Field(..., ge=1, le=5, description="Content quality 1-5")
    organization_rating: int = Field(..., ge=1, le=5, description="Organization rating 1-5")
    venue_rating: int = Field(..., ge=1, le=5, description="Venue rating 1-5")
    speaker_rating: Optional[int] = Field(None, ge=1, le=5, description="Speaker rating 1-5")
    what_liked: Optional[str] = Field(None, max_length=1000)
    what_improve: Optional[str] = Field(None, max_length=1000)
    additional_comments: Optional[str] = Field(None, max_length=1000)
    would_recommend: bool = True

    @validator('overall_rating', 'content_quality', 'organization_rating', 'venue_rating', 'speaker_rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class FeedbackResponse(BaseModel):
    id: int
    event_id: int
    student_prn: str
    student_name: Optional[str] = None
    overall_rating: int
    content_quality: int
    organization_rating: int
    venue_rating: int
    speaker_rating: Optional[int]
    what_liked: Optional[str]
    what_improve: Optional[str]
    additional_comments: Optional[str]
    would_recommend: bool
    sentiment_score: Optional[int]
    ai_summary: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    event_id: int
    total_responses: int
    avg_overall_rating: float
    avg_content_quality: float
    avg_organization: float
    avg_venue: float
    avg_speaker: Optional[float] = None
    recommendation_percentage: float
    sentiment_positive: int
    sentiment_neutral: int
    sentiment_negative: int


class SendFeedbackRequest(BaseModel):
    event_id: int
    custom_message: Optional[str] = None
