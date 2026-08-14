'use client';

import { useState } from 'react';
import { CheckIcon, ClipboardIcon } from '@heroicons/react/24/outline';

export type TerminalMenuItem = {
  label: string;
  command: string;
  description?: string;
};

interface TerminalMenuProps {
  items: TerminalMenuItem[];
}

export function TerminalMenu({ items }: TerminalMenuProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const handleCopy = async (command: string) => {
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(command);
        setCopied(command);
        setTimeout(() => setCopied((current) => (current === command ? null : current)), 2000);
      }
    } catch (error) {
      console.error('Failed to copy command', error);
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-950/80 shadow-inner">
      <div className="flex items-center gap-2 border-b border-white/5 bg-black/40 px-4 py-3 text-xs font-medium text-slate-400">
        <span className="flex h-2 w-2 rounded-full bg-red-500" aria-hidden />
        <span className="flex h-2 w-2 rounded-full bg-yellow-400" aria-hidden />
        <span className="flex h-2 w-2 rounded-full bg-green-500" aria-hidden />
        <span className="ml-3 font-mono">aion@ci:~</span>
      </div>
      <ul className="divide-y divide-white/5">
        {items.map((item) => (
          <li key={item.command} className="flex flex-col gap-3 px-4 py-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-sm font-semibold text-white">{item.label}</p>
              {item.description ? (
                <p className="mt-1 text-xs text-slate-300">{item.description}</p>
              ) : null}
              <code className="mt-3 block rounded-lg border border-white/10 bg-black/40 px-3 py-2 font-mono text-xs text-emerald-200">
                {item.command}
              </code>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={() => handleCopy(item.command)}
                className="glass-button inline-flex items-center gap-2 text-xs"
                aria-label={`Copy ${item.label} command`}
              >
                {copied === item.command ? (
                  <CheckIcon className="h-4 w-4" />
                ) : (
                  <ClipboardIcon className="h-4 w-4" />
                )}
                {copied === item.command ? 'Copied' : 'Copy'}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
