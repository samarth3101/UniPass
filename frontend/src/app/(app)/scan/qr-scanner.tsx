"use client";

import { useEffect, useRef, useState } from "react";
import { BrowserQRCodeReader } from "@zxing/browser";

type Props = {
  onScan: (text: string) => void;
};

export default function QRScanner({ onScan }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') return;
    
    const reader = new BrowserQRCodeReader();
    let controls: any;

    const startScanning = async () => {
      try {
        // Check if mediaDevices API is available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          setError("Camera API not supported on this device/browser");
          return;
        }

        // Request camera permission explicitly
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment" }
        });
        
        // Start QR code detection
        const result = await reader.decodeFromVideoDevice(
          undefined,
          videoRef.current!,
          (result) => {
            if (result) {
              onScan(result.getText());
            }
          }
        );
        controls = result;
      } catch (err: any) {
        console.error("Camera error:", err);
        setError("Camera access denied. Please grant camera permissions and reload.");
      }
    };

    startScanning();

    return () => {
      if (controls) {
        controls.stop();
      }
    };
  }, [onScan]);

  if (error) {
    return (
      <div style={{
        padding: "20px",
        textAlign: "center",
        color: "#ef4444",
        fontSize: "14px"
      }}>
        {error}
      </div>
    );
  }

  return (
    <video
      ref={videoRef}
      className="qr-video"
      autoPlay
      playsInline
      muted
    />
  );
}
