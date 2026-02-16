# 🎯 Scanner Quick Setup (Visual Guide)

## Step 1: Find Your IP Address
```
┌─────────────────────────────────────┐
│  Terminal                      × □  │
├─────────────────────────────────────┤
│ $ ifconfig | grep "inet " | grep -v 127.0.0.1
│ 
│ inet 192.168.1.10 netmask ...
│         ↑↑↑↑↑↑↑↑↑↑↑↑↑↑
│      YOUR IP ADDRESS
│
└─────────────────────────────────────┘
```

## Step 2: Configure Backend
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
python setup_mobile_scanner.py
```

**Output will show:**
```
✅ Detected IP Address: 192.168.1.10
📝 Configuring backend CORS...
   ✅ Backend .env updated
📝 Configuring frontend API URL...
   ✅ Frontend .env.local created
```

## Step 3: Start Backend
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 4: Start Frontend (New Terminal)
```bash
cd /Users/samarthpatil/Desktop/UniPass/frontend
npm run dev -- -H 0.0.0.0
```

**You should see:**
```
- Local:   http://localhost:3000
- Network: http://192.168.1.10:3000
```

## Step 5: Open on Phone

### On Your Phone:
```
┌────────────────────────────┐
│  Chrome                × ≡ │
├────────────────────────────┤
│  http://192.168.1.10:3000  │
│          /scanner-login     │
└────────────────────────────┘
```

## Visual Flow

### 📱 Phone View: Login
```
╔════════════════════════════╗
║                            ║
║         📷                 ║
║    UniPass Scanner         ║
║   Sign in to start scanning║
║                            ║
║  ┌────────────────────┐   ║
║  │ Username / Email   │   ║
║  └────────────────────┘   ║
║                            ║
║  ┌────────────────────┐   ║
║  │ Password           │   ║
║  └────────────────────┘   ║
║                            ║
║  ┌────────────────────┐   ║
║  │    Sign In         │   ║
║  └────────────────────┘   ║
║                            ║
╚════════════════════════════╝
```

### 📱 Phone View: Scanning
```
╔════════════════════════════╗
║ 📷 UniPass Scanner         ║
║ Scans: 5          [Logout] ║
╠════════════════════════════╣
║                            ║
║  ┌──────────────────┐     ║
║  │ ┌──┐        ┌──┐ │     ║
║  │ └──┘        └──┘ │     ║
║  │                  │     ║
║  │   CAMERA VIEW    │     ║
║  │                  │     ║
║  │ ┌──┐        ┌──┐ │     ║
║  │ └──┘        └──┘ │     ║
║  └──────────────────┘     ║
║                            ║
║  Point camera at QR code   ║
║                            ║
║  ┌────────────────────┐   ║
║  │ ⏸ Pause Scanning   │   ║
║  └────────────────────┘   ║
║                            ║
╚════════════════════════════╝
```

### 📱 Phone View: Success Result
```
╔════════════════════════════╗
║ 📷 UniPass Scanner         ║
║ Scans: 6          [Logout] ║
╠════════════════════════════╣
║  [Camera view continues]   ║
║                            ║
║  ┌────────────────────┐   ║
║  │ ✅  Attendance     │   ║
║  │     Marked!        │   ║
║  │                    │   ║
║  │  John Doe          │   ║
║  │  PRN123456         │   ║
║  │  Day 1 • Total: 1  │   ║
║  └────────────────────┘   ║
║    (auto-clears in 3s)    ║
╚════════════════════════════╝
```

## 🎯 Complete Command Reference

### One-Time Setup:
```bash
# Run this once:
cd /Users/samarthpatil/Desktop/UniPass/backend
python setup_mobile_scanner.py
```

### Every Time You Start:

**Terminal 1 (Backend):**
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd /Users/samarthpatil/Desktop/UniPass/frontend
npm run dev -- -H 0.0.0.0
```

**Phone Browser:**
```
http://YOUR_IP:3000/scanner-login
```

## 📋 Checklist

Before scanning, make sure:

- [ ] Both backend and frontend are running
- [ ] You can see "Network:" URL in frontend terminal
- [ ] Phone and computer are on SAME Wi-Fi
- [ ] You noted your IP address (not 127.0.0.1)
- [ ] Browser has camera permissions granted
- [ ] Good lighting in scanning area
- [ ] Scanner account credentials ready

## 🔍 Quick Tests

### Test 1: Backend API
**On phone browser:**
```
http://YOUR_IP:8000/docs
```
Should see "FastAPI - UniPass" docs page.

### Test 2: Frontend
**On phone browser:**
```
http://YOUR_IP:3000/scanner-login
```
Should see login page.

### Test 3: Camera
After login, camera should start automatically.
If not, check browser permissions:
- Chrome: Settings → Site settings → Camera
- Safari: Settings → Safari → Camera

## 🚨 Common Issues

### Issue: "Cannot connect"
**Fix:**
```bash
# Check firewall (macOS):
System Preferences → Security & Privacy → Firewall
→ Firewall Options → Unblock Node/Python
```

### Issue: "Camera not working"
**Fix:**
- Grant permissions when browser asks
- Use Chrome or Safari (not Firefox)
- Check Settings → Privacy → Camera

### Issue: "Invalid token"
**Fix:**
- Verify backend is running (check Terminal 1)
- Check .env.local has correct IP
- Try logging out and back in

## 💡 Pro Tips

### For Best Performance:
1. **Use 5GHz Wi-Fi** (faster than 2.4GHz)
2. **Keep phone charged** during events
3. **Adjust brightness** to medium-high
4. **Close other apps** to save battery
5. **Bookmark** scanner URL on home screen

### For Large Events:
1. Multiple scanners can work simultaneously
2. Each scanner sees their own scan count
3. All scans go to same database
4. Assign different scanners to different entrances

### Troubleshooting Live:
```bash
# Watch backend logs:
# Check Terminal 1 for errors

# Test API directly:
curl http://YOUR_IP:8000/
# Should return: {"message":"Welcome to UniPass API"}
```

## 📱 Mobile Browser Tips

### iOS (iPhone/iPad):
- Use Safari or Chrome
- Works in private mode
- Add to Home Screen for app-like experience

### Android:
- Use Chrome (recommended)
- Works in incognito mode
- Add to Home Screen for quick access

### Add to Home Screen:
1. Open scanner URL
2. Tap Share button
3. Select "Add to Home Screen"
4. Now opens like an app!

---

**You're ready to scan! 🎉**

If you have any issues, refer to [MOBILE_SCANNER_SETUP.md](MOBILE_SCANNER_SETUP.md) for detailed troubleshooting.
