# UniPass AI Modules - Complete Implementation Guide

**Status**: ✅ **PRODUCTION READY**  
**Last Updated**: February 17, 2026

---

## 📋 Overview

UniPass implements **2 core AI/ML modules** for intelligent event management:

1. **Attendance Anomaly Detection** - Fraud prevention using unsupervised ML
2. **Feedback Sentiment Analysis** - NLP-powered sentiment extraction and insights

These modules provide actionable intelligence for event organizers without requiring manual data labeling.

---

## 🎯 Module 1: Attendance Anomaly Detection

### Purpose
Detect suspicious attendance patterns using machine learning to prevent fraud such as:
- Proxy attendance (friend scanning for absent student)
- Screenshot abuse (sharing QR codes)
- Admin misuse (unauthorized manual overrides)
- Unrealistic check-in patterns

### Technology Stack
- **Algorithm**: Isolation Forest (unsupervised learning)
- **Library**: scikit-learn 1.4.1+
- **Features**: 8 engineered features from attendance data
- **Contamination Rate**: 5% (configurable)

### Features Analyzed

| Feature | Description | Fraud Indicator |
|---------|-------------|-----------------|
| `time_after_event_start` | Minutes between event start and scan | Too early/late scans |
| `time_since_last_scan` | Time since student's previous scan | Rapid successive scans |
| `student_attendance_rate` | Historical attendance percentage | Unusually low participation |
| `is_admin_override` | Manual admin correction flag | Potential misuse |
| `scan_hour` | Hour of day (0-23) | Unusual times (3 AM, etc.) |
| `is_weekend` | Weekend scan indicator | Weekend anomalies |
| `scans_in_last_hour` | Recent scan frequency | Batch scanning |
| `event_attendance_ratio` | Actual/capacity ratio | Over-capacity |

### API Endpoints

#### 1. Train Anomaly Detector
```http
POST /anomaly/train
Authorization: Bearer {token}
```

**Response:**
```json
{
  "status": "trained",
  "samples_used": 1243,
  "anomalies_detected": 62,
  "anomaly_rate": 4.99,
  "training_time_seconds": 2.34
}
```

#### 2. Detect Anomalies
```http
GET /anomaly/detect?event_id={event_id}
Authorization: Bearer {token}
```

**Parameters:**
- `event_id` (optional): Detect for specific event, or all if omitted

**Response:**
```json
{
  "total_checked": 450,
  "anomalies_found": 12,
  "anomaly_rate": 2.67,
  "anomalies": [
    {
      "attendance_id": 789,
      "student_prn": "PRN12345",
      "event_id": 56,
      "severity": "HIGH",
      "anomaly_score": -0.73,
      "explanation": "Scan occurred at unusual hour (3 AM); Multiple rapid scans detected",
      "scan_time": "2026-02-15T03:42:11Z",
      "scan_source": "MANUAL"
    }
  ]
}
```

#### 3. Get Anomaly Summary
```http
GET /anomaly/summary
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_anomalies": 45,
  "high_severity": 12,
  "medium_severity": 33,
  "by_scan_source": {
    "SCANNER": 15,
    "MANUAL": 30
  },
  "requires_review": 12
}
```

### Usage Example

```python
# Train the model (run weekly or after significant data changes)
POST /anomaly/train

# Detect anomalies for specific event
GET /anomaly/detect?event_id=56

# Get overall summary
GET /anomaly/summary
```

### Severity Classification
- **HIGH** (score < -0.5): Immediate review required
- **MEDIUM** (score < 0): Monitor for patterns

### Implementation Files
- **Service**: `backend/app/services/anomaly_detection_service.py`
- **Routes**: `backend/app/routes/anomaly.py`
- **Test**: `backend/test_anomaly_phase2.py`
- **Model Storage**: `backend/models/anomaly_detector.pkl`

---

## 🎯 Module 2: Feedback Sentiment Analysis

### Purpose
Automatically analyze post-event feedback using Natural Language Processing to:
- Classify sentiment as positive, neutral, or negative
- Extract key themes from textual feedback
- Generate actionable insights for organizers
- Track sentiment trends across events

### Technology Stack
- **Algorithm**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **Library**: NLTK 3.8.1+
- **Techniques**: 
  - TF-IDF for keyword extraction
  - Lemmatization and stopword removal
  - Domain-specific keyword matching
  - Confidence scoring

### Features

1. **Text Preprocessing**
   - Tokenization
   - Stopword removal
   - Lemmatization
   - Special character cleaning

