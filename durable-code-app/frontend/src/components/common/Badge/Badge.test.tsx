import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders children correctly', () => {
    render(<Badge>Badge Text</Badge>);
    expect(screen.getByText('Badge Text')).toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<Badge variant="success">Success</Badge>);
    expect(screen.getByText('Success').className).toMatch(/success/);

    rerender(<Badge variant="warning">Warning</Badge>);
    expect(screen.getByText('Warning').className).toMatch(/warning/);

    rerender(<Badge variant="error">Error</Badge>);
    expect(screen.getByText('Error').className).toMatch(/error/);

    rerender(<Badge variant="info">Info</Badge>);
    expect(screen.getByText('Info').className).toMatch(/info/);

    rerender(<Badge variant="neutral">Neutral</Badge>);
    expect(screen.getByText('Neutral').className).toMatch(/neutral/);
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<Badge size="small">Small</Badge>);
    expect(screen.getByText('Small').className).toMatch(/small/);

    rerender(<Badge size="medium">Medium</Badge>);
    expect(screen.getByText('Medium').className).toMatch(/medium/);

    rerender(<Badge size="large">Large</Badge>);
    expect(screen.getByText('Large').className).toMatch(/large/);
  });

  it('defaults to neutral variant when no variant provided', () => {
    render(<Badge>Default Badge</Badge>);
    expect(screen.getByText('Default Badge').className).toMatch(/neutral/);
  });

  it('defaults to medium size when no size provided', () => {
    render(<Badge>Default Badge</Badge>);
    expect(screen.getByText('Default Badge').className).toMatch(/medium/);
  });

  it('forwards additional props', () => {
    render(
      <Badge data-testid="custom-badge" id="test-badge">
        Badge
      </Badge>,
    );
    const badge = screen.getByText('Badge');

    expect(badge).toHaveAttribute('data-testid', 'custom-badge');
    expect(badge).toHaveAttribute('id', 'test-badge');
  });

  it('combines custom className with default classes', () => {
    render(<Badge className="custom-class">Badge</Badge>);
    const badge = screen.getByText('Badge');

    expect(badge.className).toMatch(/badge/);
    expect(badge.className).toMatch(/neutral/);
    expect(badge.className).toMatch(/medium/);
    expect(badge.className).toMatch(/custom-class/);
  });

  it('uses correct semantic HTML element', () => {
    render(<Badge>Semantic Badge</Badge>);
    const badge = screen.getByText('Semantic Badge');
    expect(badge.tagName).toBe('SPAN');
  });

  it('renders with different content types', () => {
    const { rerender } = render(<Badge>Text Badge</Badge>);
    expect(screen.getByText('Text Badge')).toBeInTheDocument();

    rerender(<Badge>123</Badge>);
    expect(screen.getByText('123')).toBeInTheDocument();

    rerender(
      <Badge>
        <span>HTML Content</span>
      </Badge>,
    );
    expect(screen.getByText('HTML Content')).toBeInTheDocument();
  });

  it('combines variant and size correctly', () => {
    render(
      <Badge variant="success" size="large">
        Success Large
      </Badge>,
    );
    const badge = screen.getByText('Success Large');

    expect(badge.className).toMatch(/badge/);
    expect(badge.className).toMatch(/success/);
    expect(badge.className).toMatch(/large/);
  });
});
