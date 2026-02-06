"use client";

import { useEffect, useState } from "react";
import "./scanners.scss";
import api from "@/services/api";
import ScannerModal from "./scanner-modal";

type Scanner = {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
  total_scans: number;
};

export default function ScannersPage() {
  const [scanners, setScanners] = useState<Scanner[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScannerId, setSelectedScannerId] = useState<number | null>(null);

  async function loadScanners() {
    try {
      setLoading(true);
      const data = await api.get("/admin/scanners");
      setScanners(data);
    } catch (error) {
      console.error("Failed to load scanners:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadScanners();
  }, []);

  if (loading) {
    return (
      <div className="scanners-page">
        <div className="loading">Loading scanners...</div>
      </div>
    );
  }

  return (
    <div className="scanners-page">
      <div className="page-header">
        <h1>Scanner Operators</h1>
        <p>View all QR code scanner operators</p>
      </div>

      <div className="scanners-grid">
        {scanners.length === 0 ? (
          <div className="no-data">No scanner operators found</div>
        ) : (
          scanners.map((scanner) => (
            <div 
              key={scanner.id} 
              className="scanner-card"
              onClick={() => setSelectedScannerId(scanner.id)}
              style={{ cursor: "pointer" }}
            >
              <div className="scanner-avatar">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="2" width="20" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
                  <path d="M7 8h0.01M7 12h0.01M7 16h0.01M12 8h5M12 12h5M12 16h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              
              <div className="scanner-info">
                <h3>{scanner.full_name || `Scanner #${scanner.id}`}</h3>
                <p className="email">{scanner.email}</p>
                <div className="scanner-stats">
                  <span className="stat-badge">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                    {scanner.total_scans || 0} scans
                  </span>
                  <span className="role-badge">Scanner Operator</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedScannerId && (
        <ScannerModal
          scannerId={selectedScannerId}
          onClose={() => setSelectedScannerId(null)}
          onUpdate={loadScanners}
        />
      )}
    </div>
  );
}
