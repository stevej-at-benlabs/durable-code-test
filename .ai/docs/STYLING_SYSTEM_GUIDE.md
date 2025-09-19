# Styling System Guide

**Purpose**: Comprehensive guide for the CSS Modules + CSS Variables theming system
**Scope**: All React components, styling patterns, theme usage, and development practices
**Created**: 2025-09-19
**Updated**: 2025-09-19
**Author**: Frontend Team (PR8 Implementation)
**Version**: 1.0

---

## Overview

This project uses a modern styling approach combining **CSS Modules** for component-scoped styles and **CSS Variables** for systematic theming. This approach ensures consistency, maintainability, and prevents style conflicts while supporting features like dark mode.

## Architecture

### Core Principles

1. **CSS Modules Only**: All component styles use CSS Modules (`.module.css` files)
2. **CSS Variables for Theming**: Use design tokens via CSS custom properties
3. **No Inline Styles**: Avoid `style={{}}` props except for truly dynamic values
4. **Scoped Styling**: Component styles are automatically namespaced
5. **Theme Consistency**: Use theme variables instead of hardcoded values

### File Structure

```
src/
├── styles/                     # Global styles and theme system
│   ├── theme/
│   │   ├── colors.css          # Color palette and semantic tokens
│   │   ├── typography.css      # Font system and text styles
│   │   ├── spacing.css         # Spacing scale and layout tokens
│   │   ├── breakpoints.css     # Responsive utilities
│   │   └── index.css           # Theme system entry point
│   ├── global.css              # Global HTML styles using theme
│   └── reset.css               # Modern CSS reset
├── components/
│   └── ComponentName/
│       ├── ComponentName.tsx
│       ├── ComponentName.module.css  # Component-scoped styles
│       ├── ComponentName.types.ts
│       ├── ComponentName.test.tsx
│       └── index.ts
└── features/
    └── featureName/
        └── components/
            └── ComponentName/
                ├── ComponentName.tsx
                ├── ComponentName.module.css
                └── ...
```

## Theme System

### 1. Colors (`src/styles/theme/colors.css`)

#### Primary Color Palette
```css
/* Usage: Brand colors and primary UI elements */
--color-primary-50: #f4e8d0;    /* Lightest background */
--color-primary-100: #e8d5b7;   /* Light backgrounds */
--color-primary-200: #ddc7a0;   /* Subtle backgrounds */
--color-primary-300: #d4af37;   /* Active/accent color */
--color-primary-400: #b8860b;   /* Interactive elements */
--color-primary-500: #8b6341;   /* Primary brand */
--color-primary-600: #654321;   /* Darker interactions */
--color-primary-700: #3c2414;   /* Dark text/borders */
```

#### Semantic Colors
```css
/* Usage: Consistent color meanings across the app */
--color-text-primary: #3c2414;     /* Main text color */
--color-text-secondary: #654321;   /* Secondary text */
--color-text-tertiary: #8b6341;    /* Muted text */
--color-text-inverse: #f4e8d0;     /* Text on dark backgrounds */

--color-background: var(--color-primary-50);  /* Page background */
--color-surface: #ffffff;                     /* Card/component backgrounds */
--color-surface-elevated: rgba(255, 255, 255, 0.95);  /* Elevated surfaces */
```

#### Component Tokens
```css
/* Usage: Specific component styling */
--button-bg-primary: var(--color-primary-300);
--button-bg-primary-hover: var(--color-primary-400);
--card-bg: var(--color-surface);
--card-border: var(--color-border-light);
--tab-bg-active: var(--color-surface-elevated);
```

### 2. Typography (`src/styles/theme/typography.css`)

#### Font System
```css
--font-primary: 'Georgia', 'Times New Roman', 'Book Antiqua', serif;
--font-secondary: 'Crimson Text', 'Playfair Display', serif;
--font-mono: 'Fira Code', 'Monaco', 'Cascadia Code', monospace;
--font-sans: 'Inter', 'Helvetica Neue', Arial, sans-serif;
```

#### Font Sizes (Progressive Scale)
```css
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
--text-5xl: 3rem;        /* 48px */
--text-6xl: 3.75rem;     /* 60px */
```

#### Component Typography
```css
--hero-title-size: clamp(var(--text-4xl), 5vw, var(--text-6xl));
--card-title-size: var(--text-lg);
--button-text-size: var(--text-base);
--tab-text-size: var(--text-base);
```

### 3. Spacing (`src/styles/theme/spacing.css`)

