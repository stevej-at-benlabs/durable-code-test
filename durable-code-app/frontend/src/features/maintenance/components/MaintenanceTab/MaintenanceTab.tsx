/**
 * Purpose: Maintenance tab for documentation and knowledge management
 * Scope: React component for AI documentation and maintenance tools
 * Overview: Simplified extraction of maintenance tab maintaining original functionality
 * Dependencies: React
 * Exports: MaintenanceTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Direct port from original with CSS classes preserved
 */

import type { ReactElement } from 'react';

export function MaintenanceTab(): ReactElement {
  return (
    <div className="tab-content maintenance-content">
      <div className="maintenance-hero">
        <h3 className="maintenance-title">
          <span className="title-icon">🧠</span>
          AI-Powered Documentation
        </h3>
        <p className="maintenance-subtitle">
          Self-maintaining documentation that evolves with your codebase, powered by
          AI-driven content generation and automatic synchronization
        </p>
      </div>

      <div className="ai-index-showcase">
        <div className="showcase-header">
          <h4>
            <span className="showcase-icon">📚</span>
            AI Agent Index (.ai/index.md)
          </h4>
          <div className="showcase-badge">Live</div>
        </div>

        <div className="index-features">
          <div className="index-feature">
            <div className="feature-icon">🤖</div>
            <h5>AI-First Documentation</h5>
            <p>
              Comprehensive index designed specifically for AI agents to understand and
              navigate your entire codebase efficiently
            </p>
          </div>
          <div className="index-feature">
            <div className="feature-icon">🔄</div>
            <h5>Auto-Synchronized</h5>
            <p>
              Documentation automatically updates as your code evolves, ensuring AI
              agents always have accurate information
            </p>
          </div>
          <div className="index-feature">
            <div className="feature-icon">📊</div>
            <h5>Structured Knowledge</h5>
            <p>
              Features, templates, standards, and guides organized in a hierarchical
              structure for optimal AI comprehension
            </p>
          </div>
          <div className="index-feature">
            <div className="feature-icon">⚡</div>
            <h5>Quick Actions</h5>
            <p>
              Pre-configured commands and workflows that AI agents can execute
              immediately for common development tasks
            </p>
          </div>
        </div>

        <div className="index-stats">
          <div className="stat-card">
            <div className="stat-value">12</div>
            <div className="stat-label">Templates</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">5</div>
            <div className="stat-label">Features</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">8</div>
            <div className="stat-label">How-To Guides</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">4</div>
            <div className="stat-label">Standards</div>
          </div>
        </div>
      </div>

      <div className="documentation-sections">
        <h4 className="section-title">
          <span className="section-icon">📖</span>
          Documentation Structure
        </h4>

        <div className="doc-cards">
          <div className="doc-card">
            <div className="doc-icon">🎯</div>
            <h5>.ai/features/</h5>
            <p>Feature-specific documentation with implementation details</p>
            <ul className="doc-list">
              <li>design-linters.md</li>
              <li>web-application.md</li>
              <li>development-tooling.md</li>
              <li>claude-integration.md</li>
              <li>testing-framework.md</li>
            </ul>
          </div>

          <div className="doc-card">
            <div className="doc-icon">📝</div>
            <h5>.ai/templates/</h5>
            <p>Code generation templates for AI agents</p>
            <ul className="doc-list">
              <li>linting-rule.py.template</li>
              <li>react-component.tsx.template</li>
              <li>web-tab.tsx.template</li>
              <li>fastapi-endpoint.py.template</li>
              <li>test-suite.py.template</li>
            </ul>
          </div>

          <div className="doc-card">
            <div className="doc-icon">📋</div>
            <h5>.ai/docs/</h5>
            <p>Standards and best practices documentation</p>
            <ul className="doc-list">
              <li>STANDARDS.md</li>
              <li>FILE_HEADER_STANDARDS.md</li>
              <li>CSS_LAYOUT_STABILITY.md</li>
              <li>BRANCH_PROTECTION.md</li>
            </ul>
          </div>

          <div className="doc-card">
            <div className="doc-icon">🔧</div>
            <h5>.ai/howto/</h5>
            <p>Step-by-step guides for common tasks</p>
            <ul className="doc-list">
              <li>run-tests.md</li>
              <li>run-linting.md</li>
              <li>setup-development.md</li>
              <li>deploy-application.md</li>
              <li>debug-issues.md</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="auto-generation-showcase">
        <h4 className="section-title">
          <span className="section-icon">✨</span>
          Auto-Generated Content
        </h4>

        <div className="generation-examples">
          <div className="example-card">
            <div className="example-header">
              <span className="example-icon">📄</span>
              <span className="example-type">README</span>
            </div>
            <p className="example-desc">
              Automatically generate README files with project overview, setup
              instructions, and API documentation
            </p>
            <code className="example-command">$ /generate-readme</code>
          </div>

          <div className="example-card">
            <div className="example-header">
              <span className="example-icon">📊</span>
              <span className="example-type">Changelog</span>
            </div>
            <p className="example-desc">
              Create detailed changelogs from git history with AI-powered categorization
              and summaries
            </p>
            <code className="example-command">$ /generate-changelog</code>
          </div>

          <div className="example-card">
            <div className="example-header">
              <span className="example-icon">📚</span>
              <span className="example-type">API Docs</span>
            </div>
            <p className="example-desc">
              Generate comprehensive API documentation from code comments and type
              definitions
            </p>
            <code className="example-command">$ /generate-api-docs</code>
          </div>

          <div className="example-card">
            <div className="example-header">
              <span className="example-icon">🔍</span>
              <span className="example-type">Code Index</span>
            </div>
            <p className="example-desc">
              Build searchable index of all functions, classes, and modules with
              descriptions
            </p>
            <code className="example-command">$ /index-codebase</code>
          </div>
        </div>
      </div>

      <div className="maintenance-tools">
        <h4 className="section-title">
          <span className="section-icon">🔧</span>
          Maintenance Commands
        </h4>

        <div className="tools-grid">
          <div className="tool-card">
            <div className="tool-icon">🔄</div>
            <h5>Update Documentation</h5>
            <p>Sync all documentation with latest code changes</p>
            <code>make update-docs</code>
          </div>

          <div className="tool-card">
            <div className="tool-icon">✅</div>
            <h5>Validate Links</h5>
            <p>Check all documentation links for broken references</p>
            <code>make check-links</code>
          </div>

          <div className="tool-card">
            <div className="tool-icon">📊</div>
            <h5>Generate Reports</h5>
            <p>Create documentation coverage and quality reports</p>
            <code>make doc-reports</code>
          </div>

          <div className="tool-card">
            <div className="tool-icon">🏷️</div>
            <h5>Tag Versions</h5>
            <p>Version and archive documentation for releases</p>
            <code>make tag-docs</code>
          </div>
        </div>
      </div>
    </div>
  );
}
