import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Menu, Command, Sparkles } from './Icons';

export default function Topbar({
  onMenuClick,
  activeTab,
  projectName,
  isScanning,
  hasResults,
  onOpenCommandPalette
}) {
  const getBreadcrumbTitle = () => {
    switch (activeTab) {
      case 'overview':
        return hasResults ? 'Assessment Results' : 'Security Assessment';
      case 'assessments':
        return 'Scan History';
      case 'findings':
        return 'Detailed Findings';
      case 'reports':
        return 'Security Reports';
      default:
        return 'Security Assessment';
    }
  };

  return (
    <header className="topbar-container">
      {/* Left: Mobile Menu Trigger + Breadcrumbs */}
      <div className="topbar-left">
        <button
          className="mobile-menu-trigger"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
        >
          <Menu size={18} />
        </button>

        <nav className="breadcrumb-nav" aria-label="Breadcrumb">
          <span className="breadcrumb-root">SSDLC Analyzer</span>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">{getBreadcrumbTitle()}</span>
          {projectName && (
            <>
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-project">{projectName}</span>
            </>
          )}
        </nav>
      </div>

      {/* Right: Status / Command Palette / Version */}
      <div className="topbar-right">
        {/* Command Palette Trigger */}
        <button
          className="command-trigger-btn"
          onClick={onOpenCommandPalette}
          title="Open Command Palette (⌘K or Ctrl+K)"
        >
          <Command size={12} />
          <span>Quick actions</span>
          <kbd className="kbd-shortcut">⌘K</kbd>
        </button>

        {/* Live Status Pill */}
        <div className="engine-status-pill">
          <span className={`status-pill-dot ${isScanning ? 'scanning-pulse' : 'online'}`}></span>
          <span className="status-pill-text">
            {isScanning ? 'ANALYZING' : 'ENGINE READY'}
          </span>
        </div>

        {/* Version Badge */}
        <div className="topbar-version-badge">v2.0.0</div>
      </div>
    </header>
  );
}
