import { NextRequest, NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { gatewayFetch } from "@/lib/gatewayClient";

type RouteContext = { params: Promise<{ segments?: string[] }> };

const actions = new Set(["enable", "disable", "test", "set-default"]);

function gatewayPath(segments: string[], method: string) {
  if (segments.length === 0 && (method === "GET" || method === "POST")) {
    return "/v1/network/proxies";
  }
  if (
    segments.length === 1 &&
    /^\d+$/.test(segments[0]) &&
    ["GET", "PUT", "DELETE"].includes(method)
  ) {
    return `/v1/network/proxies/${segments[0]}`;
  }
  if (
    segments.length === 2 &&
    /^\d+$/.test(segments[0]) &&
    actions.has(segments[1]) &&
    method === "POST"
  ) {
    return `/v1/network/proxies/${segments[0]}/${segments[1]}`;
  }
  return null;
}

async function proxy(request: NextRequest, context: RouteContext) {
  const denied = await requireApiAccess("ADMIN");
  if (denied) return denied;

  const { segments = [] } = await context.params;
  const path = gatewayPath(segments, request.method);
  if (!path) {
    return NextResponse.json(
      { error: "Unsupported proxy profile operation" },
      { status: 405 },
    );
  }

  const body = ["POST", "PUT"].includes(request.method)
    ? JSON.stringify(await request.json().catch(() => ({})))
    : undefined;

  try {
    const data = await gatewayFetch(path, {
      method: request.method,
      headers: body ? { "content-type": "application/json" } : undefined,
      body,
    });
    return NextResponse.json(data || {});
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    return NextResponse.json(
      { error: "Network proxy request failed", details: error?.body },
      { status },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;
