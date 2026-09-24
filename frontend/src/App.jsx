import { useState, useEffect } from 'react';
import './App.css';

// Components
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import Hero from './components/Hero';
import UploadPanel from './components/UploadPanel';
import ScanningView from './components/ScanningView';
import ResultsView from './components/ResultsView';
import CommandPalette from './components/CommandPalette';
import Toast from './components/Toast';
import AssessmentsList from './components/AssessmentsList';
import FindingDrawer from './components/FindingDrawer';

// API Configuration - supports both localhost and 127.0.0.1
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  // File & Scan state
  const [selectedFile, setSelectedFile] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [scanError, setScanError] = useState('');

  // Backend health state
  const [backendOnline, setBackendOnline] = useState(true);

  // Domain filter state
  const [activeDomainFilter, setActiveDomainFilter] = useState(null);

  // Toast notifications
  const [toasts, setToasts] = useState([]);

  // Drawer state
  const [selectedFinding, setSelectedFinding] = useState(null);

  // Scan history
  const [scanHistory, setScanHistory] = useState([]);

  // Command palette keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, {
          method: 'GET',
        });
        if (response.ok) {
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch (error) {
        setBackendOnline(false);
        console.warn('Backend health check failed:', error);
      }
    };

    checkBackendHealth();
  }, []);

  // Load scan history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/scans`);
        if (response.ok) {
          const data = await response.json();
          setScanHistory(data.scans || []);
        }
      } catch (error) {
        console.error('Failed to load scan history:', error);
      }
    };

    if (activeTab === 'assessments') {
      loadHistory();
    }
  }, [activeTab]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 4000);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setScanError('');
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setScanError('');
  };

  const handleStartScan = async () => {
    if (!selectedFile) {
      setScanError('Please select a ZIP file to scan');
      return;
    }

    setIsScanning(true);
    setScanError('');
    setScanResults(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/scan`, {
        method: 'POST',
        body: formData,
      });

      // Check if response is ok before parsing JSON
      if (!response.ok) {
        // Try to parse error response
        let errorMessage = 'Scan failed';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // If JSON parsing fails, use status text
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Simulate additional scan time for better UX
      await new Promise((resolve) => setTimeout(resolve, 1500));

      setScanResults(data);
      addToast('Security assessment completed successfully', 'success');
    } catch (error) {
      // Improved error handling with specific messages
      let userMessage = '';

      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        // Network error - backend unreachable
        userMessage = 'Unable to connect to the SSDLC Analyzer backend. Please ensure the FastAPI server is running on port 8000.';
        setBackendOnline(false);
      } else if (error.message.includes('Failed to fetch')) {
        // CORS or network error
        userMessage = 'Network error: Cannot reach the analyzer backend. Check that the backend is running and CORS is configured.';
        setBackendOnline(false);
      } else if (error.message.includes('ZIP') || error.message.includes('archive')) {
        // File format error
        userMessage = `Invalid file: ${error.message}`;
      } else if (error.message.includes('HTTP 413')) {
        // File too large
        userMessage = 'File too large: The uploaded ZIP exceeds the maximum size limit (100 MB).';
      } else if (error.message.includes('HTTP 4')) {
        // Client error
        userMessage = `Request error: ${error.message}`;
      } else if (error.message.includes('HTTP 5')) {
        // Server error
        userMessage = `Server error: ${error.message}. The analyzer encountered an internal error.`;
      } else {
        // Use the actual error message
        userMessage = error.message || 'An unexpected error occurred during scanning';
      }

      setScanError(userMessage);
      addToast(userMessage, 'error');
      console.error('Scan error:', error);
    } finally {
      setIsScanning(false);
    }
  };

  const handleNewScan = () => {
    setScanResults(null);
    setSelectedFile(null);
    setScanError('');
    setActiveDomainFilter(null);
    setActiveTab('overview');
  };

  const handleSelectScan = async (scanId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/scans/${scanId}`);
      if (response.ok) {
        const data = await response.json();
        setScanResults(data);
        setSelectedFile({ name: data.project || 'Repository' });
        setActiveTab('overview');
        addToast('Scan loaded successfully', 'success');
      } else {
        throw new Error('Failed to load scan');
      }
    } catch (error) {
      addToast('Failed to load scan', 'error');
    }
  };

  const handleDeleteScan = async (scanId) => {
    if (!confirm('Delete this assessment? This action cannot be undone.')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/scans/${scanId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setScanHistory((prev) => prev.filter((s) => s.scan_id !== scanId));
        addToast('Assessment deleted', 'success');
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      addToast('Failed to delete assessment', 'error');
    }
  };

  const handleNavigate = (tab) => {
    setActiveTab(tab);
    setIsMobileMenuOpen(false);
  };

  const handleSelectDomain = (domainName) => {
    setActiveDomainFilter(domainName);
    setActiveTab('overview');
  };

  const renderContent = () => {
    // Assessments list view
    if (activeTab === 'assessments') {
      return (
        <AssessmentsList
          scans={scanHistory}
          onSelectScan={handleSelectScan}
          onDeleteScan={handleDeleteScan}
          onNewScan={handleNewScan}
          isLoading={false}
        />
      );
    }

    // Findings view (same as results but filtered)
    if (activeTab === 'findings' && scanResults) {
      return (
        <ResultsView
          results={scanResults}
          fileName={selectedFile?.name}
          onNewScan={handleNewScan}
          activeDomainFilter={activeDomainFilter}
          onSelectFinding={setSelectedFinding}
          onToast={addToast}
        />
      );
    }

    // Main flow: Hero -> Upload -> Scanning -> Results
    return (
      <>
        {!selectedFile && !isScanning && !scanResults && (
          <div className="hero-section">
            <Hero
              onStartAssessment={() => {
                const uploadElem = document.querySelector('.upload-panel-wrapper');
                if (uploadElem) uploadElem.scrollIntoView({ behavior: 'smooth' });
              }}
              onViewAssessments={() => setActiveTab('assessments')}
            />
            <UploadPanel
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClearFile={handleClearFile}
              isScanning={isScanning}
              onStartScan={handleStartScan}
            />
          </div>
        )}

        {selectedFile && !isScanning && !scanResults && (
          <div className="hero-section">
            <Hero
              onStartAssessment={handleStartScan}
              onViewAssessments={() => setActiveTab('assessments')}
            />
            <UploadPanel
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onClearFile={handleClearFile}
              isScanning={isScanning}
              onStartScan={handleStartScan}
            />
          </div>
        )}

        {isScanning && (
          <ScanningView projectName={selectedFile?.name} />
        )}

        {scanResults && !isScanning && (
          <ResultsView
            results={scanResults}
            fileName={selectedFile?.name}
            onNewScan={handleNewScan}
            activeDomainFilter={activeDomainFilter}
            onSelectFinding={setSelectedFinding}
            onToast={addToast}
          />
        )}
      </>
    );
  };

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={handleNavigate}
        isMobileOpen={isMobileMenuOpen}
        setIsMobileOpen={setIsMobileMenuOpen}
        onNewScan={handleNewScan}
        historyCount={scanHistory.length}
        activeDomainFilter={activeDomainFilter}
        setActiveDomainFilter={setActiveDomainFilter}
        hasResults={!!scanResults}
      />

      {/* Main Area */}
      <div className="main-area">
        {/* Topbar */}
        <Topbar
          onMenuClick={() => setIsMobileMenuOpen(true)}
          activeTab={activeTab}
          projectName={selectedFile?.name}
          isScanning={isScanning}
          hasResults={!!scanResults}
          onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        />

        {/* Content */}
        <div className="content-container">
          {renderContent()}
        </div>

        {/* Footer */}
        <footer className="app-footer">
          <span>SSDLC Analyzer v2.0.0</span>
          <span>•</span>
          <span>Secure Development Assessment Platform</span>
          {!backendOnline && (
            <>
              <span>•</span>
              <span style={{ color: 'var(--color-danger)' }}>⚠ Backend Offline</span>
            </>
          )}
        </footer>
      </div>

      {/* Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNavigate={handleNavigate}
        onStartNewScan={handleNewScan}
        onSelectDomain={handleSelectDomain}
        hasResults={!!scanResults}
      />

      {/* Toast Notifications */}
      <Toast toasts={toasts} onDismiss={dismissToast} />

      {/* Finding Drawer */}
      {selectedFinding && (
        <FindingDrawer
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
          onCopySuccess={addToast}
        />
      )}
    </div>
  );
}

export default App;
