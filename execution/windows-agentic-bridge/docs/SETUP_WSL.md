# Setup: WSL side

1. Ensure OMERTAOS Gateway and Control endpoints are reachable (e.g., `http://localhost:3000`, `http://localhost:8000`).
2. Install Node.js 20+ and npm/pnpm inside WSL.
3. Bridge server:
   ```bash
   cd integrations/windows-agentic-bridge/bridge-server
   cp .env.example .env
   npm install
   npm run build
   node dist/index.js
   ```
4. Bridge UI:
   ```bash
   cd ../bridge-ui
   npm install
   npm run dev -- --host 0.0.0.0 --port 5173
   ```
5. Optional: launch via helper script
   ```bash
   ../scripts/run-bridge.sh
   ```
