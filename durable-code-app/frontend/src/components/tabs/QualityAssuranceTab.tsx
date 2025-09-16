import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';

export function QualityAssuranceTab(): ReactElement {
  return (
    <div className="tab-content qa-content">
      <div className="qa-hero">
        <div className="qa-hero-icon">🛡️</div>
        <h3 className="qa-title">Bulletproof Code Quality</h3>
        <p className="qa-subtitle">
          Comprehensive automated testing, custom linting, and AI-powered validation to
          ensure your code meets the highest standards
        </p>
      </div>

      <div className="qa-metrics">
        <div className="metric-card">
          <div className="metric-value">99.9%</div>
          <div className="metric-label">Uptime</div>
          <div className="metric-trend">↑ 0.3%</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">95%</div>
          <div className="metric-label">Coverage</div>
          <div className="metric-trend">↑ 5%</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">0</div>
          <div className="metric-label">Critical Bugs</div>
          <div className="metric-trend">→ 0</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">A+</div>
          <div className="metric-label">Code Grade</div>
          <div className="metric-trend">↑ 1</div>
        </div>
      </div>

      <div className="linters-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🔍</span>
            Custom Linters
          </h4>
          <div className="showcase-badge">4 Active</div>
        </div>

        <div className="linter-cards">
          <div className="linter-card">
            <div className="linter-icon">🔢</div>
            <h5>Magic Number Detection</h5>
            <p>Identifies hardcoded values that should be constants</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 12 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✅</span> 8 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">📁</div>
            <h5>File Placement</h5>
            <p>Ensures files are in correct directories</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 3 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✅</span> 3 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">🖨️</div>
            <h5>Print Statements</h5>
            <p>Prevents debug statements in production</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 5 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✅</span> 5 fixed
              </span>
            </div>
          </div>

          <div className="linter-card">
            <div className="linter-icon">📝</div>
            <h5>Naming Conventions</h5>
            <p>Validates variable and function names</p>
            <div className="linter-stats">
              <span className="stat-item">
                <span className="stat-icon">⚠️</span> 7 found
              </span>
              <span className="stat-item">
                <span className="stat-icon">✅</span> 6 fixed
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
            <div className="stage-status success">✓</div>
            <div className="stage-content">
              <h5>Build</h5>
              <p>Compile & Bundle</p>
              <span className="stage-time">2m 14s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✓</div>
            <div className="stage-content">
              <h5>Test</h5>
              <p>Unit & Integration</p>
              <span className="stage-time">3m 45s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✓</div>
            <div className="stage-content">
              <h5>Analyze</h5>
              <p>SOLID & Patterns</p>
              <span className="stage-time">1m 32s</span>
            </div>
          </div>

          <div className="stage-connector"></div>

          <div className="stage-card">
            <div className="stage-status success">✓</div>
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
