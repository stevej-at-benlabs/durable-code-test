import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Tab } from './Tab';

describe('Tab', () => {
  it('renders children correctly', () => {
    render(<Tab>Tab Label</Tab>);
    expect(screen.getByRole('tab')).toHaveTextContent('Tab Label');
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(<Tab onClick={handleClick}>Click me</Tab>);
    await user.click(screen.getByRole('tab'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies active state correctly', () => {
    const { rerender } = render(<Tab isActive={false}>Tab</Tab>);
    expect(screen.getByRole('tab').className).not.toMatch(/active/);
    expect(screen.getByRole('tab')).toHaveAttribute('aria-selected', 'false');

    rerender(<Tab isActive={true}>Tab</Tab>);
    expect(screen.getByRole('tab').className).toMatch(/active/);
    expect(screen.getByRole('tab')).toHaveAttribute('aria-selected', 'true');
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<Tab variant="default">Tab</Tab>);
    expect(screen.getByRole('tab').className).toMatch(/default/);

    rerender(<Tab variant="underline">Tab</Tab>);
    expect(screen.getByRole('tab').className).toMatch(/underline/);

    rerender(<Tab variant="pill">Tab</Tab>);
    expect(screen.getByRole('tab').className).toMatch(/pill/);
  });

  it('handles disabled state', async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();

    render(
      <Tab disabled onClick={handleClick}>
        Tab
      </Tab>,
    );
    const tab = screen.getByRole('tab');

    expect(tab).toBeDisabled();
    await user.click(tab);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it('forwards additional props', () => {
    render(
      <Tab data-testid="custom-tab" id="test-tab">
        Tab
      </Tab>,
    );
    const tab = screen.getByRole('tab');

    expect(tab).toHaveAttribute('data-testid', 'custom-tab');
    expect(tab).toHaveAttribute('id', 'test-tab');
  });

  it('combines custom className with default classes', () => {
    render(<Tab className="custom-class">Tab</Tab>);
    const tab = screen.getByRole('tab');

    expect(tab.className).toMatch(/tab/);
    expect(tab.className).toMatch(/default/);
    expect(tab.className).toMatch(/custom-class/);
  });

  it('has correct accessibility attributes', () => {
    render(<Tab>Accessible Tab</Tab>);
    const tab = screen.getByRole('tab');

    expect(tab).toHaveAttribute('role', 'tab');
    expect(tab).toHaveAttribute('type', 'button');
  });
});
