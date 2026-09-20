import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Command,
  Sparkles,
  History,
  Layers,
  Activity,
  FileText,
  Shield,
  X,
  ArrowRight
} from './Icons';

export default function CommandPalette({
  isOpen,
  onClose,
  onNavigate,
  onStartNewScan,
  onSelectDomain,
  hasResults
}) {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);

  const actions = [
    {
      id: 'new-scan',
      title: 'Start New Security Assessment',
      subtitle: 'Upload a ZIP repository for SSDLC analysis',
      icon: Sparkles,
      action: () => {
        onStartNewScan();
        onClose();
      },
    },
    {
      id: 'nav-overview',
      title: 'Go to Overview',
      subtitle: 'View assessment summary and posture score',
      icon: Layers,
      action: () => {
        onNavigate('overview');
        onClose();
      },
    },
    {
      id: 'nav-assessments',
      title: 'View Scan History',
      subtitle: 'Browse previous security assessments',
      icon: History,
      action: () => {
        onNavigate('assessments');
        onClose();
      },
    },
    {
      id: 'nav-findings',
      title: 'Inspect Findings',
      subtitle: 'View detailed security checks and evidence',
      icon: Activity,
      disabled: !hasResults,
      action: () => {
        if (hasResults) {
          onNavigate('findings');
          onClose();
        }
      },
    },
    {
      id: 'filter-req',
      title: 'Filter: Requirements Domain',
      subtitle: 'Security requirements, threat models, compliance',
      icon: Shield,
      action: () => {
        onSelectDomain('Requirements');
        onClose();
      },
    },
    {
      id: 'filter-arc',
      title: 'Filter: Architecture Domain',
      subtitle: 'Attack surface, auth mechanisms, threat modeling',
      icon: Shield,
      action: () => {
        onSelectDomain('Architecture');
        onClose();
      },
    },
    {
      id: 'filter-imp',
      title: 'Filter: Implementation Domain',
      subtitle: 'Static analysis, hardcoded secrets, code safety',
      icon: Shield,
      action: () => {
        onSelectDomain('Implementation');
        onClose();
      },
    },
    {
      id: 'filter-tst',
      title: 'Filter: Testing Domain',
      subtitle: 'DAST, SAST coverage, security test suites',
      icon: Shield,
      action: () => {
        onSelectDomain('Testing');
        onClose();
      },
    },
    {
      id: 'filter-sup',
      title: 'Filter: Supply Chain Domain',
      subtitle: 'SCA, dependency vulnerabilities, SBOM',
      icon: Shield,
      action: () => {
        onSelectDomain('Supply Chain');
        onClose();
      },
    },
    {
      id: 'filter-lfc',
      title: 'Filter: Lifecycle Domain',
      subtitle: 'CI/CD gates, security policies, maintenance',
      icon: Shield,
      action: () => {
        onSelectDomain('Lifecycle');
        onClose();
      },
    },
  ];

  const filteredActions = actions.filter(
    (action) =>
      action.title.toLowerCase().includes(search.toLowerCase()) ||
      action.subtitle.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredActions.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredActions.length) % filteredActions.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const action = filteredActions[selectedIndex];
        if (action && !action.disabled) {
          action.action();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredActions, selectedIndex, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="command-palette-overlay" onClick={onClose}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="command-palette-backdrop"
        />

        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: -10 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          className="command-palette-modal"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Search Input */}
          <div className="command-input-row">
            <Search size={16} className="command-search-icon" />
            <input
              ref={inputRef}
              type="text"
              placeholder="Type a command or search actions..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setSelectedIndex(0);
              }}
              className="command-search-input"
            />
            <kbd className="command-esc-kbd">ESC</kbd>
          </div>

          {/* Action List */}
          <div className="command-actions-list">
            {filteredActions.length > 0 ? (
              filteredActions.map((action, idx) => {
                const Icon = action.icon;
                const isSelected = idx === selectedIndex;
                return (
                  <button
                    key={action.id}
                    className={`command-action-item ${isSelected ? 'selected' : ''} ${
                      action.disabled ? 'disabled' : ''
                    }`}
                    onClick={() => !action.disabled && action.action()}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    disabled={action.disabled}
                  >
                    <div className="command-item-icon">
                      <Icon size={16} />
                    </div>
                    <div className="command-item-content">
                      <div className="command-item-title">{action.title}</div>
                      <div className="command-item-subtitle">{action.subtitle}</div>
                    </div>
                    {isSelected && (
                      <ArrowRight size={14} className="command-item-arrow" />
                    )}
                  </button>
                );
              })
            ) : (
              <div className="command-no-results">
                <span>No commands matching "{search}"</span>
              </div>
            )}
          </div>

          {/* Footer Hints */}
          <div className="command-footer">
            <div className="command-hint">
              <kbd className="hint-kbd">↑↓</kbd>
              <span>Navigate</span>
            </div>
            <div className="command-hint">
              <kbd className="hint-kbd">↵</kbd>
              <span>Execute</span>
            </div>
            <div className="command-hint">
              <kbd className="hint-kbd">ESC</kbd>
              <span>Close</span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
