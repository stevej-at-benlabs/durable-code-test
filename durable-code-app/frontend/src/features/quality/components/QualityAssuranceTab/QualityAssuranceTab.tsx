/**
 * Purpose: Quality Assurance tab for code quality tools and metrics
 * Scope: React component for QA practices and linter statistics
 * Overview: Simplified extraction of QA tab maintaining original functionality
 * Dependencies: React, React Router
 * Exports: QualityAssuranceTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Direct port from original with CSS classes preserved
 */

import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';

export function QualityAssuranceTab(): ReactElement {
  return (
    <div className="tab-content qa-content">
      <div className="qa-hero">
        <h3 className="qa-title">
          <span className="title-icon">🛡️</span>
          Bulletproof Code Quality
        </h3>
        <p className="qa-subtitle">
          Comprehensive automated testing, custom linting, and AI-powered validation to
          ensure your code meets the highest standards
        </p>
      </div>

      <div className="linters-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🔍</span>
            Custom Linters
          </h4>
          <div className="showcase-badge">18+ Active</div>
        </div>

        <div className="linter-cards">
          <div className="linter-card">
            <div className="linter-icon">🔢</div>
            <h5>Magic Number Detection</h5>
            <p>Identifies hardcoded values and complex literals</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 12 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 8 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">📁</div>
            <h5>File Organization</h5>
            <p>Ensures proper module structure and placement</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 3 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 3 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">🖨️</div>
            <h5>Print & Console Output</h5>
            <p>Detects print statements and console methods</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 5 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 5 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">📊</div>
            <h5>Logging Standards</h5>
            <p>Enforces structured logging with Loguru</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 9 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 7 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">🏗️</div>
            <h5>SOLID Principles</h5>
            <p>Validates SRP, class size, and dependencies</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 18 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 15 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">📏</div>
            <h5>Naming Conventions</h5>
            <p>Enforces consistent naming standards</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 7 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 7 fixed
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card success">
          <div className="metric-icon">🎯</div>
          <div className="metric-value">99.2%</div>
          <div className="metric-label">Code Coverage</div>
        </div>
        <div className="metric-card info">
          <div className="metric-icon">⚡</div>
          <div className="metric-value">A+</div>
          <div className="metric-label">Code Quality</div>
        </div>
        <div className="metric-card warning">
          <div className="metric-icon">🐛</div>
          <div className="metric-value">0.3</div>
          <div className="metric-label">Bugs per KLOC</div>
        </div>
        <div className="metric-card success">
          <div className="metric-icon">✅</div>
          <div className="metric-value">100%</div>
          <div className="metric-label">CI/CD Pass Rate</div>
        </div>
      </div>

      <div className="pipeline-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🚀</span>
            CI/CD Pipeline
          </h4>
          <div className="showcase-badge">All Systems Go</div>
        </div>

        <div className="pipeline-stages">
          <div className="stage-item completed">
            <div className="stage-icon">📦</div>
            <div className="stage-name">Build</div>
            <div className="stage-time">1.2s</div>
          </div>
          <div className="stage-item completed">
            <div className="stage-icon">🔍</div>
            <div className="stage-name">Lint</div>
            <div className="stage-time">0.8s</div>
          </div>
          <div className="stage-item completed">
            <div className="stage-icon">🧪</div>
            <div className="stage-name">Test</div>
            <div className="stage-time">2.4s</div>
          </div>
          <div className="stage-item completed">
            <div className="stage-icon">🛡️</div>
            <div className="stage-name">Security</div>
            <div className="stage-time">1.1s</div>
          </div>
          <div className="stage-item completed">
            <div className="stage-icon">🚀</div>
            <div className="stage-name">Deploy</div>
            <div className="stage-time">3.2s</div>
          </div>
        </div>
      </div>

      <div className="reports-section">
        <h4 className="section-title">
          <span className="section-icon">📊</span>
          Latest Reports
        </h4>
        <div className="reports-grid">
          <a href="/reports/linter-summary.html" className="report-card">
            <div className="report-icon">📋</div>
            <h5>Linter Summary</h5>
            <p>Comprehensive analysis of all linting results</p>
            <span className="report-link">View Report →</span>
          </a>
          <a href="/reports/test-coverage.html" className="report-card">
            <div className="report-icon">📈</div>
            <h5>Test Coverage</h5>
            <p>Detailed coverage metrics and gaps analysis</p>
            <span className="report-link">View Report →</span>
          </a>
          <Link to="/standards?return=QualityAssurance" className="report-card">
            <div className="report-icon">🎯</div>
            <h5>Standards Check</h5>
            <p>Compliance with coding standards and best practices</p>
            <span className="report-link">View Standards →</span>
          </Link>
        </div>
      </div>

      <div className="case-study-section">
        <div className="case-study-card">
          <h4 className="case-study-title">
            <span className="case-icon">💡</span>
            Real Impact: From 87 Issues to Zero
          </h4>
          <p className="case-study-content">
            Our custom linting framework identified and auto-fixed 87 code quality
            issues in a legacy codebase, improving maintainability scores by 43% and
            reducing bug reports by 68% in the first month.
          </p>
          <div className="case-study-stats">
            <div className="stat">
              <span className="stat-value">87→0</span>
              <span className="stat-label">Issues Fixed</span>
            </div>
            <div className="stat">
              <span className="stat-value">43%↑</span>
              <span className="stat-label">Maintainability</span>
            </div>
            <div className="stat">
              <span className="stat-value">68%↓</span>
              <span className="stat-label">Bug Reports</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
