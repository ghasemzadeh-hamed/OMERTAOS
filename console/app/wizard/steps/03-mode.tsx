'use client';

import { useState } from 'react';

const modes: Array<'native' | 'image' | 'wsl' | 'docker'> = ['native', 'image', 'wsl', 'docker'];

export default function Mode() {
  const [mode, setMode] = useState<'native' | 'image' | 'wsl' | 'docker'>('native');

  return (
    <div>
      <p>Select install mode:</p>
      {modes.map((item) => (
        <button key={item} onClick={() => setMode(item)} className={mode === item ? 'sel' : ''}>
          {item.toUpperCase()}
        </button>
      ))}
      <p>Current: {mode}</p>
    </div>
  );
}
