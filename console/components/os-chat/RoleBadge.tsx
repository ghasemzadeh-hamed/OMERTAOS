'use client';

import { Badge } from '@/components/ui/badge';
import { ChatRole } from '@/types/os-chat';

const ROLE_LABELS: Record<ChatRole, string> = {
  user: 'User',
  os: 'OS',
  agent: 'Agent',
  tool: 'Tool',
  system: 'System',
};

export function RoleBadge({ role }: { role: ChatRole }) {
  return <Badge variant="outline">{ROLE_LABELS[role] ?? role}</Badge>;
}
