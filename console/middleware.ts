import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const { pathname } = url;

  const isBypassed =
    pathname.startsWith("/api") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/assets") ||
    pathname === "/health" ||
    pathname === "/healthz" ||
    pathname === "/dashboard/health" ||
    pathname === "/favicon.ico" ||
    pathname.startsWith("/wizard") ||
    pathname.startsWith("/api/auth");

  if (!isBypassed) {
    try {
      const cookieHeader = req.headers.get("cookie") ?? "";
      const profileRes = await fetch(`${url.origin}/api/setup/profile`, {
        cache: "no-store",
        headers: cookieHeader ? { cookie: cookieHeader } : {},
      });
      if (profileRes.ok) {
        const profile = await profileRes.json();
        const setupDone = Boolean(profile?.setupDone);
        if (!setupDone && pathname !== "/setup") {
          url.pathname = "/setup";
          return NextResponse.redirect(url);
        }
        if (setupDone) {
          if (pathname === "/setup") {
            url.pathname = "/login";
            return NextResponse.redirect(url);
          }

          const sessionRes = await fetch(`${url.origin}/api/auth/session`, {
            cache: "no-store",
            headers: cookieHeader ? { cookie: cookieHeader } : {},
          });
          const sessionOk = sessionRes.ok ? await sessionRes.json() : null;
          const isAuthenticated = Boolean(sessionOk?.user);

          if (!isAuthenticated && (pathname === "/" || pathname.startsWith("/console"))) {
            url.pathname = "/login";
            return NextResponse.redirect(url);
          }

          if (isAuthenticated && pathname === "/login") {
            url.pathname = "/";
            return NextResponse.redirect(url);
          }
        }
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
