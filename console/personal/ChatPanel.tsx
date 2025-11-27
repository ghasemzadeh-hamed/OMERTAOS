'use client';

import React, { useEffect, useMemo, useRef, useState } from 'react';

type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  pending?: boolean;
  taskId?: string;
};

type ChatPanelProps = {
  intent?: string;
  title?: string;
  autoConfirm?: boolean;
};

const buildHistory = (messages: ChatMessage[]): { role: string; content: string }[] =>
  messages
    .filter((message) => message.content && (message.role === 'user' || message.role === 'assistant'))
    .map((message) => ({ role: message.role, content: message.content }));

const parseEventsText = (raw: unknown): string => {
  if (!raw) {
    return '';
  }
  let events: unknown = raw;
  if (typeof raw === 'string') {
    try {
      events = JSON.parse(raw);
    } catch (error) {
      return raw;
    }
  }
  if (!Array.isArray(events)) {
    return '';
  }
  let final = '';
  let deltas = '';
  for (const item of events) {
    if (item && typeof item === 'object') {
      const delta = (item as Record<string, unknown>).delta;
      if (typeof delta === 'string') {
        deltas += delta;
      }
      const text = (item as Record<string, unknown>).text;
      if (typeof text === 'string' && text.trim().length > 0) {
        final = text;
      }
    }
  }
  return final || deltas;
};

const ChatPanel: React.FC<ChatPanelProps> = ({ intent = 'chat', title = 'Chat', autoConfirm = false }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const sessionId = useMemo(
    () => (typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `session-${Date.now()}`),
    [],
  );

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  const closeStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  const updateAssistantMessage = (id: string, content: string, pending: boolean) => {
    setMessages((prev) =>
      prev.map((message) => (message.id === id ? { ...message, content, pending, taskId: message.taskId } : message)),
    );
  };

  const subscribeToTask = (taskId: string, messageId: string) => {
    closeStream();
    const source = new EventSource(`/api/proxy/stream/${taskId}`);
    eventSourceRef.current = source;

    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const status = payload?.status ?? payload?.result?.status;
        const agentText = typeof payload?.result?.agent === 'string' ? payload.result.agent : '';
        const eventsText = parseEventsText(payload?.result?.events);
        const errorText = typeof payload?.error?.message === 'string' ? payload.error.message : '';
        const content = errorText || agentText || eventsText;
        updateAssistantMessage(messageId, content, status !== 'OK' && !errorText);
        if (status === 'OK' || errorText) {
          closeStream();
        }
      } catch (err) {
        updateAssistantMessage(messageId, 'Streaming error.', false);
        closeStream();
      }
    };

    source.onerror = () => {
      updateAssistantMessage(messageId, 'Connection lost.', false);
      closeStream();
    };
  };

  const handleSend = async (event?: React.FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    const text = input.trim();
    if (!text || sending) {
      return;
    }
    setSending(true);
    setError(null);

    const userMessage: ChatMessage = { id: `user-${Date.now()}`, role: 'user', content: text };
    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      pending: true,
    };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput('');

    const history = [...buildHistory(messages), { role: 'user', content: text }];

    try {
      const response = await fetch('/api/proxy/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schemaVersion: '1.0',
          intent,
          params: {
            history,
            message: text,
            session_id: sessionId,
            auto_confirm: autoConfirm,
          },
          preferredEngine: 'auto',
          priority: 'normal',
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        const message = typeof data?.message === 'string' ? data.message : 'Request failed.';
        throw new Error(message);
      }

      const taskId = data?.taskId as string | undefined;
      const resultText = typeof data?.result?.agent === 'string' ? data.result.agent : '';
      const eventsText = parseEventsText(data?.result?.events);
      const content = resultText || eventsText;

      if (taskId) {
        updateAssistantMessage(assistantMessage.id, content, !content);
        subscribeToTask(taskId, assistantMessage.id);
      } else {
        updateAssistantMessage(assistantMessage.id, content || 'No response.', false);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error.';
      setError(message);
      updateAssistantMessage(assistantMessage.id, message, false);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-80 flex-col rounded border border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
        {sending && <span className="text-xs text-slate-500">Sending...</span>}
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-4 text-sm">
        {messages.map((message) => (
          <div key={message.id} className="leading-relaxed">
            <span className="font-semibold text-slate-700">{message.role === 'user' ? 'You' : 'Assistant'}:</span>{' '}
            <span className={message.pending ? 'text-slate-400' : 'text-slate-800'}>
              {message.content || '...'}
            </span>
          </div>
        ))}
        {error && <div className="text-xs text-red-600">{error}</div>}
      </div>
      <form className="flex gap-2 border-t border-slate-200 p-3" onSubmit={handleSend}>
        <input
          id="chat-input"
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
          placeholder="Type a message"
          value={input}
          onChange={(event) => setInput(event.target.value)}
        />
        <button
          type="submit"
          className="rounded bg-slate-800 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          disabled={sending}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
