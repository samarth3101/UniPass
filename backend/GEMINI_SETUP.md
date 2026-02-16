# Google Gemini AI Setup Guide

## Overview
The Lecture Intelligence Engine uses Google Gemini 1.5 Pro for audio transcription, keyword extraction, and lecture analysis.

## Getting Your API Key

1. **Visit Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account (use your student account for Gemini Pro benefits)
3. **Create API Key**: Click "Create API Key" or "Get API Key"
4. **Copy the key**: Save it securely - you won't see it again!

## Configuration

### 1. Add to Environment File

Create or edit `/backend/.env` and add:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `google-generativeai` package.

### 3. Verify Installation

Run the backend server and check for Gemini initialization:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

You should see:
```
✅ Gemini AI initialized successfully
```

If you see a warning:
```
⚠️ Warning: Gemini AI not initialized
```
Check that your API key is correctly set in `.env`

## Features Enabled

Once configured, the Lecture Intelligence Engine provides:

- 🎙️ **Audio Transcription**: Converts lecture audio to text using Gemini's multimodal capabilities
- 🔑 **Smart Keyword Extraction**: Context-aware identification of important concepts
- 📊 **Structured Summaries**: AI-generated insights with:
  - Event overview
  - Key topics discussed
  - Important quotes
  - Technical highlights
  - Audience engagement analysis
  - Recommended follow-up actions
- 💭 **Sentiment Analysis**: Tone, energy, and clarity assessment

## Supported Audio Formats

- MP3
- WAV
- M4A (AAC)

Maximum file size: 100MB

## API Rate Limits

Gemini Free Tier:
- 60 requests per minute
- 1,500 requests per day

Gemini Pro (Student):
- Higher rate limits (check Google AI Studio for current limits)
- Priority access

## Troubleshooting

### "Gemini AI is not configured"
- Ensure `GEMINI_API_KEY` is in your `.env` file
- Restart the backend server after adding the key
- Verify the key is valid at https://makersuite.google.com

### "Audio transcription failed"
- Check audio file format (must be MP3, WAV, or M4A)
- Verify file size is under 100MB
- Ensure Gemini API has quota remaining

### Import Error: "No module named 'google.generativeai'"
```bash
pip install google-generativeai
```

## Testing

Upload a lecture audio file through the Cortex → Lecture Intelligence page:

1. Select an event
2. Upload audio file (MP3, WAV, or M4A)
3. Click "Process Lecture"
4. Wait for transcription and analysis
5. View structured report with keywords and insights

## Security Best Practices

- ✅ Never commit `.env` file to git
- ✅ Use environment variables in production
- ✅ Rotate API keys periodically
- ✅ Restrict API key permissions if possible
- ❌ Don't share API keys in code or documentation
- ❌ Don't hardcode keys in application code

## Cost Considerations

Gemini API pricing (as of 2024):
- Free tier: Generous limits for testing
- Student accounts: Often include enhanced free access
- Pay-as-you-go: Check current pricing at https://ai.google.dev/pricing

## Additional Resources

- [Google AI Documentation](https://ai.google.dev/docs)
- [Gemini API Reference](https://ai.google.dev/api/python/google/generativeai)
- [Google AI Studio](https://makersuite.google.com)

---

**Need Help?** Check the backend logs for detailed error messages when processing lectures.
