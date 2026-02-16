"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import QRScanner from "@/app/(app)/scan/qr-scanner";
import "./scanner-scan.scss";

interface ScanResult {
  status: string;
  message: string;
  attendance_id?: number;
  student_name?: string;
  student_prn?: string;
  event_id?: number;
  scanned_at?: string;
  current_day?: number;
  attended_days?: number;
}

export default function ScannerScanPage() {
  const router = useRouter();
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [scanCount, setScanCount] = useState(0);
  const [cameraPermission, setCameraPermission] = useState<string>("prompt");
  const [mounted, setMounted] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const lastScannedTokenRef = useRef<string>("");
  const lastScanTimeRef = useRef<number>(0);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("unipass_token");
    if (!token) {
      router.push("/scanner-login");
    } else {
      setIsChecking(false);
    }
  }, [router]);

  if (!mounted || isChecking) {
    return (
      <div className="scan-page">
        <div className="loading-state">
          <svg className="spinner" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
        </div>
      </div>
    );
  }

  async function requestCameraPermission() {
    try {
      if (typeof window === 'undefined') {
        setError("Cannot access camera during server-side rendering");
        return;
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera API not supported on this device/browser");
        setCameraPermission("denied");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      
      stream.getTracks().forEach(track => track.stop());
      
      setCameraPermission("granted");
      setScanning(true);
    } catch (err: any) {
      console.error("Camera permission error:", err);
      setCameraPermission("denied");
      setError("Camera access denied. Please check your browser settings.");
    }
  }

  async function handleQRScan(scannedToken: string) {
    if (!scannedToken) return;
    
    // Prevent processing if already handling a scan
    if (isProcessing) return;
    
    // Prevent duplicate scans of the same token
    if (scannedToken === lastScannedTokenRef.current) return;
    
    // Cooldown period: prevent scans within 2 seconds of last scan
    const now = Date.now();
    const timeSinceLastScan = now - lastScanTimeRef.current;
    if (timeSinceLastScan < 2000) return;
    
    // Mark as processing
    setIsProcessing(true);
    lastScannedTokenRef.current = scannedToken;
    lastScanTimeRef.current = now;
    
    setError("");
    setResult(null);

    try {
      const res = await api.post(`/scan/?token=${encodeURIComponent(scannedToken)}`);
      setResult(res);
      setScanCount(prev => prev + 1);
      
      // Clear the last scanned token after 5 seconds to allow re-scanning
      setTimeout(() => {
        lastScannedTokenRef.current = "";
      }, 5000);
      
      setTimeout(() => {
        setResult(null);
      }, 3000);
    } catch (e: any) {
      setError(e?.message || "Invalid or expired token");
      
      // Clear the last scanned token on error to allow retry
      setTimeout(() => {
        lastScannedTokenRef.current = "";
      }, 3000);
      
      setTimeout(() => {
        setError("");
      }, 3000);
    } finally {
      // Allow new scans after processing
      setIsProcessing(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("unipass_token");
    localStorage.removeItem("unipass_user");
    router.push("/scanner-login");
  }

  function toggleScanning() {
    setScanning(!scanning);
  }

  return (
    <div className="scan-page">
      {/* Header */}
      <div className="scan-header">
        <div className="header-left">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <path d="M8 21h8"/>
            <path d="M12 17v4"/>
          </svg>
          <h1>Scanner</h1>
        </div>
        <div className="header-right">
          <div className="scan-badge">{scanCount}</div>
          <button onClick={handleLogout} className="logout-icon-btn" title="Logout">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>

      {/* Scanner Area */}
      <div className="scan-area">
        {cameraPermission === "prompt" ? (
          <div className="permission-prompt">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            <h2>Camera Access</h2>
            <p>Allow camera to scan QR codes</p>
            <button onClick={requestCameraPermission} className="primary-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
              Enable Camera
            </button>
          </div>
        ) : cameraPermission === "denied" ? (
          <div className="permission-denied">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <h2>Camera Blocked</h2>
            <p>Enable camera in browser settings</p>
            <button onClick={() => window.location.reload()} className="secondary-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 4 23 10 17 10"/>
                <polyline points="1 20 1 14 7 14"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              Reload
            </button>
          </div>
        ) : scanning ? (
          <div className="scanner-view">
            <QRScanner onScan={handleQRScan} />
            <div className="scan-frame">
              <div className="corner tl"></div>
              <div className="corner tr"></div>
              <div className="corner bl"></div>
              <div className="corner br"></div>
            </div>
            {isProcessing && (
              <div className="processing-overlay">
                <svg className="spinner" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                <p>Processing...</p>
              </div>
            )}
            <p className="scan-hint">{isProcessing ? "Processing scan..." : "Align QR code within frame"}</p>
          </div>
        ) : (
          <div className="paused-view">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="6" y="4" width="4" height="16"/>
              <rect x="14" y="4" width="4" height="16"/>
            </svg>
            <p>Scanner Paused</p>
          </div>
        )}
      </div>

      {/* Controls */}
      {cameraPermission === "granted" && (
        <div className="scan-controls">
          <button onClick={toggleScanning} className={`control-btn ${scanning ? 'active' : ''}`}>
            {scanning ? (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="6" y="4" width="4" height="16"/>
                  <rect x="14" y="4" width="4" height="16"/>
                </svg>
                Pause
              </>
            ) : (
              <>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                Start
              </>
            )}
          </button>
        </div>
      )}

      {/* Result Toast */}
      {result && (
        <div className={`result-toast ${result.status}`}>
          {result.status === "success" ? (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          ) : (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          )}
          <div className="toast-content">
            <strong>{result.message}</strong>
            {result.student_name && (
              <span>{result.student_name} {result.student_prn && `• ${result.student_prn}`}</span>
            )}
          </div>
        </div>
      )}

      {/* Error Toast */}
      {error && (
        <div className="error-toast">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <div className="toast-content">{error}</div>
        </div>
      )}
    </div>
  );
}
