# OMERTAOS Desktop Shell

An optional Tauri desktop surface for OMERTAOS. It complements the existing Next.js Web Console; it does not replace, copy, or change it.

## Run the web preview

```bash
npm install
npm run dev
```

Open `http://localhost:1420`.

## Run the native shell

Install the [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) for your platform, then run:

```bash
npm install
npm run tauri:dev
```

Production validation:

```bash
npm run typecheck
npm run build
npm run tauri:build
```

The Console and Gateway endpoints can be overridden with `VITE_OMERTA_CONSOLE_URL` and `VITE_OMERTA_GATEWAY_URL`. Control health is read only from the Gateway dependency response; the Desktop Shell never connects to Control directly.

## Security boundary

Terminal and Files are UI-only. This shell enables no filesystem plugin, unrestricted command execution, or broad shell permission. The URL opener is scoped to the three local OMERTAOS service URLs.
