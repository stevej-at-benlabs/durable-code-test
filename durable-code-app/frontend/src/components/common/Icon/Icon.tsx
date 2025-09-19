import React from 'react';
import styles from './Icon.module.css';
import type { IconProps } from './Icon.types';

export const Icon = React.memo<IconProps>(
  ({ emoji, label, size = 'medium', className = '', ...rest }) => {
    const classNames = [styles.icon, styles[size], className].filter(Boolean).join(' ');

    return (
      <span className={classNames} role="img" aria-label={label} {...rest}>
        {emoji}
      </span>
    );
  },
);

Icon.displayName = 'Icon';
