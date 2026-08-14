'use client';

import ChatPanel from '@/personal/ChatPanel';

export default function AgentChatPage() {
  return <ChatPanel intent="agent.chat" title="Agent Chat" autoConfirm={false} />;
}
