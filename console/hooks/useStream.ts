'use client';

import { useEffect, useRef, useState } from 'react';

export function useStream<T>(url: string, { enabled = true }: { enabled?: boolean } = {}) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const source = new EventSource(url, { withCredentials: true });
    eventSourceRef.current = source;
    source.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed as T);
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
  }, [url, enabled]);

  return { data, error };
}
