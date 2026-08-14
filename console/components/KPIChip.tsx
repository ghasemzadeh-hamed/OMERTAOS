import { motion } from 'framer-motion';

interface Props {
  label: string;
  value: string;
  trend?: number;
}

export function KPIChip({ label, value, trend }: Props) {
  return (
    <motion.div
      className="glass-card flex flex-1 flex-col gap-1 p-5"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24, type: 'spring', stiffness: 180, damping: 24 }}
    >
      <span className="text-xs uppercase tracking-wide text-slate-300">{label}</span>
      <span className="text-2xl font-semibold text-white">{value}</span>
      {typeof trend === 'number' ? (
        <span className={`text-xs ${trend >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
          {trend >= 0 ? '+' : ''}
          {trend.toFixed(1)}%
        </span>
      ) : null}
    </motion.div>
  );
}
