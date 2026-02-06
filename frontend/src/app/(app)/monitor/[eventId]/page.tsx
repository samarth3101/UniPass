"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import "./monitor.scss";

interface ScanData {
  prn: string;
  name: string;
  time: string;
}

interface MonitorData {
  type: string;
  event_title?: string;
  total_scans?: number;
  last_scan?: ScanData | null;
  prn?: string;
  name?: string;
  time?: string;
}

export default function LiveMonitorPage() {
  const params = useParams();
  const eventId = params.eventId as string;

  const [eventTitle, setEventTitle] = useState<string>("Loading...");
  const [totalScans, setTotalScans] = useState<number>(0);
  const [lastScan, setLastScan] = useState<ScanData | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [pulse, setPulse] = useState<boolean>(false);

  useEffect(() => {
    // Connect to SSE endpoint
    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/monitor/event/${eventId}`
    );

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      const data: MonitorData = JSON.parse(event.data);

      if (data.type === "initial") {
        setEventTitle(data.event_title || "Unknown Event");
        setTotalScans(data.total_scans || 0);
        setLastScan(data.last_scan || null);
      } else if (data.type === "new_scan") {
        // New scan detected!
        setTotalScans((prev) => prev + 1);
        setLastScan({
          prn: data.prn!,
          name: data.name!,
          time: data.time!,
        });

        // Trigger pulse animation
        setPulse(true);
        setTimeout(() => setPulse(false), 1000);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      eventSource.close();
    };
  }, [eventId]);

  return (
    <div className="monitor-page">
      <div className="monitor-container">
        {/* Connection Status */}
        <div className="connection-status">
          <div className={`status-indicator ${isConnected ? "connected" : "disconnected"}`}>
            <div className="dot"></div>
            {isConnected ? "LIVE" : "DISCONNECTED"}
          </div>
        </div>

        {/* Event Title */}
        <div className="event-title">
          <h1>{eventTitle}</h1>
        </div>

        {/* Live Scan Counter */}
        <div className={`scan-counter ${pulse ? "pulse" : ""}`}>
          <div className="counter-label">LIVE SCANS</div>
          <div className="counter-value">{totalScans}</div>
        </div>

        {/* Last Scan */}
        {lastScan && (
          <div className="last-scan">
            <div className="last-scan-label">LAST SCAN</div>
            <div className="last-scan-content">
              <div className="scan-prn">{lastScan.prn}</div>
              <div className="scan-name">{lastScan.name}</div>
              <div className="scan-time">{lastScan.time}</div>
            </div>
          </div>
        )}

        {!lastScan && isConnected && (
          <div className="no-scans">
            <div className="no-scans-icon">👀</div>
            <div className="no-scans-text">Waiting for first scan...</div>
          </div>
        )}
      </div>
    </div>
  );
}
