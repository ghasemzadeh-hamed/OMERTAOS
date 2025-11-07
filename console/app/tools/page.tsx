export default function ToolsIndexPage() {
  return (
    <div className="space-y-4 text-right">
      <h2 className="text-2xl font-semibold text-white/90">AION unified tools</h2>
      <p className="text-sm leading-6 text-white/70">
        Use the navigation on the left to open file management, network tuning, model lifecycle operations, and more. All sensitive actions are guarded by RBAC and environment-driven policies.
      </p>
      <p className="text-xs text-white/50">
        Tip: bookmark frequently used paths or rely on browser shortcuts for faster access. Every request flows through the Control API for auditability.
      </p>
    </div>
  );
}
