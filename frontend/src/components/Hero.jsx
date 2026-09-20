import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ShieldCheck, History } from './Icons';

export default function Hero({ onStartAssessment, onViewAssessments }) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.05,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="hero-copy-container"
    >
      {/* Eyebrow */}
      <motion.div variants={itemVariants} className="hero-eyebrow">
        <span className="eyebrow-line"></span>
        <span>SECURE SOFTWARE DEVELOPMENT LIFECYCLE</span>
      </motion.div>

      {/* Main Title */}
      <motion.h1 variants={itemVariants} className="hero-title">
        Measure the security posture of your software.
      </motion.h1>

      {/* Description */}
      <motion.p variants={itemVariants} className="hero-description">
        Analyze requirements, architecture, implementation, and testing through
        a unified security assessment engine. Identify architectural and code-level
        vulnerabilities before production.
      </motion.p>

      {/* Action Buttons */}
      <motion.div variants={itemVariants} className="hero-actions">
        <button
          className="hero-btn-primary"
          onClick={onStartAssessment}
        >
          <span>START ASSESSMENT</span>
          <ArrowRight size={14} />
        </button>

        <button
          className="hero-btn-secondary"
          onClick={onViewAssessments}
        >
          <History size={14} />
          <span>VIEW ASSESSMENTS</span>
        </button>
      </motion.div>

      {/* Quick Specs / Stats */}
      <motion.div variants={itemVariants} className="hero-stats-row">
        <div className="hero-stat-block">
          <strong className="stat-num">6</strong>
          <span className="stat-tag">SSDLC Domains</span>
        </div>
        <div className="hero-stat-divider"></div>
        <div className="hero-stat-block">
          <strong className="stat-num">32+</strong>
          <span className="stat-tag">Security Checks</span>
        </div>
        <div className="hero-stat-divider"></div>
        <div className="hero-stat-block">
          <strong className="stat-num">100%</strong>
          <span className="stat-tag">Local Processing</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
