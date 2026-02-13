'use client';
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getUser } from "@/lib/auth";
import "./topbar.scss";

export default function Topbar() {
  const pathname = usePathname();
  const [currentTime, setCurrentTime] = useState('');
  const user = getUser();
  
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
      setCurrentTime(timeString);
    };
    
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);
  
  const getPageTitle = () => {
    if (pathname === '/dashboard') return 'Dashboard';
    if (pathname === '/events') return 'Events';
    if (pathname === '/attendance') return 'Attendance';
    if (pathname.startsWith('/analytics/anomaly')) return (
      <span>
        Cortex <span style={{ color: '#6366f1', fontWeight: 700 }}>AI</span>
      </span>
    );
    if (pathname.startsWith('/analytics')) return 'Analytics';
    if (pathname === '/organizers') return 'Organizers';
    if (pathname === '/scanners') return 'Scanners';
    if (pathname === '/students') return 'Students';
    if (pathname === '/scan') return 'Scan';
    return 'Dashboard';
  };

  const getRoleDisplay = () => {
    const role = user?.role?.toLowerCase();
    switch(role) {
      case 'admin': return 'Administrator';
      case 'organizer': return 'Event Organizer';
      case 'scanner': return 'Scanner Operator';
      default: return 'User';
    }
  };

  const getRoleColor = () => {
    const role = user?.role?.toLowerCase();
    switch(role) {
      case 'admin': return '#ef4444';
      case 'organizer': return '#3b82f6';
      case 'scanner': return '#10b981';
      default: return '#6366f1';
    }
  };

  return (
    <div className="topbar">
      <h1 className="page-title">{getPageTitle()}</h1>
      <div className="topbar-right">
        <div className="system-status">
          <div className="status-indicator">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="12" r="10"/>
            </svg>
            <span className="status-text">Active</span>
          </div>
        </div>
        <div className="time-display">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{currentTime}</span>
        </div>
        <div className="role-display">
          <span 
            className="role-badge" 
            style={{ background: getRoleColor() }}
          >
            {getRoleDisplay()}
          </span>
        </div>
        <div className="user-display">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          <span>{user?.email || 'User'}</span>
        </div>
      </div>
    </div>
  );
}