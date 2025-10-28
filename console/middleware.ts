import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  if (url.pathname === "/") {
    try {
      const res = await fetch(`${url.origin}/api/onboarding/status`, { cache: "no-store" });
      const data = await res.json();
      if (!data?.onboardingComplete) {
        url.pathname = "/onboarding";
        return NextResponse.redirect(url);
      }
    } catch {
      url.pathname = "/onboarding";
      return NextResponse.redirect(url);
    }
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/"],
};
