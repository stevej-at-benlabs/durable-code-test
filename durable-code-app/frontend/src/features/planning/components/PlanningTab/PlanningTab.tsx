/**
 * Purpose: Planning tab feature component for project planning and documentation
 * Scope: React component for displaying planning resources and workflows
 * Overview: Modularized planning tab with data management via custom hook
 * Dependencies: React, usePlanning hook, CSS modules
 * Exports: PlanningTab component
 * Props/Interfaces: No props - self-contained feature component
 * Implementation: Feature-based architecture with separation of concerns
 */

import type { ReactElement } from 'react';
import { usePlanning } from '../../hooks/usePlanning';
import styles from './PlanningTab.module.css';

export function PlanningTab(): ReactElement {
  const { planningSection } = usePlanning();

  return (
    <div className={styles.container}>
      <div className={styles.hero}>
        <h3 className={styles.title}>
          <span className={styles.titleIcon}>{planningSection.icon}</span>
          {planningSection.title}
        </h3>
        <p className={styles.subtitle}>{planningSection.subtitle}</p>
      </div>

      <div className={styles.grid}>
        {planningSection.documents.map((doc) => (
          <div key={doc.id} className={styles.card}>
            <span className={styles.cardIcon}>{doc.icon}</span>
            <h4 className={styles.cardTitle}>{doc.title}</h4>
            <p className={styles.cardDescription}>{doc.description}</p>
            <a href={doc.href} className={styles.cardLink}>
              View {doc.title.split(' ')[0]} →
            </a>
            <div className={styles.cardBadge}>{doc.badge}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
