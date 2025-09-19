import React from 'react';
import styles from './Card.module.css';
import type { CardProps } from './Card.types';

export const Card = React.memo<CardProps>(
  ({
    children,
    variant = 'default',
    icon,
    title,
    badge,
    clickable = false,
    className = '',
    ...rest
  }) => {
    const classNames = [
      styles.card,
      styles[variant],
      clickable && styles.clickable,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={classNames} {...rest}>
        {icon && <div className={styles.icon}>{icon}</div>}
        {title && <h4 className={styles.title}>{title}</h4>}
        <div className={styles.content}>{children}</div>
        {badge && <div className={styles.badge}>{badge}</div>}
      </div>
    );
  },
);

Card.displayName = 'Card';
