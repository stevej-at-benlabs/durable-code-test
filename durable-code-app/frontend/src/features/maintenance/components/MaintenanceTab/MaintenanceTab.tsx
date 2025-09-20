/**
 * Purpose: Maintenance tab for documentation and knowledge management
 * Scope: React component for AI documentation and maintenance tools
 * Overview: Modularized maintenance tab with CSS Modules styling
 * Dependencies: React
 * Exports: MaintenanceTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Feature module with CSS Modules
 */

import type { ReactElement } from 'react';
import styles from './MaintenanceTab.module.css';

export function MaintenanceTab(): ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.hero}>
        <h3 className="hero-title">
          <span className={styles.titleIcon}>🧠</span>
          AI-Powered Documentation
        </h3>
        <p className="subtitle">
          Self-maintaining documentation that evolves with your codebase, powered by
          AI-driven content generation and automatic synchronization
        </p>
      </div>

      <div className={styles.showcaseSection}>
        <div className={styles.showcaseHeader}>
          <h4 className="dark-title-on-light">
            <span className={styles.showcaseIcon}>📚</span>
            AI Agent Index (.ai/index.md)
          </h4>
          <div className={`${styles.badge} ${styles.live}`}>Live</div>
        </div>

        <div className={styles.indexFeatures}>
          <div className={styles.indexFeature}>
            <div className={styles.featureIcon}>🤖</div>
            <h5 className="dark-title-on-light">AI-First Documentation</h5>
            <p className={styles.featureDesc}>
              Comprehensive index designed specifically for AI agents to understand and
              navigate your entire codebase efficiently
            </p>
          </div>
          <div className={styles.indexFeature}>
            <div className={styles.featureIcon}>🔄</div>
            <h5 className="dark-title-on-light">Auto-Synchronized</h5>
            <p className={styles.featureDesc}>
              Documentation automatically updates as your code evolves, ensuring AI
              agents always have accurate information
            </p>
          </div>
          <div className={styles.indexFeature}>
            <div className={styles.featureIcon}>📊</div>
            <h5 className="dark-title-on-light">Structured Knowledge</h5>
            <p className={styles.featureDesc}>
              Features, templates, standards, and guides organized in a hierarchical
              structure for optimal AI comprehension
            </p>
          </div>
          <div className={styles.indexFeature}>
            <div className={styles.featureIcon}>⚡</div>
            <h5 className="dark-title-on-light">Quick Actions</h5>
            <p className={styles.featureDesc}>
              Pre-configured commands and workflows that AI agents can execute
              immediately for common development tasks
            </p>
          </div>
        </div>

        <div className={styles.indexStats}>
          <div className={styles.statCard}>
            <div className={styles.statValue}>12</div>
            <div className={styles.statLabel}>Templates</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>5</div>
            <div className={styles.statLabel}>Features</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>8</div>
            <div className={styles.statLabel}>How-To Guides</div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statValue}>4</div>
            <div className={styles.statLabel}>Standards</div>
          </div>
        </div>
      </div>

      <div className={styles.docSections}>
        <h4 className="dark-title-on-light">
          <span className={styles.sectionIcon}>📖</span>
          Documentation Structure
        </h4>

        <div className={styles.docCards}>
          <div className={styles.docCard}>
            <div className={styles.docIcon}>🎯</div>
            <h5 className="dark-title-on-light">.ai/features/</h5>
            <p className={styles.docDesc}>
              Feature-specific documentation with implementation details
            </p>
            <ul className={styles.docList}>
              <li>design-linters.md</li>
              <li>web-application.md</li>
              <li>development-tooling.md</li>
              <li>claude-integration.md</li>
              <li>testing-framework.md</li>
            </ul>
          </div>

          <div className={styles.docCard}>
            <div className={styles.docIcon}>📝</div>
            <h5 className="dark-title-on-light">.ai/templates/</h5>
            <p className={styles.docDesc}>Code generation templates for AI agents</p>
            <ul className={styles.docList}>
              <li>linting-rule.py.template</li>
              <li>react-component.tsx.template</li>
              <li>web-tab.tsx.template</li>
              <li>fastapi-endpoint.py.template</li>
              <li>test-suite.py.template</li>
            </ul>
          </div>

          <div className={styles.docCard}>
            <div className={styles.docIcon}>📋</div>
            <h5 className="dark-title-on-light">.ai/docs/</h5>
            <p className={styles.docDesc}>Standards and best practices documentation</p>
            <ul className={styles.docList}>
              <li>STANDARDS.md</li>
              <li>FILE_HEADER_STANDARDS.md</li>
              <li>CSS_LAYOUT_STABILITY.md</li>
              <li>BRANCH_PROTECTION.md</li>
            </ul>
          </div>

          <div className={styles.docCard}>
            <div className={styles.docIcon}>🔧</div>
            <h5 className="dark-title-on-light">.ai/howto/</h5>
            <p className={styles.docDesc}>Step-by-step guides for common tasks</p>
            <ul className={styles.docList}>
              <li>run-tests.md</li>
              <li>run-linting.md</li>
              <li>setup-development.md</li>
              <li>deploy-application.md</li>
              <li>debug-issues.md</li>
            </ul>
          </div>
        </div>
      </div>

      <div className={styles.showcaseSection}>
        <h4 className="dark-title-on-light">
          <span className={styles.sectionIcon}>✨</span>
          Auto-Generated Content
        </h4>

        <div className={styles.generationExamples}>
          <div className={styles.exampleCard}>
            <div className={styles.exampleHeader}>
              <span className={styles.exampleIcon}>📄</span>
              <span className={styles.exampleType}>README</span>
            </div>
            <p className={styles.exampleDesc}>
              Automatically generate README files with project overview, setup
              instructions, and API documentation
            </p>
            <code className={styles.exampleCommand}>$ /generate-readme</code>
          </div>

          <div className={styles.exampleCard}>
            <div className={styles.exampleHeader}>
              <span className={styles.exampleIcon}>📊</span>
              <span className={styles.exampleType}>Changelog</span>
            </div>
            <p className={styles.exampleDesc}>
              Create detailed changelogs from git history with AI-powered categorization
              and summaries
            </p>
            <code className={styles.exampleCommand}>$ /generate-changelog</code>
          </div>

          <div className={styles.exampleCard}>
            <div className={styles.exampleHeader}>
              <span className={styles.exampleIcon}>📚</span>
              <span className={styles.exampleType}>API Docs</span>
            </div>
            <p className={styles.exampleDesc}>
              Generate comprehensive API documentation from code comments and type
              definitions
            </p>
            <code className={styles.exampleCommand}>$ /generate-api-docs</code>
          </div>

          <div className={styles.exampleCard}>
            <div className={styles.exampleHeader}>
              <span className={styles.exampleIcon}>🔍</span>
              <span className={styles.exampleType}>Code Index</span>
            </div>
            <p className={styles.exampleDesc}>
              Build searchable index of all functions, classes, and modules with
              descriptions
            </p>
            <code className={styles.exampleCommand}>$ /index-codebase</code>
          </div>
        </div>
      </div>

      <div className={styles.showcaseSection}>
        <h4 className="dark-title-on-light">
          <span className={styles.sectionIcon}>🔧</span>
          Maintenance Commands
        </h4>

        <div className={styles.toolsGrid}>
          <div className={styles.toolCard}>
            <div className={styles.toolIcon}>🔄</div>
            <h5 className="dark-title-on-light">Update Documentation</h5>
            <p className={styles.toolDesc}>
              Sync all documentation with latest code changes
            </p>
            <code className={styles.toolCommand}>make update-docs</code>
          </div>

          <div className={styles.toolCard}>
            <div className={styles.toolIcon}>✅</div>
            <h5 className="dark-title-on-light">Validate Links</h5>
            <p className={styles.toolDesc}>
              Check all documentation links for broken references
            </p>
            <code className={styles.toolCommand}>make check-links</code>
          </div>

          <div className={styles.toolCard}>
            <div className={styles.toolIcon}>📊</div>
            <h5 className="dark-title-on-light">Generate Reports</h5>
            <p className={styles.toolDesc}>
              Create documentation coverage and quality reports
            </p>
            <code className={styles.toolCommand}>make doc-reports</code>
          </div>

          <div className={styles.toolCard}>
            <div className={styles.toolIcon}>🏷️</div>
            <h5 className="dark-title-on-light">Tag Versions</h5>
            <p className={styles.toolDesc}>
              Version and archive documentation for releases
            </p>
            <code className={styles.toolCommand}>make tag-docs</code>
          </div>
        </div>
      </div>
    </div>
  );
}
