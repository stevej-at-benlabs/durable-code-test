/**
 * Durable Code - AI-Ready Project Framework
 * A comprehensive approach to building maintainable, scalable software with AI assistance
 */
import { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import type { ReactElement } from 'react';
import './App.css';
import './qa-maintenance.css';
import packageJson from '../package.json';
import Standards from './pages/Standards';
import CustomLinters from './pages/CustomLinters';
import ParticleBackground from './components/ParticleBackground';

type TabName =
  | 'Infrastructure'
  | 'Planning'
  | 'Building'
  | 'Quality Assurance'
  | 'Maintenance';

interface TabContent {
  title: string;
  icon: string;
  description: string;
  content: ReactElement;
}

function HomePage() {
  // Get initial tab from URL hash, return parameter, or default to Infrastructure
  const getInitialTab = (): TabName => {
    const hash = window.location.hash.replace('#', '');
    const urlParams = new URLSearchParams(window.location.search);
    const returnTab = urlParams.get('return');
    const validTabs: TabName[] = [
      'Infrastructure',
      'Planning',
      'Building',
      'Quality Assurance',
      'Maintenance',
    ];

    // Check hash first, then return parameter, then default
    if (validTabs.includes(hash as TabName)) {
      return hash as TabName;
    }
    if (returnTab && validTabs.includes(returnTab as TabName)) {
      return returnTab as TabName;
    }
    return 'Infrastructure';
  };

  const [activeTab, setActiveTab] = useState<TabName>(getInitialTab);

  // Update URL hash when tab changes
  const handleTabChange = (tab: TabName) => {
    setActiveTab(tab);
    window.history.pushState(null, '', `#${tab}`);
  };

  // Listen for browser back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      setActiveTab(getInitialTab());
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  // Clean up URL and set hash when return parameter is used
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const returnTab = urlParams.get('return');

    if (returnTab) {
      // Clean up the URL and set the hash
      const newUrl = window.location.pathname + `#${activeTab}`;
      window.history.replaceState(null, '', newUrl);
    }
  }, [activeTab]);

  const tabs: Record<TabName, TabContent> = {
    Infrastructure: {
      title: 'Infrastructure',
      icon: '🏗️',
      description: 'Building AI-ready projects with proper structure and context',
      content: (
        <div className="tab-content infrastructure-content">
          <div className="infrastructure-hero">
            <h3 className="infrastructure-title">
              <span className="title-icon">🚀</span>
              What Makes an AI-Ready Project?
            </h3>
            <p className="infrastructure-subtitle">
              Transform your codebase into an AI-collaborative environment with
              structured context, clear conventions, and intelligent organization.
            </p>
          </div>

          <div className="infrastructure-grid">
            <div className="infrastructure-card feature-card">
              <div className="card-icon">📁</div>
              <h4>Project Structure</h4>
              <p>
                Clear, consistent directory organization that AI can navigate
                efficiently
              </p>
              <div className="card-badge">Essential</div>
            </div>

            <div className="infrastructure-card feature-card">
              <div className="card-icon">📏</div>
              <h4>Standards & Conventions</h4>
              <p>
                Well-defined coding standards and naming conventions for consistency
              </p>
              <div className="card-badge">Essential</div>
            </div>

            <div className="infrastructure-card feature-card">
              <div className="card-icon">🧠</div>
              <h4>Context Management</h4>
              <p>Structured .ai folder with comprehensive documentation</p>
              <div className="card-badge">Essential</div>
            </div>

            <div className="infrastructure-card feature-card">
              <div className="card-icon">🤖</div>
              <h4>AI Instructions</h4>
              <p>Clear index.md files providing context for AI assistants</p>
              <div className="card-badge">Essential</div>
            </div>
          </div>

          <div className="folder-structure-section">
            <h4 className="section-title">
              <span className="section-icon">📂</span>
              The .ai Folder Structure
            </h4>
            <div className="folder-structure-container">
              <div className="folder-preview">
                <div className="folder-item root">
                  <span className="folder-icon">📦</span> .ai/
                </div>
                <div className="folder-item file">
                  <span className="folder-line">├──</span>
                  <span className="file-icon">📄</span> index.md
                  <span className="file-desc">Project overview</span>
                </div>
                <div className="folder-item folder">
                  <span className="folder-line">├──</span>
                  <span className="folder-icon">📁</span> context/
                  <span className="file-desc">Domain knowledge</span>
                </div>
                <div className="folder-item file nested">
                  <span className="folder-line">│ ├──</span>
                  <span className="file-icon">📝</span> domain.md
                </div>
                <div className="folder-item file nested">
                  <span className="folder-line">│ └──</span>
                  <span className="file-icon">📝</span> requirements.md
                </div>
                <div className="folder-item folder">
                  <span className="folder-line">├──</span>
                  <span className="folder-icon">📁</span> standards/
                  <span className="file-desc">Coding standards</span>
                </div>
                <div className="folder-item file nested">
                  <span className="folder-line">│ ├──</span>
                  <span className="file-icon">📝</span> code-style.md
                </div>
                <div className="folder-item file nested">
                  <span className="folder-line">│ └──</span>
                  <span className="file-icon">📝</span> architecture.md
                </div>
                <div className="folder-item folder">
                  <span className="folder-line">└──</span>
                  <span className="folder-icon">📁</span> templates/
                  <span className="file-desc">Code templates</span>
                </div>
                <div className="folder-item file nested">
                  <span className="folder-line"> └──</span>
                  <span className="file-icon">🔧</span> component.template
                </div>
              </div>
              <div className="folder-description">
                <h5>Structure Benefits</h5>
                <ul className="benefit-list">
                  <li>✅ AI understands project context immediately</li>
                  <li>✅ Consistent code generation</li>
                  <li>✅ Reduced hallucination and errors</li>
                  <li>✅ Faster development cycles</li>
                  <li>✅ Better code quality</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="best-practices-section">
            <h4 className="section-title">
              <span className="section-icon">⭐</span>
              Best Practices
            </h4>
            <div className="practices-grid">
              <div className="practice-card">
                <div className="practice-icon">📝</div>
                <h5>Concise Context</h5>
                <p>Keep context files focused and to the point</p>
              </div>
              <div className="practice-card">
                <div className="practice-icon">🔄</div>
                <h5>Living Documentation</h5>
                <p>Update docs as the project evolves</p>
              </div>
              <div className="practice-card">
                <div className="practice-icon">✨</div>
                <h5>Clear Examples</h5>
                <p>Include good and bad pattern examples</p>
              </div>
              <div className="practice-card">
                <div className="practice-icon">🎯</div>
                <h5>Define Boundaries</h5>
                <p>Set clear constraints and limitations</p>
              </div>
            </div>
          </div>

          <div className="stats-section">
            <div className="stat-card">
              <div className="stat-number">3x</div>
              <div className="stat-label">Faster Development</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">80%</div>
              <div className="stat-label">Less AI Errors</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">50%</div>
              <div className="stat-label">Better Code Quality</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">90%</div>
              <div className="stat-label">Context Retention</div>
            </div>
          </div>

          <div className="action-section">
            <h4 className="section-title">
              <span className="section-icon">🚀</span>
              Get Started
            </h4>
            <div className="action-links">
              <a
                href="https://github.com/stevej-at-benlabs/durable-code-test"
                className="action-link primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="link-icon">📄</span>
                View Project Structure
              </a>
              <a
                href="https://github.com/stevej-at-benlabs/durable-code-test/blob/main/README.md"
                className="action-link secondary"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span className="link-icon">📚</span>
                Project README
              </a>
            </div>
          </div>
        </div>
      ),
    },
    Planning: {
      title: 'Planning',
      icon: '📋',
      description: 'Strategic planning and documentation for AI-assisted development',
      content: (
        <div className="tab-content">
          <h3>Planning Documents</h3>
          <div className="content-section">
            <p>
              Effective planning is crucial for successful AI-assisted development. Our
              planning documents provide comprehensive guidance for project setup and
              execution.
            </p>
          </div>

          <div className="planning-links">
            <div className="link-card">
              <span className="link-icon">🔄</span>
              <h4>Development Flow</h4>
              <p>
                Visual workflow showing the complete development lifecycle with AI
                integration points
              </p>
              <a
                href="/diagrams/durable-code-flow.html?return=Planning"
                className="card-link"
              >
                View Flow Diagram →
              </a>
            </div>

            <div className="link-card">
              <span className="link-icon">📋</span>
              <h4>AI Review Sequence</h4>
              <p>Step-by-step sequence diagram for AI code review processes</p>
              <a
                href="/diagrams/ai-review-sequence.html?return=Planning"
                className="card-link"
              >
                View Sequence →
              </a>
            </div>

            <div className="link-card">
              <span className="link-icon">📅</span>
              <h4>Implementation Plan</h4>
              <p>Gantt chart showing project timeline and milestones</p>
              <a
                href="/diagrams/implementation-plan.html?return=Planning"
                className="card-link"
              >
                View Timeline →
              </a>
            </div>
          </div>
        </div>
      ),
    },
    Building: {
      title: 'Building',
      icon: '🔨',
      description: 'Tools and commands for AI-assisted code generation',
      content: (
        <div className="tab-content building-content">
          <div className="building-hero">
            <div className="hero-icon">⚡</div>
            <h3 className="building-title">AI-Powered Code Generation</h3>
            <p className="building-subtitle">
              Accelerate development with intelligent boilerplate generation and
              automated tooling
            </p>
          </div>

          <div className="cli-showcase">
            <div className="cli-header">
              <h4>
                <span className="cli-icon">💻</span>
                new-code CLI Tool
              </h4>
              <div className="cli-badge">v2.0</div>
            </div>

            <div className="command-cards">
              <div className="command-card">
                <div className="command-header">
                  <span className="command-icon">🧩</span>
                  <span className="command-type">Component</span>
                </div>
                <code className="command-syntax">$ new-code component UserProfile</code>
                <p className="command-desc">
                  Generate React/Vue/Angular components with props, state, and lifecycle
                </p>
              </div>

              <div className="command-card">
                <div className="command-header">
                  <span className="command-icon">🔧</span>
                  <span className="command-type">Service</span>
                </div>
                <code className="command-syntax">$ new-code service AuthService</code>
                <p className="command-desc">
                  Create service layers with dependency injection and error handling
                </p>
              </div>

              <div className="command-card">
                <div className="command-header">
                  <span className="command-icon">🧪</span>
                  <span className="command-type">Test</span>
                </div>
                <code className="command-syntax">$ new-code test UserProfile.test</code>
                <p className="command-desc">
                  Generate test suites with mocks, fixtures, and coverage setup
                </p>
              </div>

              <div className="command-card">
                <div className="command-header">
                  <span className="command-icon">🗄️</span>
                  <span className="command-type">API</span>
                </div>
                <code className="command-syntax">$ new-code api users</code>
                <p className="command-desc">
                  Scaffold REST/GraphQL endpoints with validation and middleware
                </p>
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
                <p>
                  Automatically detects file type and generates appropriate boilerplate
                </p>
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
                      text-anchor="middle"
                      dy=".35em"
                      fill="white"
                      font-size="14"
                      font-weight="bold"
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
                      text-anchor="middle"
                      dy=".35em"
                      fill="black"
                      font-size="14"
                      font-weight="bold"
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
                      text-anchor="middle"
                      dy=".35em"
                      fill="white"
                      font-size="14"
                      font-weight="bold"
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
              <a href="/standards?return=Building" className="action-link tertiary">
                <span className="link-icon">🎯</span>
                Standards Guide
              </a>
            </div>
          </div>
        </div>
      ),
    },
    'Quality Assurance': {
      title: 'Quality Assurance',
      icon: '✅',
      description: 'Automated testing, linting, and CI/CD for code quality',
      content: (
        <div className="tab-content qa-content">
          <div className="qa-hero">
            <div className="qa-hero-icon">🛡️</div>
            <h3 className="qa-title">Bulletproof Code Quality</h3>
            <p className="qa-subtitle">
              Comprehensive automated testing, custom linting, and AI-powered validation
              to ensure your code meets the highest standards
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
      ),
    },
    Maintenance: {
      title: 'Maintenance',
      icon: '🔧',
      description: 'Ongoing maintenance and evolution strategies',
      content: (
        <div className="tab-content maintenance-content">
          <div className="maintenance-hero">
            <div className="maintenance-hero-icon">🔧</div>
            <h3 className="maintenance-title">Sustainable Code Evolution</h3>
            <p className="maintenance-subtitle">
              Keep your codebase healthy, performant, and up-to-date with intelligent
              maintenance strategies and automated workflows
            </p>
          </div>

          <div className="health-dashboard">
            <div className="health-score">
              <div className="score-circle">
                <svg viewBox="0 0 200 200" className="score-svg">
                  <circle cx="100" cy="100" r="90" className="score-bg" />
                  <circle
                    cx="100"
                    cy="100"
                    r="90"
                    className="score-fill"
                    style={{ strokeDasharray: '502', strokeDashoffset: '50' }}
                  />
                </svg>
                <div className="score-text">
                  <div className="score-value">91</div>
                  <div className="score-label">Health Score</div>
                </div>
              </div>
            </div>

            <div className="health-metrics">
              <div className="health-metric">
                <div className="metric-icon">📦</div>
                <div className="metric-info">
                  <div className="metric-name">Dependencies</div>
                  <div className="metric-status good">All up to date</div>
                </div>
              </div>
              <div className="health-metric">
                <div className="metric-icon">🚀</div>
                <div className="metric-info">
                  <div className="metric-name">Performance</div>
                  <div className="metric-status good">98/100</div>
                </div>
              </div>
              <div className="health-metric">
                <div className="metric-icon">💾</div>
                <div className="metric-info">
                  <div className="metric-name">Tech Debt</div>
                  <div className="metric-status warning">2.3% of codebase</div>
                </div>
              </div>
              <div className="health-metric">
                <div className="metric-icon">📚</div>
                <div className="metric-info">
                  <div className="metric-name">Documentation</div>
                  <div className="metric-status good">95% coverage</div>
                </div>
              </div>
            </div>
          </div>

          <div className="maintenance-strategies">
            <h4 className="section-title">
              <span className="section-icon">🎯</span>
              Maintenance Strategies
            </h4>

            <div className="strategy-cards">
              <div className="strategy-card">
                <div className="strategy-header">
                  <div className="strategy-icon">♻️</div>
                  <h5>Smart Refactoring</h5>
                  <div className="strategy-badge">AI-Powered</div>
                </div>
                <p>
                  Intelligent code refactoring with AI assistance to improve structure
                  without breaking functionality
                </p>
                <ul className="strategy-features">
                  <li>Automated pattern detection</li>
                  <li>Safe rename operations</li>
                  <li>Extract method suggestions</li>
                  <li>Dead code elimination</li>
                </ul>
                <div className="strategy-action">
                  <button className="strategy-button">Start Refactoring →</button>
                </div>
              </div>

              <div className="strategy-card">
                <div className="strategy-header">
                  <div className="strategy-icon">📦</div>
                  <h5>Dependency Manager</h5>
                  <div className="strategy-badge">Automated</div>
                </div>
                <p>
                  Keep dependencies updated and secure with automated vulnerability
                  scanning and updates
                </p>
                <ul className="strategy-features">
                  <li>Security vulnerability alerts</li>
                  <li>Automated PR creation</li>
                  <li>Breaking change detection</li>
                  <li>License compliance</li>
                </ul>
                <div className="strategy-action">
                  <button className="strategy-button">Check Updates →</button>
                </div>
              </div>

              <div className="strategy-card">
                <div className="strategy-header">
                  <div className="strategy-icon">⚡</div>
                  <h5>Performance Monitor</h5>
                  <div className="strategy-badge">Real-time</div>
                </div>
                <p>
                  Continuous performance monitoring with automated optimization
                  suggestions
                </p>
                <ul className="strategy-features">
                  <li>Bundle size tracking</li>
                  <li>Runtime performance metrics</li>
                  <li>Memory leak detection</li>
                  <li>Optimization recommendations</li>
                </ul>
                <div className="strategy-action">
                  <button className="strategy-button">View Metrics →</button>
                </div>
              </div>
            </div>
          </div>

          <div className="debt-tracker">
            <h4 className="section-title">
              <span className="section-icon">📊</span>
              Technical Debt Tracker
            </h4>

            <div className="debt-overview">
              <div className="debt-chart">
                <div className="debt-bar">
                  <div className="debt-segment critical" style={{ width: '15%' }}>
                    <span className="debt-label">Critical (3)</span>
                  </div>
                  <div className="debt-segment high" style={{ width: '25%' }}>
                    <span className="debt-label">High (5)</span>
                  </div>
                  <div className="debt-segment medium" style={{ width: '35%' }}>
                    <span className="debt-label">Medium (7)</span>
                  </div>
                  <div className="debt-segment low" style={{ width: '25%' }}>
                    <span className="debt-label">Low (5)</span>
                  </div>
                </div>
              </div>

              <div className="debt-items">
                <div className="debt-item critical">
                  <div className="debt-priority">Critical</div>
                  <div className="debt-details">
                    <h6>Legacy authentication system</h6>
                    <p>Needs migration to OAuth 2.0</p>
                  </div>
                  <div className="debt-estimate">~8h</div>
                </div>
                <div className="debt-item high">
                  <div className="debt-priority">High</div>
                  <div className="debt-details">
                    <h6>Database query optimization</h6>
                    <p>N+1 queries in user service</p>
                  </div>
                  <div className="debt-estimate">~4h</div>
                </div>
                <div className="debt-item medium">
                  <div className="debt-priority">Medium</div>
                  <div className="debt-details">
                    <h6>Component refactoring</h6>
                    <p>Split large components</p>
                  </div>
                  <div className="debt-estimate">~6h</div>
                </div>
              </div>
            </div>
          </div>

          <div className="automation-tools">
            <h4 className="section-title">
              <span className="section-icon">🤖</span>
              Automation Tools
            </h4>

            <div className="tools-grid">
              <div className="tool-card">
                <div className="tool-icon">🔄</div>
                <h5>Auto-Update Bot</h5>
                <p>Dependabot integration for automated dependency updates</p>
                <div className="tool-status active">Active</div>
              </div>
              <div className="tool-card">
                <div className="tool-icon">📝</div>
                <h5>Doc Generator</h5>
                <p>Automated API documentation from code comments</p>
                <div className="tool-status active">Active</div>
              </div>
              <div className="tool-card">
                <div className="tool-icon">🧹</div>
                <h5>Code Cleanup</h5>
                <p>Weekly automated cleanup of unused code and imports</p>
                <div className="tool-status active">Active</div>
              </div>
              <div className="tool-card">
                <div className="tool-icon">📊</div>
                <h5>Metrics Reporter</h5>
                <p>Weekly code quality and performance reports</p>
                <div className="tool-status active">Active</div>
              </div>
            </div>
          </div>

          <div className="roadmap-section">
            <h4 className="section-title">
              <span className="section-icon">🗺️</span>
              Maintenance Roadmap
            </h4>

            <div className="roadmap-timeline">
              <div className="timeline-item completed">
                <div className="timeline-marker">✓</div>
                <div className="timeline-content">
                  <h6>Q1 2024</h6>
                  <p>Migration to TypeScript</p>
                </div>
              </div>
              <div className="timeline-item completed">
                <div className="timeline-marker">✓</div>
                <div className="timeline-content">
                  <h6>Q2 2024</h6>
                  <p>Performance optimization</p>
                </div>
              </div>
              <div className="timeline-item current">
                <div className="timeline-marker">◉</div>
                <div className="timeline-content">
                  <h6>Q3 2024</h6>
                  <p>Microservices migration</p>
                </div>
              </div>
              <div className="timeline-item upcoming">
                <div className="timeline-marker">○</div>
                <div className="timeline-content">
                  <h6>Q4 2024</h6>
                  <p>AI integration phase 2</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
  };

  return (
    <div className="app">
      <ParticleBackground />
      <header className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">Durable Code</span> with AI
          </h1>
          <p className="hero-subtitle">
            A comprehensive framework for building maintainable, scalable, and AI-ready
            software projects
          </p>
          <div className="hero-info-grid">
            <div className="project-info">
              <h3>Project Purpose</h3>
              <p>
                This project demonstrates best practices and methodologies for creating
                "durable code" - software that is maintainable, scalable, and optimized
                for AI-assisted development.
              </p>
            </div>
            <div className="project-scope">
              <h3>Key Features</h3>
              <ul>
                <li>AI-ready project structure</li>
                <li>Comprehensive planning strategies</li>
                <li>Automated quality assurance</li>
                <li>Custom development tooling</li>
                <li>Continuous improvement workflows</li>
              </ul>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <nav className="tab-navigation">
          {(Object.keys(tabs) as TabName[]).map((tabName) => (
            <button
              key={tabName}
              className={`tab-button ${activeTab === tabName ? 'active' : ''}`}
              onClick={() => handleTabChange(tabName)}
            >
              <span className="tab-icon">{tabs[tabName].icon}</span>
              <span className="tab-title">{tabs[tabName].title}</span>
            </button>
          ))}
        </nav>

        <section className="tab-container">
          <div className="tab-header">
            <h2>{tabs[activeTab].title}</h2>
            <p>{tabs[activeTab].description}</p>
          </div>
          {tabs[activeTab].content}
        </section>

        <section className="ai-principles">
          <div className="principles-container">
            <div className="principles-header">
              <h2>Fundamental AI Principles</h2>
              <p>Core concepts for successful AI-assisted development</p>
            </div>

            <div className="principles-grid">
              <div className="principle-card">
                <div className="principle-number">1</div>
                <h3>Immediate Feedback Loops</h3>
                <p>
                  AI needs instant visibility into success or failure through logs,
                  terminal output, test results, and error messages. Without immediate
                  feedback, AI cannot self-correct or validate its actions.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">Terminal</span>
                  <span className="example-tag">Logs</span>
                  <span className="example-tag">Tests</span>
                  <span className="example-tag">Errors</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">2</div>
                <h3>Contractor-Level Context</h3>
                <p>
                  AI needs the same context you'd give a new contractor: project
                  structure, business domain, coding standards, dependencies, and goals.
                  This context must be provided every session.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">.ai/index.md</span>
                  <span className="example-tag">README</span>
                  <span className="example-tag">Standards</span>
                  <span className="example-tag">Domain</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">3</div>
                <h3>Clear Success Criteria</h3>
                <p>
                  Define explicit, measurable success conditions. AI performs best when
                  it knows exactly what "done" looks like - passing tests, meeting
                  performance benchmarks, or matching specifications.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">Tests Pass</span>
                  <span className="example-tag">No Lint Errors</span>
                  <span className="example-tag">Builds Clean</span>
                  <span className="example-tag">Meets Specs</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">4</div>
                <h3>Modular Task Decomposition</h3>
                <p>
                  Break complex problems into small, verifiable steps. AI excels at
                  focused, well-defined tasks but struggles with ambiguous, open-ended
                  requests. Think functions, not monoliths.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">Small PRs</span>
                  <span className="example-tag">Single Purpose</span>
                  <span className="example-tag">Testable Units</span>
                  <span className="example-tag">Clear Scope</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">5</div>
                <h3>Explicit Over Implicit</h3>
                <p>
                  State requirements explicitly. Don't assume AI will infer conventions,
                  patterns, or constraints. Document your preferences, standards, and
                  anti-patterns clearly.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">No Magic</span>
                  <span className="example-tag">Clear Rules</span>
                  <span className="example-tag">Examples</span>
                  <span className="example-tag">Constraints</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">6</div>
                <h3>Defensive Validation</h3>
                <p>
                  Always verify AI output through automated tests, linting, type
                  checking, and builds. Trust but verify - use CI/CD pipelines to catch
                  issues before they reach production.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">CI/CD</span>
                  <span className="example-tag">Type Safety</span>
                  <span className="example-tag">Linting</span>
                  <span className="example-tag">Reviews</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">7</div>
                <h3>Version Control Everything</h3>
                <p>
                  Track all changes in git with clear commit messages. This provides
                  rollback capability, audit trails, and allows AI to understand project
                  evolution and patterns.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">Git History</span>
                  <span className="example-tag">Commits</span>
                  <span className="example-tag">Branches</span>
                  <span className="example-tag">Tags</span>
                </div>
              </div>

              <div className="principle-card">
                <div className="principle-number">8</div>
                <h3>Living Documentation</h3>
                <p>
                  Treat documentation as code - keep it in the repo, version it, and
                  update it with changes. AI can read and update docs, creating a
                  self-maintaining knowledge base.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">Markdown</span>
                  <span className="example-tag">JSDoc</span>
                  <span className="example-tag">README</span>
                  <span className="example-tag">Inline Docs</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>
          &copy; 2025 Durable Code with AI. Building the future of software development.
        </p>
        <p className="version">v{packageJson.version}</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/standards" element={<Standards />} />
      <Route path="/custom-linters" element={<CustomLinters />} />
    </Routes>
  );
}

export default App;
