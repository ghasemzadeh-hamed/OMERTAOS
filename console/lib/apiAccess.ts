import { NextResponse } from "next/server";

import { safeGetServerSession } from "@/lib/session";
import { ensureSetupState } from "@/lib/systemState";

type ApiRole = "USER" | "MANAGER" | "ADMIN";

export async function requireApiAccess(requiredRole?: ApiRole) {
  const session = await safeGetServerSession();
  if (!session?.user) {
    return NextResponse.json(
      { error: "Authentication required" },
      { status: 401 },
    );
  }

  const role = String(session.user.role ?? "USER").toUpperCase();
  if (requiredRole && role !== requiredRole) {
    return NextResponse.json(
      { error: "Insufficient permissions" },
      { status: 403 },
    );
  }

  return null;
}

export async function requireSetupOrAdminAccess() {
  try {
    if (!(await ensureSetupState())) return null;
  } catch {
    return NextResponse.json(
      { error: "Setup state unavailable" },
      { status: 503 },
    );
  }
  return requireApiAccess("ADMIN");
}
