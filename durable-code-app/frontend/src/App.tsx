/**
 * Durable Code - AI-Ready Project Framework
 * A comprehensive approach to building maintainable, scalable software with AI assistance
 */
import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import type { ReactElement } from 'react';
import './App.css';
import './qa-maintenance.css';
import packageJson from '../package.json';
import Standards from './pages/Standards';
import CustomLinters from './pages/CustomLinters';
import ParticleBackground from './components/ParticleBackground';
import { InfrastructureTab } from './components/tabs/InfrastructureTab';
import { PlanningTab } from './components/tabs/PlanningTab';
import { BuildingTab } from './components/tabs/BuildingTab';
import { QualityAssuranceTab } from './components/tabs/QualityAssuranceTab';
import { MaintenanceTab } from './components/tabs/MaintenanceTab';

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
  component: () => ReactElement;
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
      component: InfrastructureTab,
    },
    Planning: {
      title: 'Planning',
      icon: '📋',
      description: 'Strategic planning and documentation for AI-assisted development',
      component: PlanningTab,
    },
    Building: {
      title: 'Building',
      icon: '🔨',
      description: 'Tools and commands for AI-assisted code generation',
      component: BuildingTab,
    },
    'Quality Assurance': {
      title: 'Quality Assurance',
      icon: '✅',
      description: 'Automated testing, linting, and CI/CD for code quality',
      component: QualityAssuranceTab,
    },
    Maintenance: {
      title: 'Maintenance',
      icon: '🔧',
      description: 'Ongoing maintenance and evolution strategies',
      component: MaintenanceTab,
    },
  };

  const ActiveTabComponent = tabs[activeTab].component;

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
          <ActiveTabComponent />
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
                  update it with every change. AI relies on current, accurate docs to
                  understand system behavior and constraints.
                </p>
                <div className="principle-examples">
                  <span className="example-tag">README</span>
                  <span className="example-tag">API Docs</span>
                  <span className="example-tag">Comments</span>
                  <span className="example-tag">Examples</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li>
                <a href="https://github.com/stevej-at-benlabs/durable-code-test">
                  GitHub Repository
                </a>
              </li>
              <li>
                <a href="/docs">Documentation</a>
              </li>
              <li>
                <a href="/api">API Reference</a>
              </li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Community</h4>
            <ul>
              <li>
                <a href="/contributing">Contributing Guide</a>
              </li>
              <li>
                <a href="/code-of-conduct">Code of Conduct</a>
              </li>
              <li>
                <a href="/support">Support</a>
              </li>
            </ul>
          </div>
          <div className="footer-info">
            <p>&copy; 2024 Durable Code Project</p>
            <p>Version {packageJson.version}</p>
          </div>
        </div>
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
