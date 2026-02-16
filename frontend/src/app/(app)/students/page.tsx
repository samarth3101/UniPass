"use client";

import { useState, useEffect } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./students.scss";

interface ImportResult {
  total: number;
  imported: number;
  duplicates: number;
  errors: Array<{ row?: number; prn?: string; error: string }>;
}

interface DepartmentStat {
  name: string;
  count: number;
}

interface YearStat {
  year: number;
  count: number;
}

interface StudentStats {
  total_students: number;
  department_distribution: DepartmentStat[];
  year_distribution: YearStat[];
  email_stats: {
    with_email: number;
    without_email: number;
  };
}

export default function StudentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState("");
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(false);

  // Load statistics on mount and after successful import
  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoadingStats(true);
    try {
      const data = await api.get("/students/stats/overview");
      setStats(data);
    } catch (err: any) {
      console.error("Failed to load statistics:", err);
    } finally {
      setLoadingStats(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.endsWith(".csv")) {
        setError("Please select a CSV file");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError("");
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setImporting(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("unipass_token");
      const apiUrl = '/api';
      const response = await fetch(`${apiUrl}/students/bulk-import-csv`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to import students");
      }

      const data = await response.json();
      setResult(data.results);
      toast.success(`Successfully imported ${data.results.imported} students!`);
      
      // Reload statistics
      await loadStatistics();
      
      // Clear file input after successful import
      if (data.results.imported > 0) {
        setFile(null);
        const input = document.getElementById("csv-upload") as HTMLInputElement;
        if (input) input.value = "";
      }
    } catch (err: any) {
      setError(err.message || "Failed to upload file");
      toast.error(err.message || "Failed to upload file");
    } finally {
      setImporting(false);
    }
  };

  const downloadSampleCSV = () => {
    const sampleData = `prn,name,email,department,year
PRN001,John Doe,john@university.edu,Computer Science,3
PRN002,Jane Smith,jane@university.edu,Electrical Engineering,2
PRN003,Bob Johnson,bob@university.edu,Mechanical Engineering,4
PRN004,Alice Williams,alice@university.edu,Civil Engineering,1`;

    const blob = new Blob([sampleData], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "sample_students.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="students-page">
      <div className="students-header">
        <h1>Student Management</h1>
        <p>Import students in bulk from CSV files (ERP-ready system)</p>
      </div>

      <div className="import-card">
        <div className="card-header">
          <h2>Bulk Import Students</h2>
          <button className="sample-btn" onClick={downloadSampleCSV}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download Sample CSV
          </button>
        </div>

        <div className="upload-section">
          <div className="file-input-wrapper">
            <input
              id="csv-upload"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="csv-upload" className="file-label">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {file ? file.name : "Choose CSV File"}
            </label>
          </div>

          <button
            className="upload-btn"
            onClick={handleUpload}
            disabled={!file || importing}
          >
            {importing ? (
              <>
                <div className="spinner"></div>
                Importing...
              </>
            ) : (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5 5-5-5M12 12.8V2.5" />
                </svg>
                Import Students
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        )}

        {result && (
          <div className="result-section">
            <div className="result-stats">
              <div className="stat-card total">
                <div className="stat-value">{result.total}</div>
                <div className="stat-label">Total Rows</div>
              </div>
              <div className="stat-card success">
                <div className="stat-value">{result.imported}</div>
                <div className="stat-label">Imported</div>
              </div>
              <div className="stat-card warning">
                <div className="stat-value">{result.duplicates}</div>
                <div className="stat-label">Duplicates</div>
              </div>
              <div className="stat-card error">
                <div className="stat-value">{result.errors.length}</div>
                <div className="stat-label">Errors</div>
              </div>
            </div>

            {result.errors.length > 0 && (
              <div className="errors-list">
                <h3>Import Errors</h3>
                {result.errors.map((err, idx) => (
                  <div key={idx} className="error-item">
                    <strong>
                      {err.row ? `Row ${err.row}` : `PRN: ${err.prn}`}:
                    </strong>{" "}
                    {err.error}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {stats && (
        <div className="card">
          <div className="card-header">
            <h2>Student Statistics</h2>
            {loadingStats && <div className="spinner-small"></div>}
          </div>

          <div className="stats-overview">
            <div className="stat-card primary">
              <div className="stat-value">{stats.total_students}</div>
              <div className="stat-label">Total Students</div>
            </div>
            <div className="stat-card success">
              <div className="stat-value">{stats.email_stats.with_email}</div>
              <div className="stat-label">With Email</div>
            </div>
            <div className="stat-card warning">
              <div className="stat-value">{stats.email_stats.without_email}</div>
              <div className="stat-label">Without Email</div>
            </div>
          </div>

          {stats.department_distribution.length > 0 && (
            <div className="chart-section">
              <h3>Department Distribution</h3>
              <div className="bar-chart">
                {stats.department_distribution.map((dept, idx) => {
                  const maxCount = Math.max(...stats.department_distribution.map(d => d.count));
                  const percentage = (dept.count / maxCount) * 100;
                  return (
                    <div key={idx} className="bar-item">
                      <div className="bar-label">{dept.name || 'Not Specified'}</div>
                      <div className="bar-container">
                        <div 
                          className="bar-fill" 
                          style={{ width: `${percentage}%` }}
                        >
                          <span className="bar-count">{dept.count}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {stats.year_distribution.length > 0 && (
            <div className="chart-section">
              <h3>Year Distribution</h3>
              <div className="bar-chart">
                {stats.year_distribution.map((yearData, idx) => {
                  const maxCount = Math.max(...stats.year_distribution.map(y => y.count));
                  const percentage = (yearData.count / maxCount) * 100;
                  return (
                    <div key={idx} className="bar-item">
                      <div className="bar-label">
                        {yearData.year ? `Year ${yearData.year}` : 'Not Specified'}
                      </div>
                      <div className="bar-container">
                        <div 
                          className="bar-fill year-bar" 
                          style={{ width: `${percentage}%` }}
                        >
                          <span className="bar-count">{yearData.count}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="info-card">
        <h3>CSV Format Requirements</h3>
        <ul>
          <li>
            <strong>Required columns:</strong> prn, name, email, department, year
          </li>
          <li>
            <strong>PRN:</strong> Unique student identifier (e.g., PRN001, PRN002)
          </li>
          <li>
            <strong>Name:</strong> Full student name
          </li>
          <li>
            <strong>Email:</strong> Valid email address (optional)
          </li>
          <li>
            <strong>Department:</strong> Department name (optional)
          </li>
          <li>
            <strong>Year:</strong> Academic year (1-4, optional)
          </li>
          <li>
            <strong>Encoding:</strong> UTF-8
          </li>
          <li>
            <strong>Note:</strong> Duplicate PRNs will be automatically skipped
          </li>
        </ul>
      </div>

      <div className="erp-ready-badge">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        <div>
          <h4>ERP-Ready Integration</h4>
          <p>
            This system is ready for university ERP integration. Your IT team can connect their ERP
            to our <code>/students/bulk-import</code> API endpoint with JSON data.
          </p>
        </div>
      </div>
    </div>
  );
}
