'use client';

import { useState } from 'react';

export default function User() {
  const [username, setUsername] = useState('aionos');
  const [password, setPassword] = useState('');

  return (
    <div>
      <h3>Create administrator</h3>
      <label>
        Username
        <input value={username} onChange={(event) => setUsername(event.target.value)} />
      </label>
      <label>
        Password
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
      </label>
      <p>Credentials will be applied during installation.</p>
    </div>
  );
}
