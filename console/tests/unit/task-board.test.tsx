import { render, screen } from '@testing-library/react';
import { TaskBoard } from '../../components/TaskBoard';
import { describe, it, expect } from 'vitest';

const tasks = [
  { taskId: '1', intent: 'summarize', params: {}, status: 'QUEUED' },
  { taskId: '2', intent: 'summarize', params: {}, status: 'COMPLETED' },
];

describe('TaskBoard', () => {
  it('groups tasks by column', () => {
    render(<TaskBoard tasks={tasks as any} />);
    expect(screen.getByText('To do')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });
});
