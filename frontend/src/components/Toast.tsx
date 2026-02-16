"use client";

import { useEffect, useState } from 'react';
import './toast.scss';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
}

let addToastCallback: ((message: string, type: ToastType) => void) | null = null;

export const toast = {
  success: (message: string) => addToastCallback?.(message, 'success'),
  error: (message: string) => addToastCallback?.(message, 'error'),
  info: (message: string) => addToastCallback?.(message, 'info'),
  warning: (message: string) => addToastCallback?.(message, 'warning'),
};

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    addToastCallback = (message: string, type: ToastType) => {
      const id = Math.random().toString(36).substring(7);
      
      // Prevent duplicate toasts (same message and type within 1 second)
      setToasts((prev) => {
        const isDuplicate = prev.some(
          (t) => t.message === message && t.type === type
        );
        
        if (isDuplicate) {
          return prev; // Don't add duplicate
        }
        
        return [...prev, { id, message, type }];
      });

      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 5000);
    };

    return () => {
      addToastCallback = null;
    };
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type}`}
          onClick={() => removeToast(toast.id)}
        >
          <div className="toast-icon">
            {toast.type === 'success' && (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            )}
            {toast.type === 'error' && (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            )}
            {toast.type === 'info' && (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
            )}
            {toast.type === 'warning' && (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            )}
          </div>
          <div className="toast-message">{toast.message}</div>
          <button className="toast-close" onClick={() => removeToast(toast.id)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      ))}
    </div>
  );
}
