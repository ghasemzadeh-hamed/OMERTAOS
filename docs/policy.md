# Policy Engine

Policies are enforced during AI routing via heuristics:

- **Latency**: Tasks with priority ≥4 execute locally to respect latency budgets.
- **Budget**: Without an `OPENAI_API_KEY`, external API calls are skipped, preventing unexpected billing.
- **Privacy**: Sensitive intents (matching `embedding` or `vector`) use the hybrid path to keep embeddings local while augmenting with external context.
- Extend by persisting policies in the `AgentManifest` table and merging them inside `AIRouter.decide`.
