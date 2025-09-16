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
