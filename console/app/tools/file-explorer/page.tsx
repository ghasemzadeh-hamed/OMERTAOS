'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

type FileEntry = {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  modified_at?: string;
};

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';

export default function FileExplorerPage() {
  const [currentPath, setCurrentPath] = useState<string | null>(null);
  const [entries, setEntries] = useState<FileEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (path?: string | null) => {
      setLoading(true);
      setError(null);
      try {
        const url = new URL(`${CONTROL_BASE}/api/files/list`);
        if (path) {
          url.searchParams.set('path', path);
        }
        const res = await fetch(url.toString(), { credentials: 'include' });
        if (!res.ok) {
          throw new Error(`Failed to list files: ${res.status}`);
        }
        const data = await res.json();
        setEntries(data.entries ?? []);
        setCurrentPath(data.path ?? null);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [setEntries],
  );

  useEffect(() => {
    load();
  }, [load]);

  const breadcrumbs = useMemo(() => {
    if (!currentPath) {
      return [];
    }
    const parts = currentPath.split('/').filter(Boolean);
    const crumbs = parts.map((part, index) => {
      const slice = '/' + parts.slice(0, index + 1).join('/');
      return { label: part, path: slice };
    });
    return crumbs;
  }, [currentPath]);

  const goParent = () => {
    if (!currentPath) {
      load();
      return;
    }
    const parent = currentPath.substring(0, currentPath.lastIndexOf('/')) || '/';
    if (parent === '/' || parent === '') {
      load();
    } else {
      load(parent);
    }
  };

  const handleCreateFolder = async () => {
    const name = window.prompt('New folder name');
    if (!name) return;
    const base = currentPath ?? '';
    const payload = { path: base ? `${base}/${name}` : name };
    const res = await fetch(`${CONTROL_BASE}/api/files/mkdir`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const detail = await res.text();
      window.alert(`Failed to create folder: ${detail}`);
      return;
    }
    load(currentPath);
  };

  const handleDelete = async (entry: FileEntry) => {
    if (!window.confirm(`Delete ${entry.name}?`)) return;
    const res = await fetch(`${CONTROL_BASE}/api/files/delete`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: entry.path }),
    });
    if (!res.ok) {
      window.alert(`Failed to delete: ${await res.text()}`);
      return;
    }
    load(currentPath);
  };

  const handleRename = async (entry: FileEntry) => {
    const newName = window.prompt('Rename to', entry.name);
    if (!newName || newName === entry.name) return;
    const res = await fetch(`${CONTROL_BASE}/api/files/rename`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: entry.path, new_name: newName }),
    });
    if (!res.ok) {
      window.alert(`Rename failed: ${await res.text()}`);
      return;
    }
    load(currentPath);
  };

  return (
    <div className="space-y-4 text-right">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-white/90">File explorer</h2>
          <p className="text-xs text-white/60">Allowed directories are limited by the AION_ALLOWED_PATHS environment variable.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => load(currentPath)} className="rounded-xl bg-white/10 px-3 py-2 text-sm hover:bg-white/20">
            Refresh
          </button>
          <button onClick={goParent} className="rounded-xl bg-white/10 px-3 py-2 text-sm hover:bg-white/20">
            Up
          </button>
          <button onClick={handleCreateFolder} className="rounded-xl bg-emerald-500/80 px-3 py-2 text-sm text-white hover:bg-emerald-500">
            New Folder
          </button>
        </div>
      </header>
      {breadcrumbs.length > 0 && (
        <div className="text-xs text-white/65">
          {breadcrumbs.map((crumb, idx) => (
            <button
              key={crumb.path}
              onClick={() => load(crumb.path)}
              className="underline-offset-2 hover:underline"
              type="button"
            >
              {crumb.label}
              {idx < breadcrumbs.length - 1 ? ' / ' : ''}
            </button>
          ))}
        </div>
      )}
      {error && <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
      <div className="overflow-hidden rounded-2xl border border-white/10">
        <table className="min-w-full divide-y divide-white/10 text-sm">
          <thead className="bg-white/5">
            <tr>
              <th className="px-4 py-2 text-right font-medium">Name</th>
              <th className="px-4 py-2 text-right font-medium">Type</th>
              <th className="px-4 py-2 text-right font-medium">Size</th>
              <th className="px-4 py-2 text-right font-medium">Modified</th>
              <th className="px-4 py-2 text-right font-medium">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {entries.map((entry) => (
              <tr key={entry.path} className="hover:bg-white/5">
                <td className="px-4 py-2">
                  {entry.type === 'directory' ? (
                    <button className="text-emerald-300 hover:underline" onClick={() => load(entry.path)} type="button">
                      {entry.name || entry.path}
                    </button>
                  ) : (
                    <span>{entry.name}</span>
                  )}
                </td>
                <td className="px-4 py-2 capitalize text-white/70">{entry.type}</td>
                <td className="px-4 py-2 text-white/60">{entry.type === 'file' ? `${(entry.size / 1024).toFixed(1)} KB` : '-'}</td>
                <td className="px-4 py-2 text-white/60">{entry.modified_at ? new Date(entry.modified_at).toLocaleString() : '-'}</td>
                <td className="px-4 py-2 text-white/70">
                  <div className="flex gap-2">
                    <button onClick={() => handleRename(entry)} className="rounded-lg bg-white/10 px-2 py-1 text-xs hover:bg-white/20" type="button">
                      Rename
                    </button>
                    <button onClick={() => handleDelete(entry)} className="rounded-lg bg-red-500/70 px-2 py-1 text-xs hover:bg-red-500" type="button">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {entries.length === 0 && !loading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-white/60">
                  No entries found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {loading && <div className="p-3 text-center text-xs text-white/60">Loading...</div>}
      </div>
    </div>
  );
}
