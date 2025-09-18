/**
 * Purpose: Planning tab component showcasing project planning and documentation strategies
 * Scope: React component for displaying planning documents and development workflows
 * Overview: Tab component that presents planning resources for AI-assisted development
 *     including development flow diagrams, AI review sequences, and implementation
 *     timelines. Provides links to visual documentation and planning materials that
 *     help teams organize and execute AI-ready software projects effectively.
 * Dependencies: React (ReactElement)
 * Exports: PlanningTab function component
 * Props/Interfaces: No props - self-contained tab content
 * State/Behavior: Static content display with links to planning resources and diagrams
 */
import type { ReactElement } from 'react';

export function PlanningTab(): ReactElement {
  return (
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
          <span className="link-icon">📑</span>
          <h4>Feature Index</h4>
          <p>Complete index of all planning documents and artifacts</p>
          <a href="/planning/feature-index.html" className="card-link">
            View Index →
          </a>
        </div>

        <div className="link-card">
          <span className="link-icon">📊</span>
          <h4>Feature Metadata</h4>
          <p>Project configuration, team members, and timeline details</p>
          <a href="/planning/metadata.html" className="card-link">
            View Metadata →
          </a>
        </div>

        <div className="link-card">
          <span className="link-icon">📈</span>
          <h4>Progress Tracking</h4>
          <p>Current status, weekly updates, and milestone tracking</p>
          <a href="/planning/progress.html" className="card-link">
            View Progress →
          </a>
        </div>

        <div className="link-card">
          <span className="link-icon">🚀</span>
          <h4>Rollout Plan</h4>
          <p>Deployment strategy, feature flags, and phased release schedule</p>
          <a href="/planning/rollout-plan.html" className="card-link">
            View Rollout →
          </a>
        </div>

        <div className="link-card">
          <span className="link-icon">🔧</span>
          <h4>Technical Specification</h4>
          <p>Architecture overview, API endpoints, and integration details</p>
          <a href="/planning/technical-spec.html" className="card-link">
            View Spec →
          </a>
        </div>

        <div className="link-card">
          <span className="link-icon">✅</span>
          <h4>Testing Plan</h4>
          <p>Test scenarios, QA checklist, and validation criteria</p>
          <a href="/planning/testing-plan.html" className="card-link">
            View Testing →
          </a>
        </div>

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
  );
}
