# 🎯 Multi-Day Events - Quick Reference Card

## 🚀 Setup (ONE TIME)

### Run Migration
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend
python migrate_multi_day_events.py
# Type 'yes' when prompted
```

---

## 📝 Creating Multi-Day Events

### Option 1: Via API
```bash
curl -X POST http://localhost:8000/events/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Bootcamp 2026",
    "description": "3-day intensive workshop",
    "location": "Main Hall",
    "start_time": "2026-03-15T09:00:00Z",
    "end_time": "2026-03-17T17:00:00Z",
    "total_days": 3
  }'
```

### Option 2: Via SQL
```sql
-- Update existing event
UPDATE events 
SET total_days = 3 
WHERE id = 42;

-- Create new event
INSERT INTO events (title, start_time, end_time, total_days, share_slug)
VALUES ('AI Bootcamp', '2026-03-15', '2026-03-17', 3, 'ai-bootcamp-2026');
```

---

## 🔍 Checking Status

### Student's Attendance Status
```bash
GET /students/PRN123/event/42/attendance-status

Response:
{
  "total_days": 3,
  "attended_days": 2,
  "days_remaining": 1,
  "certificate_unlocked": false,
  "feedback_unlocked": false,
  "progress_percentage": 66.7,
  "days_attended_details": [
    {"day_number": 1, "scanned_at": "2026-03-15T09:15:00Z"},
    {"day_number": 2, "scanned_at": "2026-03-16T09:10:00Z"}
  ]
}
```

### Event Completion Rate
```sql
SELECT 
  e.title,
  e.total_days,
  COUNT(DISTINCT t.student_prn) as registered,
  COUNT(DISTINCT CASE 
    WHEN att.days >= e.total_days 
    THEN att.student_prn 
  END) as fully_attended
FROM events e
LEFT JOIN tickets t ON e.id = t.event_id
LEFT JOIN (
  SELECT event_id, student_prn, COUNT(DISTINCT day_number) as days
  FROM attendance
  GROUP BY event_id, student_prn
) att ON e.id = att.event_id AND t.student_prn = att.student_prn
WHERE e.id = 42
GROUP BY e.id, e.title, e.total_days;
```

---

## 📊 Common Queries

### Find All Multi-Day Events
```sql
SELECT id, title, total_days, start_time
FROM events
WHERE total_days > 1
ORDER BY start_time DESC;
```

### Students Who Completed All Days
```sql
SELECT 
  a.student_prn,
  s.name,
  COUNT(DISTINCT a.day_number) as days_attended
FROM attendance a
JOIN students s ON a.student_prn = s.prn
WHERE a.event_id = 42
GROUP BY a.student_prn, s.name
HAVING COUNT(DISTINCT a.day_number) >= (
  SELECT total_days FROM events WHERE id = 42
);
```

### Students Who Dropped Off
```sql
SELECT 
  a.student_prn,
  s.name,
  COUNT(DISTINCT a.day_number) as days_attended,
  e.total_days,
  e.total_days - COUNT(DISTINCT a.day_number) as days_missed
FROM attendance a
JOIN students s ON a.student_prn = s.prn
JOIN events e ON a.event_id = e.id
WHERE a.event_id = 42
GROUP BY a.student_prn, s.name, e.total_days
HAVING COUNT(DISTINCT a.day_number) < e.total_days
ORDER BY days_attended DESC;
```

### Day-by-Day Attendance
```sql
SELECT 
  day_number,
  COUNT(*) as total_scans,
  COUNT(DISTINCT student_prn) as unique_students,
  ROUND(
    COUNT(DISTINCT student_prn) * 100.0 / 
    (SELECT COUNT(DISTINCT student_prn) FROM attendance WHERE event_id = 42 AND day_number = 1),
    1
  ) as retention_percentage
FROM attendance
WHERE event_id = 42
GROUP BY day_number
ORDER BY day_number;
```

---

## 🎮 Testing Scenarios

### Test Single-Day Event
```bash
# Should work without changes
POST /scan with token for total_days=1 event
→ Immediate certificate unlock
```

### Test Multi-Day Event
```bash
# Day 1
POST /scan → "Day 1/3 marked" ✅

