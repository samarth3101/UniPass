"use client";

import { useEffect, useState } from "react";
import "./analytics.scss";
import api from "@/services/api";
import HelpGuide, { getHelpContent } from "@/components/HelpGuide";

interface DepartmentStats {
  branch: string;
  active_students: number;
  total_students: number;
  participation_rate: number;
  avg_events_per_student: number;
  total_attendance: number;
}

interface TimePattern {
  by_hour: { [key: string]: number };
  by_day: { [key: string]: number };
  by_hour_rate: { [key: string]: number };
  by_day_rate: { [key: string]: number };
  best_time: {
    hour: number | null;
    day: string | null;
    avg_attendance: number | null;
  };
  total_events_analyzed: number;
}

interface Summary {
  summary: {
    total_events: number;
    events_with_attendance: number;
    total_students: number;
    active_students: number;
    student_engagement_rate: number;
    total_attendance_records: number;
    avg_attendance_per_event: number;
  };
  date_range: {
    first_event: string | null;
    last_event: string | null;
    span_days: number;
  };
}

export default function DescriptiveAnalyticsPage() {
  const helpContent = getHelpContent('descriptive-analytics');
  const [deptStats, setDeptStats] = useState<DepartmentStats[]>([]);
  const [timePatterns, setTimePatterns] = useState<TimePattern | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Date range state
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [dateRangePreset, setDateRangePreset] = useState<string>("all");

  useEffect(() => {
    // Don't auto-load if custom range is selected but dates aren't set yet
    if (dateRangePreset === "custom" && (!startDate || !endDate)) {
      return;
    }
    loadAnalytics();
  }, [startDate, endDate, dateRangePreset]);

  const handlePresetChange = (preset: string) => {
    setDateRangePreset(preset);
    const today = new Date();
    let start = "";
    let end = "";

    switch (preset) {
      case "7days":
        start = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
        end = today.toISOString().split("T")[0];
        break;
      case "30days":
        start = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
        end = today.toISOString().split("T")[0];
        break;
      case "90days":
        start = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
        end = today.toISOString().split("T")[0];
        break;
      case "custom":
        // Keep current dates
        return;
      default:
        start = "";
        end = "";
    }

    setStartDate(start);
    setEndDate(end);
  };

  const applyCustomRange = () => {
    if (startDate && endDate) {
      loadAnalytics();
    }
  };

  const loadAnalytics = async (showRefreshIndicator = false) => {
    try {
      if (showRefreshIndicator) {
        setIsRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      const queryString = params.toString() ? `?${params.toString()}` : "";

      const [depts, patterns, summaryData] = await Promise.all([
        api.get(`/analytics/descriptive/departments/participation${queryString}`),
        api.get(`/analytics/descriptive/time-patterns${queryString}`),
        api.get(`/analytics/descriptive/summary${queryString}`),
      ]);

      // Note: api.get returns data directly, not wrapped in .data property
      // Add small delay for smooth transition
      await new Promise(resolve => setTimeout(resolve, 300));
      
      setDeptStats(depts.departments || []);
      setTimePatterns(patterns);
      setSummary(summaryData);
    } catch (error: any) {
      console.error("Failed to load analytics:", error);
      setError(error.message || "Failed to load analytics data");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-dashboard">
        <div className="error-state">
          <h2>Error Loading Analytics</h2>
          <p>{error}</p>
          <button onClick={() => loadAnalytics()} className="btn-retry">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`analytics-dashboard ${isRefreshing ? 'refreshing' : ''}`}>
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Analytics</h1>
          <p className="subtitle">Descriptive insights from attendance data</p>
        </div>
        
        {/* Date Range Selector */}
        <div className="date-range-selector">
          <div className="preset-buttons">
            <button
              className={dateRangePreset === "all" ? "active" : ""}
              onClick={() => handlePresetChange("all")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 6v6l4 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              All Time
            </button>
            <button
              className={dateRangePreset === "7days" ? "active" : ""}
              onClick={() => handlePresetChange("7days")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
              </svg>
              7 Days
            </button>
            <button
              className={dateRangePreset === "30days" ? "active" : ""}
              onClick={() => handlePresetChange("30days")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
              </svg>
              30 Days
            </button>
            <button
              className={dateRangePreset === "90days" ? "active" : ""}
              onClick={() => handlePresetChange("90days")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
              </svg>
              90 Days
            </button>
            <button
              className={dateRangePreset === "custom" ? "active" : ""}
              onClick={() => setDateRangePreset("custom")}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M8 14h8M8 18h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Custom Range
            </button>
          </div>
          
          {dateRangePreset === "custom" && (
            <div className="custom-date-inputs">
              <div className="date-input-group">
                <label>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="label-icon">
                    <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                  From
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  placeholder="Start date"
                />
              </div>
              <div className="date-input-group">
                <label>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="label-icon">
                    <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                  To
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  placeholder="End date"
                  min={startDate}
                />
              </div>
              <button 
                className="apply-custom-range"
                onClick={applyCustomRange}
                disabled={!startDate || !endDate}
                title={!startDate || !endDate ? "Please select both start and end dates" : "Apply date range"}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <polyline points="20 6 9 17 4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Apply
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Show message when custom range selected but dates not applied */}
      {!loading && dateRangePreset === "custom" && (!startDate || !endDate) && (
        <div className="info-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <circle cx="12" cy="8" r="0.5" fill="currentColor" stroke="currentColor" strokeWidth="1"/>
          </svg>
          <p>Please select both start and end dates, then click Apply to view analytics for your custom date range.</p>
        </div>
      )}

      {/* Overall Summary */}
      {summary && (
        <section className="summary-section">
          <h2>System Overview</h2>
          <div className="stat-cards">
            <div className="stat-card">
              <div className="stat-value">{summary.summary.total_events}</div>
              <div className="stat-label">Total Events</div>
              <div className="stat-sublabel">
                {summary.summary.events_with_attendance} with attendance
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{summary.summary.total_students}</div>
              <div className="stat-label">Total Students</div>
              <div className="stat-sublabel">
                {summary.summary.active_students} active
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {summary.summary.student_engagement_rate.toFixed(1)}%
              </div>
              <div className="stat-label">Engagement Rate</div>
              <div className="stat-sublabel">
                {summary.summary.total_attendance_records} total scans
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {summary.summary.avg_attendance_per_event.toFixed(1)}
              </div>
              <div className="stat-label">Avg Attendance</div>
              <div className="stat-sublabel">Per event</div>
            </div>
          </div>
          {summary.date_range.first_event && (
            <div className="date-range">
              <p>
                <strong>Data Range:</strong>{" "}
                {new Date(summary.date_range.first_event).toLocaleDateString()}{" "}
                to {new Date(summary.date_range.last_event!).toLocaleDateString()}{" "}
                ({summary.date_range.span_days} days)
              </p>
            </div>
          )}
        </section>
      )}

      {/* Department Participation */}
      <section className="department-stats">
        <h2>Department Participation</h2>
        {deptStats.length > 0 ? (
          <div className="table-container">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Branch</th>
                  <th>Active Students</th>
                  <th>Total Students</th>
                  <th>Participation Rate</th>
                  <th>Total Attendance</th>
                  <th>Avg Events/Student</th>
                </tr>
              </thead>
              <tbody>
                {deptStats.map((dept) => (
                  <tr key={dept.branch}>
                    <td className="branch-name">{dept.branch}</td>
                    <td>{dept.active_students}</td>
                    <td>{dept.total_students}</td>
                    <td>
                      <div className="participation-bar">
                        <div
                          className="bar-fill"
                          style={{ width: `${dept.participation_rate}%` }}
                        ></div>
                        <span className="bar-label">
                          {dept.participation_rate.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td>{dept.total_attendance}</td>
                    <td>{dept.avg_events_per_student.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="no-data">No department data available</p>
        )}
      </section>

      {/* Time Patterns */}
      {timePatterns && (
        <section className="time-patterns">
          <h2>Best Event Times Analysis</h2>
          {timePatterns.best_time && timePatterns.best_time.hour !== null && (
            <div className="best-time-display">
              <div className="recommendation-card">
                <div className="rec-header">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" fill="none"/>
                  </svg>
                  <h3>Optimal Event Timing</h3>
                </div>
                <div className="rec-content">
                  <div className="rec-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 6v6l4 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span><strong>Best Hour:</strong> {timePatterns.best_time.hour}:00</span>
                  </div>
                  <div className="rec-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/>
                      <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2"/>
                    </svg>
                    <span><strong>Best Day:</strong> {timePatterns.best_time.day}</span>
                  </div>
                  <div className="rec-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                      <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span><strong>Avg Attendance:</strong> {timePatterns.best_time.avg_attendance?.toFixed(1)} students</span>
                  </div>
                </div>
                <p className="events-analyzed">
                  Analysis based on {timePatterns.total_events_analyzed} events
                </p>
              </div>
            </div>
          )}

          <div className="patterns-grid">
            {timePatterns.by_hour && Object.keys(timePatterns.by_hour).length > 0 && (
              <div className="pattern-section">
                <h3>By Hour of Day</h3>
                <div className="patterns-list">
                  {Object.entries(timePatterns.by_hour)
                    .sort(([a], [b]) => parseInt(a) - parseInt(b))
                    .map(([hour, avg]) => (
                      <div key={hour} className="pattern-item">
                        <span className="pattern-label">{hour}:00</span>
                        <div className="pattern-bar-container">
                          <div
                            className="pattern-bar"
                            style={{
                              width: `${(avg / Math.max(...Object.values(timePatterns.by_hour))) * 100}%`,
                            }}
                          ></div>
                        </div>
                        <span className="pattern-value">{avg.toFixed(1)}</span>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {timePatterns.by_day && Object.keys(timePatterns.by_day).length > 0 && (
              <div className="pattern-section">
                <h3>By Day of Week</h3>
                <div className="patterns-list">
                  {Object.entries(timePatterns.by_day).map(([day, avg]) => (
                    <div key={day} className="pattern-item">
                      <span className="pattern-label">{day}</span>
                      <div className="pattern-bar-container">
                        <div
                          className="pattern-bar"
                          style={{
                            width: `${(avg / Math.max(...Object.values(timePatterns.by_day))) * 100}%`,
                          }}
                        ></div>
                      </div>
                      <span className="pattern-value">{avg.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Refresh Button */}
      <div className="dashboard-actions">
        <button onClick={() => loadAnalytics(true)} className="btn-refresh" disabled={isRefreshing}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          {isRefreshing ? 'Refreshing...' : 'Refresh Analytics'}
        </button>
      </div>

      {/* Help Guide */}
      {helpContent && <HelpGuide content={helpContent} />}
    </div>
  );
}
