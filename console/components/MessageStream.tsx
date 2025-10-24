'use client';

import { motion } from 'framer-motion';

interface Message {
  type: string;
  content: string;
}

export function MessageStream({ messages }: { messages: Message[] }) {
  return (
    <div className="space-y-3 overflow-y-auto max-h-[360px] pr-2">
      {messages.map((message, index) => (
        <motion.div
          key={`${message.type}-${index}`}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.18, type: 'spring', stiffness: 120 }}
          className={`rounded-lg border border-white/10 bg-white/10 backdrop-blur-xl p-4 text-sm font-mono shadow-inner shadow-black/40 ${
            message.type === 'error' ? 'text-rose-300' : 'text-emerald-200'
          }`}
        >
          <span className="mr-2 uppercase tracking-wide text-xs text-white/70">{message.type}</span>
          <span className="whitespace-pre-wrap break-words">{message.content}</span>
        </motion.div>
      ))}
    </div>
  );
}
