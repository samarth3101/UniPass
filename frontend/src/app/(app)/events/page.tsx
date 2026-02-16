"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/services/api";
import { getUser } from "@/lib/auth";
import EventsClient from "./events-client";

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const user = getUser();

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get("/events/?skip=0&limit=100");
      setEvents(data.events || data);  // Handle both paginated and non-paginated response
    } catch (error: any) {
      console.error("Failed to load events:", error);
      
      // Check if it's a permission error
      if (error?.message?.includes("access required") || error?.message?.includes("403")) {
        setError("You don't have permission to access events. Please contact an administrator.");
        
        // Redirect scanner users to scanner interface
        if (user?.role?.toLowerCase() === "scanner") {
          router.replace("/scanner-scan");
        }
      } else {
        setError(error?.message || "Failed to load events");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading events...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ 
          background: '#fee2e2', 
          border: '1px solid #fecaca', 
          borderRadius: '8px', 
          padding: '20px',
          maxWidth: '500px',
          margin: '0 auto'
        }}>
          <svg 
            width="48" 
            height="48" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="#dc2626" 
            strokeWidth="2"
            style={{ margin: '0 auto 16px' }}
          >
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3 style={{ color: '#dc2626', margin: '0 0 8px 0' }}>Access Denied</h3>
          <p style={{ color: '#991b1b', margin: 0 }}>{error}</p>
        </div>
      </div>
    );
  }

  return <EventsClient events={events} onRefresh={loadEvents} />;
}