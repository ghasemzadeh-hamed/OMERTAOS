'use client';

import { useEffect, useState } from 'react';

interface ToastMessage {
  id: number;
  type: 'success' | 'error';
  message: string;
}

export function ToastViewport() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    let id = 0;
    const handler = (event: Event) => {
      const detail = (event as CustomEvent).detail as { type: 'success' | 'error'; message: string };
      id += 1;
      setToasts((current) => [...current, { id, ...detail }]);
      setTimeout(() => {
        setToasts((current) => current.filter((toast) => toast.id !== id));
      }, 4000);
    };
    window.addEventListener('toast', handler as EventListener);
    return () => {
      window.removeEventListener('toast', handler as EventListener);
    };
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`min-w-[220px] rounded-lg border px-4 py-3 text-sm shadow-lg backdrop-blur-xl ${
            toast.type === 'error' ? 'border-rose-500/40 bg-rose-500/20 text-rose-100' : 'border-emerald-500/40 bg-emerald-500/20 text-emerald-100'
          }`}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
