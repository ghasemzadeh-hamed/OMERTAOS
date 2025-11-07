import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const { pathname } = url;

  const isBypassed =
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/assets") ||
    pathname === "/favicon.ico";

  if (!isBypassed) {
    try {
      const profileRes = await fetch(`${url.origin}/api/setup/profile`, { cache: "no-store" });
      const profile = await profileRes.json();
      const setupDone = Boolean(profile?.setupDone);
      if (!setupDone && pathname !== "/setup") {
        url.pathname = "/setup";
        return NextResponse.redirect(url);
      }
      if (setupDone && pathname === "/setup") {
        url.pathname = "/";
        return NextResponse.redirect(url);
      }
    } catch (error) {
      console.error("Profile middleware error", error);
    }
  }

  if (pathname === "/") {
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
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
