import { render, screen } from '@testing-library/react';
import { GlassCard } from '../../components/GlassCard';
import { describe, it, expect } from 'vitest';

describe('GlassCard', () => {
  it('renders title and description', () => {
    render(
      <GlassCard>
        <h3>Test title</h3>
        <p>Details</p>
      </GlassCard>
    );
    expect(screen.getByText('Test title')).toBeInTheDocument();
    expect(screen.getByText('Details')).toBeInTheDocument();
  });
});
