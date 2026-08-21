"use client";

import { useEffect, useMemo, useState } from "react";

import { ChatComposer } from "@/components/os-chat/ChatComposer";
import { ChatMessageList } from "@/components/os-chat/ChatMessageList";
import { ChatThreadList } from "@/components/os-chat/ChatThreadList";
import { Button } from "@/components/ui/button";
import {
  createChatThread,
  fetchMessages,
  fetchThreads,
  sendMessage,
} from "@/lib/osChatClient";
import { ChatMessage, ChatThread } from "@/types/os-chat";

type LocalMessage = ChatMessage & { optimistic?: boolean };

export function OsChatView({ initialThreadId }: { initialThreadId?: string }) {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [selectedThreadId, setSelectedThreadId] = useState<string | undefined>(
    initialThreadId,
  );
  const [composerValue, setComposerValue] = useState("");
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchThreads()
      .then((data) => {
        setThreads(data);
        setSelectedThreadId(
          (current) => current ?? initialThreadId ?? data[0]?.id,
        );
      })
      .catch((err) => setError(err.message));
  }, [initialThreadId]);

  useEffect(() => {
    if (!selectedThreadId) return;
    setLoadingMessages(true);
    fetchMessages(selectedThreadId)
      .then((data) => setMessages(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoadingMessages(false));
  }, [selectedThreadId]);

  const activeThread = useMemo(
    () => threads.find((thread) => thread.id === selectedThreadId),
    [threads, selectedThreadId],
  );

  const handleSend = async () => {
    if (!selectedThreadId || !composerValue.trim()) return;
    const optimistic: LocalMessage = {
      id: `pending-${Date.now()}`,
      role: "user",
      createdAtIso: new Date().toISOString(),
      contentText: composerValue,
      optimistic: true,
    };
    setMessages((prev) => [...prev, optimistic]);
    setComposerValue("");
    setSending(true);
    setError(null);
    try {
      await sendMessage(selectedThreadId, optimistic.contentText);
      const refreshed = await fetchMessages(selectedThreadId);
      setMessages(refreshed);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to send message";
      setError(message);
      setMessages((prev) => prev.filter((msg) => msg.id !== optimistic.id));
    } finally {
      setSending(false);
    }
  };

  const handleCreateThread = async (title: string) => {
    try {
      const created = await createChatThread(title);
      const updatedThreads = await fetchThreads();
      setThreads(updatedThreads);
      setSelectedThreadId(created.id);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to create thread";
      setError(message);
    }
  };

  const refreshMessages = async () => {
    if (!selectedThreadId) return;
    try {
      const data = await fetchMessages(selectedThreadId);
      setMessages(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to refresh messages";
      setError(message);
    }
  };

  return (
    <div className="flex h-full min-h-[75vh] flex-col rounded-lg border border-slate-200 bg-slate-50 shadow-sm">
      <div className="flex flex-1">
        <div className="w-80 min-w-[18rem]">
          <ChatThreadList
            threads={threads}
            selectedId={selectedThreadId}
            onSelect={(id) => setSelectedThreadId(id)}
            onCreate={handleCreateThread}
          />
        </div>
        <div className="flex flex-1 flex-col">
          <div className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
            <div>
              <p className="text-xs text-slate-500">OS Chat</p>
              <h1 className="text-lg font-semibold text-slate-800">
                {activeThread?.title ?? "Select a thread"}
              </h1>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Button variant="outline" size="sm" onClick={refreshMessages}>
                Refresh
              </Button>
            </div>
          </div>
          {error && (
            <div
              className="border-b border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700"
              role="alert"
            >
              {error}
            </div>
          )}
          {loadingMessages ? (
            <div className="flex flex-1 items-center justify-center text-sm text-slate-500">
              Loading messages...
            </div>
          ) : (
            <ChatMessageList messages={messages} />
          )}
          <ChatComposer
            value={composerValue}
            onChange={setComposerValue}
            onSend={handleSend}
            disabled={!selectedThreadId || sending}
            showStop={false}
          />
        </div>
      </div>
    </div>
  );
}
