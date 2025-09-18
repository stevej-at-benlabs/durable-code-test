/**
 * Purpose: Building tab component showcasing development tools and coding practices
 * Scope: React component for displaying development methodologies and tool integrations
 * Overview: Tab component that demonstrates the building phase of AI-ready development
 *     including code generation tools, development workflows, testing strategies, and
 *     integration practices. Shows how AI tools can enhance productivity while maintaining
 *     code quality and following established development patterns and best practices.
 * Dependencies: React (ReactElement)
 * Exports: BuildingTab function component
 * Props/Interfaces: No props - self-contained tab content
 * State/Behavior: Static content display with development tools and methodology examples
 */
import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';

export function BuildingTab(): ReactElement {
  return (
    <div className="tab-content building-content">
      <div className="building-hero">
        <div className="hero-icon">⚡</div>
        <h3 className="building-title">AI-Powered Code Generation</h3>
        <p className="building-subtitle">
          Build complete applications without writing a single line of code - powered by
          AI-driven development and intelligent automation
        </p>
      </div>

      <div className="cli-showcase">
        <div className="cli-header">
          <h4>
            <span className="cli-icon">⚡</span>
            Slash Commands
          </h4>
          <div className="cli-badge">4 Available</div>
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

          <div className="command-card">
            <div className="command-header">
              <span className="command-icon">❓</span>
              <span className="command-type">Analysis</span>
            </div>
            <code className="command-syntax">
              $ /ask How does the authentication work?
            </code>
            <p className="command-desc">
              Ask questions and get AI-powered insights about your codebase
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

      <div className="ai-templates-showcase">
        <h4 className="section-title">
          <span className="section-icon">📄</span>
          AI Templates (.ai/templates)
        </h4>
        <div className="templates-grid">
          <div className="template-card">
            <div className="template-icon">🔧</div>
            <h5>linting-rule.py</h5>
            <p>Create custom design linting rules for code quality enforcement</p>
          </div>
          <div className="template-card">
            <div className="template-icon">⚛️</div>
            <h5>react-component.tsx</h5>
            <p>Generate React components with proper typing and structure</p>
          </div>
          <div className="template-card">
            <div className="template-icon">🗂️</div>
            <h5>web-tab.tsx</h5>
            <p>Build new web application tabs with consistent UI patterns</p>
          </div>
          <div className="template-card">
            <div className="template-icon">🚀</div>
            <h5>fastapi-endpoint.py</h5>
            <p>Scaffold FastAPI endpoints with validation and error handling</p>
          </div>
          <div className="template-card">
            <div className="template-icon">🧪</div>
            <h5>test-suite.py</h5>
            <p>Create comprehensive test suites with fixtures and coverage</p>
          </div>
          <div className="template-card">
            <div className="template-icon">🔌</div>
            <h5>websocket-endpoint.py</h5>
            <p>Implement WebSocket endpoints for real-time communication</p>
          </div>
          <div className="template-card">
            <div className="template-icon">📋</div>
            <h5>workflow.html</h5>
            <p>Document development workflows with interactive HTML templates</p>
          </div>
        </div>
      </div>

      <div className="howto-guides-showcase">
        <h4 className="section-title">
          <span className="section-icon">📚</span>
          How-To Guides (.ai/howto)
        </h4>
        <div className="howto-grid">
          <div className="howto-card">
            <div className="howto-icon">🐛</div>
            <h5>Complete Debugging Guide</h5>
            <p>
              Comprehensive strategies for troubleshooting and debugging with AI
              assistance
            </p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">✨</div>
            <h5>Create Custom Linter</h5>
            <p>
              Build your own design linting rules to enforce project-specific standards
            </p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">🚀</div>
            <h5>Deploy Application</h5>
            <p>Step-by-step deployment guide for production environments</p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">🔀</div>
            <h5>GitHub Merge Workflow</h5>
            <p>Automated PR creation and merge workflows with AI validation</p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">🔍</div>
            <h5>Run Linting</h5>
            <p>Execute comprehensive linting checks across your entire codebase</p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">🧪</div>
            <h5>Run Tests</h5>
            <p>Testing strategies and commands for different test suites</p>
          </div>
          <div className="howto-card">
            <div className="howto-icon">🛠️</div>
            <h5>Setup Development</h5>
            <p>Initialize your development environment for AI-assisted coding</p>
          </div>
        </div>
      </div>

      <div className="standards-section">
        <div className="standards-card">
          <div className="standards-header">
            <h4>
              <span className="standards-icon">📋</span>
              Development Standards (.ai/docs/STANDARDS.md)
            </h4>
            <div className="standards-badge">Essential</div>
          </div>
          <div className="standards-grid">
            <div className="standard-item">
              <div className="standard-icon">📏</div>
              <div className="standard-content">
                <h5>Coding Conventions</h5>
                <p>
                  Consistent naming, formatting, and structure per .ai/docs/STANDARDS.md
                </p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">🏗️</div>
              <div className="standard-content">
                <h5>Architecture Patterns</h5>
                <p>Approved design patterns and practices documented in standards</p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">✅</div>
              <div className="standard-content">
                <h5>Quality Rules</h5>
                <p>
                  Comprehensive linting, type safety, and documentation requirements
                </p>
              </div>
            </div>
            <div className="standard-item">
              <div className="standard-icon">🚀</div>
              <div className="standard-content">
                <h5>Best Practices</h5>
                <p>Security, performance, and maintainability guidelines</p>
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
