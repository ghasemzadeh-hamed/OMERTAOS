"use client";

import { ApiEnvelope, ChatMessage, ChatThread } from "@/types/os-chat";

async function request<T>(
  url: string,
  init?: RequestInit,
): Promise<ApiEnvelope<T>> {
  const res = await fetch(url, init);
  const data = (await res
    .json()
    .catch(() => ({ ok: false, data: null }))) as ApiEnvelope<T>;
  if (!data.ok) {
    const message = data.error?.message ?? "Request failed";
    throw new Error(message);
  }
  return data;
}

export async function fetchThreads(): Promise<ChatThread[]> {
  const { data } = await request<ChatThread[]>("/api/chat/threads");
  return data;
}

export async function createChatThread(title: string): Promise<ChatThread> {
  const { data } = await request<ChatThread>("/api/chat/threads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return data;
}

export async function fetchMessages(threadId: string): Promise<ChatMessage[]> {
  const { data } = await request<ChatMessage[]>(
    `/api/chat/threads/${threadId}/messages`,
  );
  return data;
}

export async function sendMessage(
  threadId: string,
  contentText: string,
): Promise<ChatMessage> {
  const { data } = await request<ChatMessage>(
    `/api/chat/threads/${threadId}/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contentText }),
    },
  );
  return data;
}
