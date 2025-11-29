import { NextResponse } from "next/server";

const GATEWAY_BASE =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.GATEWAY_BASE_URL ||
  "http://localhost:3000";

export async function POST(req: Request) {
  const body = await req.json();
    const r = await fetch(`${GATEWAY_BASE}/admin/onboarding/submit`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await r.json();
  return NextResponse.json(data);
}
