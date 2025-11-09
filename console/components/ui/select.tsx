import * as React from 'react';

import { cn } from '@/lib/utils';

type SelectContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
  value?: string;
  onItemSelect: (value: string, label: string) => void;
  registerItem: (value: string, label: string) => void;
  getLabel: (value?: string) => string | undefined;
  triggerId: string;
  contentId: string;
};

const SelectContext = React.createContext<SelectContextValue | null>(null);

export interface SelectProps {
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

export function Select({ value, defaultValue, onValueChange, children }: SelectProps): JSX.Element {
  const [open, setOpen] = React.useState(false);
  const [internalValue, setInternalValue] = React.useState<string | undefined>(defaultValue);
  const [labels, setLabels] = React.useState<Record<string, string>>({});
  const triggerId = React.useId();
  const contentId = React.useId();

  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;

  const onItemSelect = React.useCallback(
    (next: string, label: string) => {
      if (!isControlled) {
        setInternalValue(next);
      }
      setLabels((prev) => ({ ...prev, [next]: label }));
      onValueChange?.(next);
      setOpen(false);
    },
    [isControlled, onValueChange],
  );

  const registerItem = React.useCallback((itemValue: string, label: string) => {
    setLabels((prev) => {
      if (prev[itemValue] === label) {
        return prev;
      }
      return { ...prev, [itemValue]: label };
    });
  }, []);

  const getLabel = React.useCallback((itemValue?: string) => {
    if (!itemValue) {
      return undefined;
    }
    return labels[itemValue];
  }, [labels]);

  const contextValue = React.useMemo<SelectContextValue>(
    () => ({
      open,
      setOpen,
      value: currentValue,
      onItemSelect,
      registerItem,
      getLabel,
      triggerId,
      contentId,
    }),
    [open, setOpen, currentValue, onItemSelect, registerItem, getLabel, triggerId, contentId],
  );

  return <SelectContext.Provider value={contextValue}>{children}</SelectContext.Provider>;
}

export interface SelectTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export const SelectTrigger = React.forwardRef<HTMLButtonElement, SelectTriggerProps>(
  ({ className, children, ...props }, ref) => {
    const context = React.useContext(SelectContext);
    if (!context) {
      throw new Error('SelectTrigger must be used within a Select');
    }
    return (
      <button
        type="button"
        ref={ref}
        id={context.triggerId}
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={context.open}
        aria-controls={context.contentId}
        onClick={() => context.setOpen(!context.open)}
        className={cn(
          'flex w-full items-center justify-between rounded-md border border-white/20 bg-white/10 px-3 py-2 text-sm text-white transition-colors hover:bg-white/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500',
          className,
        )}
        {...props}
      >
        {children}
      </button>
    );
  },
);
SelectTrigger.displayName = 'SelectTrigger';

export interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

export const SelectValue = ({ placeholder, className }: SelectValueProps): JSX.Element => {
  const context = React.useContext(SelectContext);
  if (!context) {
    throw new Error('SelectValue must be used within a Select');
  }

  const label = context.getLabel(context.value);
  const content = label ?? context.value ?? placeholder ?? '';

  return <span className={cn('truncate text-left text-sm', className)}>{content}</span>;
};

export interface SelectContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: 'start' | 'end' | 'center';
}

export const SelectContent = React.forwardRef<HTMLDivElement, SelectContentProps>(
  ({ className, align = 'start', children, ...props }, ref) => {
    const context = React.useContext(SelectContext);
    if (!context) {
      throw new Error('SelectContent must be used within a Select');
    }

    if (!context.open) {
      return null;
    }

    return (
      <div
        ref={ref}
        id={context.contentId}
        role="listbox"
        aria-labelledby={context.triggerId}
        className={cn(
          'z-50 mt-2 min-w-[12rem] rounded-md border border-white/20 bg-slate-900/95 p-1 text-sm shadow-xl focus:outline-none',
          align === 'end' && 'ml-auto',
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);
SelectContent.displayName = 'SelectContent';

export interface SelectItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
}

export const SelectItem = React.forwardRef<HTMLButtonElement, SelectItemProps>(
  ({ className, children, value, ...props }, ref) => {
    const context = React.useContext(SelectContext);
    if (!context) {
      throw new Error('SelectItem must be used within a Select');
    }

    const label = React.useMemo(() => {
      if (typeof children === 'string' || typeof children === 'number') {
        return String(children);
      }
      return React.Children.toArray(children)
        .map((child) => {
          if (typeof child === 'string' || typeof child === 'number') {
            return String(child);
          }
          return '';
        })
        .join('')
        .trim();
    }, [children]);

    React.useEffect(() => {
      context.registerItem(value, label);
    }, [context, value, label]);

    const isSelected = context.value === value;

    return (
      <button
        ref={ref}
        role="option"
        aria-selected={isSelected}
        onClick={() => context.onItemSelect(value, label)}
        className={cn(
          'w-full cursor-pointer rounded-md px-3 py-2 text-left transition-colors hover:bg-white/10',
          isSelected && 'bg-cyan-500/20 text-cyan-100',
          className,
        )}
        {...props}
      >
        {children}
      </button>
    );
  },
);
SelectItem.displayName = 'SelectItem';
