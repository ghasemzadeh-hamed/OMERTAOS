'use client';

import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useEffect, useMemo, useState } from 'react';
import { useUIStore } from '../state/ui.store';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';

const actions = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Projects', href: '/projects' },
  { label: 'Tasks', href: '/tasks' },
  { label: 'Agents', href: '/agents' },
  { label: 'Policies', href: '/policies' },
  { label: 'Telemetry', href: '/telemetry' },
];

export function CommandPalette() {
  const { commandPaletteOpen, closeCommandPalette, openCommandPalette } = useUIStore();
  const [query, setQuery] = useState('');
  const router = useRouter();
  const t = useTranslations('nav');

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        if (commandPaletteOpen) {
          closeCommandPalette();
        } else {
          openCommandPalette();
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [commandPaletteOpen, closeCommandPalette, openCommandPalette]);

  const results = useMemo(() => {
    return actions.filter((action) => action.label.toLowerCase().includes(query.toLowerCase()));
  }, [query]);

  return (
    <Transition appear show={commandPaletteOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={closeCommandPalette}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/40" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="glass-card w-full max-w-lg p-6">
                <Dialog.Title className="text-sm text-slate-200">{t('command_palette')}</Dialog.Title>
                <input
                  className="glass-input mt-3"
                  placeholder="Search commands"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                <ul className="mt-4 space-y-2">
                  {results.length === 0 ? (
                    <li className="text-sm text-slate-400">No results</li>
                  ) : (
                    results.map((result) => (
                      <li key={result.href}>
                        <button
                          className="glass-button w-full justify-start"
                          onClick={() => {
                            router.push(result.href);
                            closeCommandPalette();
                          }}
                        >
                          {result.label}
                        </button>
                      </li>
                    ))
                  )}
                </ul>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
