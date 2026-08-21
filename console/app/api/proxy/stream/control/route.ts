import { requireApiAccess } from "@/lib/apiAccess";

export async function GET() {
  const denied = await requireApiAccess("ADMIN");
  if (denied) return denied;

  return new Response(
    "The running Gateway does not expose a Control log stream.",
    { status: 501 },
  );
}
