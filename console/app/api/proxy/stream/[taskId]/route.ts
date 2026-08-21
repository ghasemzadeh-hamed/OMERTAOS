import { NextRequest } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { buildGatewayHeaders, resolveGatewayBase } from "@/lib/gatewayClient";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ taskId: string }> },
) {
  const denied = await requireApiAccess();
  if (denied) return denied;

  const { taskId } = await params;
  if (!/^[a-zA-Z0-9-]{1,128}$/.test(taskId)) {
    return new Response("Invalid task id", { status: 400 });
  }
  const response = await fetch(
    `${resolveGatewayBase()}/v1/stream/${encodeURIComponent(taskId)}`,
    {
      headers: await buildGatewayHeaders(request.headers),
      cache: "no-store",
    },
  );
  if (!response.ok || !response.body) {
    return new Response(await response.text(), { status: response.status });
  }
  const stream = response.body;
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
