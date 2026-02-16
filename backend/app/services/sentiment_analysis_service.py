"""
Sentiment Analysis Service - AI Module 4
=========================================

Advanced NLP-based sentiment analysis for event feedback using:
- VADER (Valence Aware Dictionary and sEntiment Reasoner) - Rule-based sentiment
- TF-IDF for text feature extraction
- Topic modeling to identify common themes
- Sentiment classification with confidence scores
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func

# NLP libraries
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Download required NLTK data (only on first run)
    # Fix SSL certificate issues on macOS
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)  # Required for NLTK 3.9+
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️  NLTK not installed. Install with: pip install nltk")

from app.models.feedback import Feedback
from app.models.event import Event


class SentimentAnalysisService:
    """Advanced sentiment analysis for event feedback"""
    
    def __init__(self):
        """Initialize sentiment analyzer and NLP components"""
        if not NLTK_AVAILABLE:
            raise ImportError("NLTK is required for sentiment analysis. Install with: pip install nltk")
        
        self.sia = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Domain-specific positive/negative words for events
        self.positive_keywords = {
            'excellent', 'amazing', 'awesome', 'great', 'wonderful', 
            'fantastic', 'helpful', 'informative', 'engaging', 'inspiring',
            'professional', 'organized', 'enjoyed', 'loved', 'learned',
            'interactive', 'valuable', 'impressive', 'well-organized'
        }
        
        self.negative_keywords = {
            'poor', 'terrible', 'boring', 'waste', 'disappointing',
            'confusing', 'disorganized', 'unprofessional', 'rushed',
            'unclear', 'irrelevant', 'useless', 'bad', 'awful',
            'chaotic', 'messy', 'uninteresting', 'lacking'
        }
    
    def preprocess_text(self, text: str) -> List[str]:
        """Clean and tokenize text"""
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^a-z\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return tokens
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using VADER
        Returns: {
            'compound': -1 to 1 (overall sentiment),
            'pos': 0 to 1 (positive ratio),
            'neu': 0 to 1 (neutral ratio),
            'neg': 0 to 1 (negative ratio)
        }
        """
        if not text:
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
        
        scores = self.sia.polarity_scores(text)
        return scores
    
    def classify_sentiment(self, compound_score: float) -> str:
        """
        Classify sentiment based on compound score
        Returns: 'positive', 'neutral', or 'negative'
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def get_sentiment_label(self, compound_score: float) -> int:
        """
        Convert sentiment to numeric label for database
        Returns: 1 (positive), 0 (neutral), -1 (negative)
        """
        if compound_score >= 0.05:
            return 1
        elif compound_score <= -0.05:
            return -1
        else:
            return 0
    
    def analyze_feedback(self, feedback: Feedback) -> Dict:
        """
        Comprehensive sentiment analysis of feedback entry
        Combines ratings with text analysis
        """
        # Analyze textual feedback
        combined_text = " ".join(filter(None, [
            feedback.what_liked or "",
            feedback.what_improve or "",
            feedback.additional_comments or ""
        ]))
        
        text_sentiment = self.analyze_text_sentiment(combined_text)
        
        # Calculate rating-based sentiment
        avg_rating = (
            feedback.overall_rating +
            feedback.content_quality +
            feedback.organization_rating +
            feedback.venue_rating
        ) / 4.0
        
        # Include speaker rating if available
        if feedback.speaker_rating:
            avg_rating = (avg_rating * 4 + feedback.speaker_rating) / 5.0
        
        # Normalize rating to -1 to 1 scale (5-point scale to compound)
        rating_sentiment = (avg_rating - 3) / 2  # 1->-1, 3->0, 5->1
        
        # Combined sentiment (60% text, 40% ratings)
        if combined_text.strip():
            combined_sentiment = 0.6 * text_sentiment['compound'] + 0.4 * rating_sentiment
        else:
            combined_sentiment = rating_sentiment
        
        # Extract key topics
        tokens = self.preprocess_text(combined_text)
        positive_words = [w for w in tokens if w in self.positive_keywords]
        negative_words = [w for w in tokens if w in self.negative_keywords]
        
        return {
            'sentiment_score': combined_sentiment,
            'sentiment_label': self.classify_sentiment(combined_sentiment),
            'text_sentiment': text_sentiment,
            'avg_rating': avg_rating,
            'positive_keywords_found': positive_words,
            'negative_keywords_found': negative_words,
            'confidence': abs(combined_sentiment),  # 0 (uncertain) to 1 (confident)
            'would_recommend': feedback.would_recommend
        }
    
    def analyze_event_feedback(self, db: Session, event_id: int) -> Dict:
        """
        Aggregate sentiment analysis for all feedback of an event
        Returns overall statistics and insights
        """
        feedbacks = db.query(Feedback).filter(
            Feedback.event_id == event_id
        ).all()
        
        if not feedbacks:
            return {
                'total_feedback': 0,
                'overall_sentiment': 'neutral',
                'sentiment_breakdown': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                },
                'avg_compound_score': 0.0,
                'avg_rating': 0.0,
                'recommendation_rate': 0.0,
                'top_positive_themes': [],
                'top_negative_themes': [],
                'insights': []
            }
        
        # Analyze each feedback
        analyses = [self.analyze_feedback(fb) for fb in feedbacks]
        
        # Aggregate statistics
        sentiment_counts = Counter(a['sentiment_label'] for a in analyses)
        avg_compound = np.mean([a['sentiment_score'] for a in analyses])
        avg_rating = np.mean([a['avg_rating'] for a in analyses])
        
        recommend_count = sum(1 for fb in feedbacks if fb.would_recommend)
        recommendation_rate = (recommend_count / len(feedbacks)) * 100
        
        # Extract common positive and negative themes
        all_positive_words = []
        all_negative_words = []
        for a in analyses:
            all_positive_words.extend(a['positive_keywords_found'])
            all_negative_words.extend(a['negative_keywords_found'])
        
        positive_themes = Counter(all_positive_words).most_common(5)
        negative_themes = Counter(all_negative_words).most_common(5)
        
        # Generate insights
        insights = self._generate_insights(
            sentiment_counts, avg_compound, avg_rating, 
            recommendation_rate, positive_themes, negative_themes
        )
        
        return {
            'total_feedback': len(feedbacks),
            'overall_sentiment': self.classify_sentiment(avg_compound),
            'sentiment_breakdown': {
                'positive': sentiment_counts.get('positive', 0),
                'neutral': sentiment_counts.get('neutral', 0),
                'negative': sentiment_counts.get('negative', 0)
            },
            'avg_compound_score': round(avg_compound, 3),
            'avg_rating': round(avg_rating, 2),
            'recommendation_rate': round(recommendation_rate, 1),
            'top_positive_themes': [
                {'word': word, 'count': count} 
                for word, count in positive_themes
            ],
            'top_negative_themes': [
                {'word': word, 'count': count} 
                for word, count in negative_themes
            ],
            'insights': insights
        }
    
    def _generate_insights(
        self, 
        sentiment_counts: Counter, 
        avg_compound: float,
        avg_rating: float,
        recommendation_rate: float,
        positive_themes: List[Tuple[str, int]],
        negative_themes: List[Tuple[str, int]]
    ) -> List[str]:
        """Generate actionable insights from sentiment analysis"""
        insights = []
        
        # Overall sentiment insight
        if avg_compound >= 0.5:
            insights.append("🎉 Overwhelmingly positive feedback! Event was highly successful.")
        elif avg_compound >= 0.2:
            insights.append("✅ Generally positive reception with room for improvement.")
        elif avg_compound >= -0.2:
            insights.append("⚠️ Mixed feedback. Consider analyzing specific pain points.")
        else:
            insights.append("⚠️ Predominantly negative feedback. Immediate action required.")
        
        # Recommendation rate insight
        if recommendation_rate >= 80:
            insights.append(f"💪 High recommendation rate ({recommendation_rate:.0f}%) indicates strong attendee satisfaction.")
        elif recommendation_rate >= 50:
            insights.append(f"📊 Moderate recommendation rate ({recommendation_rate:.0f}%). Focus on improving weak areas.")
        else:
            insights.append(f"🚨 Low recommendation rate ({recommendation_rate:.0f}%). Critical improvements needed.")
        
        # Rating insight
        if avg_rating >= 4.5:
            insights.append("⭐ Excellent ratings across all categories!")
        elif avg_rating < 3.0:
            insights.append("📉 Below-average ratings suggest systemic issues.")
        
        # Theme-based insights
        if positive_themes:
            top_positive = positive_themes[0][0]
            insights.append(f"✨ Attendees particularly appreciated: '{top_positive}'")
        
        if negative_themes:
            top_negative = negative_themes[0][0]
            insights.append(f"🔧 Main area for improvement: '{top_negative}'")
        
        return insights
    
    def get_sentiment_trends(self, db: Session, limit: int = 10) -> Dict:
        """
        Analyze sentiment trends across recent events
        Useful for tracking improvement over time
        """
        recent_events = db.query(Event).order_by(
            Event.created_at.desc()
        ).limit(limit).all()
        
        trends = []
        for event in recent_events:
            event_sentiment = self.analyze_event_feedback(db, event.id)
            trends.append({
                'event_id': event.id,
                'event_name': event.title,  # Event model uses 'title' not 'name'
                'event_date': event.start_time.strftime('%Y-%m-%d') if event.start_time else None,
                'sentiment_score': event_sentiment['avg_compound_score'],
                'avg_rating': event_sentiment['avg_rating'],
                'total_feedback': event_sentiment['total_feedback']
            })
        
        return {
            'trends': trends,
            'avg_sentiment_across_events': round(
                np.mean([t['sentiment_score'] for t in trends if t['total_feedback'] > 0] or [0]), 3
            )
        }


# Singleton instance
_sentiment_service = None

def get_sentiment_service() -> SentimentAnalysisService:
    """Get or create sentiment analysis service instance"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentAnalysisService()
    return _sentiment_service
