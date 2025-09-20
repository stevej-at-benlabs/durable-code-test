/**
 * Purpose: Quality Assurance tab for code quality tools and metrics
 * Scope: React component for QA practices and linter statistics
 * Overview: Modularized QA tab with CSS Modules styling
 * Dependencies: React, React Router
 * Exports: QualityAssuranceTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Feature module with CSS Modules
 */

import type { ReactElement } from 'react';
import { Link } from 'react-router-dom';
import styles from './QualityAssuranceTab.module.css';

export function QualityAssuranceTab(): ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.hero}>
        <h3 className="hero-title">
          <span className={styles.titleIcon}>🛡️</span>
          Bulletproof Code Quality
        </h3>
        <p className="subtitle">
          Comprehensive automated testing, custom linting, and AI-powered validation to
          ensure your code meets the highest standards
        </p>
      </div>

      <div className={styles.showcaseSection}>
        <div className={styles.showcaseHeader}>
          <h4 className="dark-title-on-light">
            <span className={styles.showcaseIcon}>🔍</span>
            Custom Linters
          </h4>
          <div className={`${styles.badge} ${styles.active}`}>18+ Active</div>
        </div>

        <div className={styles.linterCards}>
          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>🔢</div>
            <h5 className="dark-title-on-light">Magic Number Detection</h5>
            <p className={styles.linterDesc}>
              Identifies hardcoded values and complex literals
            </p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 12 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 8 fixed
              </span>
            </div>
          </div>

          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>📁</div>
            <h5 className="dark-title-on-light">File Organization</h5>
            <p className={styles.linterDesc}>
              Ensures proper module structure and placement
            </p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 3 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 3 fixed
              </span>
            </div>
          </div>

          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>🖨️</div>
            <h5 className="dark-title-on-light">Print & Console Output</h5>
            <p className={styles.linterDesc}>
              Detects print statements and console methods
            </p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 5 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 5 fixed
              </span>
            </div>
          </div>

          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>📊</div>
            <h5 className="dark-title-on-light">Logging Standards</h5>
            <p className={styles.linterDesc}>Enforces structured logging with Loguru</p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 9 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 7 fixed
              </span>
            </div>
          </div>

          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>🏗️</div>
            <h5 className="dark-title-on-light">SOLID Principles</h5>
            <p className={styles.linterDesc}>
              Validates SRP, class size, and dependencies
            </p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 18 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 15 fixed
              </span>
            </div>
          </div>

          <div className={styles.linterCard}>
            <div className={styles.linterIcon}>📏</div>
            <h5 className="dark-title-on-light">Naming Conventions</h5>
            <p className={styles.linterDesc}>Enforces consistent naming standards</p>
            <div className={styles.linterStats}>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>⚠️</span> 7 found
              </span>
              <span className={styles.statItem}>
                <span className={styles.statIcon}>✔️</span> 7 fixed
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.metricsGrid}>
        <div className={`${styles.metricCard} ${styles.success}`}>
          <div className={styles.metricIcon}>🎯</div>
          <div className={styles.metricValue}>99.2%</div>
          <div className={styles.metricLabel}>Code Coverage</div>
        </div>
        <div className={`${styles.metricCard} ${styles.info}`}>
          <div className={styles.metricIcon}>⚡</div>
          <div className={styles.metricValue}>A+</div>
          <div className={styles.metricLabel}>Code Quality</div>
        </div>
        <div className={`${styles.metricCard} ${styles.warning}`}>
          <div className={styles.metricIcon}>🐛</div>
          <div className={styles.metricValue}>0.3</div>
          <div className={styles.metricLabel}>Bugs per KLOC</div>
        </div>
        <div className={`${styles.metricCard} ${styles.success}`}>
          <div className={styles.metricIcon}>✅</div>
          <div className={styles.metricValue}>100%</div>
          <div className={styles.metricLabel}>CI/CD Pass Rate</div>
        </div>
      </div>

      <div className={styles.showcaseSection}>
        <div className={styles.showcaseHeader}>
          <h4 className={styles.showcaseTitle}>
            <span className={styles.showcaseIcon}>🚀</span>
            CI/CD Pipeline
          </h4>
          <div className={`${styles.badge} ${styles.success}`}>All Systems Go</div>
        </div>

        <div className={styles.pipelineStages}>
          <div className={`${styles.stageItem} ${styles.completed}`}>
            <div className={styles.stageIcon}>📦</div>
            <div className={styles.stageName}>Build</div>
            <div className={styles.stageTime}>1.2s</div>
          </div>
          <div className={`${styles.stageItem} ${styles.completed}`}>
            <div className={styles.stageIcon}>🔍</div>
            <div className={styles.stageName}>Lint</div>
            <div className={styles.stageTime}>0.8s</div>
          </div>
          <div className={`${styles.stageItem} ${styles.completed}`}>
            <div className={styles.stageIcon}>🧪</div>
            <div className={styles.stageName}>Test</div>
            <div className={styles.stageTime}>2.4s</div>
          </div>
          <div className={`${styles.stageItem} ${styles.completed}`}>
            <div className={styles.stageIcon}>🛡️</div>
            <div className={styles.stageName}>Security</div>
            <div className={styles.stageTime}>1.1s</div>
          </div>
          <div className={`${styles.stageItem} ${styles.completed}`}>
            <div className={styles.stageIcon}>🚀</div>
            <div className={styles.stageName}>Deploy</div>
            <div className={styles.stageTime}>3.2s</div>
          </div>
        </div>
      </div>

      <div className={styles.reportsSection}>
        <h4 className="dark-title-on-light">
          <span className={styles.sectionIcon}>📊</span>
          Latest Reports
        </h4>
        <div className={styles.reportsGrid}>
          <a href="/reports/linter-summary.html" className={styles.reportCard}>
            <div className={styles.reportIcon}>📋</div>
            <h5 className={styles.reportTitle}>Linter Summary</h5>
            <p className={styles.reportDesc}>
              Comprehensive analysis of all linting results
            </p>
            <span className={styles.reportLink}>View Report →</span>
          </a>
          <a href="/reports/test-coverage.html" className={styles.reportCard}>
            <div className={styles.reportIcon}>📈</div>
            <h5 className={styles.reportTitle}>Test Coverage</h5>
            <p className={styles.reportDesc}>
              Detailed coverage metrics and gaps analysis
            </p>
            <span className={styles.reportLink}>View Report →</span>
          </a>
          <Link to="/standards?return=QualityAssurance" className={styles.reportCard}>
            <div className={styles.reportIcon}>🎯</div>
            <h5 className={styles.reportTitle}>Standards Check</h5>
            <p className={styles.reportDesc}>
              Compliance with coding standards and best practices
            </p>
            <span className={styles.reportLink}>View Standards →</span>
          </Link>
        </div>
      </div>

      <div className={styles.caseStudySection}>
        <div className={styles.caseStudyCard}>
          <h4 className={styles.caseStudyTitle}>
            <span className={styles.caseIcon}>💡</span>
            Real Impact: From 87 Issues to Zero
          </h4>
          <p className={styles.caseStudyContent}>
            Our custom linting framework identified and auto-fixed 87 code quality
            issues in a legacy codebase, improving maintainability scores by 43% and
            reducing bug reports by 68% in the first month.
          </p>
          <div className={styles.caseStudyStats}>
            <div className={styles.stat}>
              <span className={styles.statValue}>87→0</span>
              <span className={styles.statLabel}>Issues Fixed</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>43%↑</span>
              <span className={styles.statLabel}>Maintainability</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>68%↓</span>
              <span className={styles.statLabel}>Bug Reports</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
