"use client";

import { useEffect, useState } from "react";
import api from "@/services/api";
import EventsClient from "./events-client";

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await api.get("/events/?skip=0&limit=100");
      setEvents(data.events || data);  // Handle both paginated and non-paginated response
    } catch (error) {
      console.error("Failed to load events:", error);
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

  return <EventsClient events={events} onRefresh={loadEvents} />;
}