2. **Sentiment Scoring**
   - Compound score: -1 (very negative) to +1 (very positive)
   - Component scores: positive, neutral, negative ratios
   - Confidence level based on score magnitude

3. **Theme Extraction**
   - Identifies positive keywords (excellent, amazing, helpful, etc.)
   - Identifies negative keywords (terrible, boring, waste, etc.)
   - Counts frequency for trend analysis

4. **Multi-Source Analysis**
   - Combines text sentiment (60% weight)
   - Combines numeric ratings (40% weight)
   - Recommendation flag consideration

### API Endpoints

#### 1. Event Sentiment Analysis
```http
GET /feedback/event/{event_id}/sentiment-analysis
Authorization: Bearer {token}
```

**Response:**
```json
{
  "event_id": 56,
  "event_name": "Tech Talk: AI in Modern Applications",
  "analysis": {
    "total_feedback": 45,
    "overall_sentiment": "positive",
    "sentiment_breakdown": {
      "positive": 32,
      "neutral": 10,
      "negative": 3
    },
    "avg_compound_score": 0.612,
    "avg_rating": 4.3,
    "recommendation_rate": 84.4,
    "top_positive_themes": [
      {"word": "informative", "count": 15},
      {"word": "engaging", "count": 12},
      {"word": "excellent", "count": 9}
    ],
    "top_negative_themes": [
      {"word": "rushed", "count": 3},
      {"word": "unclear", "count": 2}
    ],
    "insights": [
      "🎉 Overwhelmingly positive feedback! Event was highly successful.",
      "💪 High recommendation rate (84%) indicates strong attendee satisfaction.",
      "✨ Attendees particularly appreciated: 'informative'",
      "🔧 Main area for improvement: 'rushed'"
    ]
  }
}
```

#### 2. Sentiment Trends
```http
GET /feedback/sentiment-trends?limit=10
Authorization: Bearer {token}
```

**Parameters:**
- `limit` (optional): Number of recent events to analyze (default: 10, max: 50)

**Response:**
```json
{
  "trends": [
    {
      "event_id": 58,
      "event_name": "Workshop: Web Development",
      "event_date": "2026-02-15",
      "sentiment_score": 0.723,
      "avg_rating": 4.5,
      "total_feedback": 32
    },
    {
      "event_id": 56,
      "event_name": "Tech Talk: AI Applications",
      "event_date": "2026-02-10",
      "sentiment_score": 0.612,
      "avg_rating": 4.3,
      "total_feedback": 45
    }
  ],
  "avg_sentiment_across_events": 0.668
}
```

#### 3. Single Feedback Analysis
```http
POST /feedback/analyze-single
Authorization: Bearer {token}

{
  "feedback_id": 123
}
```

**Response:**
```json
{
  "feedback_id": 123,
  "event_id": 56,
  "student_prn": "PRN12345",
  "analysis": {
    "sentiment_score": 0.742,
    "sentiment_label": "positive",
    "text_sentiment": {
      "compound": 0.8516,
      "pos": 0.385,
      "neu": 0.615,
      "neg": 0.0
    },
    "avg_rating": 4.5,
    "positive_keywords_found": ["excellent", "informative", "engaging"],
    "negative_keywords_found": [],
    "confidence": 0.742,
    "would_recommend": true
  }
}
```

### Sentiment Classification

| Compound Score | Classification | Numeric Label |
|----------------|----------------|---------------|
| ≥ 0.05 | Positive | 1 |
| -0.05 to 0.05 | Neutral | 0 |
| ≤ -0.05 | Negative | -1 |

### Automatic Integration

The sentiment analysis automatically runs when feedback is submitted:

```python
# In /feedback/submit endpoint
sentiment_service = get_sentiment_service()
analysis = sentiment_service.analyze_feedback(new_feedback)
new_feedback.sentiment_score = sentiment_service.get_sentiment_label(
    analysis['sentiment_score']
)
```

If NLTK is unavailable, it falls back to simple rule-based sentiment using average ratings.

### Implementation Files
- **Service**: `backend/app/services/sentiment_analysis_service.py`
- **Routes**: `backend/app/routes/feedback.py` (enhanced)
- **Test**: `backend/test_sentiment_analysis.py`

---

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**
- `scikit-learn==1.4.1.post1` - Anomaly detection
- `nltk==3.8.1` - Sentiment analysis
- `numpy==1.26.4` - Numerical operations
- `pandas==2.2.1` - Data manipulation
- `joblib==1.3.2` - Model persistence

### 2. Download NLTK Data

**Option 1: Run the setup script (Recommended for macOS SSL issues)**
```bash
cd backend
python3 setup_nltk.py
```

