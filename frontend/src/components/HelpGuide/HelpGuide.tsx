"use client";

import { useState, useEffect } from 'react';
import { HelpGuideContent } from './helpGuideConfig';
import './HelpGuide.scss';

interface HelpGuideProps {
  content: HelpGuideContent;
}

export default function HelpGuide({ content }: HelpGuideProps) {
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  // Manage body overflow to prevent background scrolling
  useEffect(() => {
    if (isHelpOpen) {
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      
      return () => {
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [isHelpOpen]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Ensure overflow is restored if component unmounts while help is open
      document.body.style.overflow = '';
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
      {/* Backdrop */}
      {isHelpOpen && (
        <div 
          className="help-backdrop"
          onClick={() => setIsHelpOpen(false)}
        />
      )}

      {/* Help Bulb Button */}
      <button 
        className="help-bulb"
        onClick={() => setIsHelpOpen(!isHelpOpen)}
        aria-label="Help Guide"
        type="button"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
      </button>

      {/* Help Window */}
      {isHelpOpen && (
        <div className="help-window">
          <div className="help-header">
            <h3>How to Use {content.moduleName}</h3>
            <button 
              className="close-btn"
              onClick={() => setIsHelpOpen(false)}
              type="button"
            >
              ✕
            </button>
          </div>
          
          <div className="help-body">
            {content.sections.map((section, index) => (
              <div key={index} className="help-section">
                <h4>{section.title}</h4>
                {renderContent(section)}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