#### Spacing Scale (rem-based)
```css
--space-0: 0;
--space-1: 0.25rem;      /* 4px */
--space-2: 0.5rem;       /* 8px */
--space-3: 0.75rem;      /* 12px */
--space-4: 1rem;         /* 16px */
--space-6: 1.5rem;       /* 24px */
--space-8: 2rem;         /* 32px */
--space-12: 3rem;        /* 48px */
--space-16: 4rem;        /* 64px */
--space-20: 5rem;        /* 80px */
/* ... more scales ... */
```

#### Semantic Spacing
```css
--spacing-xs: var(--space-1);
--spacing-sm: var(--space-2);
--spacing-md: var(--space-4);
--spacing-lg: var(--space-6);
--spacing-xl: var(--space-8);
```

#### Component Spacing
```css
--container-padding: var(--space-6);
--card-padding: var(--space-6);
--button-padding-x: var(--space-6);
--button-padding-y: var(--space-3);
--tab-padding-x: var(--space-6);
--tab-padding-y: var(--space-4);
```

### 4. Breakpoints (`src/styles/theme/breakpoints.css`)

#### Standard Breakpoints
```css
--bp-xs: 320px;   /* Extra small devices */
--bp-sm: 640px;   /* Small devices (phones) */
--bp-md: 768px;   /* Medium devices (tablets) */
--bp-lg: 1024px;  /* Large devices (laptops) */
--bp-xl: 1280px;  /* Extra large devices (desktops) */
--bp-2xl: 1536px; /* 2X large devices */
```

## Component Styling Patterns

### 1. Basic Component Structure

#### TypeScript Component
```tsx
/**
 * Purpose: Example component with proper CSS Modules usage
 * Dependencies: React, CSS Modules
 * Implementation: Uses theme variables and scoped styles
 */

import type { ReactElement } from 'react';
import styles from './ExampleComponent.module.css';

interface ExampleComponentProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

export function ExampleComponent({
  variant = 'primary',
  size = 'md'
}: ExampleComponentProps): ReactElement {
  return (
    <div className={`${styles.container} ${styles[variant]} ${styles[size]}`}>
      <h3 className={styles.title}>Component Title</h3>
      <p className={styles.description}>Component description</p>
    </div>
  );
}
```

#### CSS Module File
```css
/**
 * Purpose: Styles for ExampleComponent using theme variables
 * Implementation: Component-scoped styles with CSS variables
 */

.container {
  background: var(--card-bg);
  border: 1px solid var(--color-border-light);
  border-radius: var(--space-2);
  padding: var(--card-padding);
  box-shadow: 0 2px 4px var(--card-shadow);
}

.title {
  font-size: var(--card-title-size);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.description {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

/* Variants */
.primary {
  border-color: var(--color-primary-300);
}

.secondary {
  border-color: var(--color-border-medium);
}

/* Sizes */
.sm {
  padding: var(--space-3);
}

.md {
  padding: var(--space-4);
}

.lg {
  padding: var(--space-6);
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    padding: var(--space-3);
  }

  .title {
    font-size: var(--text-base);
  }
}
```

### 2. Advanced Patterns

#### Conditional Classes
```tsx
const componentClasses = [
  styles.component,
  isActive && styles.active,
  variant && styles[variant],
  className // External classes
].filter(Boolean).join(' ');

return <div className={componentClasses}>...</div>;
```

#### CSS Custom Properties for Dynamic Values
```tsx
// For truly dynamic values that can't be predefined
<div
  className={styles.dynamicComponent}
  style={{ '--dynamic-color': userSelectedColor } as React.CSSProperties}
>
  Content
</div>
```

```css
.dynamicComponent {
  background: var(--dynamic-color, var(--color-surface));
}
```

## Dark Mode Support

### Implementation
Dark mode is implemented through CSS custom properties with data attributes:

```css
/* Light theme (default) */
:root {
  --color-background: #f4e8d0;
  --color-text-primary: #3c2414;
}

/* Dark theme */
[data-theme="dark"] {
  --color-background: #1a1a1a;
  --color-text-primary: #f4e8d0;
}
```

### Usage in Components
Components automatically inherit the correct colors through CSS variables:

```css
.component {
  background: var(--color-background);
  color: var(--color-text-primary);
  /* Colors automatically switch based on theme */
}
```

## Development Guidelines

### 1. Creating New Components

1. **Create component directory** with proper structure
2. **Use CSS Modules** for all styling (`.module.css`)
3. **Import styles** and use scoped classes
4. **Use theme variables** instead of hardcoded values
5. **Follow naming conventions** for CSS classes

### 2. CSS Class Naming

