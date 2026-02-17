# ⚡ Quick Deploy Checklist

## TL;DR - Deploy in 10 Minutes

### 1️⃣ Backend on Render (5 min)
1. Go to [render.com](https://render.com) → Sign up with GitHub
2. New Web Service → Select UniPass repo
3. Settings:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt && python setup_nltk.py`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (see below)
4. Deploy → Copy your backend URL

### 2️⃣ Frontend on Vercel (3 min)
1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Import UniPass repo
3. Root Directory: `frontend`
4. Add env var: `NEXT_PUBLIC_API_URL=<your-render-url>`
5. Deploy → Copy your frontend URL

### 3️⃣ Update CORS (1 min)
Go back to Render → Environment → Add:
```
FRONTEND_URL=<your-vercel-url>
CORS_ORIGINS=<your-vercel-url>
```

### 4️⃣ Create Admin (1 min)
Visit: `https://your-vercel-url` and register first user as admin

---

## 🔑 Required Environment Variables for Render

### Minimum (Required):
```
SECRET_KEY=[Auto-generate in Render]
DATABASE_URL=sqlite:///./unipass.db
FRONTEND_URL=https://your-app.vercel.app
CORS_ORIGINS=https://your-app.vercel.app
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
```

### Full (Recommended):
```
# Auto-generated
SECRET_KEY=[Click Generate]

# Database
DATABASE_URL=sqlite:///./unipass.db

# CORS
FRONTEND_URL=https://your-app.vercel.app
CORS_ORIGINS=https://your-app.vercel.app

# Auth
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720

# AI (Optional - for Lecture Intelligence)
GEMINI_API_KEY=AIzaSyCZUi4eCzQH3R6X4F22ErUhjqv0jXKZLZ0

# Email (Optional - for certificate emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
EMAIL_FROM=noreply@unipass.com
EMAIL_FROM_NAME=UniPass

# Server
HOST=0.0.0.0
PORT=10000
```

---

## 🎯 Pre-Demo Tips

1. **Wake up backend**: Visit backend URL 1 min before demo (Render free tier sleeps)
2. **Use UptimeRobot**: Free service to ping your backend every 5 min (keeps it awake)
3. **Create demo data**: Run `python create_sample_lecture_reports.py` before demo
4. **Test everything**: Login, create event, scan QR, generate certificate

---

## 🆓 Cost Breakdown

- ✅ Render Backend: **FREE** (750 hrs/month)
- ✅ Vercel Frontend: **FREE** (unlimited for personal)
- ✅ Database (SQLite): **FREE** (included)
- ✅ Gmail SMTP: **FREE** (built-in)
- ✅ Gemini AI: **FREE** (60 requests/min)

**Total Monthly Cost: $0.00** 💰

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **UptimeRobot**: https://uptimerobot.com (keep backend awake)
- **Full Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions

---

## 🐛 Quick Fixes

**Backend won't start?**
- Check Render logs
- Verify environment variables are set

**Frontend blank page?**
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_URL` in Vercel

**CORS error?**
- Update `CORS_ORIGINS` in Render backend
- Must match your Vercel URL exactly

**Database issues?**
- Use SQLite (no setup needed)
- Render includes persistent storage for free

---

**You're ready to impress the judges! 🚀**
