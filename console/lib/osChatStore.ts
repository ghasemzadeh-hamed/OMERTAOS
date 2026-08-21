import { ApiEnvelope, ChatMessage, ChatThread } from "@/types/os-chat";

let chatThreads: ChatThread[] = [];

const threadMessages: Record<string, ChatMessage[]> = {};

function paginate<T>(items: T[]): ApiEnvelope<T[]> {
  return {
    ok: true,
    data: items,
    meta: {
      pagination: { page: 1, pageSize: items.length, total: items.length },
    },
  };
}

export function listThreads(): ApiEnvelope<ChatThread[]> {
  return paginate([...chatThreads]);
}

export function createThread(title: string): ApiEnvelope<ChatThread> {
  const thread: ChatThread = {
    id: `thr_${Date.now()}`,
    title: title.trim() || "Untitled thread",
    createdAtIso: new Date().toISOString(),
  };
  chatThreads = [thread, ...chatThreads];
  threadMessages[thread.id] = [];
  return { ok: true, data: thread };
}

export function getMessages(threadId: string): ApiEnvelope<ChatMessage[]> {
  const messages = threadMessages[threadId] ?? [];
  return paginate(messages);
}

export function addMessage(
  threadId: string,
  contentText: string,
): ApiEnvelope<ChatMessage> {
  const trimmed = contentText.trim();
  const userMessage: ChatMessage = {
    id: `msg_${Date.now()}`,
    role: "user",
    createdAtIso: new Date().toISOString(),
    contentText: trimmed,
  };
  threadMessages[threadId] = [...(threadMessages[threadId] ?? []), userMessage];
  return { ok: true, data: userMessage };
}

export function addAssistantMessage(
  threadId: string,
  contentText: string,
  options?: { runId?: string; meta?: Record<string, unknown> },
): ApiEnvelope<ChatMessage> {
  const message: ChatMessage = {
    id: `msg_${Date.now()}`,
    role: "os",
    createdAtIso: new Date().toISOString(),
    contentText,
    runId: options?.runId,
    meta: options?.meta,
  };
  threadMessages[threadId] = [...(threadMessages[threadId] ?? []), message];
  return { ok: true, data: message };
}
