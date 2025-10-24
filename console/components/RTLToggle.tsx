'use client';

import { useRTL } from '../hooks/useRTL';
import { motion } from 'framer-motion';

export function RTLToggle() {
  const { rtl, setRTL } = useRTL();

  return (
    <motion.button
      type="button"
      onClick={() => setRTL(!rtl)}
      className="glass-button"
      aria-pressed={rtl}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 180, damping: 16 }}
    >
      {rtl ? 'RTL' : 'LTR'}
    </motion.button>
  );
}
