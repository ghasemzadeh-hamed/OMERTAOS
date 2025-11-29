import { NextResponse } from "next/server";

const GATEWAY_BASE =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.GATEWAY_BASE_URL ||
  "http://localhost:3000";

export async function POST() {
    const r = await fetch(`${GATEWAY_BASE}/admin/onboarding/apply`, {
    method: "POST",
    headers: { "content-type": "application/json" },
  });
  const data = await r.json();
  return NextResponse.json(data);
}
