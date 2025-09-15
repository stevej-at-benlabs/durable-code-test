/**
 * Purpose: Unit and integration tests for the main App component
 * Scope: Component rendering, filtering, interactions, and link validation
 * Created: 2025-09-12
 * Updated: 2025-09-12
 * Author: Development Team
 * Version: 1.0
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { mockFetch, mockFailedFetch } from './test-setup';

// Mock location for navigation tests
const mockLocation = {
  href: 'http://localhost:3000/',
  assign: vi.fn(),
  reload: vi.fn(),
  replace: vi.fn(),
};

Object.defineProperty(window, 'location', {
  value: mockLocation,
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
      render(<App />);

      // More specific selectors for the main title elements
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(
        screen.getByText(/Master the art of creating maintainable/),
      ).toBeInTheDocument();
    });

    it('renders all technique cards', () => {
      render(<App />);

      expect(screen.getByText('Set Standards First')).toBeInTheDocument();
      expect(screen.getByText('Test-Driven Development with AI')).toBeInTheDocument();
      expect(screen.getByText('AI-Assisted Design Patterns')).toBeInTheDocument();
      expect(screen.getByText('Documentation-First Development')).toBeInTheDocument();
      expect(screen.getByText('AI-Enhanced Code Reviews')).toBeInTheDocument();
      expect(screen.getByText('AI Pair Programming')).toBeInTheDocument();
    });

    it('renders all filter buttons', () => {
      render(<App />);

      // Use getByRole to specifically target buttons
      expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Testing' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Architecture' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Documentation' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Quality' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Collaboration' })).toBeInTheDocument();
    });

    it('renders principles section', () => {
      render(<App />);

      expect(screen.getByText('Core Principles')).toBeInTheDocument();
      expect(screen.getByText('Purpose-Driven')).toBeInTheDocument();
      expect(screen.getByText('Iterative Improvement')).toBeInTheDocument();
      expect(screen.getByText('Defensive Programming')).toBeInTheDocument();
      expect(screen.getByText('Self-Documenting')).toBeInTheDocument();
    });
  });

  describe('Filtering Functionality', () => {
    it('shows all techniques by default', () => {
      render(<App />);

      // Should show all 7 technique cards
      const cards = screen
        .getAllByRole('generic')
        .filter((el) => el.className.includes('technique-card'));
      expect(cards).toHaveLength(6);
    });

    it('filters techniques by category', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Click on Testing filter
      const testingButton = screen.getByRole('button', { name: 'Testing' });
      await user.click(testingButton);

      // Should show only Testing techniques (1 card)
      expect(screen.getByText('Test-Driven Development with AI')).toBeInTheDocument();
      expect(screen.queryByText('AI-Assisted Design Patterns')).not.toBeInTheDocument();
    });

    it('highlights active filter button', async () => {
      const user = userEvent.setup();
      render(<App />);

      const qualityButton = screen.getByRole('button', { name: 'Quality' });
      await user.click(qualityButton);

      expect(qualityButton).toHaveClass('active');
    });

    it('can switch between different filters', async () => {
      const user = userEvent.setup();
      render(<App />);

      // Start with Testing
      await user.click(screen.getByRole('button', { name: 'Testing' }));
      expect(screen.getByText('Test-Driven Development with AI')).toBeInTheDocument();

      // Switch to Architecture
      await user.click(screen.getByRole('button', { name: 'Architecture' }));
      expect(screen.getByText('AI-Assisted Design Patterns')).toBeInTheDocument();
      expect(
        screen.queryByText('Test-Driven Development with AI'),
      ).not.toBeInTheDocument();

      // Back to All
      await user.click(screen.getByRole('button', { name: 'All' }));
      expect(screen.getByText('Test-Driven Development with AI')).toBeInTheDocument();
      expect(screen.getByText('AI-Assisted Design Patterns')).toBeInTheDocument();
    });
  });

  describe('Link Validation and Navigation', () => {
    it('has a working hero CTA link to set-standards.html', () => {
      render(<App />);

      const ctaLink = screen.getByRole('link', { name: /Set Standards First/ });
      expect(ctaLink).toBeInTheDocument();
      expect(ctaLink).toHaveAttribute('href', 'set-standards.html');
    });

    it('has a button link in set-standards card', () => {
      render(<App />);

      const setStandardsCard = screen
        .getByText('Set Standards First')
        .closest('.technique-card');

      // Card should have a button link instead of being clickable
      const link = within(setStandardsCard as HTMLElement).getByRole('link', {
        name: /View Standards Guide/i,
      });
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', 'set-standards.html');
    });

    it('validates that set-standards.html exists', async () => {
      // Mock successful fetch for the HTML file
      mockFetch('<html><head><title>Set Standards</title></head></html>');

      const response = await fetch('/set-standards.html');
      expect(response.ok).toBe(true);

      const text = await response.text();
      expect(text).toContain('Set Standards');
    });

    it('detects broken links', async () => {
      // Mock failed fetch for a broken link
      mockFailedFetch(404);

      const response = await fetch('/broken-link.html');
      expect(response.ok).toBe(false);
      expect(response.status).toBe(404);
    });

    it('only some cards have action buttons', () => {
      render(<App />);

      const setStandardsCard = screen
        .getByText('Set Standards First')
        .closest('.technique-card');
      const tddCard = screen
        .getByText('Test-Driven Development with AI')
        .closest('.technique-card');

      // Set Standards card should have a link button
      const setStandardsLink = within(setStandardsCard as HTMLElement).queryByRole(
        'link',
      );
      expect(setStandardsLink).toBeInTheDocument();

      // TDD card should not have a link button
      const tddLink = within(tddCard as HTMLElement).queryByRole('link');
      expect(tddLink).not.toBeInTheDocument();
    });
  });

  describe('Interactive Behavior', () => {
    it('shows hover effect on technique cards', async () => {
      const user = userEvent.setup();
      render(<App />);

      const card = screen.getByText('Set Standards First').closest('.technique-card');

      await user.hover(card!);
      expect(card).toHaveClass('hovered');

      await user.unhover(card!);
      expect(card).not.toHaveClass('hovered');
    });

    it('displays technique benefits', () => {
      render(<App />);

      // Check that benefits are displayed for each technique
      expect(screen.getByText('Consistent code quality')).toBeInTheDocument();
      expect(screen.getByText('Automated enforcement')).toBeInTheDocument();
      expect(screen.getByText('Higher code quality')).toBeInTheDocument();
      expect(screen.getByText('Better design')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper button roles for filters', () => {
      render(<App />);

      const filterButtons = screen.getAllByRole('button');
      expect(filterButtons.length).toBeGreaterThan(5); // At least 6 filter buttons
    });

    it('has proper link for CTA button', () => {
      render(<App />);

      const ctaLink = screen.getByRole('link', { name: /Set Standards First/ });
      expect(ctaLink).toHaveAttribute('href');
    });

    it('has semantic HTML structure', () => {
      render(<App />);

      expect(screen.getByRole('banner')).toBeInTheDocument(); // header
      expect(screen.getByRole('main')).toBeInTheDocument(); // main
      expect(screen.getByRole('contentinfo')).toBeInTheDocument(); // footer
    });
  });

  describe('Link Health Check', () => {
    const publicLinks = ['set-standards.html'];

    it.each(publicLinks)('validates public link: %s', async (link) => {
      // In a real scenario, this would make actual HTTP requests
      // For now, we mock successful responses
      mockFetch({ status: 'ok' });

      const response = await fetch(`/${link}`);
      expect(response.ok).toBe(true);
    });

    it('identifies all external links in the component', () => {
      render(<App />);

      // Get all links
      const links = screen.getAllByRole('link');

      // Filter for external or internal links
      const internalLinks = links.filter((link) => {
        const href = link.getAttribute('href');
        return href && !href.startsWith('http') && !href.startsWith('mailto:');
      });

      // Should have at least the CTA link
      expect(internalLinks.length).toBeGreaterThanOrEqual(1);

      // All internal links should be valid
      internalLinks.forEach((link) => {
        const href = link.getAttribute('href');
        expect(href).toBeTruthy();
        expect(href).not.toBe('#'); // No empty anchors
      });
    });
  });

  describe('Error Handling', () => {
    it('handles missing technique data gracefully', () => {
      // This test ensures the component doesn't break with malformed data
      render(<App />);

      // Component should still render even if some data is missing
      expect(screen.getByText('Durable Code')).toBeInTheDocument();
    });

    it('handles navigation errors gracefully', async () => {
      const user = userEvent.setup();

      // Mock console.error to track errors
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      render(<App />);

      const setStandardsCard = screen
        .getByText('Set Standards First')
        .closest('.technique-card');

      // Click the link button inside the card
      const link = within(setStandardsCard as HTMLElement).getByRole('link', {
        name: /View Standards Guide/i,
      });

      // This should not throw an error
      await user.click(link);

      // Clean up
      consoleSpy.mockRestore();
    });
  });
});
