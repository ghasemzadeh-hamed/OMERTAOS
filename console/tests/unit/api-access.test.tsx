import { beforeEach, describe, expect, it, vi } from "vitest";

const safeGetServerSession = vi.fn();

vi.mock("@/lib/session", () => ({ safeGetServerSession }));
vi.mock("@/lib/systemState", () => ({ ensureSetupState: vi.fn() }));

describe("requireApiAccess", () => {
  beforeEach(() => {
    vi.resetModules();
    safeGetServerSession.mockReset();
  });

  it("rejects unauthenticated API requests", async () => {
    safeGetServerSession.mockResolvedValue(null);
    const { requireApiAccess } = await import("@/lib/apiAccess");

    const response = await requireApiAccess();

    expect(response?.status).toBe(401);
  });

  it("rejects non-admin users from admin APIs", async () => {
    safeGetServerSession.mockResolvedValue({ user: { role: "MANAGER" } });
    const { requireApiAccess } = await import("@/lib/apiAccess");

    const response = await requireApiAccess("ADMIN");

    expect(response?.status).toBe(403);
  });

  it("allows an authenticated admin", async () => {
    safeGetServerSession.mockResolvedValue({ user: { role: "ADMIN" } });
    const { requireApiAccess } = await import("@/lib/apiAccess");

    await expect(requireApiAccess("ADMIN")).resolves.toBeNull();
  });
});
