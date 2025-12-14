import { beforeEach, describe, expect, it, vi } from 'vitest';

import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import { ChatMessageList } from '../../../components/os-chat/ChatMessageList';
import { ChatMessage } from '../../../types/os-chat';

const BASE_MESSAGES: ChatMessage[] = [
  {
    id: '1',
    role: 'user',
    createdAtIso: '2025-12-14T12:00:00Z',
    contentText: 'Hello OS',
  },
  {
    id: '2',
    role: 'os',
    createdAtIso: '2025-12-14T12:00:01Z',
    contentText: 'Acknowledged',
    runId: 'run_abc',
  },
];

describe('ChatMessageList', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    });
  });

  it('renders messages, role badges, and run links', () => {
    render(<ChatMessageList messages={BASE_MESSAGES} />);

    expect(screen.getByText('Hello OS')).toBeInTheDocument();
    expect(screen.getByText('Acknowledged')).toBeInTheDocument();
    expect(screen.getAllByText(/OS|User/).length).toBeGreaterThan(0);
    expect(screen.getByText('Open run')).toHaveAttribute('href', '/runs/run_abc');
  });

  it('reveals tool call details when toggled', async () => {
    const toolCallMessage: ChatMessage = {
      id: '3',
      role: 'tool',
      createdAtIso: '2025-12-14T12:00:02Z',
      contentText: 'tool_call demo',
      toolCall: {
        id: 'tc_1',
        toolName: 'demo_tool',
        argsJson: '{"input":"value"}',
        status: 'running',
        resultText: 'In progress',
      },
    };

    render(<ChatMessageList messages={[...BASE_MESSAGES, toolCallMessage]} />);

    fireEvent.click(screen.getByTestId('toggle-tool-call'));

    await waitFor(() => {
      expect(screen.getByTestId('tool-call-details')).toBeInTheDocument();
      expect(screen.getByText('demo_tool')).toBeInTheDocument();
      expect(screen.getByText('In progress')).toBeInTheDocument();
    });
  });
});
