'use client';

import dynamic from 'next/dynamic';
import { useState } from 'react';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

const languageMap: Record<string, string> = {
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.ini': 'ini',
  '.py': 'python',
  '.md': 'markdown',
};

function detectLanguage(path: string) {
  const entry = Object.entries(languageMap).find(([suffix]) => path.endsWith(suffix));
  return entry ? entry[1] : 'plaintext';
}

export default function EditorPage() {
  const [path, setPath] = useState('');
  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('plaintext');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadContent = async () => {
    if (!path.trim()) {
      window.alert('Enter a file path');
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const url = new URL(`${CONTROL_BASE}/api/files/content`);
      url.searchParams.set('path', path.trim());
      const res = await fetch(url.toString(), { credentials: 'include' });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      setContent(data.content ?? '');
      setLanguage(detectLanguage(path.trim()));
      setStatus('Loaded successfully.');
    } catch (err) {
      setStatus((err as Error).message);
      setContent('');
    } finally {
      setLoading(false);
    }
  };

  const saveContent = async () => {
    if (!path.trim()) {
      window.alert('Enter a file path');
      return;
    }
    setLoading(true);
    setStatus(null);
    try {
      const res = await fetch(`${CONTROL_BASE}/api/files/save`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: path.trim(), content }),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setStatus('Saved successfully.');
    } catch (err) {
      setStatus((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 text-right">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white/90">Text / code editor</h2>
        <p className="text-xs text-white/60">Edit YAML, JSON, policy, and script files within the approved directories.</p>
      </header>
      <div className="flex flex-col gap-3 text-sm text-white/80 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="mb-1 block text-xs text-white/60">Path</span>
          <input
            value={path}
            onChange={(event) => setPath(event.target.value)}
            placeholder="/config/aionos.yaml"
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
          />
        </label>
        <label>
          <span className="mb-1 block text-xs text-white/60">Language</span>
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value)}
            className="rounded-xl border border-white/10 bg-white/5 px-3 py-2"
          >
            {['plaintext', 'yaml', 'json', 'ini', 'python', 'markdown'].map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </label>
        <div className="flex gap-2">
          <button
            onClick={loadContent}
            className="rounded-xl bg-white/10 px-4 py-2 text-sm hover:bg-white/20"
            type="button"
            disabled={loading}
          >
            Load
          </button>
          <button
            onClick={saveContent}
            className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500"
            type="button"
            disabled={loading}
          >
            Save
          </button>
        </div>
      </div>
      {status && <div className="text-xs text-white/60">{status}</div>}
      <div className="overflow-hidden rounded-2xl border border-white/10">
        <MonacoEditor
          height="520px"
          language={language}
          theme="vs-dark"
          value={content}
          onChange={(value) => setContent(value ?? '')}
          options={{ fontSize: 14, minimap: { enabled: false } }}
        />
      </div>
    </div>
  );
}
