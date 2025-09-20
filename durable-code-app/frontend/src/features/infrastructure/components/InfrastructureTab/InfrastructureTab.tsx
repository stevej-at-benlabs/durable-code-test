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

import { useCallback, useMemo } from 'react';
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
    folderStructure,
    makeTargets,
    stats,
    actionLinks,
    loading,
    error,
  } = useInfrastructure();

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
    if (item.link) {
      window.open(item.link, '_blank', 'noopener,noreferrer');
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
            <div className="card-icon">{item.icon}</div>
            <h4 className="dark-title-on-light">{item.title}</h4>
            <p>{item.description}</p>
            <div className="card-badge">{item.badge}</div>
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

  const renderMakeTargets = useCallback(() => {
    const benefits = [
      '🎯 Same command = same result',
      '🎯 Dockerized environments eliminate drift',
      '🎯 Pinned dependencies prevent surprises',
      '🎯 AI can author targets, humans verify',
      '🎯 Automation reduces human inconsistency',
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
      'Make Targets: Determinism Against AI Chaos',
      '⚙️',
      'Determinism vs AI Variability',
      benefits,
    );
  }, [makeTargets, renderFolderStructure]);

  const renderCustomLinters = useCallback(() => {
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
      '🎯 Catch violations early',
      '🎯 Prevent technical debt',
      '🎯 Automate code reviews',
      '🎯 Scale team consistency',
      '🎯 Reduce AI hallucinations',
    ];

    return renderFolderStructure(
      allItems,
      'Custom Linters: Gate Everything You Care About',
      '🔧',
      'If You Care About It, Gate It',
      benefits,
    );
  }, [renderFolderStructure]);

  const renderStats = useCallback(() => {
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

  const renderActionLinks = useCallback(() => {
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
          Rigid Infrastructure: The Foundation for AI
        </h3>
        <p className="subtitle">
          AI collaboration at scale requires uncompromising infrastructure discipline.
          This project shows some examples of the rigid standards, automated quality
          controls, and structured documentation that make AI-assisted development
          predictable and reliable.
        </p>
      </div>

      {/* Infrastructure grid */}
      {renderInfrastructureGrid()}

      {/* Folder structure section */}
      {renderFolderStructure(
        folderStructure,
        'The .ai Repository Structure',
        '📂',
        'Infrastructure Benefits',
        [
          '✅ AI agents navigate efficiently with structured index',
          '✅ Template-driven consistent code generation',
          '✅ Comprehensive standards prevent drift',
          '✅ Step-by-step guides ensure reproducibility',
          '✅ Feature docs maintain architectural integrity',
          '✅ Quality gates prevent regressions',
        ],
      )}

      {/* Make targets section */}
      {renderMakeTargets()}

      <div style={{ marginTop: '3rem' }} />

      {/* Custom linters section */}
      {renderCustomLinters()}

      <div style={{ marginTop: '3rem' }} />

      {/* Stats section */}
      {renderStats()}

      <div style={{ marginTop: '3rem' }} />

      {/* Action links section */}
      {renderActionLinks()}
    </div>
  );
}

export default InfrastructureTab;
