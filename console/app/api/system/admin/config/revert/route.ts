import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function POST(request: Request) {
  const denied = await requireApiAccess("ADMIN");
  if (denied) return denied;

  try {
    const payload = await request.json().catch(() => ({}));
    const data = await gatewayFetch("/v1/config/revert", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload ?? {}),
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Unable to revert config change", details: error?.body },
      { status },
    );
  }
}
