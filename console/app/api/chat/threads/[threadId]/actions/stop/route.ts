import { NextResponse } from "next/server";

import { requireApiAccess } from "@/lib/apiAccess";

export async function POST() {
  const denied = await requireApiAccess();
  if (denied) return denied;

  return NextResponse.json(
    {
      ok: false,
      error: "The running Gateway does not expose task cancellation.",
    },
    { status: 501 },
  );
}
