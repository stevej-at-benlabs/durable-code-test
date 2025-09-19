/**
 * Purpose: Building tab feature component for AI-powered development tools
 * Scope: React component for displaying development methodologies and tool integrations
 * Overview: Modularized building tab with commands, capabilities, templates showcase
 * Dependencies: React, React Router, useBuilding hook, CSS modules
 * Exports: BuildingTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Feature-based architecture with separation of concerns
 */

import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import { useBuilding } from '../../hooks/useBuilding';
import styles from './BuildingTab.module.css';

export function BuildingTab(): ReactElement {
  const { commands, capabilities, aiCommands, templates, howToGuides, standards } =
    useBuilding();

  return (
    <div className={styles.container}>
      {/* Hero Section */}
      <div className={styles.hero}>
        <div className={styles.heroIcon}>⚡</div>
        <h3 className={styles.title}>AI-Powered Code Generation</h3>
        <p className={styles.subtitle}>
          Build complete applications without writing a single line of code - powered by
          AI-driven development and intelligent automation
        </p>
      </div>

      {/* Slash Commands Section */}
      <section>
        <div className={styles.sectionHeader}>
          <h4 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>⚡</span>
            Slash Commands
          </h4>
          <div className={styles.sectionBadge}>4 Available</div>
        </div>

        <div className={styles.commandCards}>
          {commands.map((cmd) => (
            <div key={cmd.id} className={styles.commandCard}>
              <div className={styles.commandHeader}>
                <span className={styles.commandIcon}>{cmd.icon}</span>
                <span className={styles.commandType}>{cmd.type}</span>
              </div>
              <code className={styles.commandSyntax}>{cmd.syntax}</code>
              <p className={styles.commandDesc}>{cmd.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* New Code Capabilities Section */}
      <section>
        <div className={styles.sectionHeader}>
          <h4 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>🛠️</span>
            /new-code Capabilities
          </h4>
          <div className={styles.sectionBadge}>Smart Generation</div>
        </div>

        <div className={styles.commandCards}>
          {capabilities.map((cap) => (
            <div key={cap.id} className={styles.commandCard}>
              <div className={styles.commandHeader}>
                <span className={styles.commandIcon}>{cap.icon}</span>
                <span className={styles.commandType}>{cap.type}</span>
              </div>
              <code className={styles.commandSyntax}>{cap.syntax}</code>
              <p className={styles.commandDesc}>{cap.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* AI-Powered Commands Section */}
      <section>
        <div className={styles.sectionHeader}>
          <h4 className={styles.sectionTitle}>
            <span className={styles.sectionIcon}>🤖</span>
            AI-Powered Slash Commands
          </h4>
          <div className={styles.sectionBadge}>New</div>
        </div>

        <div className={styles.aiCommandCards}>
          {aiCommands.map((cmd) => (
            <div key={cmd.id} className={styles.aiCommandCard}>
              <div className={styles.aiCommandIcon}>{cmd.icon}</div>
              <h5 className={styles.aiCommandName}>{cmd.name}</h5>
              <p className={styles.aiCommandDesc}>{cmd.description}</p>
              <div className={styles.aiCommandFeatures}>
                {cmd.features.map((feature) => (
                  <span key={feature} className={styles.featureTag}>
                    {feature}
                  </span>
                ))}
              </div>
              <div className={styles.aiCommandModes}>
                {cmd.modes.map((mode, idx) => (
                  <div key={idx} className={styles.modeItem}>
                    <code>{mode.syntax}</code>
                    <span>{mode.description}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* AI Templates Section */}
      <section>
        <h4 className={styles.sectionTitle}>
          <span className={styles.sectionIcon}>📄</span>
          AI Templates (.ai/templates)
        </h4>
        <div className={styles.templatesGrid}>
          {templates.map((template) => (
            <div key={template.id} className={styles.templateCard}>
              <div className={styles.templateIcon}>{template.icon}</div>
              <h5 className={styles.templateName}>{template.filename}</h5>
              <p className={styles.templateDesc}>{template.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How-To Guides Section */}
      <section>
        <h4 className={styles.sectionTitle}>
          <span className={styles.sectionIcon}>📚</span>
          How-To Guides (.ai/howto)
        </h4>
        <div className={styles.howtoGrid}>
          {howToGuides.map((guide) => (
            <div key={guide.id} className={styles.howtoCard}>
              <div className={styles.howtoIcon}>{guide.icon}</div>
              <h5 className={styles.howtoTitle}>{guide.title}</h5>
              <p className={styles.howtoDesc}>{guide.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Standards Section */}
      <section>
        <div className={styles.standardsCard}>
          <div className={styles.sectionHeader}>
            <h4 className={styles.sectionTitle}>
              <span className={styles.sectionIcon}>📋</span>
              Development Standards (.ai/docs/STANDARDS.md)
            </h4>
            <div className={styles.sectionBadge}>Essential</div>
          </div>
          <div className={styles.standardsGrid}>
            {standards.map((standard) => (
              <div key={standard.id} className={styles.standardItem}>
                <div className={styles.standardIcon}>{standard.icon}</div>
                <div className={styles.standardContent}>
                  <h5>{standard.title}</h5>
                  <p>{standard.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Action Section */}
      <section className={styles.actionSection}>
        <h4 className={styles.sectionTitle}>
          <span className={styles.sectionIcon}>🚀</span>
          Get Started
        </h4>
        <div className={styles.actionLinks}>
          <a
            href="tools/new-code/README.md"
            className={`${styles.actionLink} ${styles.primary}`}
          >
            <span className={styles.linkIcon}>📖</span>
            Documentation
          </a>
          <a
            href="https://github.com/yourusername/new-code"
            className={`${styles.actionLink} ${styles.secondary}`}
          >
            <span className={styles.linkIcon}>💻</span>
            Source Code
          </a>
          <Link
            to="/standards?return=Building"
            className={`${styles.actionLink} ${styles.tertiary}`}
          >
            <span className={styles.linkIcon}>🎯</span>
            Standards Guide
          </Link>
        </div>
      </section>
    </div>
  );
}
