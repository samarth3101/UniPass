"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import api from "@/services/api";
import { toast } from "@/components/Toast";
import "./register.scss";

interface TicketData {
    ticket_id: number;
    token: string;
    already_registered?: boolean;
    message?: string;
    student: {
        prn: string;
        name: string;
        email: string;
        branch: string;
        year: number;
        division: string;
    };
    event: {
        id: number;
        title: string;
        description: string;
        location: string;
        start_time: string;
        end_time: string;
    };
}

export default function RegisterPage() {
    const { slug } = useParams();

    const [form, setForm] = useState({
        prn: "",
        name: "",
        email: "",
        branch: "",
        year: "",
        division: "",
    });

    const [ticketData, setTicketData] = useState<TicketData | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleRegister() {
        // Validation
        if (!form.prn.trim() || !form.name.trim() || !form.email.trim()) {
            toast.error("PRN, Name, and Email are required");
            return;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(form.email)) {
            toast.error("Please enter a valid email address");
            return;
        }

        // PRN validation (basic format check - adjust as needed)
        if (form.prn.length < 5) {
            toast.error("Please enter a valid PRN");
            return;
        }

        if (!form.branch || !form.year || !form.division) {
            toast.error("Please fill all required fields");
            return;
        }

        setLoading(true);

        try {
            const res = await api.post(
                `/register/slug/${slug}?prn=${form.prn}&name=${form.name}&email=${form.email}&branch=${form.branch}&year=${form.year}&division=${form.division}`
            );

            setTicketData(res);
            toast.success("Registration successful!");
        } catch (e: any) {
            toast.error(e?.message || "Registration failed");
        }

        setLoading(false);
    }

    function formatDateTime(isoString: string) {
        if (!isoString) return "N/A";
        const date = new Date(isoString);
        return date.toLocaleString("en-US", {
            weekday: "short",
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    return (
        <div className="register-page">
            <div className="card">
                {!ticketData ? (
                    <>
                        <h1>Event Registration</h1>

                        <input
                            placeholder="PRN"
                            onChange={(e) => setForm({ ...form, prn: e.target.value })}
                        />
                        <input
                            placeholder="Full Name"
                            onChange={(e) => setForm({ ...form, name: e.target.value })}
                        />
                        <input
                            placeholder="Email"
                            onChange={(e) => setForm({ ...form, email: e.target.value })}
                        />
                        <input
                            placeholder="Branch"
                            onChange={(e) => setForm({ ...form, branch: e.target.value })}
                        />
                        <input
                            placeholder="Year"
                            onChange={(e) => setForm({ ...form, year: e.target.value })}
                        />
                        <input
                            placeholder="Division"
                            onChange={(e) =>
                                setForm({ ...form, division: e.target.value })
                            }
                        />

                        <button onClick={handleRegister} disabled={loading}>
                            {loading ? "Registering..." : "Register"}
                        </button>
                    </>
                ) : (
                    <div className="ticket-container">
                        {/* Show message if already registered */}
                        {ticketData.already_registered && (
                            <div className="info-banner">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <circle cx="12" cy="12" r="10"/>
                                  <line x1="12" y1="16" x2="12" y2="12"/>
                                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                                </svg>
                                <span>{ticketData.message || "You are already registered for this event"}</span>
                            </div>
                        )}
                        
                        {/* Landscape Ticket */}
                        <div className="ticket-wrapper">
                            <div className="ticket-content">
                                {/* Left Section - Event & Student Info */}
                                <div className="ticket-left">
                                    <div className="ticket-header">
                                        <div className="ticket-logo">UNIPASS</div>
                                        <div className="ticket-id">Ticket #{ticketData.ticket_id}</div>
                                    </div>

                                    <div className="event-info">
                                        <h2>{ticketData.event.title}</h2>
                                        <p style={{fontSize: '13px', color: '#666', marginTop: '4px', lineHeight: '1.4'}}>
                                            {ticketData.event.description || "No description provided"}
                                        </p>
                                        
                                        <div className="event-meta">
                                            <div className="meta-item">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                                  <circle cx="12" cy="10" r="3"/>
                                                </svg>
                                                <span>{ticketData.event.location || "TBA"}</span>
                                            </div>
                                            <div className="meta-item">
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                                                  <line x1="16" y1="2" x2="16" y2="6"/>
                                                  <line x1="8" y1="2" x2="8" y2="6"/>
                                                  <line x1="3" y1="10" x2="21" y2="10"/>
                                                </svg>
                                                <span>{formatDateTime(ticketData.event.start_time)}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="student-info">
                                        <div className="info-row">
                                            <span className="label">Student Name</span>
                                            <span className="value">{ticketData.student.name}</span>
                                        </div>
                                        <div className="info-row">
                                            <span className="label">PRN</span>
                                            <span className="value">{ticketData.student.prn}</span>
                                        </div>
                                        <div className="info-row">
                                            <span className="label">Branch</span>
                                            <span className="value">{ticketData.student.branch || "N/A"}</span>
                                        </div>
                                        <div className="info-row">
                                            <span className="label">Year & Division</span>
                                            <span className="value">{ticketData.student.year} - {ticketData.student.division || "N/A"}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Right Section - QR Code */}
                                <div className="ticket-right">
                                    <div className="qr-section">
                                        <div className="qr-label">Entry Pass</div>
                                        <img 
                                            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/tickets/qr?token=${ticketData.token}`} 
                                            alt="QR Code"
                                            className="qr-code"
                                        />
                                        <div className="qr-instruction">Scan at entry gate</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Footer */}
                        <div className="ticket-footer">
                            <div className="success-badge">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                  <polyline points="20 6 9 17 4 12"/>
                                </svg>
                                <span>Registration Successful</span>
                            </div>
                            <div className="action-buttons">
                                <button 
                                    onClick={() => window.print()} 
                                    className="print-btn"
                                >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                      <polyline points="6 9 6 2 18 2 18 9"/>
                                      <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                                      <rect x="6" y="14" width="12" height="8"/>
                                    </svg>
                                    Print Ticket
                                </button>
                            </div>
                        </div>

                        {/* Token Section (for reference) */}
                        <div className="token-section">
                            <div className="token-label">Ticket Token (for manual entry)</div>
                            <div className="token-display">
                                <textarea 
                                    value={ticketData.token} 
                                    readOnly 
                                />
                                <button 
                                    onClick={async () => {
                                        try {
                                            await navigator.clipboard.writeText(ticketData.token);
                                            toast.success("Token copied to clipboard!");
                                        } catch (err) {
                                            toast.error("Failed to copy token");
                                        }
                                    }}
                                >
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                    </svg>
                                    Copy
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}