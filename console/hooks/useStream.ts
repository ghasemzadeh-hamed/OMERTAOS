'use client';

import { useEffect, useRef, useState } from 'react';

interface Options<T> {
  enabled?: boolean;
  onMessage?: (event: { type: string; payload: T }) => void;
}

export function useStream<T>(url: string, { enabled = true, onMessage }: Options<T> = {}) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !url) {
      return;
    }
    const source = new EventSource(url, { withCredentials: true });
    eventSourceRef.current = source;
    source.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed as T);
        onMessage?.({ type: event.type || 'message', payload: parsed });
      } catch (parseError) {
        setError('Failed to parse stream payload');
      }
    };
    source.onerror = () => {
      setError('Stream disconnected');
      source.close();
    };
    return () => {
      source.close();
      eventSourceRef.current = null;
    };
  }, [url, enabled, onMessage]);

  return { data, error };
}
