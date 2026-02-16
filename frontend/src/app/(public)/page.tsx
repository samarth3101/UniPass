"use client";

import { useEffect, useState } from "react";
import "./landing.scss";

export default function PublicLandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    
    window.addEventListener("scroll", handleScroll);

    // Intersection Observer for scroll animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observerCallback = (entries: IntersectionObserverEntry[]) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);
    
    // Observe all sections
    const sections = document.querySelectorAll('section');
    sections.forEach(section => observer.observe(section));

    // Observe cards
    const cards = document.querySelectorAll('.feature-card, .step-card, .use-case-card');
    cards.forEach((card, index) => {
      (card as HTMLElement).style.transitionDelay = `${index * 0.1}s`;
      observer.observe(card);
    });

    // Prevent scroll when mobile menu is open
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    
    return () => {
      window.removeEventListener("scroll", handleScroll);
      document.documentElement.style.scrollBehavior = 'auto';
      observer.disconnect();
      document.body.style.overflow = 'unset';
    };
  }, [mobileMenuOpen]);

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="landing-page">
      {/* FLOATING NAVBAR */}
      <header className={`floating-navbar ${scrolled ? "scrolled" : ""}`}>
        <nav className="nav-container">
          <div className="logo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6"/>
            </svg>
            UniPass
          </div>

          <div className="nav-links">
            <a href="#cortex-core">Cortex CORE</a>
            <a href="#features">Features</a>
            <a href="#ai-research">AI Research</a>
            <a href="#pricing">Pricing</a>
          </div>

          <div className="nav-actions">
            <a href="/login" className="login-btn">
              Login
            </a>
            <a href="/signup" className="signup-btn">
              Get Started
            </a>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            className={`mobile-menu-toggle ${mobileMenuOpen ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </nav>

        {/* Mobile Menu */}
        <div className={`mobile-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <div className="mobile-menu-content">
            <a href="#cortex-core" onClick={closeMobileMenu}>Cortex CORE</a>
            <a href="#features" onClick={closeMobileMenu}>Features</a>
            <a href="#ai-research" onClick={closeMobileMenu}>AI Research</a>
            <a href="#pricing" onClick={closeMobileMenu}>Pricing</a>
            <div className="mobile-menu-actions">
              <a href="/login" className="login-btn">Login</a>
              <a href="/signup" className="signup-btn">Get Started</a>
            </div>
          </div>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"/>
            </svg>
            <span>Institutional Intelligence Platform</span>
          </div>

          <h1>
            <span className="hero-brand-main">UniPass</span>
            <span className="hero-brand-sub">Powered by Cortex AI™</span>
            <span className="gradient-text">Where Campus Participation<br />Becomes Institutional Intelligence</span>
          </h1>

          <p className="hero-description">
            Transform campus events into structured, intelligent participation data — enabling governance,
            credibility, and institutional intelligence. The only platform that combines QR attendance,
            multi-role tracking, certificate ledgers, and AI-powered analytics in one unified system.
          </p>

          <div className="hero-stats">
            <div className="stat">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 1v6m0 6v6"/>
              </svg>
              <div className="stat-content">
                <div className="stat-value">Cortex CORE™</div>
                <div className="stat-label">6 Intelligence Modules</div>
              </div>
            </div>
            <div className="stat">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <div className="stat-content">
                <div className="stat-value">Trust Scoring</div>
                <div className="stat-label">Conflict Detection</div>
              </div>
            </div>
            <div className="stat">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <div className="stat-content">
                <div className="stat-value">AI Analytics</div>
                <div className="stat-label">Predictive Intelligence</div>
              </div>
            </div>
          </div>

          <div className="hero-cta">
            <a href="/signup" className="cta-primary">
              Start with Cortex Starter
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </a>
            <a href="#cortex-core" className="cta-secondary">
              Explore Cortex CORE
            </a>
          </div>
        </div>
      </section>

      {/* CORTEX CORE SECTION */}
      <section id="cortex-core" className="cortex-core-section">
        <div className="section-header">
          <span className="section-badge cortex-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 1v6m0 6v6M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M1 12h6m6 0h6M5.64 18.36l4.24-4.24m4.24-4.24l4.24-4.24"/>
            </svg>
            Cortex CORE™
          </span>
          <h2>Six Pillars of Institutional Intelligence</h2>
          <p className="cortex-subtitle">
            Advanced participation reconciliation engine that transforms raw event data into
            verified, auditable, and AI-enhanced institutional knowledge
          </p>
        </div>

        <div className="cortex-grid">
          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </div>
            <h3>Conflict Detection</h3>
            <p>Participation reconciliation with trust scoring. Identify data inconsistencies across registrations, attendance, and certificates.</p>
            <div className="module-badge">Phase 1</div>
          </div>

          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 3h18v18H3z"/>
                <path d="m3 9 9-7 9 7"/>
              </svg>
            </div>
            <h3>Student Snapshots</h3>
            <p>Historical profile tracking with temporal queries. View student participation at any point in time with complete audit trail.</p>
            <div className="module-badge">Phase 1</div>
          </div>

          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h3>Certificate System</h3>
            <p>SHA-256 verification with fraud detection. Tamper-evident digital certificates with QR validation and revocation tracking.</p>
            <div className="module-badge">Phase 1</div>
          </div>

          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="1 4 1 10 7 10"/>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
            </div>
            <h3>Audit Trail</h3>
            <p>Change history, revocations, and invalidations. Complete forensic tracking of every modification with old vs. new state comparison.</p>
            <div className="module-badge">Phase 1</div>
          </div>

          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <h3>Multi-Role Engine</h3>
            <p>Track multiple roles per student across events. Participant, volunteer, organizer — weighted certification with role hierarchy.</p>
            <div className="module-badge">Phase 1</div>
          </div>

          <div className="cortex-module">
            <div className="module-icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <h3>Transcript Generator</h3>
            <p>JSON & PDF participation transcripts. Comprehensive student activity reports with certificates, attendance records, and role summaries.</p>
            <div className="module-badge">Phase 1</div>
          </div>
        </div>

        <div className="cortex-cta">
          <p>Ready to experience the power of Cortex CORE?</p>
          <a href="/signup" className="cortex-btn">Start Free with Cortex Starter</a>
        </div>
      </section>



      {/* FEATURES SECTION */}
      <section id="features" className="features-section">
        <div className="section-header">
          <span className="section-badge">Foundation Features</span>
          <h2>Enterprise-Grade Event Management</h2>
          <p>
            Built on battle-tested infrastructure with QR ticketing, real-time monitoring,
            and automated workflows — the foundation that powers Cortex CORE
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="9" y1="9" x2="9" y2="9"/>
                <line x1="15" y1="9" x2="15" y2="9"/>
                <line x1="9" y1="15" x2="15" y2="15"/>
              </svg>
            </div>
            <h3>JWT-Secured QR Tickets</h3>
            <p>
              Digitally signed QR codes with tamper-proof JWT tokens. Each ticket
              contains encrypted event metadata, student PRN, and time-bound validity.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h3>Instant Validation</h3>
            <p>
              Online QR scanning with immediate backend verification. Duplicate scans
              blocked, attendance marked in milliseconds with full audit trail.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <h3>Real-Time Live Monitor</h3>
            <p>
              SSE-powered live dashboard shows attendance as it happens. Watch scans
              update instantly with animated counters and last-scan details.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </div>
            <h3>Automated Email Tickets</h3>
            <p>
              Professional email delivery with embedded QR codes. Students receive
              tickets instantly after registration—BookMyShow-level experience.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
            </div>
            <h3>Enterprise Audit Logs</h3>
            <p>
              Complete activity trail for compliance. Track event creation, edits,
              deletions, and every QR scan with user attribution and IP tracking.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
            <h3>AI-Powered Analytics</h3>
            <p>
              Anomaly detection for suspicious check-ins and NLP-based feedback sentiment analysis.
              Production-ready machine learning modules analyzing attendance patterns and event feedback.
            </p>
          </div>
        </div>
      </section>

      {/* AI/ML RESEARCH SECTION */}
      <section id="ai-research" className="ai-research-section">
        <div className="section-header">
          <span className="section-badge">AI Intelligence</span>
          <h2>Production AI/ML Modules</h2>
          <p>
            Two production-ready machine learning models powering intelligent event management.
            Real AI driving fraud prevention and feedback insights.
          </p>
        </div>

        <div className="ai-modules-grid">
          <div className="ai-module-card">
            <div className="module-number">01</div>
            <div className="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <h3>Attendance Anomaly Detection</h3>
            <p>
              <strong>Goal:</strong> Identify suspicious check-in patterns using unsupervised learning.
            </p>
            <ul>
              <li>Detect unusual login times (e.g., 3 AM registrations)</li>
              <li>Flag multiple rapid check-ins from same device</li>
              <li>Identify location-based anomalies (IP geolocation mismatch)</li>
              <li>Cluster analysis using K-Means/DBSCAN algorithms</li>
            </ul>
            <div className="tech-stack">
              <span>scikit-learn</span>
              <span>isolation-forest</span>
              <span>clustering</span>
            </div>
          </div>

          <div className="ai-module-card">
            <div className="module-number">02</div>
            <div className="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                <path d="M8 10h.01"/>
                <path d="M12 10h.01"/>
                <path d="M16 10h.01"/>
              </svg>
            </div>
            <h3>Feedback Sentiment Analysis</h3>
            <p>
              <strong>Goal:</strong> Analyze post-event feedback using Natural Language Processing.
            </p>
            <ul>
              <li>Classify feedback as positive, neutral, or negative sentiment</li>
              <li>Extract key topics using topic modeling (LDA)</li>
              <li>Identify common complaints or praise patterns</li>
              <li>NLP with TF-IDF, word embeddings, and sentiment classifiers</li>
            </ul>
            <div className="tech-stack">
              <span>nltk</span>
              <span>transformers</span>
              <span>sentiment-analysis</span>
            </div>
          </div>
        </div>

        <div className="research-note">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <p>
            <strong>Note:</strong> These AI/ML modules are production-ready and power Cortex AI's
            intelligence layer. Available in Pro and Enterprise plans for fraud prevention
            and automated feedback analysis.
          </p>
        </div>
      </section>

      {/* PRICING TIERS SECTION */}
      <section id="pricing" className="pricing-section">
        <div className="section-header">
          <span className="section-badge">Pricing Tiers</span>
          <h2>Choose Your Cortex Plan</h2>
          <p>
            From pilot testing to university-wide deployment — scalable plans that grow with your institution
          </p>
        </div>

        <div className="pricing-grid">
          {/* Cortex Starter */}
          <div className="pricing-card starter">
            <div className="tier-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <span>Cortex Starter</span>
            </div>
            <div className="tier-title">
              <h3>Free Trial / Institutional Pilot</h3>
              <p>Small departments, pilot testing, early adopters</p>
            </div>
            <div className="tier-price">
              <span className="price">Free</span>
              <span className="period">90-day trial</span>
            </div>
            <div className="tier-limits">
              <h4>Limits:</h4>
              <ul>
                <li>1 Admin • 3 Organizers</li>
                <li>Up to 20 Volunteers</li>
                <li>500 student registrations</li>
                <li>10 active events/month</li>
              </ul>
            </div>
            <div className="tier-features">
              <h4>Features Included:</h4>
              <ul>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Event CRUD & QR ticketing</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Multi-day attendance tracking</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Basic certificates & CSV export</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Descriptive analytics</li>
              </ul>
            </div>
            <div className="tier-support">
              <strong>Support:</strong> Email (48hr SLA) • Knowledge base
            </div>
            <a href="/signup" className="tier-cta starter-cta">Start Free Trial</a>
          </div>

          {/* Cortex Pro */}
          <div className="pricing-card pro featured">
            <div className="featured-badge">Most Popular</div>
            <div className="tier-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <span>Cortex Pro</span>
            </div>
            <div className="tier-title">
              <h3>Professional Institutional Plan</h3>
              <p>Full department / multi-event academic units</p>
            </div>
            <div className="tier-price">
              <span className="price">₹31XX/-</span>
              <span className="period">per institution/year</span>
            </div>
            <div className="tier-limits">
              <h4>Limits:</h4>
              <ul>
                <li>3 Admins • 6 Organizers</li>
                <li>Up to 45 Volunteers</li>
                <li>5,000 student registrations</li>
                <li>Unlimited events</li>
              </ul>
            </div>
            <div className="tier-features">
              <h4>Everything in Starter, plus:</h4>
              <ul>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Multi-role participation engine</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Certificate revocation system</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Longitudinal student timeline</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Participation Trust Score</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Attendance behavior analysis</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Risk flag detection</li>
              </ul>
            </div>
            <div className="tier-support">
              <strong>Support:</strong> 24×7 email + call • Onboarding session • Quarterly reports
            </div>
            <a href="/signup" className="tier-cta pro-cta">Get Pro Access</a>
          </div>

          {/* Cortex Enterprise */}
          <div className="pricing-card enterprise">
            <div className="tier-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <span>Cortex Enterprise</span>
            </div>
            <div className="tier-title">
              <h3>Premium Intelligence Suite</h3>
              <p>University-wide deployment</p>
            </div>
            <div className="tier-price">
              <span className="price">Custom</span>
              <span className="period">contact sales</span>
            </div>
            <div className="tier-limits">
              <h4>Unlimited Scale:</h4>
              <ul>
                <li>Up to 9 Admins • Unlimited Organizers</li>
                <li>Unlimited Volunteers & Students</li>
                <li>Multi-campus support</li>
              </ul>
            </div>
            <div className="tier-features">
              <h4>Everything in Pro, plus:</h4>
              <ul>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Participation Intelligence Engine</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Certificate Transparency Ledger</li>
                <li><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>API access for ERP integration</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Fraud/anomaly detection engine</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Sentiment analysis (NLP)</li>
                <li className="ai-feature"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>Institutional trust index</li>
              </ul>
            </div>
            <div className="tier-support">
              <strong>Support:</strong> 24×7 priority • Account manager • SLA guarantee • White-label option
            </div>
            <a href="/signup" className="tier-cta enterprise-cta">Contact Sales</a>
          </div>
        </div>

        <div className="addons-section">
          <h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="16 12 12 8 8 12"/>
              <line x1="12" y1="16" x2="12" y2="8"/>
            </svg>
            Optional Add-On Modules
          </h3>
          <div className="addons-grid">
            <span className="addon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
              </svg>
              Placement Participation API
            </span>
            <span className="addon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="20" x2="18" y2="10"/>
                <line x1="12" y1="20" x2="12" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
              Accreditation Analytics Pack
            </span>
            <span className="addon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="3" width="15" height="13"/>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                <circle cx="5.5" cy="18.5" r="2.5"/>
                <circle cx="18.5" cy="18.5" r="2.5"/>
              </svg>
              Blockchain Certificate Mode
            </span>
            <span className="addon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              Inter-College Federation
            </span>
            <span className="addon-badge">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="5" y="2" width="14" height="20" rx="2" ry="2"/>
                <line x1="12" y1="18" x2="12.01" y2="18"/>
              </svg>
              Mobile Scanner App
            </span>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="how-it-works-section">
        <div className="section-header">
          <h2>How UniPass Works</h2>
          <p>Simple 4-step process from event creation to AI analytics</p>
        </div>

        <div className="macbook-container">
          {/* MacBook Frame */}
          <div className="macbook">
            <div className="macbook-screen">
              {/* Screen Content with Animation */}
              <div className="screen-content">
                {/* Browser Chrome */}
                <div className="browser-chrome">
                  <div className="browser-dots">
                    <span className="dot red"></span>
                    <span className="dot yellow"></span>
                    <span className="dot green"></span>
                  </div>
                  <div className="browser-address">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="2" y1="12" x2="22" y2="12"/>
                      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                    </svg>
                    <span>unipass.app/dashboard</span>
                  </div>
                </div>

                {/* Animated Workflow Steps */}
                <div className="workflow-animation">
                  {/* Mouse Cursor */}
                  <div className="mouse-cursor">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="black" strokeWidth="1.5">
                      <path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/>
                    </svg>
                  </div>

                  <div className="workflow-step step-1">
                    <div className="step-icon">
                      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10 9 9 9 8 9"/>
                      </svg>
                    </div>
                    <div className="step-text">
                      <h4>Create Event</h4>
                      <p className="typing-text">Setting up Tech Workshop...</p>
                    </div>
                  </div>

                  <div className="workflow-step step-2">
                    <div className="step-icon">
                      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                        <polyline points="22,6 12,13 2,6"/>
                      </svg>
                    </div>
                    <div className="step-text">
                      <h4>Send Invites</h4>
                      <p className="typing-text">Sending to 245 students...</p>
                    </div>
                  </div>

                  <div className="workflow-step step-3">
                    <div className="step-icon">
                      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                      </svg>
                    </div>
                    <div className="step-text">
                      <h4>QR Validation</h4>
                      <div className="qr-scanner">
                        <div className="qr-code">
                          <div className="qr-grid">
                            <span></span><span></span><span></span>
                            <span></span><span></span><span></span>
                            <span></span><span></span><span></span>
                          </div>
                        </div>
                        <div className="scan-line"></div>
                      </div>
                    </div>
                  </div>

                  <div className="workflow-step step-4">
                    <div className="step-icon">
                      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                      </svg>
                    </div>
                    <div className="step-text">
                      <h4>AI Analysis</h4>
                      <div className="ai-stats">
                        <div className="stat-bar">
                          <span className="label">Attendance</span>
                          <div className="bar"><div className="fill" style={{width: '87%'}}></div></div>
                          <span className="value">87%</span>
                        </div>
                        <div className="stat-bar">
                          <span className="label">Engagement</span>
                          <div className="bar"><div className="fill" style={{width: '92%'}}></div></div>
                          <span className="value">92%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Step Details Below MacBook */}
          <div className="steps-grid">
            <div className="step-detail">
              <div className="step-number">1</div>
              <h3>Create Event & Send Invites</h3>
              <p>
                Admin creates event with details (title, location, date/time).
                System generates registration links and optionally pushes to ERP
                to fetch eligible student lists for automated email invites.
              </p>
            </div>

            <div className="step-detail">
              <div className="step-number">2</div>
              <h3>Students Register & Receive Tickets</h3>
              <p>
                Students register via secure link (ERP auth or Google). System
                validates, creates JWT-signed QR ticket, and sends professional
                email with embedded QR code—instant digital ticketing.
              </p>
            </div>

            <div className="step-detail">
              <div className="step-number">3</div>
              <h3>QR Scan & Real-Time Validation</h3>
              <p>
                Event handlers scan QR codes at venue. Backend verifies JWT
                signature, checks for duplicates, and marks attendance instantly.
                Live monitor shows updates in real-time with SSE.
              </p>
            </div>

            <div className="step-detail">
              <div className="step-number">4</div>
              <h3>Export Reports & AI Analysis</h3>
              <p>
                Generate PDF/CSV reports with attendance statistics. AI modules
                analyze patterns for anomaly detection using Isolation Forest ML,
                and perform NLP-based sentiment analysis on event feedback.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* USE CASES */}
      <section id="use-cases" className="use-cases-section">
        <div className="section-header">
          <h2>Built for University Events</h2>
          <p>From lectures to workshops, UniPass handles every campus scenario</p>
        </div>

        <div className="use-cases-grid">
          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2">
                <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                <path d="M6 12v5c3 3 9 3 12 0v-5"/>
              </svg>
            </div>
            <h3>Guest Lectures & Seminars</h3>
            <p>
              Track attendance for special sessions with email invites, QR tickets,
              and real-time analytics. AI predicts turnout to optimize venue planning.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polygon points="10 8 16 12 10 16 10 8"/>
              </svg>
            </div>
            <h3>Technical Workshops</h3>
            <p>
              Manage multi-session workshops with registration limits. Monitor
              attendance patterns and identify high-engagement participants.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ec4899" strokeWidth="2">
                <circle cx="12" cy="8" r="7"/>
                <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>
              </svg>
            </div>
            <h3>Hackathons & Competitions</h3>
            <p>
              Register teams, validate check-ins, and export per-teacher reports.
              AI detects anomalies like shared tickets or proxy attendance.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              </svg>
            </div>
            <h3>Cultural & Sports Events</h3>
            <p>
              Handle large-scale campus fests with capacity management. Use interest
              clustering to send targeted invites for future events.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <h3>Department Activities</h3>
            <p>
              Track department-specific events with per-class attendance lists sent
              to faculty. NLP analyzes feedback for continuous improvement.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ec4899" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
            <h3>Administrative</h3>
            <p>
              Track attendance for meetings, training sessions, and staff events.
              Centralized records for the entire institution.
            </p>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Transform Your Campus Events?</h2>
          <p>
            Join institutions using UniPass to turn participation into institutional intelligence.
            Start your free 90-day trial with Cortex Starter — no credit card required.
          </p>
          <div className="cta-buttons">
            <a href="/signup" className="cta-primary">
              Start Free with Cortex Starter
            </a>
            <a href="#pricing" className="cta-secondary">
              View Pricing Plans
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-grid">
            <div className="footer-column footer-brand">
              <h3>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 1v6m0 6v6"/>
                </svg>
                UniPass
              </h3>
              <p className="footer-powered-by">Powered by Cortex AI™</p>
              <p>
                Where campus participation becomes institutional intelligence. Built for universities
                that need governance, credibility, and AI-powered insights.
              </p>
              <div className="social-links">
                <a href="https://github.com/" target="_blank" rel="noreferrer" aria-label="GitHub">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                  </svg>
                </a>
                <a href="https://linkedin.com/" target="_blank" rel="noreferrer" aria-label="LinkedIn">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </a>
                <a href="https://twitter.com/" target="_blank" rel="noreferrer" aria-label="Twitter">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z" />
                  </svg>
                </a>
              </div>
            </div>

            <div className="footer-column">
              <h3>Product</h3>
              <ul>
                <li><a href="#cortex-core">Cortex CORE</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#ai-research">AI Research</a></li>
                <li><a href="#pricing">Pricing</a></li>
                <li><a href="/signup">Get Started</a></li>
              </ul>
            </div>

            <div className="footer-column">
              <h3>Resources</h3>
              <ul>
                <li><a href="/api/docs" target="_blank">API Documentation</a></li>
                <li><a href="/login">Login Portal</a></li>
                <li><a href="/signup">Create Account</a></li>
              </ul>
            </div>

            <div className="footer-column">
              <h3>Project</h3>
              <ul>
                <li><a href="https://github.com/" target="_blank">View on GitHub</a></li>
                <li><a href="#features">About UniPass</a></li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            <p>© {new Date().getFullYear()} UniPass™. All rights reserved.</p>
            <div className="footer-links">
              <a href="#">Privacy Policy</a>
              <a href="#">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}