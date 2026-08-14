'use client';

import { useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ToolCallEvent } from '@/types/os-chat';

const STATUS_COLORS: Record<string, string> = {
  pending: 'border-transparent bg-amber-100 text-amber-800',
  running: 'border-transparent bg-blue-100 text-blue-800',
  succeeded: 'border-transparent bg-emerald-100 text-emerald-800',
  failed: 'border-transparent bg-red-100 text-red-800',
};

export function ToolCallCard({ toolCall }: { toolCall: ToolCallEvent }) {
  const [expanded, setExpanded] = useState(false);
  const statusClass = STATUS_COLORS[toolCall.status] ?? STATUS_COLORS.pending;

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm" data-testid="tool-call-card">
      <div className="flex items-center justify-between gap-2">
        <div className="space-x-2">
          <Badge variant="outline">{toolCall.toolName}</Badge>
          <Badge className={statusClass} variant="outline">
            {toolCall.status}
          </Badge>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setExpanded((v) => !v)} data-testid="toggle-tool-call">
          {expanded ? 'Hide details' : 'Show details'}
        </Button>
      </div>
      {expanded && (
        <div className="mt-3 space-y-2" data-testid="tool-call-details">
          <div>
            <p className="text-xs font-semibold text-slate-600">Args</p>
            <pre className="whitespace-pre-wrap rounded bg-white p-2 text-xs text-slate-800">{toolCall.argsJson}</pre>
          </div>
          {toolCall.resultText && (
            <div>
              <p className="text-xs font-semibold text-slate-600">Result</p>
              <pre className="whitespace-pre-wrap rounded bg-white p-2 text-xs text-slate-800">{toolCall.resultText}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
