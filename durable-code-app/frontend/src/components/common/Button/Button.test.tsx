import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from './Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<Button onClick={handleClick}>Click</Button>);
    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<Button variant="primary">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/primary/);

    rerender(<Button variant="secondary">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/secondary/);

    rerender(<Button variant="danger">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/danger/);

    rerender(<Button variant="ghost">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/ghost/);

    rerender(<Button variant="link">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/link/);
  });

  it('applies size classes correctly', () => {
    const { rerender } = render(<Button size="small">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/small/);

    rerender(<Button size="medium">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/medium/);

    rerender(<Button size="large">Button</Button>);
    expect(screen.getByRole('button').className).toMatch(/large/);
  });

  it('handles disabled state', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(
      <Button disabled onClick={handleClick}>
        Button
      </Button>,
    );
    const button = screen.getByRole('button');

    expect(button).toBeDisabled();
    await user.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('handles loading state', () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toMatch(/loading/);
    expect(button).toBeDisabled();
    expect(button.querySelector('[class*="spinner"]')).toBeInTheDocument();
  });

  it('applies full width class when fullWidth is true', () => {
    render(<Button fullWidth>Full Width</Button>);
    expect(screen.getByRole('button').className).toMatch(/fullWidth/);
  });

  it('forwards additional props', () => {
    render(
      <Button data-testid="custom-button" type="submit">
        Submit
      </Button>,
    );
    const button = screen.getByRole('button');

    expect(button).toHaveAttribute('data-testid', 'custom-button');
    expect(button).toHaveAttribute('type', 'submit');
  });

  it('combines custom className with default classes', () => {
    render(<Button className="custom-class">Button</Button>);
    const button = screen.getByRole('button');

    expect(button.className).toMatch(/button/);
    expect(button.className).toMatch(/primary/);
    expect(button.className).toMatch(/medium/);
    expect(button.className).toMatch(/custom-class/);
  });
});
