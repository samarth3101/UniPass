"use client";

import { useSearchParams } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import api from "@/services/api";
import QRScanner from "./qr-scanner";
import "./scan.scss";

interface ScanResult {
  status: string;
  message: string;
  attendance_id?: number;
  student_name?: string;
  student_prn?: string;
  event_id?: number;
  scanned_at?: string;
}

type ScanMethod = "token" | "camera";

export default function ScanPage() {
  const params = useSearchParams();
  const eventId = params.get("event_id");

  const [scanMethod, setScanMethod] = useState<ScanMethod>("token");
  const [token, setToken] = useState("");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);

  // Stop camera when component unmounts or scan method changes
  useEffect(() => {
    if (scanMethod !== "camera") {
      setCameraActive(false);
    }
  }, [scanMethod]);

  async function verifyToken(tokenToVerify: string) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await api.post(`/scan/?token=${encodeURIComponent(tokenToVerify)}`);
      setResult(res);
      setToken("");
    } catch (e: any) {
      setError(e?.message || "Invalid or expired token");
    } finally {
      setLoading(false);
    }
  }

  async function handleTokenVerify() {
    if (!token.trim()) {
      setError("Please enter a token");
      return;
    }
    await verifyToken(token);
  }

  function handleQRScan(scannedToken: string) {
    if (!scannedToken) return;
    setError("");
    setResult(null);
    verifyToken(scannedToken);
  }

  function formatDateTime(isoString: string) {
    if (!isoString) return "N/A";
    const date = new Date(isoString);
    return date.toLocaleString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <div className="scan-page">
      <div className="scan-container">
        <h1>Scan Entry</h1>
        {eventId && <p className="event-id">Event ID: {eventId}</p>}

        {/* Scan Method Tabs */}
        <div className="scan-tabs">
          <button 
            className={scanMethod === "token" ? "tab active" : "tab"}
            onClick={() => setScanMethod("token")}
          >
            <span className="tab-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </span>
            Enter Token
          </button>
          <button 
            className={scanMethod === "camera" ? "tab active" : "tab"}
            onClick={() => setScanMethod("camera")}
          >
            <span className="tab-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </span>
            Scan QR
          </button>
        </div>

        {/* Token Entry Method */}
        {scanMethod === "token" && (
          <div className="scan-method">
            <div className="scan-form">
              <textarea
                placeholder="Paste ticket token here..."
                value={token}
                onChange={(e) => {
                  setToken(e.target.value);
                  setError("");
                  setResult(null);
                }}
                className="token-input"
              />

              <button
                onClick={handleTokenVerify}
                disabled={loading || !token.trim()}
                className="verify-btn"
              >
                {loading ? "Verifying..." : "Verify Token"}
              </button>
            </div>
          </div>
        )}

        {/* Camera Scan Method */}
        {scanMethod === "camera" && (
          <div className="scan-method camera-section">
            {!cameraActive ? (
              <button onClick={() => setCameraActive(true)} className="start-camera-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                  <circle cx="12" cy="13" r="4"/>
                </svg>
                Start Camera
              </button>
            ) : (
              <div className="camera-container">
                <QRScanner onScan={handleQRScan} />
                <div className="camera-controls">
                  <button onClick={() => setCameraActive(false)} className="stop-camera-btn">
                    Stop Camera
                  </button>
                </div>
                <p className="scan-hint">Point your camera at a QR code to scan</p>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* Result Display */}
        {result && (
          <div className={`result-card ${result.status}`}>
            <div className="result-header">
              <span className="status-icon">
                {result.status === "success" ? (
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                  </svg>
                ) : (
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                )}
              </span>
              <h2>{result.message}</h2>
            </div>

            <div className="result-details">
              {result.student_name && (
                <div className="detail-row">
                  <span className="label">Student:</span>
                  <span className="value">{result.student_name}</span>
                </div>
              )}
              
              {result.student_prn && (
                <div className="detail-row">
                  <span className="label">PRN:</span>
                  <span className="value">{result.student_prn}</span>
                </div>
              )}
              
              {result.scanned_at && (
                <div className="detail-row">
                  <span className="label">Scanned At:</span>
                  <span className="value">{formatDateTime(result.scanned_at)}</span>
                </div>
              )}
              
              {result.attendance_id && (
                <div className="detail-row">
                  <span className="label">Attendance ID:</span>
                  <span className="value">#{result.attendance_id}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}