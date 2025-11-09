import * as React from 'react';

import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'outline';
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(({ className, variant = 'default', ...props }, ref) => {
  return (
    <span
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide',
        variant === 'outline'
          ? 'border-white/40 bg-transparent text-white'
          : 'border-transparent bg-white/20 text-white',
        className,
      )}
      {...props}
    />
  );
});
Badge.displayName = 'Badge';

export { Badge };
