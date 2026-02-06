"use client";

import { useEffect, useState } from "react";
import "./scanners.scss";
import api from "@/services/api";

type Scanner = {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
};

export default function ScannersPage() {
  const [scanners, setScanners] = useState<Scanner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadScanners() {
      try {
        const data = await api.get("/admin/scanners");
        setScanners(data);
      } catch (error) {
        console.error("Failed to load scanners:", error);
      } finally {
        setLoading(false);
      }
    }

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
            <div key={scanner.id} className="scanner-card">
              <div className="scanner-avatar">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <rect x="2" y="2" width="20" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
                  <path d="M7 8h0.01M7 12h0.01M7 16h0.01M12 8h5M12 12h5M12 16h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              
              <div className="scanner-info">
                <h3>Scanner #{scanner.id}</h3>
                <p className="email">{scanner.email}</p>
                <p className="role-badge">Scanner Operator</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
