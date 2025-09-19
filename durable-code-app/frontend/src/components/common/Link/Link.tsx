import React from 'react';
import styles from './Link.module.css';
import type { LinkProps } from './Link.types';

export const Link = React.memo<LinkProps>(
  ({
    children,
    href,
    variant = 'default',
    external = false,
    className = '',
    target,
    rel,
    ...rest
  }) => {
    const classNames = [styles.link, styles[variant], className]
      .filter(Boolean)
      .join(' ');

    // Determine if link is external by checking if it starts with http/https or has external prop
    const isExternal =
      external || href.startsWith('http://') || href.startsWith('https://');

    // Set appropriate target and rel for external links
    const linkTarget = target || (isExternal ? '_blank' : undefined);
    const linkRel = rel || (isExternal ? 'noopener noreferrer' : undefined);

    const handleClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
      // For internal links, prevent page refresh (could be enhanced with router integration)
      if (!isExternal && !target) {
        // This is where you might integrate with your router (e.g., React Router)
        // For now, we'll let the default behavior happen
      }

      // Call original onClick if provided
      if (rest.onClick) {
        rest.onClick(event);
      }
    };

    return (
      <a
        className={classNames}
        href={href}
        target={linkTarget}
        rel={linkRel}
        onClick={handleClick}
        {...rest}
      >
        {children}
      </a>
    );
  },
);

Link.displayName = 'Link';
