import React, { useState } from "react";
import { createWebSocket } from "../utils/websocket";

const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useState<{ id: number; role: string; content: string }[]>([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) {
      return;
    }
    const socket = createWebSocket();
    const nextMessage = { id: Date.now(), role: "user", content: input };
    setMessages((prev) => [...prev, nextMessage]);
    socket.send(JSON.stringify({ type: "personal_chat", payload: input }));
    setInput("");
  };

  return (
    <div className="flex h-64 flex-col rounded border border-slate-200 bg-white">
      <div className="flex-1 space-y-2 overflow-y-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className="text-sm">
            <span className="font-semibold text-slate-700">{message.role}:</span> {message.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2 border-t border-slate-200 p-3">
        <input
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask your personal agent"
        />
        <button className="rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
