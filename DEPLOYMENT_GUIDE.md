# 🚀 UniPass Free Deployment Guide

## Overview
This guide will help you deploy UniPass **100% FREE** using:
- **Backend**: Render.com (Free tier)
- **Frontend**: Vercel (Free tier - Best for Next.js)
- **Database**: SQLite (already configured) or PostgreSQL (Render free tier)

---

## 🎯 Prerequisites

1. **GitHub Account** (to connect with Render & Vercel)
2. **Push your code to GitHub** (if not already done)
3. **Google Gemini API Key** (you already have: `AIzaSyCZUi4eCzQH3R6X4F22ErUhjqv0jXKZLZ0`)
4. **Gmail Account** (for SMTP emails)

---

## 📦 Step 1: Prepare Your Code for Deployment

### A. Create Backend Deployment Files

Create `/backend/render.yaml`:
```yaml
services:
  - type: web
    name: unipass-backend
    env: python
    buildCommand: pip install -r requirements.txt && python setup_nltk.py
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        value: sqlite:///./unipass.db
      - key: SECRET_KEY
        generateValue: true
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 720
```

### B. Create `setup_nltk.py` in backend folder:
```python
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
```

### C. Create Frontend Environment File

Create `/frontend/.env.production`:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

---

## 🖥️ Step 2: Deploy Backend to Render

### Option A: Auto-Deploy from GitHub (Recommended)

1. **Sign up**: Go to [render.com](https://render.com) and sign up with GitHub
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**: Select your UniPass repository
4. **Configure**:
   - **Name**: `unipass-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main` or `master`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python setup_nltk.py
     ```
   - **Start Command**: 
     ```
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`

5. **Environment Variables** (Add these in Render dashboard):
   ```
   DATABASE_URL=sqlite:///./unipass.db
   SECRET_KEY=(click "Generate" for random secure key)
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=720
   FRONTEND_URL=https://your-app.vercel.app
   CORS_ORIGINS=https://your-app.vercel.app
   GEMINI_API_KEY=AIzaSyCZUi4eCzQH3R6X4F22ErUhjqv0jXKZLZ0
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-gmail-app-password
   EMAIL_FROM=noreply@unipass.com
   EMAIL_FROM_NAME=UniPass
   HOST=0.0.0.0
   PORT=10000
   ```

6. **Deploy**: Click "Create Web Service"
7. **Note Your URL**: After deployment, copy your backend URL (e.g., `https://unipass-backend.onrender.com`)

### Option B: PostgreSQL Database (Optional - for production)

If you want PostgreSQL instead of SQLite:
1. In Render, go to "New +" → "PostgreSQL"
2. Name it `unipass-db`, select Free tier
3. Copy the "Internal Database URL"
4. Update your backend's `DATABASE_URL` environment variable with this URL

---

## 🌐 Step 3: Deploy Frontend to Vercel

1. **Sign up**: Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. **Import Project**: Click "Add New" → "Project"
3. **Select Repository**: Choose your UniPass repository
4. **Configure**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://unipass-backend.onrender.com
   ```
   (Replace with your actual Render backend URL)

6. **Deploy**: Click "Deploy"
7. **Get Your URL**: Vercel will give you a URL like `https://unipass.vercel.app`

8. **Update Backend CORS**: Go back to Render → Your backend → Environment
   - Update `FRONTEND_URL` to your Vercel URL
   - Update `CORS_ORIGINS` to your Vercel URL
   - Click "Save Changes" (backend will auto-redeploy)

---

## 📧 Step 4: Setup Gmail SMTP (Free Email Service)

1. **Enable 2-Step Verification**:
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Create App Password**:
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Other (Custom name)"
   - Name it "UniPass"
   - Copy the 16-character password

3. **Update Render Environment Variables**:
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx (the app password)
   ```

---

## ✅ Step 5: Initialize Database & Create Admin

Once backend is deployed:

1. **SSH into Render** (from Render dashboard → Shell):
   ```bash
   python create_admin.py
   ```

2. **Or use the API** - Make a POST request:
   ```bash
   curl -X POST https://unipass-backend.onrender.com/api/admin/setup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@college.edu",
       "password": "SecurePassword123!",
       "full_name": "Admin User"
     }'
   ```

---

## 🎪 Step 6: Test Your Deployment

1. **Visit your frontend**: `https://unipass.vercel.app`
2. **Check backend health**: `https://unipass-backend.onrender.com/health`
3. **Login as admin**: Use the admin credentials you created
4. **Create a test event** and verify all features work

---

## 🔧 Important Notes for Free Tier

### Render Free Tier Limitations:
- ⚠️ **Spins down after 15 minutes of inactivity** (first request takes 30-60 seconds to wake up)
- 750 hours/month free (enough for 24/7 if you only have 1 service)
- 512 MB RAM
- For demos, wake up the backend before showing to judges!

### Vercel Free Tier:
- ✅ No sleep/spin-down
- ✅ Unlimited bandwidth for personal projects
- ✅ Automatic HTTPS
- ✅ Global CDN

### To Keep Backend Awake (Optional):
Use a free uptime monitor like [UptimeRobot](https://uptimerobot.com):
- Create free account
- Add new monitor (HTTP)
- URL: `https://your-backend.onrender.com/health`
- Check interval: Every 5 minutes
- This keeps your backend warm!

---

## 🚨 Pre-Demo Checklist

Before showing to judges:

1. ✅ Visit backend URL to wake it up (if using Render free tier)
2. ✅ Test login functionality
3. ✅ Create a sample event
4. ✅ Test QR scanning
5. ✅ Test certificate generation
6. ✅ Verify AI features work (Gemini API)
7. ✅ Check email delivery

---

## 🎯 Custom Domain (Optional - Still Free!)

### For Vercel:
1. Go to Project Settings → Domains
2. Add your domain (can use free domains from [Freenom](https://www.freenom.com))

### For Render:
1. Go to Settings → Custom Domain
2. Add your domain

---

## 🐛 Troubleshooting

### Backend won't start:
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is in backend folder

### Frontend can't connect to backend:
- Check `NEXT_PUBLIC_API_URL` in Vercel
- Check CORS settings in Render backend
- Verify backend is running (visit /health endpoint)

### Database errors:
- SQLite is included, no setup needed
- If using PostgreSQL, verify DATABASE_URL format

### NLTK errors:
- Ensure `setup_nltk.py` runs during build
- Check it downloads: `vader_lexicon`, `punkt`, `stopwords`

---

## 📊 Estimated Deployment Time

- **Backend Setup**: 10-15 minutes
- **Frontend Setup**: 5 minutes
- **Testing**: 10 minutes
- **Total**: ~30 minutes ⚡

---

## 🎉 You're Live!

Your UniPass is now deployed and accessible worldwide for **FREE**! 

**Share these URLs with judges:**
- 🌐 Frontend: `https://unipass.vercel.app`
- 🔧 Backend API: `https://unipass-backend.onrender.com`
- 📖 API Docs: `https://unipass-backend.onrender.com/docs`

---

## 💡 Pro Tips for Judges

1. **Demo Account**: Create a demo admin account for judges
2. **Sample Data**: Use `create_sample_lecture_reports.py` to populate sample data
3. **Wake Up**: Visit the site 1 minute before demo to wake up Render backend
4. **Backup**: Take screenshots of working features in case of connectivity issues
5. **Documentation**: Share the `README.md` and system overview docs

---

## 🔄 Continuous Deployment

Both Render and Vercel support auto-deployment:
- Push to GitHub → Automatic deployment ✨
- No manual updates needed!

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

Good luck with your judges! 🚀
