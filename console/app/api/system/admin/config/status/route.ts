import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function GET() {
  const denied = await requireApiAccess("ADMIN");
  if (denied) return denied;

  try {
    const data = await gatewayFetch("/v1/config/status", { method: "GET" });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Unable to read config status", details: error?.body },
      { status },
    );
  }
}
