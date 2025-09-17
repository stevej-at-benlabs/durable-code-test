/**
 * Purpose: Infrastructure tab component showcasing AI-ready project setup and architecture
 * Scope: React component for displaying infrastructure best practices and project structure
 * Overview: Tab component that demonstrates infrastructure setup for AI-assisted development
 *     including project organization, tooling configuration, CI/CD setup, and development
 *     environment preparation. Shows examples of proper project structure, dependency
 *     management, and integration with AI development tools and workflows.
 * Dependencies: React (ReactElement)
 * Exports: InfrastructureTab function component
 * Props/Interfaces: No props - self-contained tab content
 * State/Behavior: Static content display with infrastructure examples and best practices
 */
import type { ReactElement } from 'react';

export function InfrastructureTab(): ReactElement {
  return (
    <div className="tab-content infrastructure-content">
      <div className="infrastructure-hero">
        <h3 className="infrastructure-title">
          <span className="title-icon">🏗️</span>
          Rigid Infrastructure: The Foundation for AI at Scale
        </h3>
        <p className="infrastructure-subtitle">
          AI collaboration at scale requires uncompromising infrastructure discipline.
          This project shows some examples of the rigid standards, automated quality
          controls, and structured documentation that make AI-assisted development
          predictable and reliable.
        </p>
      </div>

      <div className="infrastructure-grid">
        <div className="infrastructure-card feature-card">
          <div className="card-icon">🔧</div>
          <h4>Custom Linters</h4>
          <p>
            Enforce your specific standards automatically - from logging practices to
            file organization, catching violations before they enter the codebase
          </p>
          <div className="card-badge">Critical</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">⚙️</div>
          <h4>Make Targets</h4>
          <p>
            Reliable, repeatable automation that produces consistent results regardless
            of environment or developer
          </p>
          <div className="card-badge">Critical</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">🔒</div>
          <h4>Quality Gates</h4>
          <p>
            Pre-commit hooks, merge protection, and CI/CD checks creating multiple
            layers of defense
          </p>
          <div className="card-badge">Critical</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">🛡️</div>
          <h4>Merge Protection</h4>
          <p>
            Branch protection rules and CI/CD status checks preventing broken code from
            reaching main
          </p>
          <div className="card-badge">Critical</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">🔍</div>
          <h4>Automated PR Reviews</h4>
          <p>
            AI-powered code reviews ensuring strict standard adherence with greater
            detail and consistency than humans
          </p>
          <div className="card-badge">Critical</div>
        </div>

        <div className="infrastructure-card feature-card">
          <div className="card-icon">🤖</div>
          <h4>Claude Commands</h4>
          <p>
            Custom AI commands like /new-code, /ask, and /solid with template-driven
            generation
          </p>
          <div className="card-badge">Critical</div>
        </div>
      </div>

      <div className="folder-structure-section">
        <h4 className="section-title">
          <span className="section-icon">📂</span>
          The .ai Repository Structure
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">📦</span> .ai/
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📋</span> index.json
              <span className="file-desc">Quick navigation for AI agents</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📄</span> index_expanded.md
              <span className="file-desc">Comprehensive AI documentation</span>
            </div>
            <div className="folder-item folder">
              <span className="folder-line">├──</span>
              <span className="folder-icon">📁</span> docs/
              <span className="file-desc">Development standards</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📝</span> STANDARDS.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📝</span> FILE_HEADER_STANDARDS.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📝</span> CSS_LAYOUT_STABILITY.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">📝</span> BRANCH_PROTECTION.md
            </div>
            <div className="folder-item folder">
              <span className="folder-line">├──</span>
              <span className="folder-icon">📁</span> features/
              <span className="file-desc">Feature documentation</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔧</span> design-linters.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🌐</span> web-application.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">⚙️</span> development-tooling.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🤖</span> claude-integration.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">🧪</span> testing-framework.md
            </div>
            <div className="folder-item folder">
              <span className="folder-line">├──</span>
              <span className="folder-icon">📁</span> howto/
              <span className="file-desc">Step-by-step guides</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🧪</span> run-tests.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔍</span> run-linting.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🛠️</span> setup-development.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🚀</span> deploy-application.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🐛</span> debug-issues.md
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">🔬</span> debug-with-tests-and-logging.md
            </div>
            <div className="folder-item folder">
              <span className="folder-line">└──</span>
              <span className="folder-icon">📁</span> templates/
              <span className="file-desc">Production-ready templates</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">🔧</span> linting-rule.py.template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">⚛️</span> react-component.tsx.template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">📑</span> web-tab.tsx.template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">🌐</span> fastapi-endpoint.py.template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">🧪</span> test-suite.py.template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> └──</span>
              <span className="file-icon">📊</span> workflow.html.template
            </div>
          </div>
          <div className="folder-description">
            <h5>Infrastructure Benefits</h5>
            <ul className="benefit-list">
              <li>✅ AI agents navigate efficiently with structured index</li>
              <li>✅ Template-driven consistent code generation</li>
              <li>✅ Comprehensive standards prevent drift</li>
              <li>✅ Step-by-step guides ensure reproducibility</li>
              <li>✅ Feature docs maintain architectural integrity</li>
              <li>✅ Quality gates prevent regressions</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="make-targets-section">
        <h4 className="section-title">
          <span className="section-icon">⚙️</span>
          Make Targets: Determinism Against AI Chaos
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">🎯</span> Repeatable Operations
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🧪</span> test
              <span className="file-desc">
                Same tests, same environment, every time
              </span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔍</span> lint-all
              <span className="file-desc">
                Consistent quality checks across machines
              </span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🏗️</span> build
              <span className="file-desc">Identical builds from identical inputs</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🚀</span> deploy
              <span className="file-desc">Predictable deployment every time</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔧</span> setup
              <span className="file-desc">Environment setup: deterministic</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📊</span> validate
              <span className="file-desc">Quality gates with known outcomes</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🧹</span> clean
              <span className="file-desc">Reset to known clean state</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📋</span> format
              <span className="file-desc">Code formatting: same result always</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔒</span> security-scan
              <span className="file-desc">Reproducible security analysis</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">└──</span>
              <span className="file-icon">📈</span> benchmark
              <span className="file-desc">
                Performance metrics: consistent baseline
              </span>
            </div>
          </div>
          <div className="folder-description">
            <h5>Determinism vs AI Variability</h5>
            <p>
              <strong>AI isn't repeatable - make everything else deterministic.</strong>
            </p>
            <ul className="benefit-list">
              <li>🎯 Same command = same result</li>
              <li>🎯 Dockerized environments eliminate drift</li>
              <li>🎯 Pinned dependencies prevent surprises</li>
              <li>🎯 AI can author targets, humans verify</li>
              <li>🎯 Automation reduces human inconsistency</li>
            </ul>
            <p className="ai-helper">
              <strong>💡 AI Workflow:</strong> Let AI help write your Make targets, but
              make the targets themselves deterministic and verifiable.
            </p>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="custom-linters-section">
        <h4 className="section-title">
          <span className="section-icon">🔧</span>
          Custom Linters: Gate Everything You Care About
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">🎯</span> Your Project Standards
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🚫</span> print() statements
              <span className="file-desc">Ban console.log, print() everywhere</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📝</span> Logging consistency
              <span className="file-desc">Enforce single logging framework</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📁</span> File placement rules
              <span className="file-desc">Tests here, components there</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔢</span> Magic number detection
              <span className="file-desc">Constants must be named</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🏗️</span> Architecture patterns
              <span className="file-desc">SOLID, DRY, design principles</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔒</span> Security patterns
              <span className="file-desc">No hardcoded secrets</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📋</span> Naming conventions
              <span className="file-desc">Variables, functions, classes</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📦</span> Import organization
              <span className="file-desc">Dependencies, structure</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🧪</span> Test coverage rules
              <span className="file-desc">Missing tests detected</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">└──</span>
              <span className="file-icon">📚</span> Documentation requirements
              <span className="file-desc">Headers, docstrings, comments</span>
            </div>
          </div>
          <div className="folder-description">
            <h5>If You Care About It, Gate It</h5>
            <p>
              <strong>Custom linters enforce YOUR specific standards.</strong>
            </p>
            <ul className="benefit-list">
              <li>🎯 Catch violations early</li>
              <li>🎯 Prevent technical debt</li>
              <li>🎯 Automate code reviews</li>
              <li>🎯 Scale team consistency</li>
              <li>🎯 Reduce AI hallucinations</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="precommit-section">
        <h4 className="section-title">
          <span className="section-icon">🔒</span>
          Pre-commit Quality Gates
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">⚡</span> git commit
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">✂️</span> trailing-whitespace
              <span className="file-desc">Remove trailing spaces</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">📝</span> end-of-file-fixer
              <span className="file-desc">Ensure proper file endings</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">✅</span> check-yaml/json/toml
              <span className="file-desc">Validate config files</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔍</span> make lint-all
              <span className="file-desc">All Python + JS + custom linters</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">└──</span>
              <span className="file-icon">🧪</span> make test
              <span className="file-desc">Full test suite must pass</span>
            </div>
          </div>
          <div className="folder-description">
            <h5>Zero Tolerance Policy</h5>
            <p>
              <strong>Commits are blocked if any check fails.</strong>
            </p>
            <ul className="benefit-list">
              <li>🚫 No broken code in repository</li>
              <li>🚫 No formatting inconsistencies</li>
              <li>🚫 No failing tests</li>
              <li>🚫 No linting violations</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="merge-checks-section">
        <h4 className="section-title">
          <span className="section-icon">🛡️</span>
          Merge Protection & CI/CD Checks
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">🔀</span> Pull Request → main
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">👥</span> Required Reviews
              <span className="file-desc">Code review approval required</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔄</span> Up-to-date Branch
              <span className="file-desc">Must be current with main</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">✅</span> Status Checks
              <span className="file-desc">CI/CD pipeline must pass</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🧪</span> Automated Tests
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔍</span> Linting Suite
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🏗️</span> Build Verification
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔒</span> Security Scans
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">📊</span> Coverage Reports
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🚫</span> No Force Push
              <span className="file-desc">History rewriting blocked</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">🔐</span> Admin Override
              <span className="file-desc">Emergency bypass tracked</span>
            </div>
            <div className="folder-item file">
              <span className="folder-line">└──</span>
              <span className="file-icon">📋</span> Linear History
              <span className="file-desc">Clean merge strategy enforced</span>
            </div>
          </div>
          <div className="folder-description">
            <h5>Branch Protection Rules</h5>
            <p>
              <strong>Main branch is heavily protected.</strong>
            </p>
            <ul className="benefit-list">
              <li>🛡️ No direct pushes to main allowed</li>
              <li>🛡️ All changes via reviewed PRs only</li>
              <li>🛡️ CI/CD must pass before merge</li>
              <li>🛡️ Linear history maintained</li>
              <li>🛡️ Admin actions audited</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="claude-commands-section">
        <h4 className="section-title">
          <span className="section-icon">🤖</span>
          Claude AI Commands
        </h4>
        <div className="folder-structure-container">
          <div className="folder-preview">
            <div className="folder-item root">
              <span className="folder-icon">🎯</span> .claude/commands/
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">✨</span> /new-code
              <span className="file-desc">Template-driven code generation</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔍</span> Check .ai/index.json
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📋</span> Select template
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📝</span> Apply standards
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">✅</span> Include headers & tests
            </div>
            <div className="folder-item file">
              <span className="folder-line">├──</span>
              <span className="file-icon">❓</span> /ask
              <span className="file-desc">AI-powered project Q&A</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">📚</span> Reference .ai/ docs
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ ├──</span>
              <span className="file-icon">🔍</span> Examine actual code
            </div>
            <div className="folder-item file nested">
              <span className="folder-line">│ └──</span>
              <span className="file-icon">💡</span> Provide examples
            </div>
            <div className="folder-item file">
              <span className="folder-line">└──</span>
              <span className="file-icon">🏗️</span> /solid
              <span className="file-desc">SOLID principle analysis</span>
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">🤖</span> 5 parallel AI agents
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">🐍</span> Python-aware analysis
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> ├──</span>
              <span className="file-icon">📊</span> Detailed reports
            </div>
            <div className="folder-item file nested">
              <span className="folder-line"> └──</span>
              <span className="file-icon">🎯</span> Actionable recommendations
            </div>
          </div>
          <div className="folder-description">
            <h5>AI-Driven Development</h5>
            <ul className="benefit-list">
              <li>✅ Context-aware code generation</li>
              <li>✅ Standards automatically enforced</li>
              <li>✅ Template consistency guaranteed</li>
              <li>✅ Architecture principles validated</li>
              <li>✅ Comprehensive documentation reference</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="rigid-infrastructure-section">
        <h4 className="section-title">
          <span className="section-icon">🏗️</span>
          Why Rigid Infrastructure Matters for AI at Scale
        </h4>
        <div className="practices-grid">
          <div className="practice-card">
            <div className="practice-icon">🎯</div>
            <h5>Predictable Outcomes</h5>
            <p>
              AI assistants produce consistent, high-quality code when guardrails are
              enforced
            </p>
          </div>
          <div className="practice-card">
            <div className="practice-icon">🔒</div>
            <h5>Quality Gates</h5>
            <p>
              Pre-commit hooks and linting prevent AI hallucinations from entering the
              codebase
            </p>
          </div>
          <div className="practice-card">
            <div className="practice-icon">📐</div>
            <h5>Template Consistency</h5>
            <p>
              Structured templates ensure AI generates code following project patterns
            </p>
          </div>
          <div className="practice-card">
            <div className="practice-icon">🔄</div>
            <h5>Feedback Loops</h5>
            <p>
              Automated testing and linting provide immediate feedback on AI-generated
              code
            </p>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="stats-section">
        <div className="stat-card">
          <div className="stat-number">40+</div>
          <div className="stat-label">Make Targets</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">5</div>
          <div className="stat-label">Linter Categories</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">6</div>
          <div className="stat-label">Code Templates</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">100%</div>
          <div className="stat-label">Docker-based Testing</div>
        </div>
      </div>

      <div style={{ marginTop: '3rem' }}></div>

      <div className="action-section">
        <h4 className="section-title">
          <span className="section-icon">🚀</span>
          Try the Infrastructure
        </h4>
        <div className="action-links">
          <a
            href="https://github.com/stevej-at-benlabs/durable-code-test/tree/main/.ai"
            className="action-link primary"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="link-icon">📂</span>
            Explore .ai Repository
          </a>
          <a
            href="https://github.com/stevej-at-benlabs/durable-code-test/blob/main/Makefile.lint"
            className="action-link secondary"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="link-icon">🔧</span>
            View Make Targets
          </a>
          <a
            href="https://github.com/stevej-at-benlabs/durable-code-test/tree/main/tools/design_linters"
            className="action-link secondary"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="link-icon">🎯</span>
            Custom Linters
          </a>
          <a
            href="https://github.com/stevej-at-benlabs/durable-code-test/blob/main/.pre-commit-config.yaml"
            className="action-link secondary"
            target="_blank"
            rel="noopener noreferrer"
          >
            <span className="link-icon">🔒</span>
            Pre-commit Config
          </a>
        </div>
      </div>
    </div>
  );
}
