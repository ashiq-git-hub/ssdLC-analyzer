import React from 'react';
import { motion } from 'framer-motion';
import { History, Shield, ArrowRight, Trash2, Calendar, FileArchive, CheckCircle2 } from './Icons';

export default function AssessmentsList({
  scans,
  onSelectScan,
  onDeleteScan,
  onNewScan,
  isLoading
}) {
  const formatTime = (isoString) => {
    if (!isoString) return 'Just now';
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const getRiskBadge = (score) => {
    if (score >= 80) return { label: 'LOW RISK', class: 'complete' };
    if (score >= 60) return { label: 'MODERATE RISK', class: 'partial' };
    return { label: 'HIGH RISK', class: 'failed' };
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="assessments-list-view"
    >
      <div className="assessments-header">
        <div>
          <div className="assessments-eyebrow">ASSESSMENT LOGS</div>
          <h2 className="assessments-title">Security assessment history</h2>
          <p className="assessments-subtitle">
            Inspect previous scan runs, security scores, and historical findings.
          </p>
        </div>
        <button className="secondary-btn" onClick={onNewScan}>
          + New assessment
        </button>
      </div>

      {isLoading ? (
        <div className="assessments-loading-state">
          <div className="loading-spinner"></div>
          <span>Loading historical assessments...</span>
        </div>
      ) : scans && scans.length > 0 ? (
        <div className="assessments-grid">
          {scans.map((scan, idx) => {
            const score = Math.round(scan.summary?.score || scan.score || 0);
            const risk = getRiskBadge(score);

            return (
              <motion.div
                key={scan.scan_id || scan.id || idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="assessment-card"
                onClick={() => onSelectScan(scan.scan_id || scan.id)}
              >
                <div className="assessment-card-top">
                  <div className="assessment-project-info">
                    <FileArchive size={16} className="project-icon" />
                    <span className="project-name">{scan.project || scan.target || 'Project Repository'}</span>
                  </div>
                  <div className={`domain-status-badge ${risk.class}`}>
                    {risk.label}
                  </div>
                </div>

                <div className="assessment-score-row">
                  <div className="assessment-score-val">
                    <strong>{score}</strong>
                    <span>/100</span>
                  </div>
                  <div className="assessment-meta-stats">
                    <span>{scan.summary?.passed || 0} passed</span>
                    <span className="meta-sep">•</span>
                    <span>{scan.summary?.failed || 0} failed</span>
                  </div>
                </div>

                <div className="assessment-card-bottom">
                  <div className="assessment-timestamp">
                    <Calendar size={12} />
                    <span>{formatTime(scan.started_at || scan.timestamp)}</span>
                  </div>

                  <div className="assessment-card-actions">
                    {onDeleteScan && (
                      <button
                        className="assessment-delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteScan(scan.scan_id || scan.id);
                        }}
                        title="Delete assessment"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                    <button className="assessment-view-btn">
                      <span>Inspect</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div className="assessments-empty-state">
          <div className="empty-state-icon">
            <History size={32} />
          </div>
          <h3 className="empty-state-title">No assessments yet</h3>
          <p className="empty-state-desc">
            Run your first security scan to evaluate your repository against SSDLC standards.
          </p>
          <button className="hero-btn-primary" onClick={onNewScan}>
            Start first assessment
          </button>
        </div>
      )}
    </motion.div>
  );
}
