import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default properties', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');

    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Loading...');
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<LoadingSpinner size="small" />);
    expect(screen.getByRole('status').className).toMatch(/small/);

    rerender(<LoadingSpinner size="medium" />);
    expect(screen.getByRole('status').className).toMatch(/medium/);

    rerender(<LoadingSpinner size="large" />);
    expect(screen.getByRole('status').className).toMatch(/large/);
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<LoadingSpinner variant="primary" />);
    expect(screen.getByRole('status').className).toMatch(/primary/);

    rerender(<LoadingSpinner variant="secondary" />);
    expect(screen.getByRole('status').className).toMatch(/secondary/);

    rerender(<LoadingSpinner variant="light" />);
    expect(screen.getByRole('status').className).toMatch(/light/);
  });

  it('defaults to medium size when no size provided', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status').className).toMatch(/medium/);
  });

  it('defaults to primary variant when no variant provided', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status').className).toMatch(/primary/);
  });

  it('uses custom label when provided', () => {
    render(<LoadingSpinner label="Custom loading message" />);
    const spinner = screen.getByRole('status');

    expect(spinner).toHaveAttribute('aria-label', 'Custom loading message');
    expect(screen.getByText('Custom loading message')).toBeInTheDocument();
  });

  it('forwards additional props', () => {
    render(<LoadingSpinner data-testid="custom-spinner" id="test-spinner" />);
    const spinner = screen.getByRole('status');

    expect(spinner).toHaveAttribute('data-testid', 'custom-spinner');
    expect(spinner).toHaveAttribute('id', 'test-spinner');
  });

  it('combines custom className with default classes', () => {
    render(<LoadingSpinner className="custom-class" />);
    const spinner = screen.getByRole('status');

    expect(spinner.className).toMatch(/spinner/);
    expect(spinner.className).toMatch(/medium/);
    expect(spinner.className).toMatch(/primary/);
    expect(spinner.className).toMatch(/custom-class/);
  });

  it('has correct accessibility attributes', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');

    expect(spinner).toHaveAttribute('role', 'status');
    expect(spinner).toHaveAttribute('aria-label');
  });

  it('contains spinner circle element', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');
    const circle = spinner.querySelector('[class*="circle"]');

    expect(circle).toBeInTheDocument();
  });

  it('contains visually hidden text for screen readers', () => {
    render(<LoadingSpinner label="Loading data" />);

    // Text should be present but visually hidden
    expect(screen.getByText('Loading data').className).toMatch(/visuallyHidden/);
  });

  it('combines size and variant correctly', () => {
    render(<LoadingSpinner size="large" variant="secondary" />);
    const spinner = screen.getByRole('status');

    expect(spinner.className).toMatch(/spinner/);
    expect(spinner.className).toMatch(/large/);
    expect(spinner.className).toMatch(/secondary/);
  });
});
