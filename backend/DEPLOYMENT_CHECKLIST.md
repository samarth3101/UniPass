# ✅ Multi-Day Events - Deployment Checklist

## Pre-Deployment Verification

### ✅ Code Changes
- [x] Models updated (Event, Attendance)
- [x] Scan endpoint supports multi-day logic
- [x] Certificate service checks full attendance
- [x] Feedback validates all days attended
- [x] Schemas include new fields
- [x] New attendance status endpoint added
- [x] All files error-free

### ✅ Documentation Created
- [x] Migration script with safety checks
- [x] Comprehensive implementation guide
- [x] Quick reference card
- [x] Implementation summary
- [x] Visual flow diagrams
- [x] Database schema diagrams

---

## Deployment Steps

### 1️⃣ Backup Database (CRITICAL)
```bash
# PostgreSQL backup
pg_dump -U postgres -d unipass > backup_before_multiday_$(date +%Y%m%d).sql

# Or if using Docker
docker exec unipass_db pg_dump -U postgres unipass > backup.sql
```

### 2️⃣ Run Migration
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend

# Activate virtual environment if using one
# source venv/bin/activate

# Run migration
python migrate_multi_day_events.py

# Type 'yes' when prompted
```

**Expected Output:**
```
🚀 Starting Multi-Day Event Migration...
✅ Added total_days column (default: 1)
✅ Updated X existing events
✅ Added day_number column
✅ Updated Y existing attendance records
✅ Created composite index
✅ MIGRATION COMPLETED SUCCESSFULLY!
```

### 3️⃣ Verify Migration
```bash
# Check events table
psql -d unipass -c "\d events"
# Should show: total_days | integer | default 1

# Check attendance table
psql -d unipass -c "\d attendance"
# Should show: day_number | integer

# Check indexes
psql -d unipass -c "\di idx_attendance_day_lookup"
```

### 4️⃣ Restart Backend Server
```bash
cd /Users/samarthpatil/Desktop/UniPass/backend

# Stop current server (Ctrl+C in terminal)

# Restart
uvicorn main:app --reload
```

**Verify server starts without errors:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5️⃣ Test Basic Functionality
```bash
# Test 1: Check health endpoint
curl http://localhost:8000/health

# Test 2: Create a 3-day event (requires auth)
curl -X POST http://localhost:8000/events/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Multi-Day Event",
    "start_time": "2026-02-20T09:00:00Z",
    "end_time": "2026-02-22T17:00:00Z",
    "total_days": 3
  }'

# Test 3: Check attendance status endpoint
curl http://localhost:8000/students/TEST_PRN/event/1/attendance-status
```

---

## Testing Plan

### Phase 1: Backward Compatibility ✅
- [ ] Existing single-day events still work
- [ ] Events with NULL total_days default to 1
- [ ] Students can scan once and get certificate immediately
- [ ] Old attendance records show day_number = 1

### Phase 2: Multi-Day Event Creation ✅
- [ ] Create 3-day event via API
- [ ] Verify total_days saved correctly
- [ ] Event shows in dashboard

### Phase 3: QR Scanning ✅
- [ ] **Day 1**: Scan → "Day 1/3 marked"
- [ ] **Day 1 Again**: Scan → "Already marked for Day 1" (rejected)
- [ ] **Day 2**: Scan → "Day 2/3 marked"
- [ ] **Day 3**: Scan → "🎉 All days complete!"
- [ ] **Day 4**: Scan → "Event completed" (rejected)
- [ ] **Before Start**: Scan → "Event not started" (rejected)

### Phase 4: Certificate & Feedback ✅
- [ ] After 2/3 days → Certificate locked
- [ ] After 3/3 days → Certificate unlocked
- [ ] After 2/3 days → Feedback blocked
- [ ] After 3/3 days → Feedback allowed
- [ ] Certificate push only sends to 3/3 attendees

### Phase 5: Attendance Status API ✅
- [ ] `/attendance-status` returns correct progress
- [ ] Shows days attended, days remaining
- [ ] Calculates percentage correctly
- [ ] Shows lock status for certificate/feedback

---

## Rollback Plan (If Needed)

### Quick Rollback
```bash
# Restore database backup
psql -d unipass < backup_before_multiday_YYYYMMDD.sql

