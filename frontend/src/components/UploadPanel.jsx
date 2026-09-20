import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileArchive, ArrowRight, Shield, X, CheckCircle2 } from './Icons';

export default function UploadPanel({ onFileSelect, selectedFile, onClearFile, isScanning, onStartScan }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      validateAndSelectFile(file);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSelectFile(file);
    }
  };

  const validateAndSelectFile = (file) => {
    setError('');

    if (!file.name.toLowerCase().endsWith('.zip')) {
      setError('Only ZIP archives are supported');
      return;
    }

    if (file.size > 500 * 1024 * 1024) {
      setError('File size must be under 500 MB');
      return;
    }

    onFileSelect(file);
  };

  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: 0.15 }}
      className="upload-panel-wrapper"
    >
      <div className="panel-card">
        {/* Panel Header */}
        <div className="panel-card-header">
          <div className="panel-header-content">
            <div className="panel-eyebrow">NEW ASSESSMENT</div>
            <h2 className="panel-title">Scan repository</h2>
          </div>
          <div className="panel-icon-badge">
            <Shield size={20} strokeWidth={1.8} />
          </div>
        </div>

        {/* Upload Zone */}
        <AnimatePresence mode="wait">
          {!selectedFile ? (
            <motion.div
              key="upload-zone"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className={`upload-drop-zone ${isDragging ? 'dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={handleBrowseClick}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".zip"
                onChange={handleFileInput}
                className="file-input-hidden"
              />

              <motion.div
                animate={{
                  y: isDragging ? -4 : 0,
                  scale: isDragging ? 1.02 : 1
                }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                className="upload-icon-circle"
              >
                <Upload size={24} strokeWidth={1.8} />
                <span className="upload-icon-glow"></span>
              </motion.div>

              <div className="upload-text-content">
                <div className="upload-main-text">Drop repository here</div>
                <div className="upload-sub-text">or click to browse your computer</div>
              </div>

              <div className="upload-meta-tags">
                <span className="upload-meta-tag">ZIP files only</span>
                <span className="meta-separator">•</span>
                <span className="upload-meta-tag">Local processing</span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="file-selected"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.25 }}
              className="file-selected-state"
            >
              <div className="file-selected-icon">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: 'spring', stiffness: 500 }}
                >
                  <CheckCircle2 size={24} strokeWidth={1.8} />
                </motion.div>
                <span className="file-selected-glow"></span>
              </div>

              <div className="file-selected-content">
                <div className="file-selected-label">Repository ready</div>
                <div className="file-selected-name">{selectedFile.name}</div>
                <div className="file-selected-meta">
                  <FileArchive size={12} />
                  <span>{formatFileSize(selectedFile.size)}</span>
                  <span className="meta-separator">•</span>
                  <span>ZIP archive</span>
                </div>
              </div>

              <div className="file-selected-actions">
                {!isScanning && (
                  <>
                    <button
                      type="button"
                      className="start-scan-panel-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onStartScan) onStartScan();
                      }}
                    >
                      <Shield size={16} />
                      <span>START SECURITY ANALYSIS</span>
                      <ArrowRight size={14} />
                    </button>
                    <button
                      className="file-clear-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        onClearFile();
                        setError('');
                      }}
                      aria-label="Remove file"
                    >
                      <X size={16} />
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: 'auto', marginTop: 'var(--space-3)' }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              transition={{ duration: 0.2 }}
              className="upload-error-banner"
            >
              <X size={16} />
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Privacy Note */}
        <div className="upload-privacy-note">
          <Shield size={12} />
          <span>Repository contents are analyzed locally</span>
        </div>
      </div>
    </motion.div>
  );
}
