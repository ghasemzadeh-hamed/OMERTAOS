# Kimi K2 (Instruct / Thinking)

## &#x645;&#x633;&#x6cc;&#x631;&#x647;&#x627;&#x6cc; &#x627;&#x62a;&#x635;&#x627;&#x644;

- **API (&#x67e;&#x6cc;&#x634;&#x646;&#x647;&#x627;&#x62f;&#x6cc;):** `K2_API_BASE_URL` + `K2_API_KEY` + `K2_*_MODEL_ID`
  - Moonshot API: base_url = https://api.moonshot.cn/v1
  - OpenRouter: base_url = https://openrouter.ai/api/v1
- **&#x644;&#x648;&#x6a9;&#x627;&#x644;:** &#x6cc;&#x6a9; &#x633;&#x631;&#x648;&#x631; OpenAI-compatible &#x631;&#x648;&#x6cc; `${K2_LOCAL_BASE_URL}` &#x628;&#x627;&#x644;&#x627; &#x628;&#x6cc;&#x627;&#x648;&#x631;&#x6cc;&#x62f;.

## &#x627;&#x646;&#x62a;&#x62e;&#x627;&#x628; &#x645;&#x62f;&#x644;

- **Instruct:** &#x6a9;&#x627;&#x631;&#x628;&#x631;&#x6cc; &#x639;&#x645;&#x648;&#x645;&#x6cc;/&#x6a9;&#x62f;&#x646;&#x648;&#x6cc;&#x633;&#x6cc;&#x60c; &#x647;&#x632;&#x6cc;&#x646;&#x647; &#x648; &#x62a;&#x627;&#x62e;&#x6cc;&#x631; &#x6a9;&#x645;&#x62a;&#x631;.
- **Thinking (Enterprise):** &#x627;&#x633;&#x62a;&#x62f;&#x644;&#x627;&#x644; &#x637;&#x648;&#x644;&#x627;&#x646;&#x6cc;&#x60c; &#x627;&#x6cc;&#x62c;&#x646;&#x62a;&#x200c;&#x647;&#x627;&#x6cc; &#x686;&#x646;&#x62f;&#x627;&#x628;&#x632;&#x627;&#x631;&#x6cc;&#x60c; &#x648; &#x6a9;&#x627;&#x646;&#x62a;&#x6a9;&#x633;&#x62a; &#x628;&#x633;&#x6cc;&#x627;&#x631; &#x628;&#x644;&#x646;&#x62f;.

## &#x62d;&#x62f;&#x627;&#x642;&#x644;&#x200c;&#x647;&#x627; &#x648; &#x646;&#x6a9;&#x627;&#x62a; &#x627;&#x633;&#x62a;&#x642;&#x631;&#x627;&#x631; &#x644;&#x648;&#x6a9;&#x627;&#x644;

- &#x648;&#x632;&#x646;&#x200c;&#x647;&#x627; &#x62f;&#x631; Hugging Face &#x645;&#x646;&#x62a;&#x634;&#x631; &#x634;&#x62f;&#x647;&#x200c;&#x627;&#x646;&#x62f; (K2-Instruct&#x60c; K2-Thinking INT4).
- &#x628;&#x631;&#x627;&#x6cc; &#x62a;&#x62c;&#x631;&#x628;&#x647; &#x639;&#x627;&#x62f;&#x6cc; &#x644;&#x627;&#x646;&#x6af;&#x200c;&#x6a9;&#x627;&#x646;&#x62a;&#x6a9;&#x633;&#x62a; &#x628;&#x647; &#x686;&#x646;&#x62f; GPU &#x6a9;&#x644;&#x627;&#x633; H200/H100 &#x646;&#x6cc;&#x627;&#x632; &#x627;&#x633;&#x62a;.
- &#x628;&#x631;&#x627;&#x6cc; K2-Thinking &#x627;&#x632; &#x686;&#x6a9;&#x200c;&#x67e;&#x648;&#x6cc;&#x646;&#x62a; INT4 &#x627;&#x633;&#x62a;&#x641;&#x627;&#x62f;&#x647; &#x6a9;&#x646;&#x6cc;&#x62f; &#x62a;&#x627; &#x62a;&#x627;&#x62e;&#x6cc;&#x631; &#x6a9;&#x627;&#x647;&#x634; &#x6cc;&#x627;&#x628;&#x62f;.

## &#x62a;&#x633;&#x62a; &#x633;&#x631;&#x6cc;&#x639;

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

&#x645;&#x646;&#x627;&#x628;&#x639;: Moonshot API docs (base_url&#x60c; &#x633;&#x627;&#x632;&#x6af;&#x627;&#x631;&#x6cc; OpenAI/Anthropic)&#x60c; HF (&#x686;&#x6a9;&#x200c;&#x67e;&#x648;&#x6cc;&#x646;&#x62a;&#x200c;&#x647;&#x627;)&#x60c; &#x648; &#x644;&#x6cc;&#x633;&#x62a; &#x645;&#x62f;&#x644;&#x200c;&#x647;&#x627; &#x62f;&#x631; OpenRouter. [oai_citation:6&#x2021;platform.moonshot.cn](https://platform.moonshot.cn/docs/api/chat?utm_source=chatgpt.com)

---

# 8) &#x646;&#x6a9;&#x627;&#x62a; &#x627;&#x62f;&#x63a;&#x627;&#x645; &#x62f;&#x631; &#x6a9;&#x631;&#x646;&#x644;/&#x6a9;&#x646;&#x62a;&#x631;&#x644;

- **Provider &#x645;&#x634;&#x62a;&#x631;&#x6a9; OpenAI-compatible** &#x631;&#x627; reuse &#x6a9;&#x646;&#x61b; &#x641;&#x642;&#x637; `base_url` &#x648; `model` &#x648; `api_key_env` &#x627;&#x632; YAML &#x62e;&#x648;&#x627;&#x646;&#x62f;&#x647; &#x645;&#x6cc;&#x200c;&#x634;&#x648;&#x62f;.
- **Tool Calling** &#x631;&#x627; &#x631;&#x648;&#x634;&#x646; &#x628;&#x6af;&#x630;&#x627;&#x631;&#x61b; K2 &#x628;&#x631;&#x627;&#x6cc; agentic &#x637;&#x631;&#x627;&#x62d;&#x6cc; &#x634;&#x62f;&#x647;. (Moonshot &#x62a;&#x623;&#x6a9;&#x6cc;&#x62f; &#x62f;&#x627;&#x631;&#x62f;.) [oai_citation:7&#x2021;GitHub](https://github.com/MoonshotAI/Kimi-K2?utm_source=chatgpt.com)
- &#x62f;&#x631; &#x67e;&#x631;&#x648;&#x641;&#x627;&#x6cc;&#x644;&#x200c;&#x647;&#x627;&#x6cc; **User/Pro**&#x60c; `enabled` &#x628;&#x631;&#x627;&#x6cc; Thinking &#x631;&#x627; false &#x628;&#x6af;&#x630;&#x627;&#x631; &#x648; Instruct &#x631;&#x627; &#x67e;&#x6cc;&#x634;&#x200c;&#x641;&#x631;&#x636; &#x6a9;&#x646;&#x61b; &#x62f;&#x631; **Enterprise**&#x60c; rule &#x628;&#x627;&#x644;&#x627; Thinking &#x631;&#x627; &#x62a;&#x631;&#x62c;&#x6cc;&#x62d; &#x645;&#x6cc;&#x200c;&#x62f;&#x647;&#x62f;.

---
