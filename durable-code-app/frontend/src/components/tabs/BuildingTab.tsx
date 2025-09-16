import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';

export function BuildingTab(): ReactElement {
  return (
    <div className="tab-content building-content">
      <div className="building-hero">
        <div className="hero-icon">⚡</div>
        <h3 className="building-title">AI-Powered Code Generation</h3>
        <p className="building-subtitle">
          Accelerate development with intelligent boilerplate generation and automated
          tooling
        </p>
      </div>

      <div className="cli-showcase">
        <div className="cli-header">
          <h4>
            <span className="cli-icon">⚡</span>
            Slash Commands
          </h4>
          <div className="cli-badge">3 Available</div>
        </div>

        <div className="command-cards">
          <div className="command-card">
            <div className="command-header">
              <span className="command-icon">🧩</span>
              <span className="command-type">Generation</span>
            </div>
            <code className="command-syntax">
              $ /new-code Create a user authentication system with login and
              registration
            </code>
            <p className="command-desc">
              Generate production-ready code with proper structure and standards
            </p>
          </div>

          <div className="command-card">
            <div className="command-header">
              <span className="command-icon">🎯</span>
              <span className="command-type">Quality</span>
            </div>
            <code className="command-syntax">$ /solid</code>
            <p className="command-desc">
              Run parallel AI agents to check SOLID principle violations
            </p>
          </div>

          <div className="command-card">
            <div className="command-header">
              <span className="command-icon">✅</span>
              <span className="command-type">Workflow</span>
            </div>
            <code className="command-syntax">$ /done [with merge]</code>
            <p className="command-desc">
              Complete workflow with optional auto-merge after all checks pass
            </p>
          </div>
        </div>
      </div>

      <div className="new-code-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🛠️</span>
            /new-code Capabilities
          </h4>
          <div className="showcase-badge">Smart Generation</div>
        </div>

        <div className="capability-cards">
          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🧩</span>
              <span className="capability-type">Component</span>
            </div>
            <code className="capability-syntax">
              /new-code Create a user profile component with avatar, bio, and contact
              information
            </code>
            <p className="capability-desc">
              Generate React/Vue/Angular components with props, state, and lifecycle
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🔧</span>
              <span className="capability-type">Service</span>
            </div>
            <code className="capability-syntax">
              /new-code Build an authentication service with JWT token management
            </code>
            <p className="capability-desc">
              Create service layers with dependency injection and error handling
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🧪</span>
              <span className="capability-type">Test</span>
            </div>
            <code className="capability-syntax">
              /new-code Write comprehensive tests for the payment processing module
            </code>
            <p className="capability-desc">
              Generate test suites with mocks, fixtures, and coverage setup
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🗄️</span>
              <span className="capability-type">API</span>
            </div>
            <code className="capability-syntax">
              /new-code Implement a REST API for managing user subscriptions and billing
            </code>
            <p className="capability-desc">
              Scaffold REST/GraphQL endpoints with validation and middleware
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🗃️</span>
              <span className="capability-type">Database</span>
            </div>
            <code className="capability-syntax">
              /new-code Design database models for an e-commerce product catalog
            </code>
            <p className="capability-desc">
              Create database schemas, migrations, and ORM models
            </p>
          </div>

          <div className="capability-card">
            <div className="capability-header">
              <span className="capability-icon">🎨</span>
              <span className="capability-type">UI/UX</span>
            </div>
            <code className="capability-syntax">
              /new-code Build a responsive dashboard with charts and data visualization
            </code>
            <p className="capability-desc">
              Generate styled components with responsive design and accessibility
            </p>
          </div>
        </div>
      </div>

      <div className="ai-commands-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">🤖</span>
            AI-Powered Slash Commands
          </h4>
          <div className="showcase-badge">New</div>
        </div>

        <div className="ai-command-cards">
          <div className="ai-command-card">
            <div className="ai-command-icon">🎯</div>
            <h5>/solid</h5>
            <p>Parallel AI agents analyze SOLID principle violations</p>
            <div className="ai-command-features">
              <span className="feature-tag">5 AI Agents</span>
              <span className="feature-tag">Parallel Analysis</span>
              <span className="feature-tag">Smart Reports</span>
            </div>
            <div className="ai-command-modes">
              <div className="mode-item">
                <code>/solid</code>
                <span>Current branch only</span>
              </div>
              <div className="mode-item">
                <code>/solid all code</code>
                <span>Comprehensive analysis</span>
              </div>
            </div>
          </div>

          <div className="ai-command-card">
            <div className="ai-command-icon">✅</div>
            <h5>/done</h5>
            <p>
              Complete workflow automation from commit to PR with optional auto-merge
            </p>
            <div className="ai-command-features">
              <span className="feature-tag">Auto Commit</span>
              <span className="feature-tag">Quality Checks</span>
              <span className="feature-tag">Auto Merge</span>
            </div>
            <div className="ai-command-modes">
              <div className="mode-item">
                <code>/done</code>
                <span>Create PR, wait for review</span>
              </div>
              <div className="mode-item">
                <code>/done with merge</code>
                <span>Auto-merge after all checks pass</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="features-showcase">
        <h4 className="section-title">
          <span className="section-icon">✨</span>
          Powerful Features
        </h4>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h5>Smart Detection</h5>
            <p>Automatically detects file type and generates appropriate boilerplate</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔄</div>
            <h5>Convention Aware</h5>
            <p>Follows your project's existing patterns and naming conventions</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🛡️</div>
            <h5>Error Handling</h5>
            <p>Built-in error handling and logging best practices</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📦</div>
            <h5>Import Management</h5>
            <p>Automatically includes necessary imports and dependencies</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h5>Documentation</h5>
            <p>Generates JSDoc/docstrings with parameter descriptions</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚙️</div>
            <h5>Configurable</h5>
            <p>Customize templates and rules via configuration files</p>
          </div>
        </div>
      </div>

      <div className="language-support">
        <h4 className="section-title">
          <span className="section-icon">🌐</span>
          Language Support
        </h4>
        <div className="language-grid">
          <div className="language-card typescript">
            <div className="language-icon">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <rect width="24" height="24" rx="3" fill="#3178c6" />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dy=".35em"
                  fill="white"
                  fontSize="14"
                  fontWeight="bold"
                >
                  TS
                </text>
              </svg>
            </div>
            <div className="language-name">TypeScript</div>
            <div className="language-ext">.ts, .tsx</div>
          </div>
          <div className="language-card javascript">
            <div className="language-icon">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <rect width="24" height="24" rx="3" fill="#f7df1e" />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dy=".35em"
                  fill="black"
                  fontSize="14"
                  fontWeight="bold"
                >
                  JS
                </text>
              </svg>
            </div>
            <div className="language-name">JavaScript</div>
            <div className="language-ext">.js, .jsx</div>
          </div>
          <div className="language-card python">
            <div className="language-icon">🐍</div>
            <div className="language-name">Python</div>
            <div className="language-ext">.py</div>
          </div>
          <div className="language-card go">
            <div className="language-icon">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <rect width="24" height="24" rx="3" fill="#00add8" />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dy=".35em"
                  fill="white"
                  fontSize="14"
                  fontWeight="bold"
                >
                  Go
                </text>
              </svg>
            </div>
            <div className="language-name">Go</div>
            <div className="language-ext">.go</div>
          </div>
          <div className="language-card rust">
            <div className="language-icon">🦀</div>
            <div className="language-name">Rust</div>
            <div className="language-ext">.rs</div>
          </div>
          <div className="language-card more">
            <div className="language-icon">➕</div>
            <div className="language-name">More</div>
            <div className="language-ext">20+ languages</div>
          </div>
        </div>
      </div>

      <div className="standards-section">
        <div className="standards-card">
          <div className="standards-header">
            <h4>
              <span className="standards-icon">📋</span>
              Development Standards
            </h4>
            <div className="standards-badge">Essential</div>
          </div>
          <div className="standards-grid">
            <div className="standard-item">
              <div className="standard-icon">📏</div>
              <div className="standard-content">
                <h5>Coding Conventions</h5>
                <p>Consistent naming, formatting, and structure</p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">🏗️</div>
              <div className="standard-content">
                <h5>Architecture Patterns</h5>
                <p>Approved design patterns and practices</p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">✅</div>
              <div className="standard-content">
                <h5>Quality Rules</h5>
                <p>Linting, type safety, and documentation</p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">🚀</div>
              <div className="standard-content">
                <h5>Best Practices</h5>
                <p>Security, performance, and maintainability</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="action-section">
        <h4 className="section-title">
          <span className="section-icon">🚀</span>
          Get Started
        </h4>
        <div className="action-links">
          <a href="tools/new-code/README.md" className="action-link primary">
            <span className="link-icon">📖</span>
            Documentation
          </a>
          <a
            href="https://github.com/yourusername/new-code"
            className="action-link secondary"
          >
            <span className="link-icon">💻</span>
            Source Code
          </a>
          <Link to="/standards?return=Building" className="action-link tertiary">
            <span className="link-icon">🎯</span>
            Standards Guide
          </Link>
        </div>
      </div>
    </div>
  );
}
