/**
 * Dynamic Breadcrumb Navigation System
 * Tracks user navigation path and displays contextual breadcrumbs
 *
 * Follows Open-Closed Principle with extensible page registry
 */

(function () {
  'use strict';

  // Page Registry - follows Open-Closed Principle
  // Can be extended without modifying existing code
  class PageRegistry {
    constructor() {
      this.pages = new Map();
      this.initializeDefaultPages();
    }

    // Register a new page without modifying existing code
    register(path, config) {
      this.pages.set(path, config);
      return this;
    }

    // Get page metadata
    get(path) {
      return this.pages.get(path);
    }

    // Check if page exists
    has(path) {
      return this.pages.has(path);
    }

    // Initialize with default pages
    // This method is closed for modification but the registry is open for extension
    initializeDefaultPages() {
      this.register('/', {
        title: 'Home',
        icon: '🏠',
        isRoot: true,
      })
        .register('/index.html', {
          title: 'Home',
          icon: '🏠',
          isRoot: true,
        })
        .register('/ci-cd-pipeline.html', {
          title: 'CI/CD Pipeline',
          icon: '🚀',
          possibleParents: ['/'],
        })
        .register('/custom-linters.html', {
          title: 'Custom Linters',
          icon: '🎯',
          possibleParents: ['/', '/ci-cd-pipeline.html', '/set-standards.html'],
        })
        .register('/set-standards.html', {
          title: 'Standards Guide',
          icon: '📖',
          possibleParents: ['/'],
        });
    }
  }

  // Storage key for navigation history
  const STORAGE_KEY = 'navigation_path';
  const MAX_HISTORY = 10;

  class BreadcrumbNavigator {
    constructor(pageRegistry) {
      this.pageRegistry = pageRegistry;
      this.history = this.loadHistory();
      this.currentPath = this.normalizePath(window.location.pathname);
    }

    normalizePath(path) {
      // Normalize paths to always have .html extension where appropriate
      if (path === '/' || path === '') {
        return '/';
      }
      if (!path.endsWith('.html') && !path.endsWith('/')) {
        return path + '.html';
      }
      return path;
    }

    loadHistory() {
      try {
        const stored = sessionStorage.getItem(STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
      } catch (e) {
        // Silently fail and return empty history
        // Error loading navigation history is not critical
        return [];
      }
    }

    saveHistory() {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(this.history));
      } catch (e) {
        // Silently fail - saving history is not critical
        // Storage might be full or disabled
      }
    }

    updateHistory() {
      // Remove current path if it exists in history (to avoid duplicates)
      this.history = this.history.filter((path) => path !== this.currentPath);

      // Add current path to history
      this.history.push(this.currentPath);

      // Keep only the last MAX_HISTORY entries
      if (this.history.length > MAX_HISTORY) {
        this.history = this.history.slice(-MAX_HISTORY);
      }

      this.saveHistory();
    }

    buildBreadcrumbTrail() {
      const trail = [];
      const metadata = this.pageRegistry.get(this.currentPath);

      if (!metadata) {
        // If page not in metadata, show default breadcrumb
        return this.buildDefaultTrail();
      }

      // If this is the root page, no breadcrumbs needed
      if (metadata.isRoot) {
        return [];
      }

      // Check if we came from a valid parent page
      const referrer = document.referrer;
      let parentPath = null;

      if (referrer) {
        try {
          const referrerUrl = new URL(referrer);
          const referrerPath = this.normalizePath(referrerUrl.pathname);

          // Check if referrer is a valid parent for this page
          if (
            metadata.possibleParents &&
            metadata.possibleParents.includes(referrerPath)
          ) {
            parentPath = referrerPath;
          }
        } catch (e) {
          // Invalid referrer URL, ignore
        }
      }

      // If no valid parent from referrer, check history
      if (!parentPath && this.history.length > 1) {
        // Look through history in reverse to find a valid parent
        for (let i = this.history.length - 2; i >= 0; i--) {
          const historyPath = this.history[i];
          if (
            metadata.possibleParents &&
            metadata.possibleParents.includes(historyPath)
          ) {
            parentPath = historyPath;
            break;
          }
        }
      }

      // Build the trail
      if (parentPath) {
        // If we have a valid parent, build trail from root to parent to current
        trail.push(this.createBreadcrumbItem('/', true));

        if (parentPath !== '/') {
          const parentMetadata = this.pageRegistry.get(parentPath);
          if (parentMetadata) {
            trail.push(this.createBreadcrumbItem(parentPath, true));
          }
        }
      } else {
        // Default: just show Home as parent
        trail.push(this.createBreadcrumbItem('/', true));
      }

      // Add current page (not as link)
      trail.push(this.createBreadcrumbItem(this.currentPath, false));

      return trail;
    }

    buildDefaultTrail() {
      const trail = [];
      trail.push(this.createBreadcrumbItem('/', true));

      // Try to determine page title from document
      const pageTitle = document.title.split('-')[0].trim() || 'Current Page';
      trail.push({
        title: pageTitle,
        path: this.currentPath,
        icon: '📄',
        isLink: false,
      });

      return trail;
    }

    createBreadcrumbItem(path, isLink = true) {
      const metadata = this.pageRegistry.get(path) || {};
      return {
        title: metadata.title || 'Unknown',
        path: path,
        icon: metadata.icon || '📄',
        isLink: isLink,
      };
    }

    renderBreadcrumbs() {
      const trail = this.buildBreadcrumbTrail();

      if (trail.length === 0) {
        return ''; // No breadcrumbs for home page
      }

      const items = trail
        .map((item, index) => {
          const isLast = index === trail.length - 1;

          if (item.isLink) {
            const href = item.path === '/' ? '/' : item.path;
            return `
                        <a href="${href}" class="breadcrumb-link">
                            ${item.icon ? item.icon + ' ' : ''}${item.title}
                        </a>
                        ${!isLast ? '<span class="separator">›</span>' : ''}
                    `;
          } else {
            return `
                        <span class="current">
                            ${item.icon ? item.icon + ' ' : ''}${item.title}
                        </span>
                    `;
          }
        })
        .join('');

      return `<div class="breadcrumb">${items}</div>`;
    }

    injectBreadcrumbs() {
      // Look for existing breadcrumb container
      let container = document.querySelector('.breadcrumb');

      if (!container) {
        // If no breadcrumb container, look for nav-header
        const navHeader = document.querySelector('.nav-header');
        if (navHeader) {
          container = document.createElement('div');
          container.className = 'breadcrumb';
          navHeader.appendChild(container);
        }
      }

      if (container) {
        container.innerHTML = this.renderBreadcrumbs()
          .replace('<div class="breadcrumb">', '')
          .replace('</div>', '');
      }

      // Update history after rendering
      this.updateHistory();
    }

    init() {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => this.injectBreadcrumbs());
      } else {
        this.injectBreadcrumbs();
      }

      // Add styles if not already present
      if (!document.querySelector('#breadcrumb-styles')) {
        const styles = document.createElement('style');
        styles.id = 'breadcrumb-styles';
        styles.textContent = `
                    .breadcrumb {
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                        font-size: 0.95rem;
                        flex-wrap: wrap;
                    }
                    .breadcrumb-link {
                        color: #0066cc;
                        text-decoration: none;
                    }
                    .breadcrumb-link:hover {
                        text-decoration: underline;
                    }
                    .breadcrumb .separator {
                        color: #999;
                        margin: 0 0.25rem;
                    }
                    .breadcrumb .current {
                        color: #333;
                        font-weight: 600;
                    }
                `;
        document.head.appendChild(styles);
      }
    }
  }

  // Create the page registry (extensible without modification)
  const pageRegistry = new PageRegistry();

  // Initialize breadcrumb navigator with the registry
  const navigator = new BreadcrumbNavigator(pageRegistry);
  navigator.init();

  // Expose both registry and navigator to global scope
  // This allows external code to extend the registry without modifying this file
  window.BreadcrumbPageRegistry = pageRegistry;
  window.BreadcrumbNavigator = navigator;

  // Example of how to extend from external code:
  // window.BreadcrumbPageRegistry.register('/new-page.html', {
  //   title: 'New Page',
  //   icon: '📑',
  //   possibleParents: ['/']
  // });
})();
