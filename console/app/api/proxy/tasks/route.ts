import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function GET() {
  const denied = await requireApiAccess();
  if (denied) return denied;

  return NextResponse.json(
    { error: "Task listing is not supported by the Gateway." },
    { status: 405 },
  );
}

export async function POST(request: Request) {
  const denied = await requireApiAccess();
  if (denied) return denied;

  try {
    const body = await request.json();
    const data = await gatewayFetch("/v1/tasks", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch (error) {
    const status =
      typeof (error as { status?: unknown }).status === "number"
        ? (error as { status: number }).status
        : 502;
    return NextResponse.json({ error: "Unable to submit task" }, { status });
  }
}
