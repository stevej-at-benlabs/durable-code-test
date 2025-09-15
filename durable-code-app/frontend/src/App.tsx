/**
 * Home page showcasing different techniques for authoring durable code with AI
 * Demonstrates best practices, patterns, and methodologies for AI-assisted development
 */
import { useState } from 'react';
import './App.css';
import packageJson from '../package.json';

interface Technique {
  id: string;
  title: string;
  description: string;
  category: 'Testing' | 'Architecture' | 'Documentation' | 'Quality' | 'Collaboration';
  icon: string;
  benefits: string[];
  links?: { label: string; url: string }[];
}

const techniques: Technique[] = [
  {
    id: 'set-standards',
    title: 'Set Standards First',
    description:
      'Define comprehensive development standards before AI generates code. Front-load quality requirements, patterns, and constraints.',
    category: 'Quality',
    icon: '🎯',
    benefits: [
      'Consistent code quality',
      'Automated enforcement',
      'Clear expectations',
      'Reduced refactoring',
    ],
    links: [{ label: '📖 View Standards Guide', url: 'set-standards.html' }],
  },
  {
    id: 'tdd',
    title: 'Test-Driven Development with AI',
    description:
      'Write tests first, then let AI generate implementation that passes all tests.',
    category: 'Testing',
    icon: '🧪',
    benefits: [
      'Higher code quality',
      'Better design',
      'Automated verification',
      'Regression prevention',
    ],
  },
  {
    id: 'design-patterns',
    title: 'AI-Assisted Design Patterns',
    description:
      'Leverage AI to implement proven architectural patterns correctly and consistently.',
    category: 'Architecture',
    icon: '🏗️',
    benefits: [
      'Consistent structure',
      'Maintainable code',
      'Scalable solutions',
      'Team alignment',
    ],
  },
  {
    id: 'doc-driven',
    title: 'Documentation-First Development',
    description:
      'Start with comprehensive docs, then use AI to generate code that matches specifications.',
    category: 'Documentation',
    icon: '📚',
    benefits: [
      'Clear requirements',
      'Better communication',
      'Easier onboarding',
      'Reduced ambiguity',
    ],
    links: [{ label: '📊 View CI/CD Pipeline Diagram', url: 'ci-cd-pipeline.html' }],
  },
  {
    id: 'code-review',
    title: 'AI-Enhanced Code Reviews',
    description:
      'Use AI to catch issues, suggest improvements, and ensure adherence to standards.',
    category: 'Quality',
    icon: '🔍',
    benefits: [
      'Faster reviews',
      'Consistent standards',
      'Learning opportunities',
      'Issue prevention',
    ],
    links: [{ label: '🚀 CI/CD Pipeline & Checks', url: 'ci-cd-pipeline.html' }],
  },
  {
    id: 'pair-programming',
    title: 'AI Pair Programming',
    description:
      'Collaborate with AI as a coding partner for real-time feedback and suggestions.',
    category: 'Collaboration',
    icon: '👥',
    benefits: [
      'Continuous feedback',
      'Knowledge sharing',
      'Reduced bugs',
      'Faster development',
    ],
  },
];

function App() {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [hoveredTechnique, setHoveredTechnique] = useState<string | null>(null);

  const categories = ['All', ...Array.from(new Set(techniques.map((t) => t.category)))];
  const filteredTechniques =
    selectedCategory === 'All'
      ? techniques
      : techniques.filter((t) => t.category === selectedCategory);

  return (
    <div className="app">
      <header className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="gradient-text">Durable Code</span> with AI
          </h1>
          <p className="hero-subtitle">
            Master the art of creating maintainable, scalable, and robust software
            through AI-assisted development techniques
          </p>
          <div className="hero-actions">
            <a href="set-standards.html" className="hero-cta">
              🎯 Set Standards First
            </a>
          </div>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-number">6</span>
              <span className="stat-label">Core Techniques</span>
            </div>
            <div className="stat">
              <span className="stat-number">5</span>
              <span className="stat-label">Categories</span>
            </div>
            <div className="stat">
              <span className="stat-number">∞</span>
              <span className="stat-label">Possibilities</span>
            </div>
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="techniques-section">
          <div className="section-header">
            <h2>Proven Techniques</h2>
            <p>
              Explore different approaches to building durable code with AI assistance
            </p>
          </div>

          <div className="filter-bar">
            {categories.map((category) => (
              <button
                key={category}
                className={`filter-btn ${selectedCategory === category ? 'active' : ''}`}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>

          <div className="techniques-grid">
            {filteredTechniques.map((technique) => (
              <div
                key={technique.id}
                className={`technique-card ${hoveredTechnique === technique.id ? 'hovered' : ''}`}
                onMouseEnter={() => setHoveredTechnique(technique.id)}
                onMouseLeave={() => setHoveredTechnique(null)}
              >
                <div className="card-header">
                  <span className="card-icon">{technique.icon}</span>
                  <span className="card-category">{technique.category}</span>
                </div>
                <h3 className="card-title">{technique.title}</h3>
                <p className="card-description">{technique.description}</p>
                <div className="card-benefits">
                  <h4>Key Benefits:</h4>
                  <ul>
                    {technique.benefits.map((benefit, index) => (
                      <li key={index}>{benefit}</li>
                    ))}
                  </ul>
                </div>
                {technique.links && (
                  <div className="card-links">
                    {technique.links.map((link, index) => (
                      <a
                        key={index}
                        href={link.url}
                        className="card-link"
                        onClick={(e) => {
                          e.stopPropagation();
                          window.location.href = link.url;
                        }}
                      >
                        {link.label}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="principles-section">
          <div className="section-header">
            <h2>Core Principles</h2>
            <p>Fundamental guidelines for creating durable code with AI</p>
          </div>

          <div className="principles-grid">
            <div className="principle-item">
              <div className="principle-icon">🎯</div>
              <h3>Purpose-Driven</h3>
              <p>Every line of code should serve a clear, well-defined purpose</p>
            </div>
            <div className="principle-item">
              <div className="principle-icon">🔄</div>
              <h3>Iterative Improvement</h3>
              <p>Continuously refine and enhance code quality through AI feedback</p>
            </div>
            <div className="principle-item">
              <div className="principle-icon">🛡️</div>
              <h3>Defensive Programming</h3>
              <p>Anticipate failures and build robust error handling mechanisms</p>
            </div>
            <div className="principle-item">
              <div className="principle-icon">📖</div>
              <h3>Self-Documenting</h3>
              <p>Code should be readable and self-explanatory to humans and AI</p>
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

export default App;
