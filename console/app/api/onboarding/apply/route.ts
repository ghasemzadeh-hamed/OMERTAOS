import { NextResponse } from "next/server";

const CONTROL_BASE = process.env.CONTROL_BASE_URL || "http://control:8000";

export async function POST() {
  const r = await fetch(`${CONTROL_BASE}/admin/onboarding/apply`, {
    method: "POST",
    headers: { "content-type": "application/json" },
  });
  const data = await r.json();
  return NextResponse.json(data);
}
