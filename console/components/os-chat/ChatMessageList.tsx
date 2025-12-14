'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { ChatMessage } from '@/types/os-chat';

import { RoleBadge } from './RoleBadge';
import { ToolCallCard } from './ToolCallCard';

function formatTime(iso?: string) {
  if (!iso) return '';
  const date = new Date(iso);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function copyToClipboard(text: string) {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(() => {});
  }
}

type ChatMessageListProps = {
  messages: ChatMessage[];
};

export function ChatMessageList({ messages }: ChatMessageListProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const sorted = useMemo(() => [...messages].sort((a, b) => a.createdAtIso.localeCompare(b.createdAtIso)), [messages]);

  return (
    <div className="flex-1 space-y-3 overflow-y-auto p-4" data-testid="chat-message-list">
      {sorted.map((message) => (
        <div key={message.id} className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
          <div className="flex items-center justify-between gap-2 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <RoleBadge role={message.role} />
              <span>{formatTime(message.createdAtIso)}</span>
            </div>
            <div className="flex items-center gap-2">
              {message.runId && (
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/runs/${message.runId}`}>Open run</Link>
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  copyToClipboard(message.contentText);
                  setCopiedId(message.id);
                  setTimeout(() => setCopiedId(null), 1500);
                }}
              >
                {copiedId === message.id ? 'Copied' : 'Copy'}
              </Button>
            </div>
          </div>
          <p className="mt-2 whitespace-pre-wrap text-sm text-slate-800">{message.contentText}</p>
          {message.toolCall && <div className="mt-3"><ToolCallCard toolCall={message.toolCall} /></div>}
        </div>
      ))}
      {messages.length === 0 && (
        <div className="rounded border border-dashed border-slate-200 p-4 text-center text-sm text-slate-500">
          No messages yet. Ask the OS to run, debug, or patch.
        </div>
      )}
    </div>
  );
}