```css
/* Use descriptive, component-scoped names */
.componentName { }          /* Root component class */
.componentElement { }       /* Sub-elements */
.componentModifier { }      /* State/variant modifiers */

/* Examples */
.card { }                   /* Card component root */
.cardHeader { }             /* Card header element */
.cardPrimary { }            /* Primary variant */
.cardActive { }             /* Active state */
```

### 3. Responsive Design

```css
/* Mobile-first approach using our breakpoint variables */
.component {
  padding: var(--space-3);
}

@media (min-width: 768px) {
  .component {
    padding: var(--space-6);
  }
}

@media (min-width: 1024px) {
  .component {
    padding: var(--space-8);
  }
}
```

### 4. Animation and Transitions

```css
.interactive {
  transition: all 0.2s ease;
  /* Use consistent timing and easing */
}

.interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px var(--card-shadow);
}
```

## Best Practices

### ✅ Do's

1. **Use CSS Variables**: Always use theme variables for colors, spacing, fonts
2. **CSS Modules Only**: All component styles in `.module.css` files
3. **Semantic Naming**: Use descriptive class names that describe purpose
4. **Mobile-First**: Design for mobile, enhance for larger screens
5. **Consistent Spacing**: Use spacing scale variables for all gaps/padding
6. **Accessible Colors**: Ensure proper contrast ratios for text

### ❌ Don'ts

1. **No Inline Styles**: Avoid `style={{}}` except for dynamic values
2. **No Hardcoded Values**: Don't use raw px/hex values, use variables
3. **No Global CSS**: Don't add styles to global scope unless absolutely necessary
4. **No !important**: Avoid using `!important` declarations
5. **No Deep Nesting**: Keep CSS specificity low, avoid deep nesting

## Migration from Old Styles

### Converting Existing Components

1. **Identify inline styles** and hardcoded values
2. **Create CSS Module file** for the component
3. **Replace hardcoded values** with theme variables
4. **Update component** to use CSS classes
5. **Test thoroughly** to ensure no visual regressions

### Example Migration

**Before (old approach):**
```tsx
<div style={{
  backgroundColor: '#ffffff',
  padding: '16px',
  borderRadius: '8px',
  marginBottom: '24px'
}}>
  <h3 style={{ color: '#3c2414', fontSize: '18px' }}>Title</h3>
</div>
```

**After (new approach):**
```tsx
<div className={styles.card}>
  <h3 className={styles.title}>Title</h3>
</div>
```

```css
.card {
  background: var(--color-surface);
  padding: var(--space-4);
  border-radius: var(--space-2);
  margin-bottom: var(--space-6);
}

.title {
  color: var(--color-text-primary);
  font-size: var(--text-lg);
}
```

## Troubleshooting

### Common Issues

1. **CSS Variables Not Working**: Ensure theme system is imported in `main.tsx`
2. **Styles Not Applied**: Check CSS Module import and class naming
3. **Style Conflicts**: Use browser dev tools to inspect CSS specificity
4. **Missing Variables**: Verify variable exists in theme files

### Debugging Tips

1. **Inspect CSS Variables**: Use browser dev tools to check computed values
2. **Check Import Path**: Ensure CSS Module file is correctly imported
3. **Verify Class Names**: CSS Modules transforms class names, check actual output
4. **Test Without Variables**: Temporarily use hardcoded values to isolate issues

## Performance Considerations

1. **CSS Modules are bundled**: Unused styles are tree-shaken
2. **CSS Variables are efficient**: Browser-native theming support
3. **Minimal runtime cost**: Styles are processed at build time
4. **Cache-friendly**: Static CSS files with good caching headers

## Future Enhancements

1. **CSS-in-JS Migration**: Potential future migration to styled-components or emotion
2. **Design System Package**: Extract theme into reusable npm package
3. **Advanced Theming**: Support for user-customizable themes
4. **CSS Container Queries**: Adopt when browser support improves

---

## Quick Reference

### Importing and Using Styles
```tsx
import styles from './Component.module.css';

export function Component() {
  return (
    <div className={styles.container}>
      <span className={styles.text}>Hello World</span>
    </div>
  );
}
```

### Common CSS Variables
```css
/* Colors */
--color-text-primary
--color-text-secondary
--color-background
--color-surface
--color-primary-300

/* Spacing */
--space-1, --space-2, --space-4, --space-6, --space-8

/* Typography */
--text-sm, --text-base, --text-lg, --text-xl
--font-weight-normal, --font-weight-medium, --font-weight-bold

/* Component Tokens */
--card-padding, --button-padding-x, --tab-padding-y
```

This styling system provides a solid foundation for maintainable, scalable, and consistent UI development while supporting modern features like dark mode and responsive design.
