'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';

type User = { id: string; email: string; name: string; role: string };

export default function AuthToolsPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [tokens, setTokens] = useState<any[]>([]);
  const [tokenName, setTokenName] = useState('');
  const [tokenScopes, setTokenScopes] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [available, setAvailable] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [userRes, roleRes, tokenRes] = await Promise.all([
        fetch(`${CONTROL_BASE}/api/auth/users`, { credentials: 'include' }),
        fetch(`${CONTROL_BASE}/api/auth/roles`, { credentials: 'include' }),
        fetch(`${CONTROL_BASE}/api/auth/tokens`, { credentials: 'include' }),
      ]);
      const failed = [userRes, roleRes, tokenRes].find((response) => !response.ok);
      if (failed) throw new Error(`Auth management API unavailable (HTTP ${failed.status})`);

      const data = await userRes.json();
      setUsers(data.users ?? []);
      const roleData = await roleRes.json();
      setRoles(roleData.roles ?? []);
      const tokenData = await tokenRes.json();
      setTokens(tokenData.tokens ?? []);
      setAvailable(true);
      setStatus(null);
    } catch (error) {
      setAvailable(false);
      setStatus(error instanceof Error ? error.message : 'Auth management API unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const updateRole = async (userId: string, role: string) => {
    const res = await fetch(`${CONTROL_BASE}/api/auth/users/${userId}/roles`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role }),
    });
    if (!res.ok) {
      setStatus(`Failed to update role: ${await res.text()}`);
      return;
    }
    setStatus('Role updated');
    void load();
  };

  const createToken = async () => {
    if (!tokenName.trim()) {
      setStatus('Token name required');
      return;
    }
    const res = await fetch(`${CONTROL_BASE}/api/auth/tokens`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: tokenName.trim(), scopes: tokenScopes.split(',').map((scope) => scope.trim()).filter(Boolean) }),
    });
    if (!res.ok) {
      setStatus(`Failed to create token: ${await res.text()}`);
      return;
    }
    const data = await res.json();
    setStatus(`Token created: ${data.token}`);
    setTokenName('');
    setTokenScopes('');
    void load();
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Auth &amp; Role Manager</h2>
        <p className="text-xs text-white/60">Manage RBAC assignments and scoped API tokens.</p>
      </header>
      {status && <div className="border border-amber-400/30 bg-amber-400/10 p-3 text-sm text-amber-100">{status}</div>}
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">Users</h3>
        <div className="overflow-hidden rounded-xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-sm">
            <thead className="bg-white/5">
              <tr>
                <th className="px-4 py-2 text-right">Email</th>
                <th className="px-4 py-2 text-right">Role</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-white/5">
                  <td className="px-4 py-2 text-white/80">{user.email}</td>
                  <td className="px-4 py-2 text-white/80">
                    <select
                      value={user.role}
                      onChange={(event) => updateRole(user.id, event.target.value)}
                      disabled={!available}
                      className="rounded-xl border border-white/10 bg-white/5 px-3 py-2"
                    >
                      {roles.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
        <h3 className="text-lg font-semibold text-white/85">Create API token</h3>
        <label className="block space-y-1">
          <span className="text-xs text-white/60">Name</span>
          <input value={tokenName} onChange={(event) => setTokenName(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <label className="block space-y-1">
          <span className="text-xs text-white/60">Scopes (comma separated)</span>
          <input value={tokenScopes} onChange={(event) => setTokenScopes(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <button disabled={!available || loading} onClick={createToken} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-40" type="button">
          {loading ? 'Checking API...' : 'Create token'}
        </button>
      </section>
      <section className="space-y-3 rounded-2xl border border-white/10 bg-black/50 p-4 text-xs text-emerald-100">
        <h3 className="text-sm font-semibold text-white/80">Tokens</h3>
        <pre className="max-h-64 overflow-auto">{JSON.stringify(tokens, null, 2)}</pre>
      </section>
    </div>
  );
}
