'use client';

import { useSession, signOut } from 'next-auth/react';
import { useMemo } from 'react';
import { canAccess } from '../lib/rbac';

export function useAuth() {
  const { data, status } = useSession();

  const role = data?.user?.role ?? 'user';
  const permissions = useMemo(
    () => ({
      canManagePolicies: canAccess(role, 'policies'),
      canManageAgents: canAccess(role, 'agents'),
      canViewTelemetry: canAccess(role, 'telemetry'),
    }),
    [role]
  );

  return {
    session: data,
    status,
    role,
    permissions,
    signOut,
  };
}
