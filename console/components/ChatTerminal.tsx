'use client';

import { useCallback, useMemo, useState } from 'react';
import { useStream } from '../hooks/useStream';
import { CommandBar } from './CommandBar';
import { MessageStream } from './MessageStream';
import { useToast } from '../hooks/useToast';

interface ChatOptions {
  engine: 'local' | 'api' | 'hybrid';
  privacy: 'local-only' | 'allow-api' | 'hybrid';
  target: 'kernel' | 'module' | 'memory' | 'task';
}

export function ChatTerminal() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{ type: string; content: string }>>([]);
  const [options, setOptions] = useState<ChatOptions>({ engine: 'local', privacy: 'allow-api', target: 'task' });
  const [isExecuting, setExecuting] = useState(false);
  const toast = useToast();

  const streamUrl = useMemo(() => {
    if (!sessionId) {
      return '';
    }
    return `/api/proxy/chat/stream/${sessionId}`;
  }, [sessionId]);

  useStream<{ type: string; payload: unknown }>(streamUrl, {
    enabled: Boolean(sessionId),
    onMessage: (event) => {
      setMessages((prev) => [...prev, { type: event.type, content: JSON.stringify(event.payload, null, 2) }]);
    },
  });

  const handleSubmit = useCallback(
    async (command: string) => {
      setExecuting(true);
      try {
        const response = await fetch('/api/proxy/chat/execute', {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ command, options }),
        });
        if (!response.ok) {
          throw new Error(`Command failed with ${response.status}`);
        }
        const payload = await response.json();
        setSessionId(payload.sessionId);
        setMessages((prev) => [...prev, { type: 'info', content: `Session ${payload.sessionId}` }]);
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        toast.error(message);
        setMessages((prev) => [...prev, { type: 'error', content: message }]);
      } finally {
        setExecuting(false);
      }
    },
    [options, toast]
  );

  return (
    <div className="flex flex-col gap-4 rounded-3xl border border-white/15 bg-white/10 p-6 backdrop-blur-2xl shadow-2xl shadow-black/40">
      <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.2em] text-white/70">
        <span>ChatOps Terminal</span>
        <div className="flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[10px] text-white/80">
          Engine
          <select
            className="bg-transparent text-white/90 focus:outline-none"
            value={options.engine}
            onChange={(event) => setOptions((current) => ({ ...current, engine: event.target.value as ChatOptions['engine'] }))}
          >
            <option value="local">Local</option>
            <option value="api">Cloud API</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[10px] text-white/80">
          Privacy
          <select
            className="bg-transparent text-white/90 focus:outline-none"
            value={options.privacy}
            onChange={(event) => setOptions((current) => ({ ...current, privacy: event.target.value as ChatOptions['privacy'] }))}
          >
            <option value="allow-api">Allow API</option>
            <option value="local-only">Local only</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-[10px] text-white/80">
          Target
          <select
            className="bg-transparent text-white/90 focus:outline-none"
            value={options.target}
            onChange={(event) => setOptions((current) => ({ ...current, target: event.target.value as ChatOptions['target'] }))}
          >
            <option value="task">Task</option>
            <option value="module">Module</option>
            <option value="kernel">Kernel</option>
            <option value="memory">Memory</option>
          </select>
        </div>
      </div>
      <MessageStream messages={messages} />
      <CommandBar onSubmit={handleSubmit} busy={isExecuting} />
    </div>
  );
}
