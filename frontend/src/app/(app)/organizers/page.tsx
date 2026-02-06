"use client";

import { useEffect, useState } from "react";
import "./organizers.scss";
import api from "@/services/api";
import OrganizerModal from "./organizer-modal";

type Organizer = {
  id: number;
  email: string;
  full_name: string;
  created_at: string;
  event_count: number;
  total_registrations: number;
  total_attended: number;
};

export default function OrganizersPage() {
  const [organizers, setOrganizers] = useState<Organizer[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrganizerId, setSelectedOrganizerId] = useState<number | null>(null);

  useEffect(() => {
    async function loadOrganizers() {
      try {
        const data = await api.get("/admin/organizers");
        setOrganizers(data);
      } catch (error) {
        console.error("Failed to load organizers:", error);
      } finally {
        setLoading(false);
      }
    }

    loadOrganizers();
  }, []);

  if (loading) {
    return (
      <div className="organizers-page">
        <div className="loading">Loading organizers...</div>
      </div>
    );
  }

  return (
    <div className="organizers-page">
      <div className="page-header">
        <h1>Organizers Management</h1>
        <p>View all event organizers and their activity</p>
      </div>

      <div className="organizers-grid">
        {organizers.length === 0 ? (
          <div className="no-data">No organizers found</div>
        ) : (
          organizers.map((organizer) => (
            <div 
              key={organizer.id} 
              className="organizer-card"
              onClick={() => setSelectedOrganizerId(organizer.id)}
              style={{ cursor: "pointer" }}
            >
              <div className="organizer-header">
                <div className="organizer-avatar">
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/>
                    <path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="organizer-info">
                  <h3>{organizer.full_name || `Organizer #${organizer.id}`}</h3>
                  <p className="email">{organizer.email}</p>
                </div>
              </div>

              <div className="organizer-stats">
                <div className="stat-item">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                  <div>
                    <span className="stat-value">{organizer.event_count}</span>
                    <span className="stat-label">Events Created</span>
                  </div>
                </div>

                <div className="stat-item">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  <div>
                    <span className="stat-value">{organizer.total_registrations}</span>
                    <span className="stat-label">Total Registrations</span>
                  </div>
                </div>

                <div className="stat-item">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <div>
                    <span className="stat-value">{organizer.total_attended}</span>
                    <span className="stat-label">Total Attended</span>
                  </div>
                </div>
              </div>

              <div className="attendance-rate">
                <div className="rate-label">Attendance Rate</div>
                <div className="rate-bar">
                  <div 
                    className="rate-fill"
                    style={{
                      width: `${organizer.total_registrations > 0 
                        ? (organizer.total_attended / organizer.total_registrations * 100) 
                        : 0}%`
                    }}
                  ></div>
                </div>
                <div className="rate-value">
                  {organizer.total_registrations > 0 
                    ? Math.round((organizer.total_attended / organizer.total_registrations) * 100)
                    : 0}%
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedOrganizerId && (
        <OrganizerModal
          organizerId={selectedOrganizerId}
          onClose={() => setSelectedOrganizerId(null)}
        />
      )}
    </div>
  );
}