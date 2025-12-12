import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/setup", "/health", "/healthz", "/dashboard/health", "/onboarding"];

const isStaticAsset = (pathname: string) =>
  pathname.startsWith("/_next") || pathname.startsWith("/assets") || pathname === "/favicon.ico";

export async function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const { pathname } = url;

  const isBypassed =
    pathname.startsWith("/api") ||
    isStaticAsset(pathname) ||
    PUBLIC_PATHS.includes(pathname);

  if (!isBypassed) {
    try {
      const cookieHeader = req.headers.get("cookie") ?? "";
      const bootstrapRes = await fetch(`${url.origin}/api/system/bootstrap`, {
        cache: "no-store",
        headers: cookieHeader ? { cookie: cookieHeader } : {},
      });

      if (bootstrapRes.ok) {
        const { setupDone, onboardingComplete, authenticated, setupUnknown } = await bootstrapRes.json();

        if (!setupDone && pathname !== "/setup") {
          url.pathname = "/setup";
          return NextResponse.redirect(url);
        }

        if (setupDone && pathname === "/setup") {
          url.pathname = authenticated ? "/" : "/login";
          return NextResponse.redirect(url);
        }

        if (setupDone && !authenticated && pathname !== "/login") {
          url.pathname = "/login";
          return NextResponse.redirect(url);
        }

        if (setupDone && authenticated && !onboardingComplete && pathname !== "/onboarding") {
          url.pathname = "/onboarding";
          return NextResponse.redirect(url);
        }

        if (setupDone && authenticated && pathname === "/login") {
          url.pathname = "/";
          return NextResponse.redirect(url);
        }

        if (setupUnknown) {
          url.pathname = "/unavailable";
          return NextResponse.rewrite(url);
        }
      } else {
        url.pathname = "/unavailable";
        return NextResponse.rewrite(url);
      }
    } catch (error) {
      console.error("[console] middleware bootstrap error", error);
      url.pathname = "/unavailable";
      return NextResponse.rewrite(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|assets).*)"],
};
