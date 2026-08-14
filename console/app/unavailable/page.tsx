export default function UnavailablePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
      <div className="space-y-3 text-center">
        <h1 className="text-xl font-semibold">Console unavailable</h1>
        <p className="text-sm text-white/70">
          We could not reach the gateway to determine setup or authentication state. Please ensure the gateway is running and
          try again.
        </p>
        <a className="text-emerald-200 hover:text-emerald-100" href="/healthz">
          View health endpoint
        </a>
      </div>
    </main>
  );
}
