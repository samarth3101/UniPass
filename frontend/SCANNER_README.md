# 📷 UniPass Scanner Interface

A minimalist, mobile-optimized scanning interface for event organizers and scanners.

## ✨ Features

- **🔐 Simple Login**: Username + password only
- **📸 Auto QR Detection**: Real-time QR code scanning
- **✅ Instant Feedback**: Success/error messages with auto-dismiss
- **📊 Scan Counter**: Track scans in current session
- **⏸️ Pause/Resume**: Control scanning flow
- **🌙 Dark Theme**: Optimized for low-light conditions
- **📱 Mobile-First**: Designed specifically for phones
- **🎯 Minimalist**: Zero clutter, maximum efficiency

## 🚀 Quick Start

### For Users (Scanners):

1. **Open your phone browser**
2. **Navigate to:** `http://YOUR_IP:3000/scanner-login`
3. **Login** with your credentials
4. **Point camera** at QR codes
5. **Done!** Automatic scanning

### For Admins (Setup):

```bash
# 1. Configure for mobile access
cd /Users/samarthpatil/Desktop/UniPass/backend
python setup_mobile_scanner.py

# 2. Follow the printed instructions to start servers
```

See [MOBILE_SCANNER_SETUP.md](../MOBILE_SCANNER_SETUP.md) for detailed guide.

## 🎨 Scanner UI

### Login Page (`/scanner-login`)
- Clean, centered login form
- UniPass branding
- Mobile-optimized inputs
- Error feedback

### Scan Page (`/scanner-scan`)
- Full-screen camera view
- Visual scan corners (animated)
- Success/warning/error cards
- Scan counter badge
- Pause/Resume button
- Logout option

## 🔧 Technical Details

### Routes:
- `/scanner-login` - Scanner login page
- `/scanner-scan` - QR scanning interface

### Tech Stack:
- **Framework**: Next.js 14 (App Router)
- **QR Library**: @zxing/browser
- **Styling**: SCSS modules
- **Auth**: JWT tokens (localStorage)

### API Endpoints Used:
- `POST /auth/login` - Scanner authentication
- `POST /scan/?token={token}` - QR code verification

## 🎯 User Flow

```
1. Scanner opens /scanner-login on phone
   ↓
2. Enters username & password
   ↓
3. Auto-redirect to /scanner-scan
   ↓
4. Camera starts automatically
   ↓
5. Point at student QR code
   ↓
6. Auto-detect & verify
   ↓
7. Show result (3 sec auto-clear)
   ↓
8. Continue scanning next student
```

## 📱 Mobile Optimization

### Portrait Mode
- Camera view: 1:1 aspect ratio
- Scan area: 70% of frame
- Corner indicators for alignment
- Large touch targets (44px minimum)

### Performance
- Auto-clear results after 3 seconds
- Single QR detection per scan
- Optimized camera stream
- Lightweight UI components

### UX Features
- Visual feedback (colors, animations)
- Haptic feedback (where supported)
- Auto-dismiss messages
- Session scan counter
- One-tap logout

## 🔐 Security

- JWT token authentication
- Token stored in localStorage
- Auto-redirect if not logged in
- Logout clears all credentials
- CORS-protected API calls

## 🎨 Styling

### Color Scheme
- **Primary**: Purple gradient (#667eea → #764ba2)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)
- **Background**: Dark navy (#0f172a)

### Responsive Breakpoints
- Mobile: < 768px (primary target)
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🛠️ Development

### Local Testing (Same Device)
```bash
# Access on same computer:
http://localhost:3000/scanner-login
```

### Network Testing (Phone)
```bash
# 1. Find your IP:
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. Access on phone:
http://YOUR_IP:3000/scanner-login
```

### Debug Mode
```typescript
// Add to scanner-scan/page.tsx:
console.log("Scanned token:", scannedToken);
console.log("Result:", result);
```

## 📊 Scanner Permissions Required

**Camera Access**: Required for QR scanning
- Browser will prompt on first use
- Grant permission to enable scanning
- Use Chrome/Safari for best support

**Network Access**: Required for API calls
- Phone must be on same network as server
- Check firewall settings if connection fails

## 🐛 Troubleshooting

### Camera not starting:
- Grant camera permissions in browser settings
- Ensure good lighting
- Try Chrome or Safari

### Login fails:
- Check username/password
- Verify backend is running
- Check network connectivity

### QR not detected:
- Ensure adequate lighting
- Hold phone steady (1-2 feet away)
- Clean camera lens
- Check QR code is clear/unobstructed

### Connection errors:
- Verify same Wi-Fi network
- Check IP address is correct
- Confirm backend/frontend are running
- Review CORS settings

## 💡 Tips for Scanners

1. **Lighting**: Ensure good overhead lighting
2. **Distance**: Hold 1-2 feet from QR code
3. **Stability**: Keep phone steady during scan
4. **Battery**: Keep phone charged
5. **Network**: Stay on same Wi-Fi
6. **Screen**: Keep screen brightness up
7. **Position**: Portrait mode works best
8. **Focus**: Wait for visual corners to align

## 📈 Future Enhancements

- [ ] Offline mode with sync
- [ ] Bulk scan mode
- [ ] Scanner statistics dashboard
- [ ] Custom sound effects
- [ ] Vibration feedback
- [ ] Manual token entry fallback
- [ ] Event selection dropdown
- [ ] Scanner profiles
- [ ] Dark/light theme toggle
- [ ] Multiple language support

## 📞 Support

If you encounter issues:
1. Check [MOBILE_SCANNER_SETUP.md](../MOBILE_SCANNER_SETUP.md)
2. Verify network configuration
3. Test API endpoint: `http://YOUR_IP:8000/docs`
4. Check browser console for errors
5. Review backend logs

---

**Built with ❤️ for UniPass Event Management**
