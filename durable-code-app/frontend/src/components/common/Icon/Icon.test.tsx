import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Icon } from './Icon';

describe('Icon', () => {
  it('renders emoji correctly', () => {
    render(<Icon emoji="🚀" label="Rocket" />);
    expect(screen.getByRole('img')).toHaveTextContent('🚀');
  });

  it('has correct accessibility attributes', () => {
    render(<Icon emoji="❤️" label="Heart" />);
    const icon = screen.getByRole('img');

    expect(icon).toHaveAttribute('role', 'img');
    expect(icon).toHaveAttribute('aria-label', 'Heart');
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<Icon emoji="⭐" label="Star" size="small" />);
    expect(screen.getByRole('img').className).toMatch(/small/);

    rerender(<Icon emoji="⭐" label="Star" size="medium" />);
    expect(screen.getByRole('img').className).toMatch(/medium/);

    rerender(<Icon emoji="⭐" label="Star" size="large" />);
    expect(screen.getByRole('img').className).toMatch(/large/);

    rerender(<Icon emoji="⭐" label="Star" size="xl" />);
    expect(screen.getByRole('img').className).toMatch(/xl/);
  });

  it('defaults to medium size when no size provided', () => {
    render(<Icon emoji="🎉" label="Celebration" />);
    expect(screen.getByRole('img').className).toMatch(/medium/);
  });

  it('forwards additional props', () => {
    render(<Icon emoji="🔥" label="Fire" data-testid="custom-icon" id="test-icon" />);
    const icon = screen.getByRole('img');

    expect(icon).toHaveAttribute('data-testid', 'custom-icon');
    expect(icon).toHaveAttribute('id', 'test-icon');
  });

  it('combines custom className with default classes', () => {
    render(<Icon emoji="💎" label="Diamond" className="custom-class" />);
    const icon = screen.getByRole('img');

    expect(icon.className).toMatch(/icon/);
    expect(icon.className).toMatch(/medium/);
    expect(icon.className).toMatch(/custom-class/);
  });

  it('handles complex emojis correctly', () => {
    render(<Icon emoji="👨‍💻" label="Man technologist" />);
    expect(screen.getByRole('img')).toHaveTextContent('👨‍💻');
    expect(screen.getByRole('img')).toHaveAttribute('aria-label', 'Man technologist');
  });

  it('uses correct semantic HTML element', () => {
    render(<Icon emoji="🌟" label="Star" />);
    const icon = screen.getByRole('img');
    expect(icon.tagName).toBe('SPAN');
  });
});
