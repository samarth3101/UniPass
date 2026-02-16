# 📱 Mobile Scanner Setup Guide

## Overview
This guide will help you set up UniPass Scanner for mobile access. Scanners can use their phones to login and scan QR codes displayed on student screens.

---

## 🚀 Quick Setup Guide

### Step 1: Find Your Computer's IP Address

#### On macOS:
```bash
# Open Terminal and run:
ifconfig | grep "inet " | grep -v 127.0.0.1
```

#### On Windows:
```bash
# Open Command Prompt and run:
ipconfig
# Look for "IPv4 Address" under your active network adapter
```

#### On Linux:
```bash
hostname -I
```

**Example IP:** `192.168.1.10` (yours will be different)

---

### Step 2: Configure Backend for Network Access

1. **Open Backend `.env` file:**
   ```bash
   cd /Users/samarthpatil/Desktop/UniPass/backend
   nano .env
   ```

2. **Update CORS_ORIGINS to allow all origins (for testing):**
   ```env
   # Add or update these lines:
   CORS_ORIGINS=*
   FRONTEND_URL=http://localhost:3000
   ```

3. **Alternative: Specify your exact IP:**
   ```env
   CORS_ORIGINS=http://192.168.1.10:3000,http://localhost:3000
   ```

4. **Run Backend on all interfaces:**
   ```bash
   cd /Users/samarthpatil/Desktop/UniPass/backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### Step 3: Configure Frontend for Network Access

1. **Create/Update Frontend `.env.local` file:**
   ```bash
   cd /Users/samarthpatil/Desktop/UniPass/frontend
   nano .env.local
   ```

2. **Add your computer's IP address:**
   ```env
   NEXT_PUBLIC_API_URL=http://192.168.1.10:8000
   ```
   Replace `192.168.1.10` with YOUR actual IP address from Step 1.

3. **Run Frontend:**
   ```bash
   cd /Users/samarthpatil/Desktop/UniPass/frontend
   npm run dev -- -H 0.0.0.0
   ```

---

### Step 4: Access Scanner on Mobile

1. **Make sure your phone is on the SAME Wi-Fi network as your computer**

2. **On your phone's browser, navigate to:**
   ```
   http://192.168.1.10:3000/scanner-login
   ```
   (Replace `192.168.1.10` with your computer's IP)

3. **Login with scanner credentials:**
   - Username: Your scanner username
   - Password: Your scanner password

4. **Start scanning!**
   - After login, you'll see the camera interface
   - Point your phone at QR codes on student screens
   - Automatic detection and verification

---

## 🎯 Scanner Workflow

```
1. Open mobile browser
   ↓
2. Go to: http://YOUR_IP:3000/scanner-login
   ↓
3. Login with credentials
   ↓
4. Camera automatically starts
   ↓
5. Point at QR code
   ↓
6. Automatic scan & verification
   ↓
7. See success/error message (3 sec)
   ↓
