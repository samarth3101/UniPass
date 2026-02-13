"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getUser, logout } from "@/lib/auth";
import { useState } from "react";
import "./sidebar.scss";

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();
  // Normalize role to lowercase for consistent comparison
  const role = user?.role?.toLowerCase() || "scanner";
  const [expandedItems, setExpandedItems] = useState<string[]>(["/analytics"]);

  const toggleExpand = (href: string) => {
    setExpandedItems((prev) =>
      prev.includes(href) ? prev.filter((h) => h !== href) : [...prev, href]
    );
  };

  const renderLabel = (label: string, isAI: boolean = false) => {
    if (isAI && label === "Cortex AI") {
      return (
        <>
          Cortex <span style={{ color: '#6366f1', fontWeight: 600 }}>AI</span>
        </>
      );
    }
    return label;
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  // Define menu items with role requirements
  const menuItems = [
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
      label: "Cortex AI",
      href: "/analytics",
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Z"/>
          <path d="M12 6v12"/>
          <path d="M6 12h12"/>
          <circle cx="12" cy="12" r="2"/>
          <path d="M8 8l-1.5-1.5"/>
          <path d="M16 8l1.5-1.5"/>
          <path d="M8 16l-1.5 1.5"/>
          <path d="M16 16l1.5 1.5"/>
        </svg>
      ),
      roles: ["admin", "organizer"],
      isAI: true,
      subItems: [
        { label: "Anomaly Detection", href: "/analytics/anomaly" },
        { label: "Prediction Model", href: "/analytics/prediction", disabled: true },
      ],
    },
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

  // Filter menu items based on user role
  const visibleItems = menuItems.filter((item) =>
    item.roles.includes(role)
  );

  return (
    <aside className="sidebar">
      <div className="logo-section">
        <h2 className="logo">UniPass</h2>
      </div>

      <nav>
        {visibleItems.map((item) => (
          <div key={item.href}>
            {item.subItems ? (
              <>
                <div
                  className={`nav-item ${item.isAI ? "ai-glow" : ""} ${
                    pathname.startsWith(item.href) ? "active" : ""
                  }`}
                  onClick={() => toggleExpand(item.href)}
                >
                  <span className="icon">{item.icon}</span>
                  <span className="label">{renderLabel(item.label, item.isAI)}</span>
                  <svg
                    className={`expand-arrow ${expandedItems.includes(item.href) ? "expanded" : ""}`}
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>
                <div className={`submenu ${expandedItems.includes(item.href) ? "expanded" : ""}`}>
                  {item.subItems.map((subItem) => (
                    <Link
                      key={subItem.href}
                      href={subItem.disabled ? "#" : subItem.href}
                      className={`submenu-item ${
                        pathname === subItem.href ? "active" : ""
                      } ${subItem.disabled ? "disabled" : ""}`}
                      onClick={(e) => subItem.disabled && e.preventDefault()}
                    >
                      {subItem.label}
                      {subItem.disabled && (
                        <span className="coming-soon">Soon</span>
                      )}
                    </Link>
                  ))}
                </div>
              </>
            ) : (
              <Link
                href={item.href}
                className={pathname === item.href ? "active" : ""}
              >
                <span className="icon">{item.icon}</span>
                <span className="label">{item.label}</span>
              </Link>
            )}
          </div>
        ))}
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