import { Router } from "express";
import fetch from "node-fetch";
import { cfg } from "../config.js";
import { requireAuth } from "../lib/auth.js";

const r = Router();
const endpoints = ["propose", "apply", "revert"];

endpoints.forEach((name) => {
  r.post(`/v1/config/${name}`, requireAuth("ADMIN"), async (req, res) => {
    const upstream = await fetch(`${cfg.CONTROL_BASE}/v1/config/${name}`, {
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
});

r.post("/v1/router/policy/reload", requireAuth("ADMIN"), async (_req, res) => {
  const upstream = await fetch(`${cfg.CONTROL_BASE}/v1/router/policy/reload`, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${cfg.AUTH_TOKEN}`
    }
  });
  const text = await upstream.text();
  res.status(upstream.status)
    .type(upstream.headers.get("content-type") || "application/json")
    .send(text);
});

export default r;
