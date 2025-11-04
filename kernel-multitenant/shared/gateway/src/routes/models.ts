import { Router } from "express";

const r = Router();

r.get("/v1/models", (_req, res) => {
  res.json({ items: [] });
});

export default r;
