import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";

const GATEWAY_BASE =
  process.env.NEXT_PUBLIC_GATEWAY_URL ||
  process.env.GATEWAY_BASE_URL ||
  "http://localhost:3000";

export async function POST() {
  const denied = await requireApiAccess("ADMIN");
  if (denied) return denied;

  const r = await fetch(`${GATEWAY_BASE}/admin/onboarding/apply`, {
    method: "POST",
    headers: { "content-type": "application/json" },
  });
  const data = await r.json();
  return NextResponse.json(data);
}
