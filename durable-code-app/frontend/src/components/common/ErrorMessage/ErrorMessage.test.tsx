import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorMessage } from './ErrorMessage';

describe('ErrorMessage', () => {
  it('renders message correctly', () => {
    render(<ErrorMessage message="Test error message" />);
    expect(screen.getByText('Test error message')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(<ErrorMessage message="Error occurred" title="Error Title" />);
    expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('Error Title');
  });

  it('does not render title when not provided', () => {
    render(<ErrorMessage message="Error occurred" />);
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { rerender } = render(<ErrorMessage message="Test" variant="error" />);
    expect(screen.getByRole('alert').className).toMatch(/error/);

    rerender(<ErrorMessage message="Test" variant="warning" />);
    expect(screen.getByRole('alert').className).toMatch(/warning/);

    rerender(<ErrorMessage message="Test" variant="info" />);
    expect(screen.getByRole('alert').className).toMatch(/info/);
  });

  it('defaults to error variant when no variant provided', () => {
    render(<ErrorMessage message="Test message" />);
    expect(screen.getByRole('alert').className).toMatch(/error/);
  });

  it('displays correct icons for variants', () => {
    const { rerender } = render(<ErrorMessage message="Test" variant="error" />);
    expect(screen.getByText('❌')).toBeInTheDocument();

    rerender(<ErrorMessage message="Test" variant="warning" />);
    expect(screen.getByText('⚠️')).toBeInTheDocument();

    rerender(<ErrorMessage message="Test" variant="info" />);
    expect(screen.getByText('ℹ️')).toBeInTheDocument();
  });

  it('renders children when provided', () => {
    render(
      <ErrorMessage message="Error occurred">
        <p>Additional error details</p>
      </ErrorMessage>,
    );
    expect(screen.getByText('Additional error details')).toBeInTheDocument();
  });

  it('renders dismiss button when onDismiss provided', () => {
    const handleDismiss = vi.fn();
    render(<ErrorMessage message="Error" onDismiss={handleDismiss} />);

    const dismissButton = screen.getByLabelText('Dismiss message');
    expect(dismissButton).toBeInTheDocument();
    expect(dismissButton).toHaveTextContent('✕');
  });

  it('calls onDismiss when dismiss button clicked', async () => {
    const handleDismiss = vi.fn();
    const user = userEvent.setup();

    render(<ErrorMessage message="Error" onDismiss={handleDismiss} />);

    await user.click(screen.getByLabelText('Dismiss message'));
    expect(handleDismiss).toHaveBeenCalledTimes(1);
  });

  it('does not render dismiss button when onDismiss not provided', () => {
    render(<ErrorMessage message="Error" />);
    expect(screen.queryByLabelText('Dismiss message')).not.toBeInTheDocument();
  });

  it('forwards additional props', () => {
    render(<ErrorMessage message="Error" data-testid="custom-error" id="test-error" />);
    const errorMessage = screen.getByRole('alert');

    expect(errorMessage).toHaveAttribute('data-testid', 'custom-error');
    expect(errorMessage).toHaveAttribute('id', 'test-error');
  });

  it('combines custom className with default classes', () => {
    render(<ErrorMessage message="Error" className="custom-class" />);
    const errorMessage = screen.getByRole('alert');

    expect(errorMessage.className).toMatch(/errorMessage/);
    expect(errorMessage.className).toMatch(/error/);
    expect(errorMessage.className).toMatch(/custom-class/);
  });

  it('has correct accessibility attributes', () => {
    render(<ErrorMessage message="Accessible error" />);
    const errorMessage = screen.getByRole('alert');

    expect(errorMessage).toHaveAttribute('role', 'alert');
    expect(errorMessage).toHaveAttribute('aria-live', 'polite');
  });

  it('icon has correct accessibility attributes', () => {
    render(<ErrorMessage message="Error with icon" />);
    const icon = screen.getByText('❌');

    expect(icon).toHaveAttribute('role', 'img');
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });

  it('renders complex structure correctly', () => {
    const handleDismiss = vi.fn();
    render(
      <ErrorMessage
        message="Complex error message"
        title="Error Title"
        variant="warning"
        onDismiss={handleDismiss}
      >
        <button>Retry Action</button>
      </ErrorMessage>,
    );

    expect(screen.getByRole('heading', { level: 4 })).toHaveTextContent('Error Title');
    expect(screen.getByText('Complex error message')).toBeInTheDocument();
    expect(screen.getByText('⚠️')).toBeInTheDocument();
    expect(screen.getByLabelText('Dismiss message')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry Action' })).toBeInTheDocument();
  });
});