8. Continue scanning next student
```

---

## 🔧 Complete Setup Commands

### Terminal 1 - Backend:
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Frontend:
```bash
cd /Users/samarthpatil/Desktop/UniPass/frontend
npm run dev -- -H 0.0.0.0
```

---

## 📱 Scanner Features

### ✅ What Scanners Can Do:
- Simple login interface
- Automatic QR code detection
- Real-time scan feedback
- Scan counter
- Pause/Resume scanning
- Auto-clear results (3 seconds)
- Mobile-optimized UI
- Dark theme for low light
- Visual scan corners
- Logout option

### 🎨 Scanner UI Features:
- **Minimalist Design**: No clutter, just scanning
- **Large Scan Area**: Full-screen QR detection
- **Visual Feedback**: Green for success, yellow for already scanned, red for errors
- **Scan Counter**: Track number of scans in session
- **Pause Button**: Temporarily stop scanning
- **Auto-dismiss**: Results clear after 3 seconds
- **Mobile-First**: Optimized for phone screens

---

## 🛠️ Troubleshooting

### Problem: Can't connect from phone

**Solution 1: Check Firewall**
```bash
# macOS - Allow port 3000 and 8000:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/node
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/local/bin/node
```

**Solution 2: Verify CORS**
- Make sure `CORS_ORIGINS=*` in backend `.env`
- Restart backend after changing `.env`

**Solution 3: Check Network**
- Phone and computer must be on same Wi-Fi
- Try pinging your computer's IP from another device

### Problem: Camera not working

**Solution:**
- Grant camera permissions when browser asks
- Use Chrome or Safari (best QR support)
- Ensure good lighting
- Hold phone steady

### Problem: "Invalid token" errors

**Solution:**
- Make sure backend is running
- Check `NEXT_PUBLIC_API_URL` points to correct IP
- Verify scanner has logged in successfully

---

## 🔐 Security Notes

### For Production Deployment:

1. **Use HTTPS:**
   ```env
   NEXT_PUBLIC_API_URL=https://your-domain.com
   ```

2. **Restrict CORS:**
   ```env
   CORS_ORIGINS=https://your-domain.com
   ```

3. **Use Strong Passwords:**
   - Scanner accounts should have unique passwords
   - Use role: `ORGANIZER` or create custom `SCANNER` role

4. **Network Security:**
   - Use VPN if scanning over public networks
   - Consider SSL certificate for production
   - Use environment-specific configs

---

## 🎓 Scanner Account Setup

### Create a Scanner User:

```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
python create_admin.py
```

**Then update the role:**
```python
# In Python shell or create_scanner.py:
from app.db.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()

scanner = User(
    username="scanner1",
    email="scanner1@example.com",
    role=UserRole.ORGANIZER,  # or ADMIN
    password="hashed_password_here"
)

db.add(scanner)
db.commit()
```

Or use existing organizer/admin accounts.

---

## 📊 Testing the Setup

### Test Checklist:
- [ ] Backend running on `0.0.0.0:8000`
- [ ] Frontend running on `0.0.0.0:3000`
- [ ] Can access `http://YOUR_IP:3000` from phone
- [ ] Can access `http://YOUR_IP:8000/docs` from phone
- [ ] Scanner login page loads on phone
- [ ] Can login successfully
- [ ] Camera starts automatically
- [ ] Can scan QR codes
- [ ] See success feedback

---

## 🌐 URL Reference

### Scanner URLs:
- **Login:** `http://YOUR_IP:3000/scanner-login`
- **Scan Interface:** `http://YOUR_IP:3000/scanner-scan`

### Main App URLs (for reference):
- **Student Dashboard:** `http://YOUR_IP:3000/dashboard`
- **Admin Dashboard:** `http://YOUR_IP:3000`
- **Backend API Docs:** `http://YOUR_IP:8000/docs`

---

## 💡 Pro Tips

1. **Bookmark Scanner URL:** Save `scanner-login` page to phone home screen
2. **Keep Screen On:** Enable "Stay Awake" in phone settings
3. **Portrait Mode:** Scanner works best in portrait orientation
4. **Good Lighting:** Ensure adequate light for QR scanning
5. **Stable Position:** Mount phone or use tripod for high-volume scanning
6. **Battery:** Keep phone charging during long events
7. **Network:** Use 5GHz Wi-Fi for better performance
8. **Clear Cache:** If issues, clear browser cache and reload

---

## 📞 Support

If you encounter issues:
1. Check that both services are running (backend + frontend)
2. Verify IP address is correct
3. Ensure same Wi-Fi network
4. Check firewall settings
5. Review CORS configuration
6. Test API endpoint directly: `http://YOUR_IP:8000/docs`

---

## 🚀 Quick Start Commands (Copy-Paste)

```bash
# Find your IP (macOS/Linux):
ifconfig | grep "inet " | grep -v 127.0.0.1

# Start Backend:
cd /Users/samarthpatil/Desktop/UniPass/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Frontend (in new terminal):
cd /Users/samarthpatil/Desktop/UniPass/frontend
npm run dev -- -H 0.0.0.0

# On Phone Browser:
# Open: http://YOUR_IP:3000/scanner-login
```

---

**You're all set! 🎉**

Your minimalist scanner interface is ready. Scanners can now login on their phones and start scanning QR codes instantly!
