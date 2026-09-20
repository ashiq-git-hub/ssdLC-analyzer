import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Layers,
  FileCode,
  FileText,
  Activity,
  History,
  Terminal,
  Server,
  X,
  Sparkles,
  Sliders,
  CheckCircle2,
  FolderGit2
} from './Icons';

export default function Sidebar({
  activeTab,
  setActiveTab,
  isMobileOpen,
  setIsMobileOpen,
  onNewScan,
  historyCount = 0,
  activeDomainFilter,
  setActiveDomainFilter,
  hasResults
}) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'new-scan', label: 'New Assessment', icon: Sparkles, badge: 'READY' },
    { id: 'assessments', label: 'Assessments', icon: History, count: historyCount },
    { id: 'findings', label: 'Findings', icon: Activity, disabled: !hasResults },
    { id: 'reports', label: 'Reports', icon: FileText, disabled: !hasResults },
  ];

  const lifecycleDomains = [
    { id: 'Requirements', label: 'Requirements', code: 'REQ' },
    { id: 'Architecture', label: 'Architecture', code: 'ARC' },
    { id: 'Implementation', label: 'Implementation', code: 'IMP' },
    { id: 'Testing', label: 'Testing', code: 'TST' },
    { id: 'Supply Chain', label: 'Supply Chain', code: 'SUP' },
    { id: 'Lifecycle', label: 'Lifecycle', code: 'LFC' },
  ];

  const handleNavClick = (id) => {
    if (id === 'new-scan') {
      onNewScan();
    } else {
      setActiveTab(id);
    }
    setIsMobileOpen(false);
  };

  const handleDomainClick = (domainId) => {
    if (activeDomainFilter === domainId) {
      setActiveDomainFilter(null);
    } else {
      setActiveDomainFilter(domainId);
      if (activeTab !== 'overview' && activeTab !== 'findings') {
        setActiveTab('overview');
      }
    }
    setIsMobileOpen(false);
  };

  const sidebarContent = (
    <div className="sidebar-inner">
      {/* Brand */}
      <div className="brand-header">
        <div className="brand-badge">
          <Shield size={18} className="brand-icon" />
          <span className="brand-glow"></span>
        </div>
        <div className="brand-titles">
          <span className="brand-title-main">SSDLC</span>
          <span className="brand-title-sub">ANALYZER</span>
        </div>
        {isMobileOpen && (
          <button
            className="mobile-close-btn"
            onClick={() => setIsMobileOpen(false)}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Workspace Section */}
      <div className="sidebar-group">
        <div className="sidebar-group-title">WORKSPACE</div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`nav-btn ${isActive ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
                onClick={() => !item.disabled && handleNavClick(item.id)}
                disabled={item.disabled}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeNavIndicator"
                    className="active-nav-indicator"
                    transition={{ type: 'spring', stiffness: 450, damping: 35 }}
                  />
                )}
                <Icon size={16} className="nav-btn-icon" />
                <span className="nav-btn-label">{item.label}</span>
                {item.badge && <span className="nav-badge-pill">{item.badge}</span>}
                {item.count > 0 && <span className="nav-count-pill">{item.count}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security Lifecycle Domains */}
      <div className="sidebar-group">
        <div className="sidebar-group-title">
          <span>SECURITY LIFECYCLE</span>
          {activeDomainFilter && (
            <button
              className="clear-filter-btn"
              onClick={() => setActiveDomainFilter(null)}
              title="Clear filter"
            >
              RESET
            </button>
          )}
        </div>
        <div className="domain-nav-list">
          {lifecycleDomains.map((domain) => {
            const isFilterActive = activeDomainFilter === domain.id;
            return (
              <button
                key={domain.id}
                className={`domain-nav-btn ${isFilterActive ? 'active-filter' : ''}`}
                onClick={() => handleDomainClick(domain.id)}
              >
                <span className="domain-code-tag">{domain.code}</span>
                <span className="domain-label">{domain.label}</span>
                {isFilterActive && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="filter-active-dot"
                  />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* System Status Footer */}
      <div className="sidebar-footer">
        <div className="system-status-card">
          <div className="status-indicator">
            <span className="status-ping-dot"></span>
            <span className="status-dot"></span>
          </div>
          <div className="status-details">
            <div className="status-title-row">
              <span className="status-label">Analyzer Online</span>
            </div>
            <div className="status-meta">
              <span>LOCAL ENGINE</span>
              <span className="meta-sep">•</span>
              <span>v2.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="sidebar-desktop">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="mobile-backdrop"
              onClick={() => setIsMobileOpen(false)}
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              className="sidebar-mobile-drawer"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
