#!/usr/bin/env python3
"""
Keep-Alive Script for Render Free Tier
======================================

This script pings your backend to keep it awake during demos.
Run this 5 minutes before your demo presentation.

Usage:
    python keep_alive.py https://your-backend.onrender.com

Alternative: Use UptimeRobot (recommended)
    - Free service: https://uptimerobot.com
    - Automatically pings every 5 minutes
    - No need to run this script
"""

import time
import sys
import requests
from datetime import datetime

def ping_backend(url, duration_minutes=30):
    """
    Ping backend every 5 minutes to keep it awake
    
    Args:
        url: Backend URL (e.g., https://your-backend.onrender.com)
        duration_minutes: How long to keep pinging (default: 30 minutes)
    """
    health_url = f"{url.rstrip('/')}/health"
    interval_seconds = 5 * 60  # 5 minutes
    end_time = time.time() + (duration_minutes * 60)
    
    print("=" * 60)
    print("🚀 RENDER KEEP-ALIVE SCRIPT")
    print("=" * 60)
    print(f"\n📍 Backend URL: {url}")
    print(f"⏰ Duration: {duration_minutes} minutes")
    print(f"🔄 Ping interval: 5 minutes")
    print(f"\n💡 Tip: Use UptimeRobot for automatic monitoring!")
    print("   https://uptimerobot.com (free)\n")
    print("=" * 60)
    
    ping_count = 0
    
    try:
        while time.time() < end_time:
            ping_count += 1
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                print(f"\n[{timestamp}] Ping #{ping_count}...", end=" ")
                response = requests.get(health_url, timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ OK (Status: {response.status_code})")
                else:
                    print(f"⚠️  Warning (Status: {response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed: {e}")
            
            # Calculate time until next ping
            remaining_time = end_time - time.time()
            if remaining_time > interval_seconds:
                print(f"💤 Sleeping for 5 minutes... (Next ping at {datetime.fromtimestamp(time.time() + interval_seconds).strftime('%H:%M:%S')})")
                time.sleep(interval_seconds)
            else:
                break
                
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE - Sent {ping_count} pings")
        print("Your backend should be warm and ready!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print(f"⏸️  STOPPED - Sent {ping_count} pings")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Error: Backend URL required")
        print(f"\nUsage: python {sys.argv[0]} <backend-url>")
        print(f"Example: python {sys.argv[0]} https://unipass-backend.onrender.com")
        print("\n💡 Better option: Use UptimeRobot (https://uptimerobot.com)")
        sys.exit(1)
    
    backend_url = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    ping_backend(backend_url, duration)
