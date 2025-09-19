import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('renders children correctly', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders with icon', () => {
    render(<Card icon="🎉">Content</Card>);
    expect(screen.getByText('🎉')).toBeInTheDocument();
  });

  it('renders with title', () => {
    render(<Card title="Card Title">Content</Card>);
    expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('Card Title');
  });

  it('renders with badge', () => {
    render(<Card badge="New">Content</Card>);
    expect(screen.getByText('New')).toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { container, rerender } = render(<Card variant="default">Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/default/);

    rerender(<Card variant="feature">Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/feature/);

    rerender(<Card variant="stat">Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/stat/);

    rerender(<Card variant="principle">Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/principle/);
  });

  it('applies clickable class when clickable is true', () => {
    const { container } = render(<Card clickable>Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/clickable/);
  });

  it('combines custom className with default classes', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect((container.firstChild as HTMLElement).className).toMatch(/card/);
    expect((container.firstChild as HTMLElement).className).toMatch(/custom-class/);
  });

  it('forwards additional props', () => {
    const { container } = render(
      <Card data-testid="test-card" role="article">
        Content
      </Card>,
    );
    expect(container.firstChild).toHaveAttribute('data-testid', 'test-card');
    expect(container.firstChild).toHaveAttribute('role', 'article');
  });

  it('renders all elements together', () => {
    render(
      <Card icon="🚀" title="Full Card" badge="Premium" clickable>
        This is the card content
      </Card>,
    );

    expect(screen.getByText('🚀')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('Full Card');
    expect(screen.getByText('This is the card content')).toBeInTheDocument();
    expect(screen.getByText('Premium')).toBeInTheDocument();
  });
});
