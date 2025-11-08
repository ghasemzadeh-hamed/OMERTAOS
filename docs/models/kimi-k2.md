# Kimi K2 (Instruct / Thinking)

## مسیرهای اتصال
- **API (پیشنهادی):** `K2_API_BASE_URL` + `K2_API_KEY` + `K2_*_MODEL_ID`
  - Moonshot API: base_url = https://api.moonshot.cn/v1
  - OpenRouter:   base_url = https://openrouter.ai/api/v1
- **لوکال:** یک سرور OpenAI-compatible روی `${K2_LOCAL_BASE_URL}` بالا بیاورید.

## انتخاب مدل
- **Instruct:** کاربری عمومی/کدنویسی، هزینه و تاخیر کمتر.
- **Thinking (Enterprise):** استدلال طولانی، ایجنت‌های چندابزاری، و کانتکست بسیار بلند.

## حداقل‌ها و نکات استقرار لوکال
- وزن‌ها در Hugging Face منتشر شده‌اند (K2-Instruct، K2-Thinking INT4).
- برای تجربه عادی لانگ‌کانتکست به چند GPU کلاس H200/H100 نیاز است.
- برای K2-Thinking از چک‌پوینت INT4 استفاده کنید تا تاخیر کاهش یابد.

## تست سریع
```bash
curl -s ${K2_API_BASE_URL}/chat/completions \
 -H "Authorization: Bearer ${K2_API_KEY}" \
 -H "Content-Type: application/json" \
 -d '{
   "model": "'"${K2_INSTRUCT_MODEL_ID}"'",
   "messages": [{"role":"user","content":"Hello K2!"}],
   "tools":[{"type":"function","function":{"name":"ping","parameters":{"type":"object"}}}]
 }'
```

منابع: Moonshot API docs (base_url، سازگاری OpenAI/Anthropic)، HF (چک‌پوینت‌ها)، و لیست مدل‌ها در OpenRouter.  [oai_citation:6‡platform.moonshot.cn](https://platform.moonshot.cn/docs/api/chat?utm_source=chatgpt.com)

---

# 8) نکات ادغام در کرنل/کنترل

- **Provider مشترک OpenAI-compatible** را reuse کن؛ فقط `base_url` و `model` و `api_key_env` از YAML خوانده می‌شود.  
- **Tool Calling** را روشن بگذار؛ K2 برای agentic طراحی شده. (Moonshot تأکید دارد.)  [oai_citation:7‡GitHub](https://github.com/MoonshotAI/Kimi-K2?utm_source=chatgpt.com)  
- در پروفایل‌های **User/Pro**، `enabled` برای Thinking را false بگذار و Instruct را پیش‌فرض کن؛ در **Enterprise**، rule بالا Thinking را ترجیح می‌دهد.

---
