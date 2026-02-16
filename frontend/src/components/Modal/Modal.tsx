"use client";

import { useEffect } from 'react';
import './Modal.scss';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
}

export default function Modal({ isOpen, onClose, title, children, size = 'medium' }: ModalProps) {
  // Manage body overflow to prevent background scrolling
  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll when modal is open
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      
      return () => {
        // Restore original overflow when modal closes
        document.body.style.overflow = originalOverflow;
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-backdrop" onClick={onClose} />
      <div className={`modal-container modal-${size}`}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose} type="button">
            ×
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </>
  );
}
