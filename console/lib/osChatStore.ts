import { ApiEnvelope, ChatMessage, ChatThread, ToolCallEvent } from '@/types/os-chat';

let chatThreads: ChatThread[] = [
  {
    id: 'thr_sample',
    title: 'OS model onboarding',
    createdAtIso: '2025-12-14T12:00:00Z',
  },
  {
    id: 'thr_observability',
    title: 'Investigate failed tool call',
    createdAtIso: '2025-12-14T12:01:00Z',
  },
];

const threadMessages: Record<string, ChatMessage[]> = {
  thr_sample: [
    {
      id: 'msg_1',
      role: 'user',
      createdAtIso: '2025-12-14T12:00:01Z',
      contentText: 'Create an agent for repo analysis and run a smoke test.',
    },
    {
      id: 'msg_2',
      role: 'os',
      createdAtIso: '2025-12-14T12:00:02Z',
      contentText: 'I can validate secrets, create the agent, and run a smoke test.',
      meta: {
        intent: 'create_agent_and_run',
        env: 'prod',
        requestedActions: ['validate_secrets', 'create_agent', 'run_smoke_test'],
      },
    },
    {
      id: 'msg_3',
      role: 'tool',
      createdAtIso: '2025-12-14T12:00:04Z',
      contentText: 'tool_call repo_scan',
      toolCall: {
        id: 'tc_1',
        toolName: 'repo_scan',
        argsJson: '{"paths":["./"],"include":"docs"}',
        status: 'running',
        resultText: '',
        startedAtIso: '2025-12-14T12:00:04Z',
      },
    },
    {
      id: 'msg_4',
      role: 'tool',
      createdAtIso: '2025-12-14T12:00:05Z',
      contentText: 'tool_call repo_scan result',
      toolCall: {
        id: 'tc_1',
        toolName: 'repo_scan',
        argsJson: '{"paths":["./"],"include":"docs"}',
        status: 'succeeded',
        resultText: 'Found config files: docs/omertaos_console_prd.md',
        startedAtIso: '2025-12-14T12:00:04Z',
        endedAtIso: '2025-12-14T12:00:05Z',
      },
    },
    {
      id: 'msg_5',
      role: 'os',
      createdAtIso: '2025-12-14T12:01:10Z',
      contentText:
        'Run created: run_123 (FAILED: TOOL_ERROR HTTP_504). Suggested fix: increase timeout.',
      runId: 'run_123',
      meta: {
        errorClass: 'TOOL_ERROR',
        errorCode: 'HTTP_504',
        suggestedActions: ['retry_with_override', 'disable_tool_temporarily'],
      },
    },
  ],
  thr_observability: [
    {
      id: 'msg_6',
      role: 'user',
      createdAtIso: '2025-12-14T12:02:00Z',
      contentText: 'Inspect run run_456 and explain policy denials.',
    },
    {
      id: 'msg_7',
      role: 'os',
      createdAtIso: '2025-12-14T12:02:02Z',
      contentText: 'Found policy denial for tool usage. Rule id: policy_9.',
      meta: {
        intent: 'explain_policy',
        ruleId: 'policy_9',
      },
    },
  ],
};

function paginate<T>(items: T[]): ApiEnvelope<T[]> {
  return {
    ok: true,
    data: items,
    meta: {
      pagination: { page: 1, pageSize: items.length, total: items.length },
    },
  };
}

export function listThreads(): ApiEnvelope<ChatThread[]> {
  return paginate([...chatThreads]);
}

export function createThread(title: string): ApiEnvelope<ChatThread> {
  const thread: ChatThread = {
    id: `thr_${Date.now()}`,
    title: title.trim() || 'Untitled thread',
    createdAtIso: new Date().toISOString(),
  };
  chatThreads = [thread, ...chatThreads];
  threadMessages[thread.id] = [
    {
      id: `msg_${Date.now()}`,
      role: 'os',
      createdAtIso: thread.createdAtIso,
      contentText: 'Thread created. Ask the OS to run, debug, or patch.',
    },
  ];
  return { ok: true, data: thread };
}

export function getMessages(threadId: string): ApiEnvelope<ChatMessage[]> {
  const messages = threadMessages[threadId] ?? [];
  return paginate(messages);
}

function buildEchoToolCall(argsJson: string): ToolCallEvent {
  return {
    id: `tc_${Date.now()}`,
    toolName: 'echo_debug',
    argsJson,
    status: 'succeeded',
    resultText: 'Request captured for audit. No external action executed.',
    startedAtIso: new Date().toISOString(),
    endedAtIso: new Date().toISOString(),
  };
}

export function addMessage(threadId: string, contentText: string): ApiEnvelope<ChatMessage> {
  const trimmed = contentText.trim();
  const userMessage: ChatMessage = {
    id: `msg_${Date.now()}`,
    role: 'user',
    createdAtIso: new Date().toISOString(),
    contentText: trimmed,
  };
  const osReply: ChatMessage = {
    id: `msg_${Date.now() + 1}`,
    role: 'os',
    createdAtIso: new Date().toISOString(),
    contentText: 'Acknowledged. Planning actions based on the OS Chat contract.',
    toolCall: buildEchoToolCall(JSON.stringify({ requested: trimmed })),
  };

  threadMessages[threadId] = [...(threadMessages[threadId] ?? []), userMessage, osReply];
  return { ok: true, data: userMessage };
}

export function stopThread(): ApiEnvelope<{ stopped: boolean }> {
  return { ok: true, data: { stopped: true } };
}
