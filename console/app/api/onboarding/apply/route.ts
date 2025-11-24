import { NextResponse } from "next/server";

const CONTROL_BASE =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.CONTROL_BASE_URL ||
  "http://localhost:8080";

export async function POST() {
  const r = await fetch(`${CONTROL_BASE}/admin/onboarding/apply`, {
    method: "POST",
    headers: { "content-type": "application/json" },
  });
  const data = await r.json();
  return NextResponse.json(data);
}
