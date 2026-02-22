import { Request, Response, NextFunction } from "express";

export type Role = "ADMIN" | "USER";

export function requireAuth(role: Role = "ADMIN") {
  return (req: Request, res: Response, next: NextFunction) => {
    const header = req.headers.authorization || "";
    const token = header.startsWith("Bearer ") ? header.slice(7) : "";
    if (!token) {
      return res.status(401).json({ error: "missing token" });
    }
    const isAdmin = token.length > 0 && token === process.env.AUTH_TOKEN;
    if (role === "ADMIN" && !isAdmin) {
      return res.status(403).json({ error: "forbidden" });
    }
    (req as any).role = isAdmin ? "ADMIN" : "USER";
    next();
  };
}
