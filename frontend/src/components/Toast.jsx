import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, X, ShieldAlert } from './Icons';

export default function Toast({ toasts, onDismiss }) {
  return (
    <div className="toast-container">
      <AnimatePresence>
        {toasts.map((toast) => {
          const isSuccess = toast.type === 'success';
          const isError = toast.type === 'error';

          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 16, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className={`toast-item ${toast.type || 'info'}`}
            >
              <div className="toast-icon">
                {isSuccess && <CheckCircle2 size={16} />}
                {isError && <AlertCircle size={16} />}
                {!isSuccess && !isError && <ShieldAlert size={16} />}
              </div>
              <div className="toast-message">{toast.message}</div>
              <button
                className="toast-close-btn"
                onClick={() => onDismiss(toast.id)}
                aria-label="Dismiss notification"
              >
                <X size={14} />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
