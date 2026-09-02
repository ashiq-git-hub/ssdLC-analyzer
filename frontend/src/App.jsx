import { useState } from "react";
import "./App.css";

const domains = [
  {
    name: "Requirements",
    short: "REQ",
    description: "Security requirements and policies",
  },
  {
    name: "Architecture",
    short: "ARC",
    description: "Threat modeling and system design",
  },
  {
    name: "Implementation",
    short: "IMP",
    description: "Code security and secrets",
  },
  {
    name: "Testing",
    short: "TST",
    description: "Security and automated testing",
  },
];

function Icon({ type, size = 18 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.8",
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };

  const icons = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),

    scan: (
      <>
        <circle cx="11" cy="11" r="6" />
        <path d="m16 16 5 5" />
        <path d="M8.5 11h5" />
        <path d="M11 8.5v5" />
      </>
    ),

    shield: (
      <>
        <path d="M12 3 20 6v5c0 5.2-3.4 8.5-8 10-4.6-1.5-8-4.8-8-10V6l8-3Z" />
        <path d="m8.5 12 2.2 2.2 4.8-5" />
      </>
    ),

    file: (
      <>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
        <path d="M14 2v6h6" />
        <path d="M8 13h8" />
        <path d="M8 17h5" />
      </>
    ),

    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5v.1h-2.6v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1A1.7 1.7 0 0 0 8 15a1.7 1.7 0 0 0-1.5-1H6.4v-2.6h.1A1.7 1.7 0 0 0 8 10a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.5v-.1H15v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1h.1V14h-.1a1.7 1.7 0 0 0-1.5 1Z" />
      </>
    ),

    upload: (
      <>
        <path d="M12 16V4" />
        <path d="m7 9 5-5 5 5" />
        <path d="M5 20h14" />
      </>
    ),

    check: (
      <>
        <path d="m5 12 4 4L19 6" />
      </>
    ),

    x: (
      <>
        <path d="m7 7 10 10" />
        <path d="m17 7-10 10" />
      </>
    ),

    arrow: (
      <>
        <path d="M5 12h14" />
        <path d="m13 6 6 6-6 6" />
      </>
    ),

    activity: (
      <>
        <path d="M3 12h4l3-8 4 16 3-8h4" />
      </>
    ),

    package: (
      <>
        <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" />
        <path d="m4.5 7.8 7.5 4.2 7.5-4.2" />
        <path d="M12 12v9" />
      </>
    ),
  };

  return <svg {...common}>{icons[type]}</svg>;
}

