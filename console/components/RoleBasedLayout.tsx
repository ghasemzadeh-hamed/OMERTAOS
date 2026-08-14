import React from "react";
import Link from "next/link";
import { useUIStore } from "../state/ui.store";

const RoleBasedLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const role = useUIStore((state) => state.role);
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">AION-OS Console</h1>
            <p className="text-xs text-slate-500">Active Role: {role}</p>
          </div>
          <nav className="flex items-center gap-4 text-sm text-slate-700">
            <Link href="/" className="hover:text-slate-900">
              Dashboard
            </Link>
            <Link href="/governance" className="hover:text-slate-900">
              Governance
            </Link>
            <Link href="/workflows" className="hover:text-slate-900">
              Workflows
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
};

export default RoleBasedLayout;
