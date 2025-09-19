import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Link } from './Link';

describe('Link', () => {
  it('renders children correctly', () => {
    render(<Link href="/test">Link Text</Link>);
    expect(screen.getByRole('link')).toHaveTextContent('Link Text');
  });

  it('applies href correctly', () => {
    render(<Link href="/test-path">Test Link</Link>);
    expect(screen.getByRole('link')).toHaveAttribute('href', '/test-path');
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(
      <Link href="/test" onClick={handleClick}>
        Clickable Link
      </Link>,
    );
    await user.click(screen.getByRole('link'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(
      <Link href="/test" variant="default">
        Link
      </Link>,
    );
    expect(screen.getByRole('link').className).toMatch(/default/);

    rerender(
      <Link href="/test" variant="primary">
        Link
      </Link>,
    );
    expect(screen.getByRole('link').className).toMatch(/primary/);

    rerender(
      <Link href="/test" variant="muted">
        Link
      </Link>,
    );
    expect(screen.getByRole('link').className).toMatch(/muted/);

    rerender(
      <Link href="/test" variant="danger">
        Link
      </Link>,
    );
    expect(screen.getByRole('link').className).toMatch(/danger/);
  });

  it('handles external links with http protocol', () => {
    render(<Link href="http://example.com">External Link</Link>);
    const link = screen.getByRole('link');

    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('handles external links with https protocol', () => {
    render(<Link href="https://example.com">External Link</Link>);
    const link = screen.getByRole('link');

    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('handles external links with external prop', () => {
    render(
      <Link href="/relative-path" external>
        External Link
      </Link>,
    );
    const link = screen.getByRole('link');

    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  it('does not set target for internal links', () => {
    render(<Link href="/internal-path">Internal Link</Link>);
    const link = screen.getByRole('link');

    expect(link).not.toHaveAttribute('target');
    expect(link).not.toHaveAttribute('rel');
  });

  it('allows custom target and rel to override defaults', () => {
    render(
      <Link href="https://example.com" target="_self" rel="custom-rel">
        Custom Link
      </Link>,
    );
    const link = screen.getByRole('link');

    expect(link).toHaveAttribute('target', '_self');
    expect(link).toHaveAttribute('rel', 'custom-rel');
  });

  it('forwards additional props', () => {
    render(
      <Link href="/test" data-testid="custom-link" id="test-link">
        Link
      </Link>,
    );
    const link = screen.getByRole('link');

    expect(link).toHaveAttribute('data-testid', 'custom-link');
    expect(link).toHaveAttribute('id', 'test-link');
  });

  it('combines custom className with default classes', () => {
    render(
      <Link href="/test" className="custom-class">
        Link
      </Link>,
    );
    const link = screen.getByRole('link');

    expect(link.className).toMatch(/link/);
    expect(link.className).toMatch(/default/);
    expect(link.className).toMatch(/custom-class/);
  });

  it('uses correct semantic HTML element', () => {
    render(<Link href="/test">Semantic Link</Link>);
    const link = screen.getByRole('link');
    expect(link.tagName).toBe('A');
  });
});
