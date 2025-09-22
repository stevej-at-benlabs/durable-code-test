/**
 * Purpose: Infrastructure tab component showcasing AI-ready project setup and architecture
 * Scope: Feature-based React component for displaying infrastructure best practices
 * Overview: Modern React component demonstrating infrastructure setup for AI-assisted development
 *     including project organization, tooling configuration, CI/CD setup, and development
 *     environment preparation. Modularized with proper separation of concerns, CSS modules,
 *     and comprehensive error handling following established patterns.
 * Dependencies: React, infrastructure hooks, common components, CSS modules
 * Exports: InfrastructureTab component (default export), InfrastructureTabProps interface
 * Props/Interfaces: Optional className and error handling callback
 * State/Behavior: Fetches infrastructure data via hook, displays modular content sections
 */

import { useCallback, useMemo, useState } from 'react';
import type { ReactElement } from 'react';
import { ErrorMessage, LoadingSpinner } from '../../../../components/common';
import { useInfrastructure } from '../../hooks/useInfrastructure';
import type {
  FolderItem,
  InfrastructureItem,
  InfrastructureTabProps,
} from '../../types/infrastructure.types';
import styles from './InfrastructureTab.module.css';

/**
 * InfrastructureTab component
 *
 * @param props - Component props
 * @returns Rendered infrastructure tab component
 */
