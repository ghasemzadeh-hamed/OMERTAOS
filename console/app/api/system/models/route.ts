import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function GET() {
  const denied = await requireApiAccess();
  if (denied) return denied;

  try {
    const data = await gatewayFetch("/v1/models", { method: "GET" });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Unable to load models", details: error?.body },
      { status },
    );
  }
}