# Revert code changes (Git)
cd /Users/samarthpatil/Desktop/UniPass
git checkout HEAD~1 backend/
```

### Partial Rollback (Keep Data)
```sql
-- Remove new columns (WARNING: Data loss)
ALTER TABLE events DROP COLUMN IF EXISTS total_days;
ALTER TABLE attendance DROP COLUMN IF EXISTS day_number;
DROP INDEX IF EXISTS idx_attendance_day_lookup;
```

---

## Post-Deployment Monitoring

### Day 1 - Critical Monitoring
- [ ] Check server logs for errors
- [ ] Monitor database connections
- [ ] Test 5-10 real student scans
- [ ] Verify attendance records have day_number
- [ ] Check response times for /scan endpoint

### Week 1 - Functional Testing
- [ ] Create real multi-day event
- [ ] Monitor student scans across days
- [ ] Test certificate unlocking logic
- [ ] Verify feedback gating works
- [ ] Check analytics queries performance

### Month 1 - Performance Review
- [ ] Analyze dropout patterns
- [ ] Review completion rates
- [ ] Optimize database queries if needed
- [ ] Gather organizer feedback
- [ ] Collect student feedback

---

## Success Metrics

### Technical
- ✅ Migration completed without errors
- ✅ Zero downtime during deployment
- ✅ All endpoints return 200 OK
- ✅ Database queries under 100ms
- ✅ No duplicate day scans recorded

### Functional
- ✅ Single-day events work as before
- ✅ Multi-day events track days correctly
- ✅ Certificate unlock at 100% attendance
- ✅ Feedback only from complete attendees
- ✅ Progress tracking accurate

### Business
- ✅ Organizers can create multi-day events
- ✅ Students see attendance progress
- ✅ Certificate credibility maintained
- ✅ Better feedback quality (full attendees only)
- ✅ Dropout analytics available

---

## Known Limitations & Future Enhancements

### Current Limitations
- ⚠️ No grace period for late scans (e.g., scan Day 2 on Day 3)
- ⚠️ Day calculation based on calendar days (not event times)
- ⚠️ No admin override for partial attendance certificates
- ⚠️ No email notifications for missed days

### Recommended Enhancements (Future)
1. **Grace Period**: Allow scanning previous days within 24 hours
2. **Admin Override**: Let admins manually mark attendance
3. **Reminders**: Email students who missed a day
4. **Flexible Days**: Non-consecutive days (Day 1, 3, 5)
5. **Partial Certificates**: "Attended 2/3 days" certificates
6. **Analytics Dashboard**: Visual dropout curves

---

## Support Resources

### Documentation
- 📄 [MULTI_DAY_EVENTS_GUIDE.md](../UniPass_DOCS/MULTI_DAY_EVENTS_GUIDE.md) - Full implementation guide
- 📄 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick commands and queries
- 📄 [MULTI_DAY_IMPLEMENTATION_SUMMARY.md](MULTI_DAY_IMPLEMENTATION_SUMMARY.md) - Technical summary

### Code Reference
- 🔧 [migrate_multi_day_events.py](migrate_multi_day_events.py) - Database migration
- 🔧 [app/routes/scan.py](app/routes/scan.py) - QR scan logic
- 🔧 [app/services/certificate_service.py](app/services/certificate_service.py) - Certificate eligibility
- 🔧 [app/routes/feedback.py](app/routes/feedback.py) - Feedback validation

### Troubleshooting
```bash
# View recent logs
tail -f /var/log/unipass/backend.log

# Check database connections
psql -d unipass -c "SELECT count(*) FROM pg_stat_activity;"

# Test endpoint manually
curl -v http://localhost:8000/scan -X POST -d '{"token":"..."}'

# Query attendance data
psql -d unipass -c "SELECT event_id, day_number, COUNT(*) FROM attendance GROUP BY event_id, day_number;"
```

---

## Sign-Off

### Pre-Deployment
- [ ] Code reviewed and tested locally
- [ ] Database backup completed
- [ ] Migration script tested on staging
- [ ] Documentation reviewed
- [ ] Team notified

### Post-Deployment
- [ ] Migration successful
- [ ] Server restarted
- [ ] All tests passed
- [ ] Monitoring active
- [ ] Stakeholders informed

---

**Deployment Date**: _________________  
**Deployed By**: _________________  
**Status**: [ ] Success [ ] Issues [ ] Rolled Back  
**Notes**: _________________

---

**Ready to Deploy?** ✅  
**Estimated Downtime**: < 2 minutes (migration + restart)  
**Risk Level**: Low (backward compatible, non-destructive)  
**Rollback Time**: < 5 minutes
