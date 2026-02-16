"use client";

import { useEffect, useState } from "react";
import "./dashboard.scss";
import api from "@/services/api";
import { getUserRole } from "@/lib/auth";

type Event = {
  id: number;
  title: string;
  location: string;
  start_time: string;
  end_time: string;
};

type Summary = {
  total_registered: number;
  total_attended: number;
};

type DashboardStats = {
  totalEvents: number;
  totalRegistrations: number;
  totalAttendance: number;
  avgAttendanceRate: number;
  upcomingEvents: number;
  todayEvents: number;
};

export default function DashboardPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalEvents: 0,
    totalRegistrations: 0,
    totalAttendance: 0,
    avgAttendanceRate: 0,
    upcomingEvents: 0,
    todayEvents: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const role = getUserRole();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const response: { total: number; skip: number; limit: number; events: Event[] } = await api.get("/events/");
        const eventsData = response.events || [];
        setEvents(eventsData);

        // Calculate comprehensive stats
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        
        let totalRegs = 0;
        let totalAtt = 0;
        let upcomingCount = 0;
        let todayCount = 0;

        // Fetch stats for each event
        for (const event of eventsData) {
          try {
            const summary: Summary = await api.get(`/attendance/event/${event.id}/summary`);
            totalRegs += summary.total_registered || 0;
            totalAtt += summary.total_attended || 0;
          } catch (err) {
            // Event might not have data yet
          }

          const eventStart = new Date(event.start_time);
          const eventDay = new Date(eventStart.getFullYear(), eventStart.getMonth(), eventStart.getDate());
          
          if (eventStart > now) upcomingCount++;
          if (eventDay.getTime() === today.getTime()) todayCount++;
        }

        const avgRate = totalRegs > 0 ? Math.round((totalAtt / totalRegs) * 100) : 0;

        setStats({
          totalEvents: eventsData.length,
          totalRegistrations: totalRegs,
          totalAttendance: totalAtt,
          avgAttendanceRate: avgRate,
          upcomingEvents: upcomingCount,
          todayEvents: todayCount,
        });
      } catch (error) {
        console.error("Failed to load dashboard:", error);
        setError(error instanceof Error ? error.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard" style={{ padding: "2rem", textAlign: "center" }}>
        <div className="error-state" style={{ 
          background: "#fee", 
          padding: "2rem", 
          borderRadius: "8px",
          color: "#c00" 
        }}>
          <h2>Error Loading Dashboard</h2>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              padding: "0.5rem 1rem",
              background: "#c00",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const upcomingEvents = events
    .filter((e) => new Date(e.start_time) > new Date())
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  const recentEvents = events
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
    .slice(0, 4);

  return (
    <div className="dashboard">
      {/* Welcome Header */}
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Welcome back</h1>
          <p className="welcome-subtitle">
            Here's what's happening with your events today
          </p>
        </div>
        <div className="time-display">
          <div className="current-time">
            {currentTime.toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit',
              hour12: true 
            })}
          </div>
          <div className="current-date">
            {currentTime.toLocaleDateString('en-US', { 
              weekday: 'long',
              month: 'long',
              day: 'numeric'
            })}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Events</div>
            <div className="stat-value">{stats.totalEvents}</div>
            <div className="stat-meta">
              <span className="stat-badge">{stats.upcomingEvents} upcoming</span>
            </div>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Registrations</div>
            <div className="stat-value">{stats.totalRegistrations}</div>
            <div className="stat-meta">
              <span className="stat-badge">{stats.totalAttendance} attended</span>
            </div>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-label">Attendance Rate</div>
            <div className="stat-value">{stats.avgAttendanceRate}%</div>
            <div className="stat-meta">
              <span className="stat-badge">Average across all events</span>
            </div>
          </div>
        </div>

        <div className="stat-card accent">
          <div className="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <polyline points="12 6 12 12 16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <div className="stat-content">
            <div className="stat-label">Today's Events</div>
            <div className="stat-value">{stats.todayEvents}</div>
            <div className="stat-meta">
              <span className="stat-badge">
                {stats.todayEvents === 0 ? "No events" : "Active now"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content">
        {/* Upcoming Events */}
        <div className="content-card upcoming-card">
          <div className="card-header">
            <div className="header-left">
              <h3>Upcoming Events</h3>
              <span className="card-count">{upcomingEvents.length} scheduled</span>
            </div>
            <a href="/events" className="view-all-link">View all →</a>
          </div>
          
          <div className="upcoming-events-list">
            {upcomingEvents.length > 0 ? (
              upcomingEvents.map((event) => {
                const startDate = new Date(event.start_time);
                const now = new Date();
                
                // Compare dates without time to fix "tomorrow" bug
                const eventDay = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
                const daysUntil = Math.round((eventDay.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
                
                return (
                  <div key={event.id} className="upcoming-event-item">
                    <div className="event-date-badge">
                      <div className="badge-month">
                        {startDate.toLocaleDateString('en-US', { month: 'short' })}
                      </div>
                      <div className="badge-day">
                        {startDate.getDate()}
                      </div>
                    </div>
                    <div className="event-details">
                      <h4>{event.title}</h4>
                      <div className="event-meta">
                        <span className="meta-item">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" strokeWidth="2"/>
                            <circle cx="12" cy="10" r="3" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                          {event.location}
                        </span>
                        <span className="meta-item">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                            <polyline points="12 6 12 12 16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          </svg>
                          {startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                    <div className="event-countdown">
                      <span className="countdown-badge">
                        {daysUntil === 0 ? 'Today' : daysUntil === 1 ? 'Tomorrow' : `${daysUntil} days`}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                  <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                </svg>
                <p>No upcoming events</p>
                <a href="/events" className="create-event-link">Create your first event</a>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions & Recent Activity */}
        <div className="sidebar-cards">
          {/* Quick Actions */}
          <div className="content-card quick-actions-card">
            <div className="card-header">
              <h3>Quick Actions</h3>
            </div>
            <div className="quick-actions">
              <a href="/events" className="action-btn primary-action">
                <div className="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="action-content">
                  <div className="action-title">Create Event</div>
                  <div className="action-desc">Set up a new event</div>
                </div>
              </a>

              <a href="/scan" className="action-btn">
                <div className="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2"/>
                    <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <div className="action-content">
                  <div className="action-title">Scan QR Code</div>
                  <div className="action-desc">Mark attendance</div>
                </div>
              </a>

              <a href="/attendance" className="action-btn">
                <div className="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div className="action-content">
                  <div className="action-title">View Analytics</div>
                  <div className="action-desc">Check attendance stats</div>
                </div>
              </a>
            </div>
          </div>

          {/* Recent Events */}
          <div className="content-card recent-activity-card">
            <div className="card-header">
              <h3>Recent Events</h3>
              <span className="card-count">{recentEvents.length}</span>
            </div>
            <div className="recent-events">
              {recentEvents.length > 0 ? (
                recentEvents.map((event) => {
                  const isPast = new Date(event.end_time) < new Date();
                  return (
                    <div key={event.id} className="recent-event-item">
                      <div className={`event-status ${isPast ? 'completed' : 'active'}`}></div>
                      <div className="event-info">
                        <div className="event-name">{event.title}</div>
                        <div className="event-date">
                          {new Date(event.start_time).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="empty-state-small">
                  <p>No events yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