# Day 1 again
POST /scan → "Already marked for Day 1" ❌

# Day 2
POST /scan → "Day 2/3 marked" ✅

# Day 3
POST /scan → "🎉 All days complete!" ✅

# Day 4
POST /scan → "Event completed" ❌
```

---

## 🐛 Troubleshooting

### Problem: "days_attended is 0 but student scanned"
```sql
-- Check if day_number is NULL
SELECT * FROM attendance 
WHERE student_prn = 'PRN123' AND event_id = 42;

-- Fix: Re-run migration
UPDATE attendance SET day_number = 1 WHERE day_number IS NULL;
```

### Problem: "Certificate unlocked too early"
```sql
-- Verify logic counts DISTINCT days
SELECT 
  student_prn,
  COUNT(*) as total_scans,
  COUNT(DISTINCT day_number) as unique_days
FROM attendance
WHERE event_id = 42
GROUP BY student_prn;
```

### Problem: "Cannot scan on Day 2"
```sql
-- Check event start date and total_days
SELECT 
  id, 
  title, 
  start_time, 
  total_days,
  start_time + INTERVAL '1 day' as day_2_start
FROM events
WHERE id = 42;
```

---

## 📱 Frontend Integration

### React/Next.js Component
```tsx
import { useEffect, useState } from 'react';

export function AttendanceProgress({ prn, eventId }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetch(`/api/students/${prn}/event/${eventId}/attendance-status`)
      .then(r => r.json())
      .then(setStatus);
  }, [prn, eventId]);

  if (!status) return <div>Loading...</div>;

  return (
    <div className="attendance-card">
      <h3>Attendance Progress</h3>
      <div className="progress-bar">
        <div 
          className="progress-fill"
          style={{ width: `${status.progress_percentage}%` }}
        />
      </div>
      <p>{status.attended_days} / {status.total_days} days completed</p>
      
      <button 
        disabled={!status.certificate_unlocked}
        className={status.certificate_unlocked ? 'btn-primary' : 'btn-disabled'}
      >
        {status.certificate_unlocked 
          ? '🎓 Download Certificate' 
          : `🔒 Complete ${status.days_remaining} more day(s)`
        }
      </button>
      
      <button disabled={!status.feedback_unlocked}>
        {status.feedback_unlocked 
          ? '📝 Submit Feedback' 
          : '🔒 Unlock after full attendance'
        }
      </button>
    </div>
  );
}
```

---

## 🔒 Access Control

| Endpoint | Auth | Description |
|----------|------|-------------|
| `POST /scan` | Public (JWT in token) | Mark attendance |
| `GET /students/{prn}/event/{event_id}/attendance-status` | Public | Check progress |
| `POST /certificates/event/{event_id}/push` | ORGANIZER/ADMIN | Push certificates |
| `POST /feedback/send-requests/{event_id}` | ORGANIZER/ADMIN | Send feedback requests |
| `POST /feedback/submit` | Public | Submit feedback (validated) |

---

## 💡 Pro Tips

1. **Set realistic total_days**: 1-7 days recommended for workshops
2. **Monitor Day 1 → Day 2 dropout**: High dropout = scheduling issue
3. **Grace Period**: Consider manual admin overrides for late scans
4. **Analytics**: Track retention curves to optimize future events
5. **Communication**: Send daily reminders to students about attendance

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| Migration errors | Check PostgreSQL connection |
| Duplicate day scans | Validate day_number in query |
| Certificate not unlocking | Verify `COUNT(DISTINCT day_number)` |
| NULL day_number | Re-run migration script |
| Wrong current_day | Check event.start_time timezone |

---

## 🎉 Success Indicators

- ✅ Migration completed without errors
- ✅ Single-day events still work normally
- ✅ Multi-day events track days correctly
- ✅ Duplicate same-day scans rejected
- ✅ Certificate unlocks only after all days
- ✅ Feedback gated behind full attendance
- ✅ Progress API returns correct percentages

---

**Version**: UniPass Multi-Day v1.0  
**Last Updated**: February 12, 2026  
**Status**: Production Ready ✅
