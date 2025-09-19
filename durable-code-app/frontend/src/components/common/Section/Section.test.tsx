import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Section } from './Section';

describe('Section', () => {
  it('renders children correctly', () => {
    render(<Section>Section content</Section>);
    expect(screen.getByText('Section content')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(<Section title="Section Title">Content</Section>);
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(
      'Section Title',
    );
  });

  it('does not render title when not provided', () => {
    render(<Section>Content</Section>);
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('applies variant classes correctly', () => {
    const { container, rerender } = render(
      <Section variant="default">Content</Section>,
    );
    expect((container.firstChild as HTMLElement).className).toMatch(/default/);

    rerender(<Section variant="highlighted">Content</Section>);
    expect((container.firstChild as HTMLElement).className).toMatch(/highlighted/);

    rerender(<Section variant="bordered">Content</Section>);
    expect((container.firstChild as HTMLElement).className).toMatch(/bordered/);
  });

  it('forwards additional props', () => {
    const { container } = render(
      <Section data-testid="custom-section" id="test-section">
        Content
      </Section>,
    );
    const section = container.firstChild as HTMLElement;

    expect(section).toHaveAttribute('data-testid', 'custom-section');
    expect(section).toHaveAttribute('id', 'test-section');
  });

  it('combines custom className with default classes', () => {
    const { container } = render(<Section className="custom-class">Content</Section>);
    const section = container.firstChild as HTMLElement;

    expect(section.className).toMatch(/section/);
    expect(section.className).toMatch(/default/);
    expect(section.className).toMatch(/custom-class/);
  });

  it('uses correct semantic HTML element', () => {
    const { container } = render(<Section>Content</Section>);
    const section = container.firstChild as HTMLElement;
    expect(section.tagName).toBe('SECTION');
  });

  it('renders complex content structure', () => {
    render(
      <Section title="Test Section">
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
      </Section>,
    );

    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Test Section');
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
    expect(screen.getByText('Paragraph 2')).toBeInTheDocument();
  });
});
