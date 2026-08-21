import { NextResponse } from "next/server";
import { z } from "zod";

import { requireSetupOrAdminAccess } from "@/lib/apiAccess";
import { updateProfileState } from "@/lib/profile";

const payloadSchema = z.object({
  profile: z.enum(["user", "professional", "enterprise-vip"]),
  setupDone: z.boolean().optional(),
});

export async function POST(request: Request) {
  const denied = await requireSetupOrAdminAccess();
  if (denied) return denied;

  const json = await request.json().catch(() => ({}));
  const parsed = payloadSchema.safeParse(json);
  if (!parsed.success) {
    return NextResponse.json({ error: "Invalid profile" }, { status: 400 });
  }

  try {
    const data = await updateProfileState({
      profile: parsed.data.profile,
      setupDone: parsed.data.setupDone ?? true,
    });
    return NextResponse.json(data);
  } catch (error: any) {
    const status = typeof error?.status === "number" ? error.status : 502;
    const message = error?.message || "Unable to persist profile";
    const hint = error?.body ? JSON.stringify(error.body) : undefined;
    return NextResponse.json({ error: message, hint }, { status });
  }
}
