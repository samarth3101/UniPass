"use client";

import { useState, useEffect } from 'react';
import { HelpGuideContent } from './helpGuideConfig';
import './HelpGuide.scss';

interface HelpGuideProps {
  content: HelpGuideContent;
  showToastOnMount?: boolean;
}

export default function HelpGuide({ content, showToastOnMount = false }: HelpGuideProps) {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // Periodic tooltip display
  useEffect(() => {
    // Show tooltip initially after 3 seconds
    const initialTimer = setTimeout(() => {
      setShowTooltip(true);
      // Hide after 5 seconds
      setTimeout(() => setShowTooltip(false), 5000);
    }, 3000);

    // Then show periodically every 45 seconds
    const periodicInterval = setInterval(() => {
      setShowTooltip(true);
      // Hide after 5 seconds
      setTimeout(() => setShowTooltip(false), 5000);
    }, 45000);

    return () => {
      clearTimeout(initialTimer);
      clearInterval(periodicInterval);
    };
  }, []);

  const renderContent = (section: any) => {
    if (section.type === 'paragraph') {
      return <p>{section.content}</p>;
    }

    if (section.type === 'list') {
      return (
        <ul>
          {(Array.isArray(section.content) ? section.content : [section.content]).map((item: string, idx: number) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      );
    }

    if (section.type === 'ordered-list') {
      return (
        <ol>
          {(Array.isArray(section.content) ? section.content : [section.content]).map((item: string, idx: number) => (
            <li key={idx}>{item}</li>
          ))}
        </ol>
      );
    }

    return <p>{String(section.content)}</p>;
  };

  return (
    <>
      {/* Floating Help Button with Tooltip */}
      <div className="help-float-container">
        <button 
          className="help-float-button"
          onClick={() => {
            setIsHelpOpen(!isHelpOpen);
            setShowTooltip(false); // Hide tooltip when help opens
          }}
          aria-label="Toggle help guide"
          title={`Help: ${content.moduleName}`}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </button>
        
        {/* Pill-shaped Tooltip - Appears Periodically */}
        {showTooltip && !isHelpOpen && (
          <div className="help-tooltip-pill">
            Know more about Cortex AI
          </div>
        )}
      </div>

      {/* Help Guide Window */}
      {isHelpOpen && (
        <div className="help-guide-window">
          <div className="help-header">
            <h3>How to Use {content.moduleName}</h3>
            <button 
              className="close-help"
              onClick={() => setIsHelpOpen(false)}
              aria-label="Close help"
            >
              ✕
            </button>
          </div>
          
          <div className="help-content">
            {content.sections.map((section, index) => (
              <section key={index}>
                <h4>{section.title}</h4>
                {renderContent(section)}
              </section>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
