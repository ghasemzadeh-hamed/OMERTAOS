'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Props {
  endpoint: string;
}

export function LogStream({ endpoint }: Props) {
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    const connect = async () => {
      const response = await fetch(endpoint, { signal: controller.signal });
      const reader = response.body?.getReader();
      if (!reader) {
        return;
      }
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setLines((prev) => [...prev.slice(-100), chunk]);
      }
    };
    connect();
    return () => controller.abort();
  }, [endpoint]);

  return (
    <motion.div className="glass-card max-h-72 overflow-auto p-4 text-xs text-emerald-200" layout>
      {lines.length === 0 ? 'Waiting for logs…' : lines.map((line, index) => <div key={index}>{line}</div>)}
    </motion.div>
  );
}
