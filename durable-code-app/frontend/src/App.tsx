/**
 * Durable Code - AI-Ready Project Framework
 * A comprehensive approach to building maintainable, scalable software with AI assistance
 */
import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import type { ReactElement } from 'react';
import './App.css';
import packageJson from '../package.json';
import Standards from './pages/Standards';

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
        <div className="tab-content">
          <h3>What Makes an AI-Ready Project?</h3>
          <div className="content-section">
            <h4>Essential Elements</h4>
            <ul className="feature-list">
              <li>
                <strong>Project Structure:</strong> Clear, consistent directory
                organization that AI can navigate
              </li>
              <li>
                <strong>Standards & Conventions:</strong> Well-defined coding standards
                and naming conventions
              </li>
              <li>
                <strong>Context Management:</strong> Structured .ai folder with
                comprehensive documentation
              </li>
              <li>
                <strong>AI Instructions:</strong> Clear index.md files providing context
                for AI assistants
              </li>
            </ul>
          </div>

          <div className="content-section">
            <h4>The .ai Folder Structure</h4>
            <div className="code-block">
              <pre>{`.ai/
├── index.md          # Project overview and AI instructions
├── context/          # Domain knowledge and business rules
│   ├── domain.md
│   └── requirements.md
├── standards/        # Coding standards and patterns
│   ├── code-style.md
│   └── architecture.md
└── templates/        # Reusable code templates
    └── component.template`}</pre>
            </div>
          </div>

          <div className="content-section">
            <h4>Best Practices</h4>
            <ul className="feature-list">
              <li>Keep context files concise and focused</li>
              <li>Update documentation as the project evolves</li>
              <li>Include examples of good and bad patterns</li>
              <li>Define clear boundaries and constraints</li>
            </ul>
          </div>

          <div className="action-links">
            <a
              href="https://github.com/stevej-at-benlabs/durable-code-test"
              className="action-link"
            >
              📄 View Project Structure
            </a>
            <a
              href="https://github.com/stevej-at-benlabs/durable-code-test/blob/main/README.md"
              className="action-link"
            >
              📚 Project README
            </a>
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
        <div className="tab-content">
          <h3>Building Tools</h3>
          <div className="content-section">
            <h4>new-code Command</h4>
            <p>
              Our custom CLI tool for generating boilerplate code with AI assistance.
            </p>

            <div className="code-block">
              <pre>{`# Generate a new component
$ new-code component UserProfile

# Generate a new service
$ new-code service AuthenticationService

# Generate a new test file
$ new-code test UserProfile.test`}</pre>
            </div>
          </div>

          <div className="content-section">
            <h4>Features</h4>
            <ul className="feature-list">
              <li>Automatic file extension detection</li>
              <li>Language-appropriate boilerplate generation</li>
              <li>Integrated error handling and logging</li>
              <li>Follows project conventions automatically</li>
              <li>Includes necessary imports and headers</li>
            </ul>
          </div>

          <div className="content-section">
            <h4>Supported File Types</h4>
            <div className="file-types-grid">
              <div className="file-type">TypeScript/React (.tsx, .ts)</div>
              <div className="file-type">Python (.py)</div>
              <div className="file-type">JavaScript (.js, .jsx)</div>
              <div className="file-type">Go (.go)</div>
              <div className="file-type">Rust (.rs)</div>
              <div className="file-type">And more...</div>
            </div>
          </div>

          <div className="content-section">
            <h4>Standards Guide</h4>
            <p>
              Comprehensive development standards and best practices for consistent code
              quality.
            </p>
            <ul className="feature-list">
              <li>
                <strong>Coding Conventions:</strong> Naming, formatting, and structure
                standards
              </li>
              <li>
                <strong>Architecture Patterns:</strong> Approved design patterns and
                practices
              </li>
              <li>
                <strong>Code Quality Rules:</strong> Linting, type safety, and
                documentation requirements
              </li>
              <li>
                <strong>Best Practices:</strong> Security, performance, and
                maintainability guidelines
              </li>
            </ul>
          </div>

          <div className="action-links">
            <a href="tools/new-code/README.md" className="action-link">
              📖 new-code Documentation
            </a>
            <a href="https://github.com/yourusername/new-code" className="action-link">
              💻 View Source Code
            </a>
            <a href="/standards?return=Building" className="action-link">
              🎯 Development Standards Guide
            </a>
          </div>
        </div>
      ),
    },
    'Quality Assurance': {
      title: 'Quality Assurance',
      icon: '✅',
      description: 'Automated testing, linting, and CI/CD for code quality',
      content: (
        <div className="tab-content">
          <h3>Quality Assurance</h3>

          <div className="content-section">
            <h4>Custom Linters</h4>
            <p>
              Advanced linting rules beyond standard tools to enforce project-specific
              standards.
            </p>
            <ul className="feature-list">
              <li>
                <strong>Magic Number Detection:</strong> Identifies hardcoded values
                that should be constants
              </li>
              <li>
                <strong>File Placement Validation:</strong> Ensures files are in correct
                directories
              </li>
              <li>
                <strong>Print Statement Blocking:</strong> Prevents debug statements in
                production
              </li>
              <li>
                <strong>Naming Convention Enforcement:</strong> Validates variable and
                function names
              </li>
            </ul>
            <div className="action-links-inline">
              <a
                href="custom-linters.html?return=Quality Assurance"
                className="action-link"
              >
                View Custom Linters →
              </a>
              <a
                href="linter-violations-case-study.html?return=Quality Assurance"
                className="action-link"
              >
                Case Studies →
              </a>
            </div>
          </div>

          <div className="content-section">
            <h4>CI/CD Pipeline</h4>
            <p>Comprehensive GitHub Actions workflow with AI-powered checks.</p>
            <ul className="feature-list">
              <li>
                <strong>SOLID Principles Validation:</strong> AI checks for violations
              </li>
              <li>
                <strong>Design Pattern Analysis:</strong> Ensures proper implementation
              </li>
              <li>
                <strong>Test Coverage Requirements:</strong> Enforces minimum coverage
              </li>
              <li>
                <strong>Performance Benchmarking:</strong> Tracks performance metrics
              </li>
            </ul>
            <div className="action-links-inline">
              <a
                href="ci-cd-pipeline.html?return=Quality Assurance"
                className="action-link"
              >
                View Pipeline →
              </a>
              <a
                href="ocp-case-study.html?return=Quality Assurance"
                className="action-link"
              >
                OCP Case Study →
              </a>
            </div>
          </div>

          <div className="content-section">
            <h4>Design Checks</h4>
            <p>Automated validation of architectural decisions and design patterns.</p>
            <div className="code-block">
              <pre>{`# Run design checks
$ make check-design

# Run SOLID principle validation
$ python tools/design-linters/solid_checker.py

# Check file placement
$ python tools/design-linters/file_placement_linter.py`}</pre>
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
        <div className="tab-content">
          <h3>Maintenance</h3>
          <div className="content-section">
            <p className="placeholder-message">
              This section is under development. It will include:
            </p>
            <ul className="feature-list">
              <li>Refactoring strategies with AI assistance</li>
              <li>Dependency management and updates</li>
              <li>Performance monitoring and optimization</li>
              <li>Technical debt tracking and resolution</li>
              <li>Documentation maintenance workflows</li>
              <li>Continuous improvement processes</li>
            </ul>
          </div>

          <div className="coming-soon">
            <span className="coming-soon-icon">🚧</span>
            <p>Coming Soon</p>
          </div>
        </div>
      ),
    },
  };

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">Durable Code</span> with AI
          </h1>
          <p className="hero-subtitle">
            A comprehensive framework for building maintainable, scalable, and AI-ready
            software projects
          </p>
          <div className="project-info">
            <h3>Project Purpose</h3>
            <p>
              This project demonstrates best practices and methodologies for creating
              "durable code" - software that is maintainable, scalable, and optimized
              for AI-assisted development. We showcase how to structure projects,
              enforce standards, and leverage automation to build robust applications
              that stand the test of time.
            </p>
          </div>
          <div className="project-scope">
            <h3>Scope</h3>
            <ul>
              <li>AI-ready project structure and context management</li>
              <li>Comprehensive planning and documentation strategies</li>
              <li>Automated quality assurance and testing</li>
              <li>Custom tooling for efficient development</li>
              <li>Continuous improvement and maintenance workflows</li>
            </ul>
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
    </Routes>
  );
}

export default App;
