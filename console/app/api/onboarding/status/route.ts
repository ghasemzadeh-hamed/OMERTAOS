import { NextResponse } from "next/server";

const CONTROL_BASE =
  process.env.NEXT_PUBLIC_CONTROL_BASE ||
  process.env.CONTROL_BASE_URL ||
  "http://localhost:8000";

export async function GET() {
  try {
    const r = await fetch(`${CONTROL_BASE}/admin/onboarding/status`, {
      headers: { "content-type": "application/json" },
      cache: "no-store",
    });
    const data = await r.json();
    return NextResponse.json(data);
  } catch (e) {
    // اگر کنترل هنوز بالا نیامده باشد
    return NextResponse.json({ onboardingComplete: false });
  }
}
