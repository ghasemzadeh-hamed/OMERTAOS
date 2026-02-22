import express from "express";
import cors from "cors";
import configRoutes from "./routes/config.js";
import modelsRoutes from "./routes/models.js";
import sealRoutes from "./routes/seal.js";
import { cfg } from "./config.js";

const app = express();
app.use(cors({ origin: cfg.CORS_ORIGIN, credentials: false }));
app.use(express.json({ limit: "4mb" }));

app.get("/healthz", (_req, res) => {
  res.json({ ok: true, seal: cfg.FEATURE_SEAL });
});

app.use(configRoutes);
app.use(modelsRoutes);
app.use(sealRoutes);

app.listen(cfg.PORT, () => {
  console.log(`GW up on :${cfg.PORT}`);
});
