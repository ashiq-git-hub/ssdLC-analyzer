import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  ShieldAlert,
  ShieldCheck,
  FileCode,
  Check,
  Copy,
  ExternalLink,
  Terminal,
  ArrowRight
} from './Icons';

export default function FindingDrawer({ finding, onClose, onCopySuccess }) {
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!finding) return null;

  const handleCopyRemediation = () => {
    if (finding.remediation) {
      navigator.clipboard.writeText(finding.remediation);
      setCopied(true);
      if (onCopySuccess) onCopySuccess('Remediation guidance copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getSeverityBadgeClass = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'severity-tag-critical';
      case 'HIGH':
        return 'severity-tag-high';
      case 'MEDIUM':
        return 'severity-tag-medium';
      case 'LOW':
        return 'severity-tag-low';
      default:
        return 'severity-tag-info';
    }
  };

  return (
    <AnimatePresence>
      <div className="drawer-overlay" onClick={onClose}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="drawer-backdrop"
        />

        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 30, stiffness: 320 }}
          className="drawer-container"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Drawer Header */}
          <div className="drawer-header">
            <div className="drawer-header-left">
              <div className="drawer-eyebrow">FINDING INSPECTION</div>
              <div className="drawer-meta-badges">
                {finding.severity && (
                  <span className={`drawer-severity-badge ${getSeverityBadgeClass(finding.severity)}`}>
                    {finding.severity}
                  </span>
                )}
                <span className="drawer-domain-tag">{finding.domain}</span>
                <span className={`drawer-status-tag ${finding.status?.toLowerCase()}`}>
                  {finding.status}
                </span>
              </div>
            </div>

            <button className="drawer-close-btn" onClick={onClose} aria-label="Close drawer">
              <X size={18} />
            </button>
          </div>

          {/* Drawer Body */}
          <div className="drawer-body">
            {/* Title */}
            <h2 className="drawer-title">{finding.name}</h2>

            {/* Description */}
            <div className="drawer-section">
              <div className="drawer-section-label">DESCRIPTION</div>
              <p className="drawer-text-body">{finding.description || finding.detail}</p>
            </div>

            {/* Detail / Impact */}
            {finding.detail && finding.description && (
              <div className="drawer-section">
                <div className="drawer-section-label">ASSESSMENT DETAIL</div>
                <p className="drawer-text-body">{finding.detail}</p>
              </div>
            )}

            {/* Code Evidence Panel */}
            {finding.evidence && (
              <div className="drawer-section">
                <div className="drawer-section-label">
                  <Terminal size={12} />
                  <span>TECHNICAL EVIDENCE</span>
                </div>
                <div className="code-evidence-block">
                  <div className="code-evidence-header">
                    <div className="evidence-file-info">
                      <FileCode size={13} />
                      <span>{finding.files?.[0] || 'Repository Context'}</span>
                      {finding.line && <span className="evidence-line-tag">Line {finding.line}</span>}
                    </div>
                  </div>
                  <pre className="code-evidence-content">
                    <code>{finding.evidence}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* Remediation Action */}
            {finding.remediation && (
              <div className="drawer-section remediation-section">
                <div className="drawer-section-label">
                  <ShieldCheck size={13} />
                  <span>RECOMMENDED ACTION</span>
                </div>
                <div className="remediation-content-card">
                  <p className="remediation-text">{finding.remediation}</p>
                  <div className="remediation-actions-row">
                    <button
                      className="remediation-copy-btn"
                      onClick={handleCopyRemediation}
                    >
                      {copied ? <Check size={14} /> : <Copy size={14} />}
                      <span>{copied ? 'Copied' : 'Copy Guidance'}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Technical Metadata */}
            <div className="drawer-section">
              <div className="drawer-section-label">METADATA</div>
              <div className="metadata-properties-grid">
                <div className="metadata-property-row">
                  <span className="prop-name">Category</span>
                  <span className="prop-val">{finding.category || 'Security Control'}</span>
                </div>
                {finding.tool && (
                  <div className="metadata-property-row">
                    <span className="prop-name">Analyzer Rule</span>
                    <span className="prop-val mono">{finding.tool}</span>
                  </div>
                )}
                {finding.rule_id && (
                  <div className="metadata-property-row">
                    <span className="prop-name">Rule ID</span>
                    <span className="prop-val mono">{finding.rule_id}</span>
                  </div>
                )}
                {finding.confidence && (
                  <div className="metadata-property-row">
                    <span className="prop-name">Confidence</span>
                    <span className="prop-val">{finding.confidence}</span>
                  </div>
                )}
              </div>
            </div>

            {/* References */}
            {finding.references && finding.references.length > 0 && (
              <div className="drawer-section">
                <div className="drawer-section-label">STANDARDS & REFERENCES</div>
                <ul className="references-list">
                  {finding.references.map((ref, idx) => (
                    <li key={idx} className="reference-item">
                      <ExternalLink size={12} />
                      <a href={ref} target="_blank" rel="noopener noreferrer">
                        {ref}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
