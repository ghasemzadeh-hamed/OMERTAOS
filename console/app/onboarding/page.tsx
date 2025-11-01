"use client";
import { useState } from "react";

type Msg = { role: "bot" | "user"; text: string };
type Step = {
  id: string;
  prompt: string;
  fields: Array<{ key: string; label: string; placeholder?: string; type?: "text" | "password" | "number" }>;
  validate?: (values: Record<string, string>) => string | null;
};

const STEPS: Step[] = [
  {
    id: "welcome",
    prompt: "Welcome to AION-OS! Type 'ready' to begin the guided setup.",
    fields: [{ key: "ready", label: "Type ready to continue", placeholder: "ready", type: "text" }],
    validate: (v) => (v.ready?.trim()?.toLowerCase() === "ready" ? null : "Please type ready to continue."),
  },
  {
    id: "admin",
    prompt: "Admin setup: provide the initial console credentials.",
    fields: [
      { key: "email", label: "Email or username", type: "text" },
      { key: "password", label: "Password", type: "password" },
    ],
  },
  {
    id: "models",
    prompt: "Model routing: choose the default provider (openai, gemini, local).",
    fields: [
      { key: "provider", label: "Provider", placeholder: "openai", type: "text" },
      { key: "apiKey", label: "API Key (if required)", type: "password" },
      { key: "defaultModel", label: "Default model", placeholder: "gpt-4o-mini", type: "text" },
    ],
  },
  {
    id: "gateway",
    prompt: "Gateway configuration: port and optional API key.",
    fields: [
      { key: "port", label: "Gateway port", placeholder: "8080", type: "number" },
      { key: "apiKey", label: "API Key (leave blank to auto-generate)", type: "text" },
    ],
  },
  {
    id: "finalize",
    prompt: "Almost done! Type 'confirm' to apply the configuration.",
    fields: [{ key: "confirm", label: "Type confirm to finish", placeholder: "confirm", type: "text" }],
    validate: (v) => (v.confirm?.trim()?.toLowerCase() === "confirm" ? null : "Please type confirm to finish."),
  },
];

export default function OnboardingPage() {
  const [messages, setMessages] = useState<Msg[]>([{ role: "bot", text: STEPS[0].prompt }]);
  const [stepIdx, setStepIdx] = useState(0);
  const step = STEPS[stepIdx];
  const [values, setValues] = useState<Record<string, string>>({});

  const sendToBackend = async (payload: any) => {
    const res = await fetch("/api/onboarding/submit", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    return res.json();
  };

  const applyChanges = async () => {
    await fetch("/api/onboarding/apply", { method: "POST" });
  };

  const onSubmit = async (e: any) => {
    e.preventDefault();
    const userText = Object.entries(values)
      .map(([k, v]) => `${k}: ${v}`)
      .join(" | ");
    setMessages((m) => [...m, { role: "user", text: userText || "-" }]);

    if (step.validate) {
      const err = step.validate(values);
      if (err) {
        setMessages((m) => [...m, { role: "bot", text: err }]);
        return;
      }
    }

    await sendToBackend({ stepId: step.id, answers: values });
    setValues({});

    if (step.id === "finalize") {
      setMessages((m) => [...m, { role: "bot", text: "Applying configuration..." }]);
      await applyChanges();
      setMessages((m) => [...m, { role: "bot", text: "Setup complete! Redirecting to the console." }]);
      window.location.href = "/";
      return;
    }

    const next = stepIdx + 1;
    setStepIdx(next);
    setMessages((m) => [...m, { role: "bot", text: STEPS[next].prompt }]);
  };

  return (
    <div className="min-h-screen p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">AION-OS Guided Onboarding</h1>
      <div className="border rounded-xl p-4 space-y-3 bg-white/60 backdrop-blur">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === "bot" ? "text-right" : "text-left"}>
            <div className={`inline-block px-3 py-2 rounded-2xl ${msg.role === "bot" ? "bg-gray-100" : "bg-blue-100"}`}>
              {msg.text}
            </div>
          </div>
        ))}
        <form onSubmit={onSubmit} className="space-y-3">
          {step.fields.map((f) => (
            <div key={f.key} className="flex flex-col">
              <label className="text-sm mb-1">{f.label}</label>
              <input
                type={f.type || "text"}
                placeholder={f.placeholder || ""}
                value={values[f.key] || ""}
                onChange={(e) => setValues((v) => ({ ...v, [f.key]: e.target.value }))}
                className="border rounded-lg px-3 py-2"
              />
            </div>
          ))}
          <button className="px-4 py-2 rounded-xl border">Continue</button>
        </form>
      </div>
    </div>
  );
}
