import { NextResponse } from "next/server";

const GATEWAY_BASE =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.GATEWAY_BASE_URL ||
  "http://localhost:3000";

export async function GET() {
  try {
    const r = await fetch(`${GATEWAY_BASE}/admin/onboarding/status`, {
      headers: { "content-type": "application/json" },
      cache: "no-store",
    });
    const data = await r.json();
    return NextResponse.json(data);
  } catch (e) {
    // Fall back to incomplete onboarding state when control API is unreachable
    return NextResponse.json({ onboardingComplete: false });
  }
}
