import React from 'react';
import styles from './Section.module.css';
import type { SectionProps } from './Section.types';

export const Section = React.memo<SectionProps>(
  ({ children, title, variant = 'default', className = '', ...rest }) => {
    const classNames = [styles.section, styles[variant], className]
      .filter(Boolean)
      .join(' ');

    return (
      <section className={classNames} {...rest}>
        {title && <h2 className={styles.title}>{title}</h2>}
        <div className={styles.content}>{children}</div>
      </section>
    );
  },
);

Section.displayName = 'Section';