function App() {
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".zip")) {
      setError("Only ZIP repositories are supported.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError("");
    setResults(null);
  };

  const handleScan = async () => {
    if (!file) {
      setError("Select a project ZIP before starting the analysis.");
      return;
    }

    setScanning(true);
    setError("");
    setResults(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/scan", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Scan failed.");
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setResults(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the SSDLC Analyzer API."
      );
    } finally {
      setScanning(false);
    }
  };

  const getDomainResults = (domain) => {
    if (!results?.results) return [];

    return results.results.filter(
      (result) => result.domain === domain
    );
  };

  const getDomainScore = (domain) => {
    const checks = getDomainResults(domain);

    if (!checks.length) return 0;

    const passed = checks.filter(
      (check) => check.passed
    ).length;

    return Math.round((passed / checks.length) * 100);
  };

  const passedCount =
    results?.results?.filter((result) => result.passed).length || 0;

  const failedCount =
    results?.results?.filter((result) => !result.passed).length || 0;

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-mark">
            <Icon type="shield" size={21} />
          </div>

          <div>
            <div className="brand-name">
              SSDLC<span> Analyzer</span>
            </div>
            <div className="brand-version">SECURITY PLATFORM</div>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-label">WORKSPACE</div>

          <button className="nav-item active">
            <Icon type="grid" />
            <span>Overview</span>
          </button>

          <button className="nav-item">
            <Icon type="scan" />
            <span>Repository Scan</span>
          </button>

          <button className="nav-item">
            <Icon type="activity" />
            <span>Security Checks</span>
          </button>
        </div>

        <div className="sidebar-section">
          <div className="sidebar-label">ASSESSMENT</div>

          {domains.map((domain) => (
            <button className="nav-item" key={domain.name}>
              <span className="nav-code">{domain.short}</span>
              <span>{domain.name}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">

          <div className="system-status">
            <span className="status-dot"></span>

            <div>
              <strong>Analyzer Online</strong>
              <span>API connection ready</span>
            </div>
          </div>

          <button className="nav-item">
            <Icon type="settings" />
            <span>Settings</span>
          </button>

        </div>
      </aside>

      {/* MAIN AREA */}
      <div className="main-area">

        {/* TOP BAR */}
        <header className="topbar">

          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-separator">/</span>
            <strong>Security Assessment</strong>
          </div>

          <div className="topbar-right">

            <div className="live-indicator">
              <span></span>
              Local scanner
            </div>

            <div className="version-pill">
              v1.0.0
            </div>

          </div>
        </header>

        <main className="content">

          {/* HERO */}
          <section className="hero-section">

            <div className="hero-copy">

              <div className="eyebrow">
                <span className="eyebrow-line"></span>
                SECURE DEVELOPMENT ASSESSMENT
              </div>

              <h1>
                Understand how secure
                <br />
                your software really is.
              </h1>

              <p>
                Analyze a repository against core Secure Software
                Development Lifecycle practices and identify
                security gaps before they become vulnerabilities.
              </p>

              <div className="hero-stats">

                <div>
                  <strong>8</strong>
                  <span>Security checks</span>
                </div>

                <div>
                  <strong>4</strong>
                  <span>SSDLC domains</span>
                </div>

                <div>
                  <strong>100%</strong>
                  <span>Local analysis</span>
                </div>

              </div>

            </div>

            {/* UPLOAD PANEL */}
            <div className="scan-panel">

              <div className="panel-header">
                <div>
                  <span className="panel-kicker">
                    NEW ASSESSMENT
                  </span>

                  <h2>Scan repository</h2>
                </div>

                <div className="panel-icon">
                  <Icon type="scan" size={20} />
                </div>
              </div>

              <label
                className={`drop-zone ${
                  file ? "has-file" : ""
                }`}
              >

                <input
                  type="file"
                  accept=".zip"
                  onChange={handleFileChange}
                />

                <div className="upload-circle">
                  <Icon type="upload" size={23} />
                </div>

                {file ? (
                  <>
                    <strong>{file.name}</strong>
                    <span>
                      Repository ready for analysis
                    </span>

                    <div className="file-meta">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                      <span>•</span>
                      ZIP archive
                    </div>
                  </>
                ) : (
                  <>
                    <strong>
                      Drop your repository here
                    </strong>

                    <span>
                      or click to browse your computer
                    </span>

                    <div className="file-meta">
                      ZIP files only
                      <span>•</span>
                      Local processing
                    </div>
                  </>
                )}

              </label>

              <button
                className="primary-button"
                onClick={handleScan}
                disabled={scanning || !file}
              >

                {scanning ? (
                  <>
                    <span className="button-spinner"></span>
                    Analyzing repository
                  </>
                ) : (
                  <>
                    Start security analysis
                    <Icon type="arrow" size={18} />
                  </>
                )}

              </button>

              {error && (
                <div className="error-message">
                  <Icon type="x" size={16} />
                  <span>{error}</span>
                </div>
              )}

              <div className="privacy-note">
                <Icon type="shield" size={14} />
                Repository contents are analyzed locally.
              </div>

            </div>

          </section>

          {/* SCANNING STATE */}
          {scanning && (
            <section className="scanning-panel">

              <div className="scan-animation">
                <div className="scan-ring"></div>
                <div className="scan-ring ring-two"></div>

                <div className="scan-center">
                  <Icon type="shield" size={25} />
                </div>
              </div>

              <div className="scanning-copy">
                <span className="panel-kicker">
                  ANALYSIS IN PROGRESS
                </span>

                <h2>Inspecting your repository</h2>

                <p>
                  Running static analysis, secret detection,
                  architecture checks and security tests.
                </p>
              </div>

              <div className="scan-progress">
                <span></span>
              </div>

            </section>
          )}

          {/* RESULTS */}
          {results && !scanning && (
            <section className="results-section">

              {/* SCORE HEADER */}
              <div className="results-heading">

                <div>
                  <div className="eyebrow">
                    <span className="eyebrow-line"></span>
                    ASSESSMENT COMPLETE
                  </div>

                  <h2>Security assessment</h2>

                  <p>
                    Analysis results for{" "}
                    <strong>
                      {file?.name || "repository"}
                    </strong>
                  </p>
                </div>

                <button
                  className="secondary-button"
                  onClick={() => {
                    setResults(null);
                    setFile(null);
                  }}
                >
                  New assessment
                </button>

              </div>

              {/* SCORE OVERVIEW */}
              <div className="overview-grid">

                <div className="score-card-large">

                  <div className="score-info">

                    <span className="panel-kicker">
                      OVERALL SECURITY SCORE
                    </span>

                    <div className="big-score">
                      {results.score}
                      <span>%</span>
                    </div>

                    <p>
                      {results.passed_checks} of{" "}
                      {results.total_checks} security checks
                      passed.
                    </p>

                  </div>

                  <div
                    className="score-donut"
                    style={{
                      "--score": `${results.score * 3.6}deg`,
                    }}
                  >
                    <div className="score-donut-inner">
                      <strong>{results.score}</strong>
                      <span>score</span>
                    </div>
                  </div>

                </div>

                <div className="metric-card">

                  <div className="metric-icon success">
                    <Icon type="check" />
                  </div>

                  <span>Checks passed</span>

                  <strong>{passedCount}</strong>

                  <small>
                    Controls meeting the expected criteria
                  </small>

                </div>

                <div className="metric-card">

                  <div className="metric-icon danger">
                    <Icon type="x" />
                  </div>

                  <span>Checks requiring attention</span>

                  <strong>{failedCount}</strong>

                  <small>
                    Security controls that need improvement
                  </small>

                </div>

              </div>

              {/* DOMAINS */}
              <div className="section-heading">

                <div>
                  <span className="panel-kicker">
                    SECURITY FRAMEWORK
                  </span>

                  <h2>SSDLC domains</h2>
                </div>

                <span className="section-count">
                  4 domains
                </span>

              </div>

              <div className="domain-grid">

                {domains.map((domain, index) => {
                  const score = getDomainScore(domain.name);
                  const checks = getDomainResults(domain.name);
                  const passed = checks.filter(
                    (check) => check.passed
                  ).length;

                  return (
                    <div
                      className="domain-card"
                      key={domain.name}
                      style={{
                        "--delay": `${index * 80}ms`,
                      }}
                    >

                      <div className="domain-top">

                        <div className="domain-number">
                          0{index + 1}
                        </div>

                        <div
                          className={`domain-status ${
                            score === 100
                              ? "complete"
                              : score > 0
                              ? "partial"
                              : "failed"
                          }`}
                        >
                          {score === 100
                            ? "PASS"
                            : score > 0
                            ? "REVIEW"
                            : "FAILED"}
                        </div>

                      </div>

                      <h3>{domain.name}</h3>

                      <p>{domain.description}</p>

                      <div className="domain-score-row">
                        <strong>{score}%</strong>

                        <span>
                          {passed}/{checks.length} passed
                        </span>
                      </div>

                      <div className="progress-track">
                        <div
                          className={`progress-value ${
                            score === 100
                              ? "complete"
                              : ""
                          }`}
                          style={{
                            width: `${score}%`,
                          }}
                        ></div>
                      </div>

                    </div>
                  );
                })}

              </div>

              {/* DETAILED CHECKS */}
              <div className="section-heading detailed-heading">

                <div>
                  <span className="panel-kicker">
                    CONTROL RESULTS
                  </span>

                  <h2>Detailed security checks</h2>
                </div>

                <span className="section-count">
                  {results.total_checks} checks
                </span>

              </div>

              <div className="checks-list">

                {results.results.map((result, index) => (
                  <div
                    className="check-row"
                    key={index}
                    style={{
                      "--delay": `${index * 45}ms`,
                    }}
                  >

                    <div
                      className={`result-icon ${
                        result.passed
                          ? "passed"
                          : "failed"
                      }`}
                    >
                      <Icon
                        type={
                          result.passed ? "check" : "x"
                        }
                        size={17}
                      />
                    </div>

                    <div className="check-main">

                      <div className="check-title-row">
                        <strong>{result.name}</strong>

                        <span className="domain-tag">
                          {result.domain}
                        </span>
                      </div>

                      <p>{result.detail}</p>

                    </div>

                    <div
                      className={`result-label ${
                        result.passed
                          ? "passed"
                          : "failed"
                      }`}
                    >
                      {result.passed
                        ? "PASS"
                        : "ACTION REQUIRED"}
                    </div>

                  </div>
                ))}

              </div>

            </section>
          )}

          {/* EMPTY STATE */}
          {!results && !scanning && (
            <section className="framework-section">

              <div className="section-heading">

                <div>
                  <span className="panel-kicker">
                    WHAT WE CHECK
                  </span>

                  <h2>Security assessment framework</h2>

                  <p>
                    Your repository is evaluated across four
                    areas of the secure development lifecycle.
                  </p>
                </div>

              </div>

              <div className="framework-grid">

                {domains.map((domain, index) => (
                  <div
                    className="framework-card"
                    key={domain.name}
                  >

                    <div className="framework-number">
                      0{index + 1}
                    </div>

                    <div className="framework-icon">
                      <Icon type="shield" size={20} />
                    </div>

                    <h3>{domain.name}</h3>

                    <p>{domain.description}</p>

                    <span>
                      Explore checks
                      <Icon type="arrow" size={15} />
                    </span>

                  </div>
                ))}

              </div>

            </section>
          )}

        </main>

        <footer className="footer">
          <span>SSDLC Analyzer</span>
          <span>Secure Development Assessment Platform</span>
          <span>v1.0.0</span>
        </footer>

      </div>
    </div>
  );
}

export default App;