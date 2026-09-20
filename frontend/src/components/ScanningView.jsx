import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Activity, Terminal, CheckCircle2 } from './Icons';

const phases = [
  { id: 'init', label: 'Repository inspection', duration: 800 },
  { id: 'requirements', label: 'Requirements analysis', duration: 1200 },
  { id: 'architecture', label: 'Architecture analysis', duration: 1500 },
  { id: 'implementation', label: 'Implementation analysis', duration: 2000 },
  { id: 'testing', label: 'Testing analysis', duration: 1300 },
  { id: 'supply', label: 'Supply chain analysis', duration: 1100 },
  { id: 'lifecycle', label: 'Lifecycle analysis', duration: 900 },
];

export default function ScanningView({ projectName }) {
  const [activePhase, setActivePhase] = useState(0);
  const [completedPhases, setCompletedPhases] = useState([]);
  const [stats, setStats] = useState({ files: 0, checks: 0 });
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    // Simulate phase progression
    let phaseTimeout;
    if (activePhase < phases.length) {
      phaseTimeout = setTimeout(() => {
        setCompletedPhases((prev) => [...prev, activePhase]);
        setActivePhase((prev) => prev + 1);
      }, phases[activePhase].duration);
    }

    return () => clearTimeout(phaseTimeout);
  }, [activePhase]);

  useEffect(() => {
    // Simulate file/check counting
    const interval = setInterval(() => {
      setStats((prev) => ({
        files: Math.min(prev.files + Math.floor(Math.random() * 15) + 5, 247),
        checks: Math.min(prev.checks + Math.floor(Math.random() * 3) + 1, 32),
      }));
    }, 400);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Elapsed time counter
    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="scanning-view-wrapper"
    >
      <div className="scanning-console">
        {/* Console Header */}
        <div className="scanning-header">
          <div className="scanning-header-content">
            <div className="scanning-eyebrow">SECURITY ANALYSIS</div>
            <h2 className="scanning-title">{projectName || 'Analyzing repository'}</h2>
          </div>

          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="scanning-spinner-badge"
          >
            <Shield size={20} strokeWidth={1.8} />
          </motion.div>
        </div>

        {/* Phase List */}
        <div className="scanning-phases-container">
          <div className="scanning-phases-list">
            {phases.map((phase, index) => {
              const isCompleted = completedPhases.includes(index);
              const isActive = activePhase === index;
              const isPending = index > activePhase;

              return (
                <motion.div
                  key={phase.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.08 }}
                  className={`scanning-phase-row ${
                    isCompleted ? 'completed' : isActive ? 'active' : 'pending'
                  }`}
                >
                  <div className="phase-status-icon">
                    {isCompleted ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 500 }}
                      >
                        <CheckCircle2 size={16} strokeWidth={2} />
                      </motion.div>
                    ) : isActive ? (
                      <motion.div
                        animate={{ scale: [1, 1.15, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="phase-active-pulse"
                      >
                        <Activity size={16} strokeWidth={2} />
                      </motion.div>
                    ) : (
                      <div className="phase-pending-dot" />
                    )}
                  </div>
                  <span className="phase-label">{phase.label}</span>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Current Activity */}
        <div className="scanning-activity-section">
          <div className="activity-section-title">
            <Terminal size={14} />
            <span>CURRENT ACTIVITY</span>
          </div>

          <motion.div
            key={activePhase}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="activity-current-text"
          >
            {activePhase < phases.length ? phases[activePhase].label : 'Finalizing analysis...'}
          </motion.div>

          {/* Stats Grid */}
          <div className="scanning-stats-grid">
            <div className="scanning-stat-item">
              <div className="stat-label">FILES INSPECTED</div>
              <motion.div
                key={stats.files}
                initial={{ scale: 1.1 }}
                animate={{ scale: 1 }}
                className="stat-value"
              >
                {stats.files}
              </motion.div>
            </div>

            <div className="scanning-stat-item">
              <div className="stat-label">CHECKS COMPLETED</div>
              <motion.div
                key={stats.checks}
                initial={{ scale: 1.1 }}
                animate={{ scale: 1 }}
                className="stat-value"
              >
                {stats.checks} / 32
              </motion.div>
            </div>

            <div className="scanning-stat-item">
              <div className="stat-label">ELAPSED</div>
              <motion.div className="stat-value stat-time">
                {formatTime(elapsedTime)}
              </motion.div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="scanning-progress-track">
          <motion.div
            className="scanning-progress-fill"
            initial={{ width: '0%' }}
            animate={{ width: `${((completedPhases.length) / phases.length) * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>
    </motion.div>
  );
}
