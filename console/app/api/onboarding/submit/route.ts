import { NextResponse } from "next/server";

const CONTROL_BASE =
  process.env.NEXT_PUBLIC_CONTROL_BASE ||
  process.env.CONTROL_BASE_URL ||
  "http://localhost:8000";

export async function POST(req: Request) {
  const body = await req.json();
  const r = await fetch(`${CONTROL_BASE}/admin/onboarding/submit`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await r.json();
  return NextResponse.json(data);
}
