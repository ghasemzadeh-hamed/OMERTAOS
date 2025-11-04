import "dotenv/config";

export const cfg = {
  CONTROL_BASE: process.env.CONTROL_BASE ?? "http://127.0.0.1:8010",
  PORT: parseInt(process.env.PORT ?? "8000", 10),
  FEATURE_SEAL: (process.env.FEATURE_SEAL ?? "0") === "1",
  AUTH_TOKEN: process.env.AUTH_TOKEN ?? "",
  CORS_ORIGIN: process.env.CORS_ORIGIN ?? "*"
};