export function InfrastructureTab({
  className = '',
  onError,
}: InfrastructureTabProps): ReactElement {
  const {
    infrastructureItems,
    folderStructure: _folderStructure,
    makeTargets,
    stats,
    actionLinks,
    loading,
    error,
  } = useInfrastructure();

  // State for clicked popup
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  // Component classes
  const componentClasses = useMemo(() => {
    return [
      styles.infrastructureTab,
      'tab-content',
      'infrastructure-content',
      className,
      loading && styles.loading,
      error && styles.error,
    ]
      .filter(Boolean)
      .join(' ');
  }, [className, loading, error]);

  // Event handlers
  const handleItemClick = useCallback((item: InfrastructureItem) => {
    if (item.popup) {
      setSelectedItem(item.id);
    }
  }, []);

  // Error propagation
  if (error) {
    onError?.(error);
  }

  // Render helpers
  const renderInfrastructureGrid = useCallback(() => {
    return (
      <div className={styles.infrastructureGrid}>
        {infrastructureItems.map((item) => (
          <div
            key={item.id}
            className={`${styles.infrastructureCard} feature-card`}
            onClick={() => handleItemClick(item)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleItemClick(item);
              }
            }}
          >
            <div className={styles.cardContent}>
              <div className={styles.cardIcon}>{item.icon}</div>
              <h4 className={styles.cardTitle}>{item.title}</h4>
              <span className={styles.clickHint}>Click to explore</span>
            </div>
          </div>
        ))}
      </div>
    );
  }, [infrastructureItems, handleItemClick]);

  const renderFolderStructure = useCallback(
    (
      items: FolderItem[],
      title: string,
      icon: string,
      description: string,
      benefits: string[],
    ) => {
      return (
        <div className={styles.folderSection}>
          <h4 className="dark-title-on-light">
            <span className="section-icon">{icon}</span>
            {title}
          </h4>
          <div className={styles.folderContainer}>
            <div className={styles.folderPreview}>
              {items.map((item) => {
                const linePrefix =
                  item.depth === 0
                    ? ''
                    : item.depth === 1
                      ? item.isLast
                        ? '└──'
                        : '├──'
                      : item.parentIsLast
                        ? item.isLast
                          ? ' └──'
                          : ' ├──'
                        : item.isLast
                          ? '│ └──'
                          : '│ ├──';

                return (
                  <div
                    key={item.id}
                    className={`${styles.folderItem} ${item.type === 'folder' ? styles.folder : styles.file} ${item.depth > 0 ? styles.nested : styles.root}`}
                  >
                    {linePrefix && (
                      <span className={styles.folderLine}>{linePrefix}</span>
                    )}
                    <span className={styles.icon}>{item.icon}</span>
                    <span className={styles.name}>{item.name}</span>
                    {item.description && (
                      <span className={styles.description}>{item.description}</span>
                    )}
                  </div>
                );
              })}
            </div>
            <div className={styles.folderDescription}>
              <h5>{description}</h5>
              <ul className={styles.benefitList}>
                {benefits.map((benefit, index) => (
                  <li key={index}>{benefit}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      );
    },
    [],
  );

  const _renderMakeTargets = useCallback(() => {
    const benefits = [
      '🔴 Problem: "Works on my machine" syndrome',
      '✅ Solution: Docker wraps everything, pinned versions',
      '🔴 Problem: AI code works once, fails later',
      '✅ Solution: Deterministic execution via make targets',
      '🔴 Problem: Environment drift between dev/prod',
      '✅ Solution: Identical containers everywhere',
      '🔴 Example: make test = same result on any machine',
    ];

    const makeTargetItems: FolderItem[] = makeTargets.map((target, index) => ({
      id: target.name,
      type: 'file' as const,
      name: target.name,
      icon: target.icon,
      description: target.description,
      depth: 1,
      isLast: index === makeTargets.length - 1,
    }));

    // Add root item
    const allItems: FolderItem[] = [
      {
        id: 'repeatable-operations',
        type: 'folder',
        name: 'Repeatable Operations',
        icon: '🎯',
        depth: 0,
      },
      ...makeTargetItems,
    ];

    return renderFolderStructure(
      allItems,
      'Make Targets: Your Shield Against "It Worked Yesterday"',
      '⚙️',
      'Abstract: Deterministic Operations',
      benefits,
    );
  }, [makeTargets, renderFolderStructure]);

  const _renderCustomLinters = useCallback(() => {
    const linterItems: FolderItem[] = [
      {
        id: 'print-statements',
        type: 'file',
        name: 'print() statements',
        icon: '🚫',
        description: 'Ban console.log, print() everywhere',
        depth: 1,
      },
      {
        id: 'logging-consistency',
        type: 'file',
        name: 'Logging consistency',
        icon: '📝',
        description: 'Enforce single logging framework',
        depth: 1,
      },
      {
        id: 'file-placement',
        type: 'file',
        name: 'File placement rules',
        icon: '📁',
        description: 'Tests here, components there',
        depth: 1,
      },
      {
        id: 'magic-numbers',
        type: 'file',
        name: 'Magic number detection',
        icon: '🔢',
        description: 'Constants must be named',
        depth: 1,
      },
      {
        id: 'architecture',
        type: 'file',
        name: 'Architecture patterns',
        icon: '🏗️',
        description: 'SOLID, DRY, design principles',
        depth: 1,
      },
      {
        id: 'security',
        type: 'file',
        name: 'Security patterns',
        icon: '🔒',
        description: 'No hardcoded secrets',
        depth: 1,
      },
      {
        id: 'naming',
        type: 'file',
        name: 'Naming conventions',
        icon: '📋',
        description: 'Variables, functions, classes',
        depth: 1,
      },
      {
        id: 'imports',
        type: 'file',
        name: 'Import organization',
        icon: '📦',
        description: 'Dependencies, structure',
        depth: 1,
      },
      {
        id: 'coverage',
        type: 'file',
        name: 'Test coverage rules',
        icon: '🧪',
        description: 'Missing tests detected',
        depth: 1,
      },
      {
        id: 'docs',
        type: 'file',
        name: 'Documentation requirements',
        icon: '📚',
        description: 'Headers, docstrings, comments',
        depth: 1,
        isLast: true,
      },
    ];

    const allItems: FolderItem[] = [
      {
        id: 'project-standards',
        type: 'folder',
        name: 'Your Project Standards',
        icon: '🎯',
        depth: 0,
      },
      ...linterItems,
    ];

    const benefits = [
      '🔴 Problem: Standard linters miss architecture issues',
      '✅ Solution: Custom rules for SOLID, patterns, security',
      '🔴 Problem: AI generates anti-patterns',
      '✅ Solution: Gate specific violations before commit',
      '🔴 Problem: Manual code review misses issues',
      '✅ Solution: Automated enforcement, consistent standards',
      '🔴 Example: Block print(), enforce error handling',
    ];

    return renderFolderStructure(
      allItems,
      'Custom Design Linters: Beyond Syntax to Architecture',
      '🔧',
      'Abstract: Enforce What Matters to YOUR Project',
      benefits,
    );
  }, [renderFolderStructure]);

  const _renderStats = useCallback(() => {
    return (
      <div className={styles.statsSection}>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>{stats.makeTargets}+</div>
          <div className={styles.statLabel}>Make Targets</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>{stats.linterCategories}</div>
          <div className={styles.statLabel}>Linter Categories</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>{stats.codeTemplates}</div>
          <div className={styles.statLabel}>Code Templates</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statNumber}>{stats.dockerCoverage}</div>
          <div className={styles.statLabel}>Docker-based Testing</div>
        </div>
      </div>
    );
  }, [stats]);

  const _renderActionLinks = useCallback(() => {
    return (
      <div className={styles.actionSection}>
        <h4 className="dark-title-on-light">
          <span className="section-icon">🚀</span>
          Try the Infrastructure
        </h4>
        <div className={styles.actionLinks}>
          {actionLinks.map((link) => (
            <a
              key={link.id}
              href={link.url}
              className={`${styles.actionLink} ${styles[link.type]}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className={styles.linkIcon}>{link.icon}</span>
              {link.text}
            </a>
          ))}
        </div>
      </div>
    );
  }, [actionLinks]);

  // Find selected item for popup
  const selectedInfraItem = useMemo(() => {
    if (!selectedItem) return null;
    return infrastructureItems.find((item) => item.id === selectedItem);
  }, [selectedItem, infrastructureItems]);

  // Loading state
  if (loading) {
    return (
      <div className={componentClasses}>
        <LoadingSpinner className={styles.loadingSpinner} />
        <p>Loading infrastructure data...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={componentClasses}>
        <ErrorMessage
          message={error.message}
          title="Error loading infrastructure"
          variant="error"
          onDismiss={() => window.location.reload()}
          className={styles.errorMessage}
        />
      </div>
    );
  }

  // Main render
  return (
    <div className={componentClasses}>
      {/* Hero section */}
      <div className={styles.infrastructureHero}>
        <h3 className="hero-title">
          <span className={styles.titleIcon}>🏗️</span>
          Why Rigid Infrastructure Matters for AI Development
        </h3>
        <p className="subtitle">
          AI coding assistants are powerful but unpredictable. Without strict repository
          controls, they create inconsistent code, violate conventions, and introduce
          subtle bugs that compound over time. The solution isn't to restrict AI, but to
          create <strong>rigid infrastructure</strong> that channels its creativity
          productively. When every file has a defined location, every operation runs
          identically, and every violation gets caught automatically, AI becomes a
          reliable engineering partner instead of a source of technical debt. The
          patterns below show how to build this foundation.
        </p>
      </div>

      {/* Infrastructure grid */}
      {renderInfrastructureGrid()}

      {/* Popup rendered at component level */}
      {selectedInfraItem && selectedInfraItem.popup && (
        <>
          <div className={styles.popupBackdrop} onClick={() => setSelectedItem(null)} />
          <div className={styles.structuredPopup}>
            {/* Document Header */}
            <div className={styles.documentHeader}>
              <h2 className={styles.documentTitle}>
                <span className={styles.documentIcon}>{selectedInfraItem.icon}</span>
                {selectedInfraItem.title}
              </h2>
              <button
                className={styles.closeButton}
                onClick={() => setSelectedItem(null)}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className={styles.popupContainer}>
              {/* Problem Section */}
              <div className={styles.popupSection}>
                <h3 className={styles.sectionTitle}>
                  <span className={styles.sectionIcon}>🔴</span>
                  The Problem
                </h3>
                <div className={styles.sectionContent}>
                  <h4>{selectedInfraItem.popup.problem.title}</h4>
                  <ul className={styles.pointsList}>
                    {selectedInfraItem.popup.problem.points.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Solution Section */}
              <div className={styles.popupSection}>
                <h3 className={styles.sectionTitle}>
                  <span className={styles.sectionIcon}>✅</span>
                  Our Solution
                </h3>
                <div className={styles.sectionContent}>
                  <h4>{selectedInfraItem.popup.solution.title}</h4>
                  <ul className={styles.pointsList}>
                    {selectedInfraItem.popup.solution.points.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Example Section */}
              <div className={styles.popupSection}>
                <h3 className={styles.sectionTitle}>
                  <span className={styles.sectionIcon}>💻</span>
                  Example from Our Code
                </h3>
                <div className={styles.exampleHeader}>
                  <span className={styles.exampleTitle}>
                    {selectedInfraItem.popup.example.title}
                  </span>
                  {selectedInfraItem.popup.example.file && (
                    <span className={styles.exampleFile}>
                      {selectedInfraItem.popup.example.file}
                    </span>
                  )}
                </div>
                <pre className={styles.codeBlock}>
                  <code
                    className={`language-${selectedInfraItem.popup.example.language}`}
                  >
                    {selectedInfraItem.popup.example.code}
                  </code>
                </pre>
              </div>
            </div>

            {/* Links Section - Outside scrollable area */}
            {selectedInfraItem.popup.links && (
              <div className={styles.popupLinks}>
                {selectedInfraItem.popup.links.map((link, index) => (
                  <a
                    key={index}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.popupLink}
                  >
                    {link.text} →
                  </a>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default InfrastructureTab;
