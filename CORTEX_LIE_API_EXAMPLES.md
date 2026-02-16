# Cortex Lecture Intelligence Engine (LIE)
## API Examples, LLM Prompts, and Sample Responses

---

## 📋 **Table of Contents**

1. [API Endpoints](#api-endpoints)
2. [LLM Prompt Template](#llm-prompt-template)
3. [Example API Responses](#example-api-responses)
4. [Integration Examples](#integration-examples)
5. [Production Configuration](#production-configuration)

---

## 🚀 **API Endpoints**

### 1. Upload Lecture Audio

**Endpoint:** `POST /ai/lecture/upload/{event_id}`

**Authentication:** Required (Admin or Event Organizer)

**Request:**
```bash
curl -X POST "http://localhost:8000/ai/lecture/upload/42" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@lecture_recording.mp3"
```

**Response:**
```json
{
  "report_id": 123,
  "event_id": 42,
  "status": "completed",
  "message": "Audio uploaded and processing initiated",
  "filename": "event_42_20260217_143052.mp3"
}
```

**Supported Formats:** MP3, WAV, M4A  
**Max File Size:** 100MB

---

### 2. Get Lecture Report

**Endpoint:** `GET /ai/lecture/report/{event_id}`

**Authentication:** Required (Admin or Event Organizer)

**Request:**
```bash
curl -X GET "http://localhost:8000/ai/lecture/report/42" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:** See [Full Response Example](#full-report-response) below.

---

### 3. Get All Reports

**Endpoint:** `GET /ai/lecture/reports/all?limit=50`

**Authentication:** Required (Admin or Organizer)

**Request:**
```bash
curl -X GET "http://localhost:8000/ai/lecture/reports/all?limit=20" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**
```json
{
  "total": 2,
  "reports": [
    {
      "report_id": 123,
      "event_id": 42,
      "event_title": "Advanced Machine Learning Workshop",
      "status": "completed",
      "generated_at": "2026-02-17T14:30:52.123456Z",
      "keywords_count": 15,
      "has_transcript": true
    },
    {
      "report_id": 122,
      "event_id": 41,
      "event_title": "Web Development Bootcamp",
      "status": "completed",
      "generated_at": "2026-02-16T10:15:30.654321Z",
      "keywords_count": 12,
      "has_transcript": true
    }
  ]
}
```

---

### 4. Delete Report

**Endpoint:** `DELETE /ai/lecture/report/{report_id}`

**Authentication:** Required (Admin or Event Organizer)

**Request:**
```bash
curl -X DELETE "http://localhost:8000/ai/lecture/report/123" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Response:**
```json
{
  "message": "Report deleted successfully"
}
```

---

## 🤖 **LLM Prompt Template**

### Recommended Model: GPT-4 or GPT-3.5-turbo

```python
LECTURE_SUMMARY_PROMPT = """
You are an expert educational content analyst. Analyze the following lecture transcript and generate a comprehensive structured report.

**Event Context:**
- Event Title: {event_title}
- Event Description: {event_description}
- Detected Keywords: {keywords_list}

**Lecture Transcript:**
{transcript}

**Instructions:**
1. Thoroughly analyze the transcript
2. Identify key educational moments
3. Extract actionable insights
4. Generate a structured JSON response

**Required JSON Format:**
{{
  "event_overview": "Provide a concise 2-3 sentence summary of the entire lecture",
  "key_topics_discussed": [
    "Topic 1",
    "Topic 2",
    "Topic 3",
    "..."
  ],
  "important_quotes": [
    "Memorable quote 1",
    "Memorable quote 2",
    "Memorable quote 3"
  ],
  "technical_highlights": "Detailed paragraph about technical concepts, frameworks, tools, or methodologies discussed",
  "audience_engagement_summary": "Analysis of Q&A sessions, audience participation, interaction patterns, and engagement levels",
  "recommended_followup_actions": [
    "Actionable item 1",
    "Actionable item 2",
    "Actionable item 3",
    "..."
  ]
}}

**Guidelines:**
- Be specific and concrete
- Use educational terminology
- Focus on actionable insights
- Maintain professional tone
- Ensure JSON is valid and properly formatted

Generate the structured report now:
"""
```

### Usage with OpenAI:

```python
import openai

def generate_lecture_summary(event_title, event_description, keywords, transcript):
    prompt = LECTURE_SUMMARY_PROMPT.format(
        event_title=event_title,
        event_description=event_description,
        keywords_list=", ".join(keywords),
        transcript=transcript[:4000]  # Truncate if needed
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert educational content analyst specializing in lecture summarization."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    return response.choices[0].message.content
```

---

## 📊 **Example API Responses**

### Full Report Response

```json
{
  "report_id": 123,
  "event": {
    "id": 42,
    "title": "Advanced Machine Learning Workshop",
    "description": "Deep dive into neural networks and practical applications",
    "start_time": "2026-02-17T10:00:00Z"
  },
  "status": "completed",
  "error_message": null,
  "transcript": "Welcome everyone to today's workshop on Advanced Machine Learning techniques. Today we'll be covering neural networks, deep learning architectures, and practical applications in computer vision. Let's start with the fundamentals of backpropagation and gradient descent. These concepts are crucial for understanding how neural networks learn from data. We'll also discuss regularization techniques like dropout and batch normalization that help prevent overfitting. Finally, we'll explore transfer learning and how pre-trained models can accelerate your development process.",
  "keywords": [
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
  ],
  "summary": {
    "event_overview": "This comprehensive workshop provided an in-depth exploration of advanced machine learning techniques, focusing on neural network fundamentals, practical implementation strategies, and modern optimization approaches. Participants gained hands-on experience with regularization methods and transfer learning applications.",
    "key_topics_discussed": [
      "Neural Network Architectures",
      "Backpropagation Algorithm",
      "Gradient Descent Optimization",
      "Regularization Techniques",
      "Dropout and Batch Normalization",
      "Transfer Learning",
      "Computer Vision Applications",
      "Overfitting Prevention"
    ],
    "important_quotes": [
      "Understanding the fundamentals is crucial before diving into advanced topics",
      "Transfer learning can significantly accelerate your development process",
      "Always validate your models with proper test data to avoid overfitting"
    ],
    "technical_highlights": "The workshop covered essential neural network concepts including backpropagation mechanics and gradient descent optimization algorithms. Special emphasis was placed on regularization techniques such as dropout (randomly disabling neurons during training) and batch normalization (normalizing layer inputs). The session concluded with practical transfer learning demonstrations, showcasing how pre-trained models like ResNet and VGG can be fine-tuned for custom computer vision tasks, significantly reducing training time and data requirements.",
    "audience_engagement_summary": "High level of audience engagement was observed throughout the session. Multiple participants asked clarifying questions during the backpropagation explanation, indicating strong interest in understanding the mathematical foundations. The Q&A session extended beyond scheduled time due to numerous practical implementation questions. Several attendees requested code repositories and additional learning resources for self-paced study.",
    "recommended_followup_actions": [
      "Share Jupyter notebooks and code examples from the workshop",
      "Create supplementary video tutorials for complex topics like backpropagation",
      "Schedule follow-up session on advanced architectures (CNNs, RNNs, Transformers)",
      "Provide curated reading list including research papers and documentation",
      "Create practice assignments with real-world datasets",
      "Set up a dedicated Slack/Discord channel for ongoing Q&A",
      "Organize hackathon focused on applying learned techniques to real problems"
    ]
  },
  "audio_filename": "event_42_20260217_143052.mp3",
  "generated_at": "2026-02-17T14:30:52.123456Z",
  "generated_by": {
    "id": 5,
    "email": "organizer@university.edu",
    "full_name": "Dr. Jane Smith"
  }
}
```

---

## 🔧 **Integration Examples**

### Python Client Example

```python
import requests

class LectureAIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def upload_audio(self, event_id: int, audio_file_path: str):
        """Upload audio file for processing"""
        with open(audio_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/ai/lecture/upload/{event_id}",
                headers=self.headers,
                files=files
            )
        return response.json()
    
    def get_report(self, event_id: int):
        """Retrieve lecture report"""
        response = requests.get(
            f"{self.base_url}/ai/lecture/report/{event_id}",
            headers=self.headers
        )
        return response.json()
    
    def get_all_reports(self, limit: int = 50):
        """Get all reports"""
        response = requests.get(
            f"{self.base_url}/ai/lecture/reports/all?limit={limit}",
            headers=self.headers
        )
        return response.json()

# Usage
client = LectureAIClient("http://localhost:8000", "your_jwt_token")

# Upload audio
result = client.upload_audio(
    event_id=42,
    audio_file_path="recordings/ml_workshop.mp3"
)
print(f"Upload status: {result['status']}")

# Get report
report = client.get_report(event_id=42)
print(f"Event: {report['event']['title']}")
print(f"Keywords: {', '.join(report['keywords'])}")
```

### JavaScript/TypeScript Example

```typescript
class LectureAIClient {
  constructor(
    private baseUrl: string,
    private token: string
  ) {}

  async uploadAudio(eventId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${this.baseUrl}/ai/lecture/upload/${eventId}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`
        },
        body: formData
      }
    );

    return await response.json();
  }

  async getReport(eventId: number) {
    const response = await fetch(
      `${this.baseUrl}/ai/lecture/report/${eventId}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`
        }
      }
    );

    return await response.json();
  }
}

// Usage
const client = new LectureAIClient(
  'http://localhost:8000',
  'your_jwt_token'
);

// Upload and get report
const fileInput = document.querySelector('input[type="file"]');
const file = fileInput.files[0];

const uploadResult = await client.uploadAudio(42, file);
console.log('Upload result:', uploadResult);

const report = await client.getReport(42);
console.log('Report:', report);
```

---

## ⚙️ **Production Configuration**

### Environment Variables

Add to your `.env` file:

```bash
# OpenAI API (for production transcription and summarization)
OPENAI_API_KEY=sk-your-api-key-here

# Audio Processing Configuration
MAX_AUDIO_FILE_SIZE_MB=100
AUDIO_STORAGE_PATH=/var/unipass/storage/audio

# Processing Timeout (seconds)
AUDIO_PROCESSING_TIMEOUT=600

# Background Processing Threshold (minutes)
ASYNC_PROCESSING_THRESHOLD=45
```

### Enable OpenAI Whisper Transcription

Update `backend/app/services/lecture_ai_service.py`:

```python
import openai
from app.core.config import settings

async def transcribe_audio(self, audio_path: str) -> str:
    """Convert audio to text using OpenAI Whisper API"""
    openai.api_key = settings.OPENAI_API_KEY
    
    with open(audio_path, "rb") as audio_file:
        transcript = await openai.Audio.atranscribe(
            model="whisper-1",
            file=audio_file
        )
    
    return transcript["text"]
```

### Enable GPT-4 Summarization

```python
async def generate_structured_summary(
    self,
    event_title: str,
    event_description: str,
    keywords: List[str],
    transcript: str
) -> Dict:
    """Generate AI summary using GPT-4"""
    openai.api_key = settings.OPENAI_API_KEY
    
    prompt = LECTURE_SUMMARY_PROMPT.format(
        event_title=event_title,
        event_description=event_description,
        keywords_list=", ".join(keywords),
        transcript=transcript[:4000]
    )
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert educational content analyst."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    summary_text = response.choices[0].message.content
    return json.loads(summary_text)
```

### Background Processing for Long Audio

For audio files longer than 45 minutes, implement background task processing:

```python
from fastapi import BackgroundTasks

@router.post("/upload/{event_id}")
async def upload_lecture_audio(
    event_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    # Check audio duration
    duration = await get_audio_duration(file)
    
    if duration > 45 * 60:  # 45 minutes in seconds
        # Process in background
        background_tasks.add_task(
            process_audio_background,
            event_id,
            user_id,
            file
        )
        return {
            "message": "Audio queued for background processing",
            "status": "queued"
        }
    else:
        # Process immediately
        service = LectureAIService(db)
        report = await service.process_lecture_audio(event_id, current_user.id, file)
        return {"report_id": report.id, "status": report.status}
```

---

## 📈 **Performance Tips**

1. **Optimize Transcription:**
   - Use Whisper API for best accuracy
   - Consider local Whisper for cost savings
   - Pre-process audio (noise reduction, normalization)

2. **Keyword Extraction:**
   - KeyBERT for semantic keywords
   - TF-IDF for quick extraction
   - Combine both for best results

3. **Caching:**
   - Cache transcripts to avoid reprocessing
   - Store intermediate results

4. **Error Handling:**
   - Implement retry logic for API failures
   - Log all processing steps
   - Provide clear error messages

---

## 🎯 **Next Steps**

To move from MVP to production:

1. **Install Dependencies:**
   ```bash
   pip install openai keybert
   ```

2. **Set API Key:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Run Migration:**
   ```bash
   cd backend
   python migrate_lecture_ai.py
   ```

4. **Test Upload:**
   - Start backend: `cd backend && uvicorn app.main:app --reload`
   - Navigate to: `http://localhost:3000/cortex/lecture-ai`
   - Upload test audio file

5. **Monitor Logs:**
   - Check processing status
   - Verify report generation
   - Test error scenarios

---

**Documentation Version:** 1.0  
**Last Updated:** February 17, 2026  
**Author:** Cortex Development Team
