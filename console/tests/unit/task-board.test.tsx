import { render, screen } from '@testing-library/react';
import { TaskBoard } from '../../components/TaskBoard';
import { describe, it, expect } from 'vitest';

const tasks = [
  { taskId: '1', intent: 'summarize', params: {}, status: 'PENDING' },
  { taskId: '2', intent: 'summarize', params: {}, status: 'OK' },
];

describe('TaskBoard', () => {
  it('groups tasks by column', () => {
    render(<TaskBoard tasks={tasks as any} />);
    expect(screen.getByText('To do')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getAllByText('1').length).toBeGreaterThan(0);
  });
});
