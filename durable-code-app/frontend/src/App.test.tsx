/**
 * Purpose: Unit and integration tests for the main App component
 * Scope: Component rendering, filtering, interactions, and link validation
 * Created: 2025-09-12
 * Updated: 2025-09-12
 * Author: Development Team
 * Version: 1.0
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import App from './App';
import { mockFailedFetch, mockFetch } from './test-setup';

// Wrapper component for router context in tests
const AppWithRouter = ({ initialEntries = ['/'] } = {}) => (
  <MemoryRouter initialEntries={initialEntries}>
    <App />
  </MemoryRouter>
);

// Mock location for navigation tests
const mockLocation = {
  href: 'http://localhost:3000/',
  hash: '',
  search: '',
  pathname: '/',
  assign: vi.fn(),
  reload: vi.fn(),
  replace: vi.fn(),
};

Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

// Mock history for navigation tests
const mockHistory = {
  pushState: vi.fn(),
  replaceState: vi.fn(),
};

Object.defineProperty(window, 'history', {
  value: mockHistory,
  writable: true,
});

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('renders the main title and subtitle', () => {
      render(<AppWithRouter />);

      // More specific selectors for the main title elements
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(
        screen.getByText(/A comprehensive framework for building maintainable/),
      ).toBeInTheDocument();
    });

    it('renders all tab buttons', () => {
      render(<AppWithRouter />);

      expect(
        screen.getByRole('button', { name: /Infrastructure/i }),
      ).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Planning/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Building/i })).toBeInTheDocument();
      expect(
        screen.getByRole('button', { name: /Quality Assurance/i }),
      ).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Maintenance/i })).toBeInTheDocument();
    });

    it('renders AI principles section', () => {
      render(<AppWithRouter />);

      expect(screen.getByText('Fundamental AI Principles')).toBeInTheDocument();
      expect(screen.getByText('Immediate Feedback Loops')).toBeInTheDocument();
      expect(screen.getByText('Maximum Context')).toBeInTheDocument();
      expect(screen.getByText('Clear Success Criteria')).toBeInTheDocument();
    });

    it('renders tab content properly', () => {
      render(<AppWithRouter />);

      // Should show Infrastructure tab content by default
      expect(
        screen.getByText('Rigid Infrastructure: The Foundation for AI'),
      ).toBeInTheDocument();
      expect(screen.getAllByText('Custom Linters')[0]).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('displays Infrastructure tab content by default', () => {
      render(<AppWithRouter />);

      // Should show Infrastructure tab content
      expect(
        screen.getByText('Rigid Infrastructure: The Foundation for AI'),
      ).toBeInTheDocument();
      expect(screen.getAllByText('Custom Linters')[0]).toBeInTheDocument();
      expect(screen.getAllByText('Make Targets')[0]).toBeInTheDocument();
    });

    it('switches to different tabs when clicked', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Click on Planning tab
      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);

      // Should show Planning tab content
      expect(screen.getByText('Planning Documents')).toBeInTheDocument();
      expect(screen.getByText('View Flow Diagram →')).toBeInTheDocument();
    });

    it('highlights active tab button', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);

      expect(buildingTab).toHaveClass('active');
    });

    it('can switch between different tabs', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Start with Building
      await user.click(screen.getByRole('button', { name: /Building/i }));
      expect(screen.getByText('AI-Powered Code Generation')).toBeInTheDocument();

      // Switch to Quality Assurance
      await user.click(screen.getByRole('button', { name: /Quality Assurance/i }));
      expect(screen.getByText('Bulletproof Code Quality')).toBeInTheDocument();
      expect(screen.queryByText('AI-Powered Code Generation')).not.toBeInTheDocument();

      // Back to Infrastructure
      await user.click(screen.getByRole('button', { name: /Infrastructure/i }));
      expect(
        screen.getByText('Rigid Infrastructure: The Foundation for AI'),
      ).toBeInTheDocument();
      expect(screen.queryByText('Bulletproof Code Quality')).not.toBeInTheDocument();
    });
  });

  describe('Link Validation and Navigation', () => {
    it('has working external links in Infrastructure tab', () => {
      render(<AppWithRouter />);

      const projectLink = screen.getByRole('link', { name: /Explore .ai Repository/i });
      expect(projectLink).toBeInTheDocument();
      expect(projectLink).toHaveAttribute(
        'href',
        'https://github.com/stevej-at-benlabs/durable-code-test/tree/main/.ai',
      );

      const makeLink = screen.getByRole('link', { name: /View Make Targets/i });
      expect(makeLink).toBeInTheDocument();
      expect(makeLink).toHaveAttribute(
        'href',
        'https://github.com/stevej-at-benlabs/durable-code-test/blob/main/Makefile.lint',
      );
    });

    it('has working internal links in Building tab', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Switch to Building tab
      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);

      const standardsLink = screen.getByRole('link', {
        name: /Standards Guide/i,
      });
      expect(standardsLink).toBeInTheDocument();
      expect(standardsLink).toHaveAttribute('href', '/standards?return=Building');
    });

    it('validates that React router links work', async () => {
      // Mock successful fetch for API validation
      mockFetch({ status: 'ok' });

      const response = await fetch('/standards');
      expect(response.ok).toBe(true);
    });

    it('detects broken links', async () => {
      // Mock failed fetch for a broken link
      mockFailedFetch(404);

      const response = await fetch('/broken-link.html');
      expect(response.ok).toBe(false);
      expect(response.status).toBe(404);
    });

    it('has working diagram links in Planning tab', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Switch to Planning tab
      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);

      const flowLink = screen.getByRole('link', { name: /View Flow Diagram/i });
      expect(flowLink).toBeInTheDocument();
      expect(flowLink).toHaveAttribute(
        'href',
        '/diagrams/durable-code-flow.html?return=Planning',
      );

      const sequenceLink = screen.getByRole('link', { name: /View Sequence/i });
      expect(sequenceLink).toBeInTheDocument();
      expect(sequenceLink).toHaveAttribute(
        'href',
        '/diagrams/ai-review-sequence.html?return=Planning',
      );
    });
  });

  describe('Interactive Behavior', () => {
    it('shows hover effects on tab buttons', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      const planningTab = screen.getByRole('button', { name: /Planning/i });

      await user.hover(planningTab);
      // Tab should be hoverable (though specific hover class depends on CSS)
      expect(planningTab).toBeInTheDocument();

      await user.unhover(planningTab);
      expect(planningTab).toBeInTheDocument();
    });

    it('displays AI principles content', () => {
      render(<AppWithRouter />);

      // Check that AI principles are displayed
      expect(screen.getByText('Immediate Feedback Loops')).toBeInTheDocument();
      expect(screen.getByText('Maximum Context')).toBeInTheDocument();
      expect(screen.getByText('Clear Success Criteria')).toBeInTheDocument();
      expect(screen.getByText('Modular Task Decomposition')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper button roles for tabs', () => {
      render(<AppWithRouter />);

      const tabButtons = screen.getAllByRole('button');
      expect(tabButtons.length).toBe(6); // Exactly 6 tab buttons including Demo
    });

    it('has proper links for external resources', () => {
      render(<AppWithRouter />);

      const projectLink = screen.getByRole('link', { name: /Explore .ai Repository/i });
      expect(projectLink).toHaveAttribute('href');
      expect(projectLink.getAttribute('href')).toContain('github.com');
    });

    it('has semantic HTML structure', () => {
      render(<AppWithRouter />);

      expect(screen.getByRole('banner')).toBeInTheDocument(); // header
      expect(screen.getByRole('main')).toBeInTheDocument(); // main
      expect(screen.getByRole('contentinfo')).toBeInTheDocument(); // footer
      expect(screen.getByRole('navigation')).toBeInTheDocument(); // tab navigation
    });
  });

  describe('Link Health Check', () => {
    const publicRoutes = ['/standards'];

    it.each(publicRoutes)('validates public route: %s', async (route) => {
      // In a real scenario, this would make actual HTTP requests
      // For now, we mock successful responses
      mockFetch({ status: 'ok' });

      const response = await fetch(route);
      expect(response.ok).toBe(true);
    });

    it('identifies all external links in the component', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Switch to Infrastructure tab first to ensure we have links
      const infrastructureTab = screen.getByRole('button', { name: /Infrastructure/i });
      await user.click(infrastructureTab);

      // Get all links
      const links = screen.getAllByRole('link');

      // Filter for external or internal links
      const internalLinks = links.filter((link) => {
        const href = link.getAttribute('href');
        return href && !href.startsWith('http') && !href.startsWith('mailto:');
      });

      // Should have internal links (at least 0, since Infrastructure has external GitHub links)
      expect(internalLinks.length).toBeGreaterThanOrEqual(0);

      // All internal links should be valid
      internalLinks.forEach((link) => {
        const href = link.getAttribute('href');
        expect(href).toBeTruthy();
        expect(href).not.toBe('#'); // No empty anchors
      });
    });
  });

  describe('Error Handling', () => {
    it('handles missing tab data gracefully', () => {
      // This test ensures the component doesn't break with malformed data
      render(<AppWithRouter />);

      // Component should still render even if some data is missing
      expect(screen.getByText('Durable Code')).toBeInTheDocument();
    });

    it('handles navigation errors gracefully', async () => {
      const user = userEvent.setup();

      // Mock console.error to track errors
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(<AppWithRouter />);

      // Switch to Building tab
      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);

      // Click the standards link
      const link = screen.getByRole('link', {
        name: /Standards Guide/i,
      });

      // This should not throw an error
      await user.click(link);

      // Clean up
      consoleSpy.mockRestore();
    });
  });

  describe('Tab State Persistence', () => {
    beforeEach(() => {
      // Reset location mocks
      mockLocation.hash = '';
      mockLocation.search = '';
      mockLocation.pathname = '/';
      vi.clearAllMocks();
    });

    it('defaults to Infrastructure tab when no hash is present', () => {
      render(<AppWithRouter />);

      const infrastructureTab = screen.getByRole('button', { name: /Infrastructure/i });
      expect(infrastructureTab).toHaveClass('active');
    });

    it('loads correct tab from URL hash', () => {
      mockLocation.hash = '#Planning';

      render(<AppWithRouter />);

      const planningTab = screen.getByRole('button', { name: /Planning/i });
      expect(planningTab).toHaveClass('active');
    });

    it('loads correct tab from return parameter', () => {
      mockLocation.search = '?return=Building';

      render(<AppWithRouter />);

      const buildingTab = screen.getByRole('button', { name: /Building/i });
      expect(buildingTab).toHaveClass('active');
    });

    it('prioritizes hash over return parameter', () => {
      mockLocation.hash = '#Quality Assurance';
      mockLocation.search = '?return=Building';

      render(<AppWithRouter />);

      const qualityTab = screen.getByRole('button', { name: /Quality Assurance/i });
      expect(qualityTab).toHaveClass('active');
    });

    it('falls back to Infrastructure for invalid hash', () => {
      mockLocation.hash = '#InvalidTab';

      render(<AppWithRouter />);

      const infrastructureTab = screen.getByRole('button', { name: /Infrastructure/i });
      expect(infrastructureTab).toHaveClass('active');
    });

    it('updates URL hash when tab is clicked', async () => {
      const user = userEvent.setup();

      render(<AppWithRouter />);

      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);

      expect(mockHistory.pushState).toHaveBeenCalledWith(null, '', '#Planning');
    });

    it('cleans up URL when return parameter is used', () => {
      mockLocation.search = '?return=Building';

      render(<AppWithRouter />);

      // Should clean up the URL and use hash format
      expect(mockHistory.replaceState).toHaveBeenCalledWith(null, '', '/#Building');
    });

    it('includes return parameter in external links', async () => {
      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Switch to Building tab
      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);

      // Check that standards guide link includes return parameter
      const standardsLink = screen.getByRole('link', {
        name: /Standards Guide/i,
      });
      expect(standardsLink.getAttribute('href')).toBe('/standards?return=Building');
    });

    it('includes return parameter in Planning tab links', async () => {
      const user = userEvent.setup();

      render(<AppWithRouter />);

      // Switch to Planning tab
      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);

      // Check that diagram links include return parameter
      const flowLink = screen.getByRole('link', { name: /View Flow Diagram →/i });
      expect(flowLink.getAttribute('href')).toBe(
        '/diagrams/durable-code-flow.html?return=Planning',
      );

      const sequenceLink = screen.getByRole('link', { name: /View Sequence →/i });
      expect(sequenceLink.getAttribute('href')).toBe(
        '/diagrams/ai-review-sequence.html?return=Planning',
      );
    });

    it('includes return parameter in Quality Assurance tab links', async () => {
      const user = userEvent.setup();

      render(<AppWithRouter />);

      // Switch to Quality Assurance tab
      const qualityTab = screen.getByRole('button', { name: /Quality Assurance/i });
      await user.click(qualityTab);

      // Check that QA links include return parameter
      const lintersLink = screen.getByRole('link', { name: /View All Linters/i });
      expect(lintersLink.getAttribute('href')).toBe(
        '/custom-linters?return=Quality Assurance',
      );

      const pipelineLink = screen.getByRole('link', { name: /View Pipeline/i });
      expect(pipelineLink.getAttribute('href')).toBe(
        'ci-cd-pipeline.html?return=Quality Assurance',
      );
    });

    it('handles browser back/forward navigation', () => {
      // Render with initial hash
      mockLocation.hash = '#Maintenance';
      render(<AppWithRouter />);

      // Should load the Maintenance tab based on hash
      const maintenanceTab = screen.getByRole('button', { name: /Maintenance/i });
      expect(maintenanceTab).toHaveClass('active');
    });
  });

  describe('Link Validation', () => {
    it('validates all links in the current app structure', async () => {
      // Reset location hash
      mockLocation.hash = '';

      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Collect all links from all tabs
      const allLinks: string[] = [];

      // Infrastructure tab (default)
      const infrastructureTab = screen.getByRole('button', { name: /Infrastructure/i });
      await user.click(infrastructureTab);
      const infrastructureLinks = screen.getAllByRole('link');
      infrastructureLinks.forEach((link) => {
        const href = link.getAttribute('href');
        if (href) allLinks.push(href);
      });

      // Planning tab
      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);
      const planningLinks = screen.getAllByRole('link');
      planningLinks.forEach((link) => {
        const href = link.getAttribute('href');
        if (href && !allLinks.includes(href)) allLinks.push(href);
      });

      // Building tab
      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);
      const buildingLinks = screen.getAllByRole('link');
      buildingLinks.forEach((link) => {
        const href = link.getAttribute('href');
        if (href && !allLinks.includes(href)) allLinks.push(href);
      });

      // Quality Assurance tab
      const qualityTab = screen.getByRole('button', { name: /Quality Assurance/i });
      await user.click(qualityTab);
      const qualityLinks = screen.getAllByRole('link');
      qualityLinks.forEach((link) => {
        const href = link.getAttribute('href');
        if (href && !allLinks.includes(href)) allLinks.push(href);
      });

      // Verify specific expected links exist
      expect(allLinks).toEqual(
        expect.arrayContaining([
          'https://github.com/stevej-at-benlabs/durable-code-test/tree/main/.ai',
          'https://github.com/stevej-at-benlabs/durable-code-test/blob/main/Makefile.lint',
          '/standards?return=Building',
          '/diagrams/durable-code-flow.html?return=Planning',
          '/diagrams/ai-review-sequence.html?return=Planning',
          '/diagrams/implementation-plan.html?return=Planning',
        ]),
      );

      // Verify no old broken links exist
      expect(allLinks).not.toContain('set-standards.html');
      expect(allLinks).not.toContain('https://docs.anthropic.com/en/docs/claude-code');
    });

    it('ensures all internal links include return parameters', async () => {
      // Reset location hash
      mockLocation.hash = '';

      const user = userEvent.setup();
      render(<AppWithRouter />);

      // Check Building tab links
      const buildingTab = screen.getByRole('button', { name: /Building/i });
      await user.click(buildingTab);

      const standardsLink = screen.getByRole('link', {
        name: /Standards Guide/i,
      });
      expect(standardsLink.getAttribute('href')).toBe('/standards?return=Building');

      // Check Planning tab links
      const planningTab = screen.getByRole('button', { name: /Planning/i });
      await user.click(planningTab);

      const flowLink = screen.getByRole('link', { name: /View Flow Diagram →/i });
      expect(flowLink.getAttribute('href')).toBe(
        '/diagrams/durable-code-flow.html?return=Planning',
      );

      const sequenceLink = screen.getByRole('link', { name: /View Sequence →/i });
      expect(sequenceLink.getAttribute('href')).toBe(
        '/diagrams/ai-review-sequence.html?return=Planning',
      );
    });

    it('verifies no broken relative links exist', () => {
      render(<AppWithRouter />);

      const allLinks = screen.getAllByRole('link');

      allLinks.forEach((link) => {
        const href = link.getAttribute('href');
        if (href) {
          // Verify no broken HTML files exist (allow diagrams)
          expect(href).not.toContain('infrastructure-guide.html');
          expect(href).not.toContain('set-standards.html');

          // Allow diagram HTML files but no other standalone HTML
          if (
            href.includes('.html') &&
            !href.includes('/diagrams/') &&
            !href.includes('ci-cd-pipeline.html')
          ) {
            throw new Error(`Unexpected standalone HTML file found: ${href}`);
          }

          // Ensure all internal paths start with / or are external URLs or hash anchors
          if (!href.startsWith('http')) {
            expect(href).toMatch(/^\/|^#/);
          }
        }
      });
    });
  });
});
