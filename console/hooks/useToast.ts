'use client';

export function useToast() {
  return {
    success: (message: string) => {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'success', message } }));
      }
    },
    error: (message: string) => {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('toast', { detail: { type: 'error', message } }));
      }
    },
  };
}
