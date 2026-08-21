import { NextRequest, NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";
import { createThread, listThreads } from "@/lib/osChatStore";

export async function GET() {
  const denied = await requireApiAccess();
  if (denied) return denied;

  const result = listThreads();
  return NextResponse.json(result);
}

export async function POST(request: NextRequest) {
  const denied = await requireApiAccess();
  if (denied) return denied;

  const body = await request.json().catch(() => ({}));
  const title = typeof body?.title === "string" ? body.title : "";
  const result = createThread(title);
  return NextResponse.json(result, { status: result.ok ? 200 : 400 });
}
