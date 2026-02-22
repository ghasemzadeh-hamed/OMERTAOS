import { Router } from "express";
import fetch from "node-fetch";
import { cfg } from "../config.js";
import { requireAuth } from "../lib/auth.js";
import { sseHeaders } from "../lib/sse.js";

const r = Router();

r.post("/v1/seal/jobs", requireAuth("ADMIN"), async (req, res) => {
  if (!cfg.FEATURE_SEAL) {
    return res.status(403).json({ error: "SEAL disabled" });
  }
  const upstream = await fetch(`${cfg.CONTROL_BASE}/v1/seal/jobs`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "authorization": `Bearer ${cfg.AUTH_TOKEN}`
    },
    body: JSON.stringify(req.body || {})
  });
  const text = await upstream.text();
  res.status(upstream.status)
    .type(upstream.headers.get("content-type") || "application/json")
    .send(text);
});

r.get("/v1/seal/jobs/:id/status", requireAuth("ADMIN"), async (req, res) => {
  const upstream = await fetch(`${cfg.CONTROL_BASE}/v1/seal/jobs/${req.params.id}/status`, {
    headers: {
      "authorization": `Bearer ${cfg.AUTH_TOKEN}`
    }
  });
  const text = await upstream.text();
  res.status(upstream.status)
    .type(upstream.headers.get("content-type") || "application/json")
    .send(text);
});

r.get("/v1/seal/streams/:id", requireAuth("ADMIN"), async (req, res) => {
  if (!cfg.FEATURE_SEAL) {
    return res.status(403).json({ error: "SEAL disabled" });
  }
  sseHeaders(res);
  const upstream = await fetch(`${cfg.CONTROL_BASE}/v1/seal/streams/${req.params.id}`, {
    headers: {
      accept: "text/event-stream",
      authorization: `Bearer ${cfg.AUTH_TOKEN}`
    }
  });
  upstream.body?.pipe(res);
});

export default r;
