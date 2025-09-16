import type { ReactElement } from 'react';

export function InfrastructureTab(): ReactElement {
  return (
    <div className="tab-content infrastructure-content">
      <div className="infrastructure-hero">
        <h3 className="infrastructure-title">
          <span className="title-icon">🚀</span>
          What Makes an AI-Ready Project?
        </h3>
        <p className="infrastructure-subtitle">
          Transform your codebase into an AI-collaborative environment with structured
          context, clear conventions, and intelligent organization.
        </p>
      </div>

      <div className="infrastructure-grid">
        <div className="infrastructure-card feature-card">
          <div className="card-icon">📁</div>
          <h4>Project Structure</h4>
          <p>
            Clear, consistent directory organization that AI can navigate efficiently
          </p>
          <div className="card-badge">Essential</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">📏</div>
          <h4>Standards & Conventions</h4>
          <p>Well-defined coding standards and naming conventions for consistency</p>
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
  );
}
