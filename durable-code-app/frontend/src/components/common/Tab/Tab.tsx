import React from 'react';
import styles from './Tab.module.css';
import type { TabProps } from './Tab.types';

export const Tab = React.memo<TabProps>(
  ({ children, isActive = false, variant = 'default', className = '', ...rest }) => {
    const classNames = [
      styles.tab,
      styles[variant],
      isActive && styles.active,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button
        className={classNames}
        type="button"
        role="tab"
        aria-selected={isActive}
        {...rest}
      >
        {children}
      </button>
    );
  },
);

Tab.displayName = 'Tab';
