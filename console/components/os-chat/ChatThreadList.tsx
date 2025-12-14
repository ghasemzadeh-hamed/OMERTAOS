'use client';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ChatThread } from '@/types/os-chat';

type ChatThreadListProps = {
  threads: ChatThread[];
  selectedId?: string;
  onSelect: (threadId: string) => void;
  onCreate: (title: string) => Promise<void>;
};

export function ChatThreadList({ threads, selectedId, onSelect, onCreate }: ChatThreadListProps) {
  const [title, setTitle] = useState('');
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!title.trim()) return;
    setCreating(true);
    await onCreate(title.trim());
    setTitle('');
    setCreating(false);
  };

  return (
    <div className="flex h-full flex-col border-r border-slate-200 bg-white" data-testid="chat-thread-list">
      <div className="border-b border-slate-200 p-3">
        <h2 className="text-sm font-semibold text-slate-800">Threads</h2>
        <div className="mt-2 flex gap-2">
          <Input
            placeholder="New thread title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                handleCreate();
              }
            }}
          />
          <Button size="sm" onClick={handleCreate} disabled={creating || !title.trim()}>
            Create
          </Button>
        </div>
      </div>
      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        {threads.map((thread) => (
          <button
            key={thread.id}
            className={`w-full rounded px-3 py-2 text-left text-sm transition hover:bg-slate-100 ${
              thread.id === selectedId ? 'bg-slate-100 font-semibold' : 'bg-transparent'
            }`}
            onClick={() => onSelect(thread.id)}
          >
            <div className="truncate">{thread.title}</div>
            <div className="text-xs text-slate-500">{new Date(thread.createdAtIso).toLocaleString()}</div>
          </button>
        ))}
        {threads.length === 0 && (
          <div className="rounded border border-dashed border-slate-200 p-3 text-center text-sm text-slate-500">
            No threads yet.
          </div>
        )}
      </div>
    </div>
  );
}