**Option 2: Manual download**
```python
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

**If you encounter SSL certificate errors on macOS:**
The service automatically handles SSL certificate verification issues. The `setup_nltk.py` script disables SSL verification temporarily to download required data.

### 3. Train Anomaly Detector

```bash
# Using test script
python test_anomaly_phase2.py

# Or via API
POST /anomaly/train
```

### 4. Test Sentiment Analysis

```bash
python test_sentiment_analysis.py
```

---

## 🧪 Testing

### Anomaly Detection Tests

```bash
cd backend
python test_anomaly_phase2.py
```

**Tests:**
- ✅ Service initialization
- ✅ Feature engineering
- ✅ Model training
- ✅ Anomaly detection
- ✅ Explanation generation

### Sentiment Analysis Tests

```bash
cd backend
python test_sentiment_analysis.py
```

**Tests:**
- ✅ NLTK installation check
- ✅ Service initialization
- ✅ Text preprocessing
- ✅ Sample text analysis
- ✅ Real feedback analysis
- ✅ Event-level aggregation
- ✅ Sentiment trends

---

## 📊 Performance Metrics

### Anomaly Detection
- **Training Time**: ~2-5 seconds for 1000 records
- **Detection Speed**: ~100ms for 500 attendances
- **Memory Usage**: ~50MB (model + data)
- **Accuracy**: Depends on contamination tuning (default 5%)

### Sentiment Analysis
- **Analysis Speed**: ~10ms per feedback entry
- **Batch Processing**: ~500ms for 50 feedbacks
- **Memory Usage**: ~30MB (NLTK data)
- **Accuracy**: VADER achieves ~0.96 F1-score on social media text

---

## 🔒 Security & Permissions

Both modules require **organizer-level permissions**:
- Only organizers/admins can access AI endpoints
- Fraud detection results are logged to audit trail
- Student-specific data is anonymized in aggregations

---

## 📈 Future Enhancements (Removed from Scope)

The following modules were considered but **NOT IMPLEMENTED**:

❌ **Attendance Prediction Model**
- Reason: Requires extensive historical data (1+ years)
- Alternative: Use descriptive analytics from Phase 1

❌ **Student Interest Clustering**
- Reason: Privacy concerns with student profiling
- Alternative: Manual event categorization by organizers

---

## 🛠️ Troubleshooting

### Issue: "NLTK data not found"
**Solution:**
```python
import nltk
nltk.download('all')  # Download all required data
```

### Issue: "Sentiment analysis service unavailable"
**Solution:**
```bash
pip install nltk
python -c "import nltk; nltk.download('vader_lexicon')"
```

### Issue: "Model not trained" for anomaly detection
**Solution:**
```bash
POST /anomaly/train  # Train the model first
```

### Issue: Low anomaly detection accuracy
**Solution:**
- Adjust `contamination` parameter (default: 0.05)
- Retrain model with more recent data
- Review feature engineering for domain-specific patterns

---

## 📚 Resources

### Documentation
- **Anomaly Detection**: `UniPass_DOCS/AI_PHASE_2_ANOMALY_DETECTION.md`
- **Analytics**: `UniPass_DOCS/AI_PHASE_1_DESCRIPTIVE_ANALYTICS.md`
- **AI Journey**: `UniPass_DOCS/UNIPASS_AI_JOURNEY.md`

### Scientific References
- **Isolation Forest**: Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008)
- **VADER**: Hutto, C., & Gilbert, E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis

### Libraries
- [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [NLTK VADER](https://www.nltk.org/howto/sentiment.html)

---

## ✅ Production Checklist

- [x] Dependencies installed (`requirements.txt`)
- [x] NLTK data downloaded
- [x] Anomaly detector trained
- [x] Test scripts pass successfully
- [x] API endpoints secured with authentication
- [x] Error handling with graceful fallbacks
- [x] Audit logging for fraud detection
- [x] Performance optimized (batch processing)
- [x] Documentation complete

---

## 🎯 Quick Reference

### Anomaly Detection
```bash
# Train
POST /anomaly/train

# Detect
GET /anomaly/detect?event_id=56

# Summary
GET /anomaly/summary
```

### Sentiment Analysis
```bash
# Event sentiment
GET /feedback/event/56/sentiment-analysis

# Trends
GET /feedback/sentiment-trends?limit=10

# Single feedback
POST /feedback/analyze-single
```

---

**End of AI Modules Implementation Guide**  
For support, see `UNIPASS_SYSTEM_OVERVIEW.md` or contact the development team.
