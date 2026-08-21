import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ taskId: string }> },
) {
  const denied = await requireApiAccess();
  if (denied) return denied;

  const { taskId } = await params;
  if (!/^[a-zA-Z0-9-]{1,128}$/.test(taskId)) {
    return NextResponse.json({ error: "Invalid task id" }, { status: 400 });
  }
  try {
    const data = await gatewayFetch(`/v1/tasks/${encodeURIComponent(taskId)}`, {
      method: "GET",
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Unable to load task", details: error?.body },
      { status },
    );
  }
}
