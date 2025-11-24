import "dotenv/config";

type CorsOrigin = boolean | string | string[];

function resolveCorsOrigin(): CorsOrigin {
  const raw = process.env.CORS_ORIGIN ?? "*";

  // In dev, "*" means "reflect whatever origin the browser sends".
  // This keeps local DX simple while still allowing explicit
  // allowlists in production via comma-separated values.
  if (raw === "*") {
    return true;
  }

  const parts = raw
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0);

  if (parts.length === 0) {
    // Fall back to permissive behaviour if misconfigured, so the
    // gateway still starts; operators can tighten this later.
    return true;
  }

  if (parts.length === 1) {
    return parts[0];
  }

  return parts;
}

export const cfg = {
  CONTROL_BASE: process.env.CONTROL_BASE ?? "http://127.0.0.1:8010",
  PORT: parseInt(process.env.PORT ?? "8000", 10),
  FEATURE_SEAL: (process.env.FEATURE_SEAL ?? "0") === "1",
  AUTH_TOKEN: process.env.AUTH_TOKEN ?? "",
  CORS_ORIGIN: resolveCorsOrigin()
};
