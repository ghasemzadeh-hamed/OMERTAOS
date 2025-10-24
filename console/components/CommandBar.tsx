'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';

interface Props {
  onSubmit: (command: string) => Promise<void>;
  busy?: boolean;
}

export function CommandBar({ onSubmit, busy = false }: Props) {
  const [command, setCommand] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!command.trim()) {
      return;
    }
    await onSubmit(command.trim());
    setCommand('');
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18 }}
      className="flex items-center gap-2 rounded-xl border border-white/15 bg-white/10 p-3 backdrop-blur-xl shadow-lg shadow-black/30"
    >
      <input
        className="flex-1 bg-transparent text-sm text-white placeholder:text-white/50 focus:outline-none"
        placeholder="/install agent ghcr.io/..."
        value={command}
        onChange={(event) => setCommand(event.target.value)}
      />
      <button
        type="submit"
        disabled={busy}
        className="inline-flex items-center rounded-lg border border-white/30 bg-white/20 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-white/90 transition-all duration-200 hover:-translate-y-0.5 hover:bg-white/30 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <PaperAirplaneIcon className="mr-1 h-4 w-4" />
        Send
      </button>
    </motion.form>
  );
}
