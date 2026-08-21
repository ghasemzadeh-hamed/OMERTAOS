import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function GET(
  _: Request,
  context: { params: Promise<{ id: string }> },
) {
  const denied = await requireApiAccess();
  if (denied) return denied;

  try {
    const { id } = await context.params;
    const data = await gatewayFetch(`/api/agents/${encodeURIComponent(id)}`, {
      method: "GET",
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Unable to load agent", details: error?.body },
      { status },
    );
  }
}
