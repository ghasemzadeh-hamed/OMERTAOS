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
    prompt:
      "سلام! من دستیار راه‌انداز AION-OS هستم. برای شروع بنویس «بله».",
    fields: [{ key: "ready", label: "بگو بله تا شروع کنیم", placeholder: "بله", type: "text" }],
    validate: (v) => (v.ready?.trim()?.toLowerCase() === "بله" ? null : "لطفاً بنویس بله"),
  },
  {
    id: "admin",
    prompt: "یک ادمین بسازیم: ایمیل و گذرواژهٔ امن را وارد کن.",
    fields: [
      { key: "email", label: "ایمیل ادمین", type: "text" },
      { key: "password", label: "گذرواژه", type: "password" },
    ],
  },
  {
    id: "models",
    prompt: "ارائه‌دهندهٔ مدل پیش‌فرض؟ (openai, gemini, local)",
    fields: [
      { key: "provider", label: "Provider", placeholder: "openai", type: "text" },
      { key: "apiKey", label: "API Key (در صورت نیاز)", type: "password" },
      { key: "defaultModel", label: "نام مدل پیش‌فرض", placeholder: "gpt-4o-mini", type: "text" },
    ],
  },
  {
    id: "gateway",
    prompt: "تنظیمات Gateway: پورت و API Key",
    fields: [
      { key: "port", label: "پورت", placeholder: "8080", type: "number" },
      { key: "apiKey", label: "API Key (اگر خالی بماند تولید می‌شود)", type: "text" },
    ],
  },
  {
    id: "finalize",
    prompt: "اعمال تنظیمات و ری‌لود سرویس‌ها انجام شود؟ (بنویس بله)",
    fields: [{ key: "confirm", label: "تأیید", placeholder: "بله", type: "text" }],
    validate: (v) => (v.confirm?.trim()?.toLowerCase() === "بله" ? null : "برای ادامه بنویس بله"),
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
    setMessages((m) => [...m, { role: "user", text: userText || "—" }]);

    if (step.validate) {
      const err = step.validate(values);
      if (err) {
        setMessages((m) => [...m, { role: "bot", text: `❗ ${err}` }]);
        return;
      }
    }

    await sendToBackend({ stepId: step.id, answers: values });
    setValues({});

    if (step.id === "finalize") {
      setMessages((m) => [...m, { role: "bot", text: "در حال اعمال تنظیمات و ری‌لود سرویس‌ها..." }]);
      await applyChanges();
      setMessages((m) => [...m, { role: "bot", text: "تمام شد! حالا داشبورد آماده است." }]);
      window.location.href = "/";
      return;
    }

    const next = stepIdx + 1;
    setStepIdx(next);
    setMessages((m) => [...m, { role: "bot", text: STEPS[next].prompt }]);
  };

  return (
    <div className="min-h-screen p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">AION-OS • نصب تعاملی</h1>
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
          <button className="px-4 py-2 rounded-xl border">ارسال</button>
        </form>
      </div>
    </div>
  );
}
