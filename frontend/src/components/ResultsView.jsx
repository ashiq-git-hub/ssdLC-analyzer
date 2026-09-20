import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, CheckCircle2, AlertTriangle, X, ArrowRight } from './Icons';

export default function ResultsView({ results, fileName, onNewScan, activeDomainFilter, onSelectFinding }) {
  const [scoreValue, setScoreValue] = useState(0);
  const [metricsVisible, setMetricsVisible] = useState(false);

  const summary = results?.summary || {};
  const domains = results?.domains || [];
  const findings = results?.findings || [];

  // Animate score on mount
  useEffect(() => {
    const targetScore = summary.score || 0;
    const duration = 1200;
    const steps = 60;
    const increment = targetScore / steps;
    let current = 0;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      current = Math.min(current + increment, targetScore);
      setScoreValue(Math.round(current));

      if (step >= steps) {
        clearInterval(timer);
        setScoreValue(targetScore);
      }
    }, duration / steps);

    // Show metrics after score animation
    setTimeout(() => setMetricsVisible(true), 600);

    return () => clearInterval(timer);
  }, [summary.score]);

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'var(--severity-critical)',
      HIGH: 'var(--severity-high)',
      MEDIUM: 'var(--severity-medium)',
      LOW: 'var(--severity-low)',
      INFO: 'var(--severity-info)',
    };
    return colors[severity] || colors.INFO;
  };

  const getStatusColor = (status) => {
    const colors = {
      PASS: 'var(--color-success)',
      FAIL: 'var(--color-danger)',
      WARN: 'var(--color-warning)',
      SKIPPED: 'var(--color-text-muted)',
      ERROR: 'var(--color-danger)',
    };
    return colors[status] || colors.SKIPPED;
  };

  const getRiskLevel = () => {
    const score = summary.score || 0;
    if (score >= 80) return { label: 'LOW', color: 'var(--color-success)' };
    if (score >= 60) return { label: 'MODERATE', color: 'var(--color-warning)' };
    if (score >= 40) return { label: 'HIGH', color: 'var(--severity-high)' };
    return { label: 'CRITICAL', color: 'var(--severity-critical)' };
  };

  const riskLevel = getRiskLevel();

  // Filter findings by domain if filter is active
  const filteredFindings = activeDomainFilter
    ? findings.filter((f) => f.domain === activeDomainFilter)
    : findings;

  const filteredDomains = activeDomainFilter
    ? domains.filter((d) => d.domain === activeDomainFilter)
    : domains;

  const hasCriticalFindings = summary.critical > 0 || summary.high > 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="results-view-wrapper"
    >
      {/* Results Header */}
      <div className="results-header-section">
        <div className="results-header-content">
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="results-eyebrow"
          >
            <span className="eyebrow-line"></span>
            ASSESSMENT COMPLETE
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="results-title"
          >
            Security assessment
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="results-subtitle"
          >
            Analysis results for <strong>{fileName}</strong>
          </motion.p>
        </div>

        <motion.button
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.25 }}
          whileHover={{ scale: 1.02, y: -1 }}
          whileTap={{ scale: 0.98 }}
          className="secondary-btn"
          onClick={onNewScan}
        >
          New assessment
        </motion.button>
      </div>

      {/* Score Overview */}
      <div className="overview-cards-grid">
        {/* Large Score Card */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="score-card-primary"
        >
          <div className="score-card-content">
            <div className="score-eyebrow">SECURITY POSTURE</div>
            <div className="score-display">
              <motion.div
                className="score-number"
                key={scoreValue}
              >
                {scoreValue}
              </motion.div>
              <span className="score-denominator">/100</span>
            </div>
            <div className="score-risk-label" style={{ color: riskLevel.color }}>
              {riskLevel.label} RISK
            </div>
          </div>

          {/* Score Ring */}
          <div className="score-ring-container">
            <svg className="score-ring-svg" viewBox="0 0 120 120">
              <circle
                className="score-ring-track"
                cx="60"
                cy="60"
                r="54"
                fill="none"
                strokeWidth="8"
              />
              <motion.circle
                className="score-ring-fill"
                cx="60"
                cy="60"
                r="54"
                fill="none"
                strokeWidth="8"
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: scoreValue / 100 }}
                transition={{ duration: 1.2, ease: 'easeOut' }}
                style={{
                  stroke: riskLevel.color,
                  transformOrigin: '50% 50%',
                  transform: 'rotate(-90deg)',
                }}
              />
            </svg>
            <div className="score-ring-center">
              <div className="score-ring-number">{scoreValue}</div>
              <div className="score-ring-label">SCORE</div>
            </div>
          </div>
        </motion.div>

        {/* Metric Cards */}
        <AnimatePresence>
          {metricsVisible && (
            <>
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ delay: 0.35 }}
                className="metric-card-item"
              >
                <div className="metric-icon-badge success">
                  <CheckCircle2 size={18} strokeWidth={2} />
                </div>
                <div className="metric-label">CHECKS PASSED</div>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
                  className="metric-value"
                >
                  {summary.passed || 0}
                </motion.div>
                <div className="metric-description">Controls meeting expected criteria</div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ delay: 0.4 }}
                className="metric-card-item"
              >
                <div className="metric-icon-badge danger">
                  <X size={18} strokeWidth={2} />
                </div>
                <div className="metric-label">REQUIRING ATTENTION</div>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.45, type: 'spring', stiffness: 200 }}
                  className="metric-value"
                >
                  {summary.failed || 0}
                </motion.div>
                <div className="metric-description">Security controls needing improvement</div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* Critical Findings Alert */}
      {hasCriticalFindings && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="critical-alert-banner"
        >
          <AlertTriangle size={20} strokeWidth={2} />
          <div className="alert-content">
            <div className="alert-title">Critical findings detected</div>
            <div className="alert-description">
              {summary.critical > 0 && `${summary.critical} CRITICAL`}
              {summary.critical > 0 && summary.high > 0 && ', '}
              {summary.high > 0 && `${summary.high} HIGH`} severity findings require immediate
              attention.
            </div>
          </div>
        </motion.div>
      )}

      {/* Domain Performance Section */}
      <div className="section-header-row">
        <div className="section-header-content">
          <div className="section-eyebrow">
            <span className="eyebrow-line"></span>
            SSDLC DOMAINS
          </div>
          <h3 className="section-title">Domain performance</h3>
        </div>
        <div className="section-count-badge">
          {filteredDomains.length} {activeDomainFilter ? 'filtered' : 'domains'}
        </div>
      </div>

      {/* Domain Grid */}
      <div className="domain-cards-grid">
        {filteredDomains.map((domain, index) => {
          const domainScore = domain.score || 0;
          const statusType =
            domainScore === 100 ? 'complete' : domainScore > 50 ? 'partial' : 'failed';

          return (
            <motion.div
              key={domain.domain}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55 + index * 0.05 }}
              whileHover={{ y: -3, transition: { duration: 0.2 } }}
              className="domain-performance-card"
            >
              <div className="domain-card-header">
                <div className="domain-number-tag">0{index + 1}</div>
                <div className={`domain-status-badge ${statusType}`}>
                  {statusType === 'complete' ? 'STRONG' : statusType === 'partial' ? 'REVIEW' : 'WEAK'}
                </div>
              </div>

              <h4 className="domain-card-title">{domain.domain}</h4>
              <div className="domain-card-weight">Weight: {(domain.weight * 100).toFixed(0)}%</div>

              <div className="domain-score-display-row">
                <div className="domain-score-number">{domainScore}%</div>
                <div className="domain-score-fraction">
                  {domain.passed}/{domain.total} passed
                </div>
              </div>

              <div className="domain-progress-track">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${domainScore}%` }}
                  transition={{ delay: 0.6 + index * 0.05, duration: 0.6, ease: 'easeOut' }}
                  className={`domain-progress-fill ${statusType}`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Detailed Findings Section */}
      <div className="section-header-row">
        <div className="section-header-content">
          <div className="section-eyebrow">
            <span className="eyebrow-line"></span>
            DETAILED FINDINGS
          </div>
          <h3 className="section-title">Security checks</h3>
        </div>
        <div className="section-count-badge">
          {filteredFindings.length} {activeDomainFilter ? 'filtered' : 'checks'}
        </div>
      </div>

      {/* Findings List */}
      <div className="findings-list-container">
        {filteredFindings.map((finding, index) => {
          const statusColor = getStatusColor(finding.status);
          const severityColor = finding.severity ? getSeverityColor(finding.severity) : null;

          return (
            <motion.div
              key={finding.id || index}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + index * 0.03 }}
              whileHover={{ x: 4, transition: { duration: 0.15 } }}
              className="finding-row clickable"
              onClick={() => onSelectFinding?.(finding)}
            >
              <div className="finding-status-icon" style={{ borderColor: statusColor, color: statusColor }}>
                {finding.status === 'PASS' ? (
                  <CheckCircle2 size={16} strokeWidth={2} />
                ) : finding.status === 'SKIPPED' ? (
                  <ArrowRight size={16} strokeWidth={2} />
                ) : (
                  <X size={16} strokeWidth={2} />
                )}
              </div>

              <div className="finding-content">
                <div className="finding-title-row">
                  <span className="finding-title">{finding.name}</span>
                  <span className="finding-domain-tag">{finding.domain}</span>
                  {finding.severity && (
                    <span
                      className="finding-severity-badge"
                      style={{ backgroundColor: severityColor }}
                    >
                      {finding.severity}
                    </span>
                  )}
                </div>
                <p className="finding-detail">{finding.detail}</p>
                {finding.evidence && (
                  <div className="finding-evidence">{finding.evidence}</div>
                )}
                {finding.remediation && finding.status === 'FAIL' && (
                  <div className="finding-remediation">
                    <ArrowRight size={12} />
                    <span>{finding.remediation}</span>
                  </div>
                )}
              </div>

              <div
                className="finding-status-label"
                style={{ borderColor: statusColor, color: statusColor }}
              >
                {finding.status}
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
