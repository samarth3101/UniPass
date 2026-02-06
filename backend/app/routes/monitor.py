from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.student import Student
from sqlalchemy import func
import asyncio
import json
from typing import Dict, Set
from datetime import datetime

router = APIRouter(prefix="/monitor", tags=["Live Monitor"])

# In-memory event broadcasting system
# Maps event_id -> set of asyncio queues for connected clients
event_monitors: Dict[int, Set[asyncio.Queue]] = {}


def broadcast_scan_event(event_id: int, scan_data: dict):
    """
    Broadcast a scan event to all connected monitors for this event
    Called from scan.py when a QR code is scanned
    """
    if event_id not in event_monitors:
        return
    
    # Send to all connected monitors
    for queue in event_monitors[event_id]:
        try:
            queue.put_nowait(scan_data)
        except asyncio.QueueFull:
            # Skip if queue is full
            pass


async def event_stream(event_id: int, db: Session):
    """
    Server-Sent Events stream for live monitoring
    Sends initial data + live updates when scans happen
    """
    # Register this monitor
    queue = asyncio.Queue(maxsize=100)
    
    if event_id not in event_monitors:
        event_monitors[event_id] = set()
    event_monitors[event_id].add(queue)
    
    try:
        # Send initial data
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            yield f"data: {json.dumps({'error': 'Event not found'})}\n\n"
            return
        
        # Get current attendance count
        total_scans = db.query(func.count(Attendance.id)).filter(
            Attendance.event_id == event_id
        ).scalar() or 0
        
        # Get last scan
        last_scan = db.query(Attendance).filter(
            Attendance.event_id == event_id
        ).order_by(Attendance.scanned_at.desc()).first()
        
        last_scan_data = None
        if last_scan:
            student = db.query(Student).filter(Student.prn == last_scan.student_prn).first()
            last_scan_data = {
                "prn": last_scan.student_prn,
                "name": student.name if student else "Unknown",
                "time": last_scan.scanned_at.strftime("%H:%M:%S")
            }
        
        initial_data = {
            "type": "initial",
            "event_title": event.title,
            "total_scans": total_scans,
            "last_scan": last_scan_data
        }
        
        yield f"data: {json.dumps(initial_data)}\n\n"
        
        # Keep connection alive and send updates
        while True:
            try:
                # Wait for new scan with timeout
                scan_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(scan_data)}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat every 30 seconds
                yield f": heartbeat\n\n"
            
    except asyncio.CancelledError:
        # Client disconnected
        pass
    finally:
        # Cleanup: remove this monitor
        if event_id in event_monitors:
            event_monitors[event_id].discard(queue)
            if not event_monitors[event_id]:
                del event_monitors[event_id]


@router.get("/event/{event_id}")
async def monitor_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    SSE endpoint for real-time event monitoring
    Returns a stream of scan events
    """
    return StreamingResponse(
        event_stream(event_id, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
