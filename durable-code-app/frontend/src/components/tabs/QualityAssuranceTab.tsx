/**
 * Purpose: Quality Assurance tab component showcasing code quality tools and metrics
 * Scope: React component for displaying QA practices, linter statistics, and CI/CD pipeline
 * Overview: Tab component that demonstrates comprehensive quality assurance capabilities including
 *     custom linter statistics, code quality metrics, CI/CD pipeline status, and automated testing
 *     results. Shows real-time metrics for magic number detection, file placement validation,
 *     print statement detection, and naming convention enforcement. Includes links to detailed
 *     reports and case studies demonstrating the effectiveness of the quality assurance process.
 * Dependencies: React (ReactElement), React Router (Link)
 * Exports: QualityAssuranceTab function component
 * Props/Interfaces: No props - self-contained tab content
 * State/Behavior: Static content display with navigation links to QA tools and reports
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
                <span className="stat-icon">⚠️</span> 6 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 4 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">🎯</div>
            <h5>Code Complexity</h5>
            <p>Detects excessive nesting and deep functions</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 4 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✔️</span> 3 fixed
              </span>
            </div>
          </div>
        </div>

        <div className="linter-actions">
          <Link
            to="/custom-linters?return=Quality Assurance"
            className="action-button primary"
          >
            <span className="button-icon">🔍</span>
            View All Linters
          </Link>
          <a
            href="linter-violations-case-study.html?return=Quality Assurance"
            className="action-button secondary"
          >
            <span className="button-icon">📊</span>
            Case Studies
          </a>
        </div>
      </div>

      <div className="pipeline-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🚀</span>
            CI/CD Pipeline
          </h4>
          <div className="showcase-badge success">All Passing</div>
        </div>

        <div className="pipeline-stages">
          <div className="stage-card">
            <div className="stage-status success">✔</div>
            <div className="stage-content">
              <h5>Build</h5>
              <p>Compile & Bundle</p>
              <span className="stage-time">2m 14s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✔</div>
            <div className="stage-content">
              <h5>Test</h5>
              <p>Unit & Integration</p>
              <span className="stage-time">3m 45s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✔</div>
            <div className="stage-content">
              <h5>Analyze</h5>
              <p>SOLID & Patterns</p>
              <span className="stage-time">1m 32s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✔</div>
            <div className="stage-content">
              <h5>Deploy</h5>
              <p>Production Ready</p>
              <span className="stage-time">45s</span>
            </div>
          </div>
        </div>

        <div className="pipeline-features">
          <div className="pipeline-feature">
            <div className="feature-icon">🤖</div>
            <h5>AI-Powered Checks</h5>
            <p>SOLID principles validation with intelligent analysis</p>
          </div>
          <div className="pipeline-feature">
            <div className="feature-icon">🎨</div>
            <h5>Pattern Analysis</h5>
            <p>Ensures proper design pattern implementation</p>
          </div>
          <div className="pipeline-feature">
            <div className="feature-icon">📈</div>
            <h5>Coverage Tracking</h5>
            <p>Enforces minimum 80% test coverage</p>
          </div>
          <div className="pipeline-feature">
            <div className="feature-icon">⚡</div>
            <h5>Performance Tests</h5>
            <p>Automated benchmarking and regression detection</p>
          </div>
        </div>

        <div className="pipeline-actions">
          <a
            href="ci-cd-pipeline.html?return=Quality Assurance"
            className="action-button primary"
          >
            <span className="button-icon">🔄</span>
            View Pipeline
          </a>
          <a
            href="ocp-case-study.html?return=Quality Assurance"
            className="action-button secondary"
          >
            <span className="button-icon">📚</span>
            OCP Case Study
          </a>
        </div>
      </div>

      <div className="commands-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">⚙️</span>
            Quick Commands
          </h4>
        </div>
        <div className="command-grid">
          <div className="command-item">
            <code>make check-design</code>
            <p>Run all design checks</p>
          </div>
          <div className="command-item">
            <code>make lint-custom</code>
            <p>Run custom linters</p>
          </div>
          <div className="command-item">
            <code>make test-coverage</code>
            <p>Generate coverage report</p>
          </div>
          <div className="command-item">
            <code>make validate-solid</code>
            <p>Check SOLID principles</p>
          </div>
        </div>
      </div>
    </div>
  );
}
