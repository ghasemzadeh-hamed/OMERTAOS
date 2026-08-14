'use client';

import { useCallback } from 'react';

import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

type ChatComposerProps = {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  onStop?: () => void;
  disabled?: boolean;
  placeholder?: string;
  showStop?: boolean;
};

export function ChatComposer({
  value,
  onChange,
  onSend,
  onStop,
  disabled,
  placeholder = 'Ask the OS to run, debug, or patch',
  showStop,
}: ChatComposerProps) {
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        onSend();
      }
    },
    [onSend],
  );

  return (
    <div className="border-t border-slate-200 bg-white p-3" data-testid="chat-composer">
      <label className="sr-only" htmlFor="os-chat-input">
        OS Chat message
      </label>
      <Textarea
        id="os-chat-input"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className="min-h-[80px] resize-none"
      />
      <div className="mt-2 flex items-center justify-between">
        <p className="text-xs text-slate-500">Enter to send, Shift+Enter for newline</p>
        <div className="flex gap-2">
          {showStop && (
            <Button variant="outline" size="sm" onClick={onStop} disabled={disabled}>
              Stop
            </Button>
          )}
          <Button size="sm" onClick={onSend} disabled={disabled || !value.trim()}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
