"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getUser, logout } from "@/lib/auth";
import { useEffect, useRef, useState } from "react";
import "./sidebar.scss";

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();
  const role = user?.role?.toLowerCase() || "scanner";
  const navRef = useRef<HTMLElement>(null);
  const [indicatorStyle, setIndicatorStyle] = useState({ top: 0, height: 0, opacity: 0 });
  const [isCortexActive, setIsCortexActive] = useState(false);

  useEffect(() => {
    if (navRef.current) {
      const activeLink = navRef.current.querySelector('.nav-item.active') as HTMLElement;
      if (activeLink) {
        const navTop = navRef.current.getBoundingClientRect().top;
        const linkRect = activeLink.getBoundingClientRect();
        const isCortex = activeLink.classList.contains('cortex-item');
        setIsCortexActive(isCortex);
        setIndicatorStyle({
          top: linkRect.top - navTop,
          height: linkRect.height,
          opacity: 1
        });
      }
    }
  }, [pathname]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  // Organized menu structure
  const mainItems = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Events",
      href: "/events",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Attendance",
      href: "/attendance",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Scan",
      href: "/scan",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
      ),
      roles: ["admin", "organizer", "scanner"],
    },
  ];

  const cortexItems = [
    {
      label: "CORE",
      href: "/ps1",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4"/>
          <path d="M12 18v4"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Lecture Intelligence",
      href: "/cortex/lecture-ai",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Anomaly Detection",
      href: "/analytics/anomaly",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Sentiment Analysis",
      href: "/analytics/sentiment",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
          <line x1="9" y1="9" x2="9.01" y2="9"/>
          <line x1="15" y1="9" x2="15.01" y2="9"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
  ];

  const managementItems = [
    {
      label: "Organizers",
      href: "/organizers",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      roles: ["admin"],
    },
    {
      label: "Scanners",
      href: "/scanners",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="2" width="20" height="20" rx="2"/>
          <path d="M7 8h0.01M7 12h0.01M7 16h0.01M12 8h5M12 12h5M12 16h5"/>
        </svg>
      ),
      roles: ["admin"],
    },
    {
      label: "Volunteers",
      href: "/volunteers",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
    },
    {
      label: "Students",
      href: "/students",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      ),
      roles: ["admin"],
    },
  ];

  const visibleMainItems = mainItems.filter((item) => item.roles.includes(role));
  const visibleCortexItems = cortexItems.filter((item) => item.roles.includes(role));
  const visibleManagementItems = managementItems.filter((item) => item.roles.includes(role));

  return (
    <aside className="sidebar">
      <div className="logo-section">
        <h2 className="logo">UniPass</h2>
      </div>

      <nav ref={navRef}>
        <div 
          className={`sliding-indicator ${isCortexActive ? 'cortex-gradient' : ''}`}
          style={{
            top: `${indicatorStyle.top}px`,
            height: `${indicatorStyle.height}px`,
            opacity: indicatorStyle.opacity
          }}
        />
        
        {/* Main Section */}
        {visibleMainItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item ${pathname === item.href ? "active" : ""}`}
          >
            <span className="icon">{item.icon}</span>
            <span className="label">{item.label}</span>
          </Link>
        ))}

        {/* CORTEX Section */}
        {visibleCortexItems.length > 0 && (
          <>
            <div className="section-divider">
              <span className="section-label cortex-label">CORTEX</span>
            </div>
            {visibleCortexItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item cortex-item ${pathname === item.href ? "active" : ""}`}
              >
                <span className="icon">{item.icon}</span>
                <span className="label">{item.label}</span>
              </Link>
            ))}
          </>
        )}

        {/* Management Section */}
        {visibleManagementItems.length > 0 && (
          <>
            <div className="section-divider">
              <span className="section-label">Management</span>
            </div>
            {visibleManagementItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-item ${pathname === item.href ? "active" : ""}`}
              >
                <span className="icon">{item.icon}</span>
                <span className="label">{item.label}</span>
              </Link>
            ))}
          </>
        )}
      </nav>

      <div className="sidebar-footer">
        <p className="user-info">
          {user?.email}
        </p>
        <button onClick={handleLogout} className="logout-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Logout
        </button>
      </div>
    </aside>
  );
}