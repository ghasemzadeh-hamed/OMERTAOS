import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function WindowsBridgePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-white/90">Windows Agentic Bridge</h2>
          <p className="text-sm text-white/70">
            \u0645\u0639\u0631\u0641\u06cc \u0633\u0631\u06cc\u0639 \u067e\u0644 MCP \u062f\u0627\u062e\u0644 WSL \u0628\u0631\u0627\u06cc \u062f\u0633\u062a\u0631\u0633\u06cc Agentic \u0648\u06cc\u0646\u062f\u0648\u0632 \u0628\u0647 \u0642\u0627\u0628\u0644\u06cc\u062a\u200c\u0647\u0627\u06cc OMERTAOS.
          </p>
        </div>
        <Badge className="bg-emerald-600/80">WSL + MCP</Badge>
      </div>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u067e\u0644\u0627\u0646 \u0627\u062c\u0631\u0627\u06cc\u06cc \u062e\u0644\u0627\u0635\u0647</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ol className="list-decimal space-y-2 pl-5">
            <li>OMERTA \u0631\u0648\u06cc WSL: \u0646\u0635\u0628 Docker Desktop + WSL2\u060c \u06a9\u0644\u0648\u0646 repo \u0648 \u0627\u062c\u0631\u0627\u06cc <code>./install.sh --profile user</code> \u06cc\u0627 <code>docker compose</code>.</li>
            <li>\u0633\u0644\u0627\u0645\u062a \u0627\u0648\u0644\u06cc\u0647: <code>curl http://localhost:3000/healthz</code> \u0648 <code>curl http://localhost:8000/healthz</code>.</li>
            <li>\u0633\u0627\u062e\u062a OMERTA MCP Bridge \u062f\u0631 WSL: \u062a\u0639\u0631\u06cc\u0641 \u062d\u062f\u0627\u0642\u0644 \u0627\u0628\u0632\u0627\u0631\u0647\u0627 (<code>run_task</code>\u060c <code>list_agents</code>\u060c <code>get_health</code>) \u0628\u0627 <code>OMERTA_GATEWAY_URL</code> \u0648 \u062a\u0648\u06a9\u0646 dev.</li>
            <li>Manifest \u0648 ODR \u0631\u0648\u06cc \u0648\u06cc\u0646\u062f\u0648\u0632: \u062b\u0628\u062a JSON \u0628\u0627 <code>wsl.exe</code>\u060c \u0627\u062c\u0631\u0627\u06cc <code>odr.exe mcp add ...</code> \u0648 \u062a\u0633\u062a <code>odr.exe mcp list</code>.</li>
            <li>Agent Host \u0646\u0645\u0648\u0646\u0647 (\u0627\u062e\u062a\u06cc\u0627\u0631\u06cc): \u06cc\u06a9 Agent \u0633\u0627\u062f\u0647 \u0628\u0627 Microsoft Agent Framework \u06a9\u0647 \u0627\u0628\u0632\u0627\u0631\u0647\u0627\u06cc <code>omerta_run_task</code> \u0648 <code>omerta_list_agents</code> \u0631\u0627 \u0635\u062f\u0627 \u0628\u0632\u0646\u062f.</li>
          </ol>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u06af\u0627\u0645 \u06f1: \u0622\u0645\u0627\u062f\u0647\u200c\u0633\u0627\u0632\u06cc WSL \u0648 OMERTAOS</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>Docker Desktop + WSL2 \u0631\u0627 \u0641\u0639\u0627\u0644 \u06a9\u0646\u06cc\u062f \u0648 \u062a\u0648\u0632\u06cc\u0639 Ubuntu \u0631\u0627 \u0622\u0645\u0627\u062f\u0647 \u0646\u06af\u0647 \u062f\u0627\u0631\u06cc\u062f.</li>
            <li>\u0645\u062e\u0632\u0646 <code>OMERTAOS</code> \u0631\u0627 \u062f\u0631 WSL \u06a9\u0644\u0648\u0646 \u06a9\u0646\u06cc\u062f \u0648 <code>./install.sh --profile user</code> \u06cc\u0627 \u067e\u0631\u0648\u0641\u0627\u06cc\u0644 <code>compose dev</code> \u0631\u0627 \u0627\u062c\u0631\u0627 \u06a9\u0646\u06cc\u062f.</li>
            <li>\u0633\u0644\u0627\u0645\u062a Gateway \u0648 Control \u0631\u0627 \u0628\u0627 <code>curl</code> \u0631\u0648\u06cc \u067e\u0648\u0631\u062a\u200c\u0647\u0627\u06cc 3000 \u0648 8000 \u0628\u0631\u0631\u0633\u06cc \u06a9\u0646\u06cc\u062f.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u06af\u0627\u0645 \u06f2: \u067e\u06cc\u0627\u062f\u0647\u200c\u0633\u0627\u0632\u06cc \u067e\u0644 MCP \u062f\u0627\u062e\u0644 WSL</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>\u062f\u0631 \u0645\u0633\u06cc\u0631 <code>integrations/windows-agentic-bridge</code> \u06cc\u06a9 MCP server (Node/TypeScript \u06cc\u0627 Python) \u0628\u0633\u0627\u0632\u06cc\u062f\u061b \u0646\u0645\u0648\u0646\u0647 TypeScript \u0622\u0645\u0627\u062f\u0647 \u0627\u0633\u062a.</li>
            <li>\u0648\u0631\u0648\u062f\u06cc/\u062e\u0631\u0648\u062c\u06cc \u0627\u0628\u0632\u0627\u0631\u0647\u0627 \u0631\u0627 \u0628\u0627 JSON Schema \u062a\u0639\u0631\u06cc\u0641 \u06a9\u0646\u06cc\u062f\u061b \u062d\u062f\u0627\u0642\u0644 <code>run_task</code>\u060c <code>list_agents</code> \u0648 <code>get_health</code> \u0631\u0627 \u0641\u0639\u0627\u0644 \u06a9\u0646\u06cc\u062f.</li>
            <li>\u0627\u062a\u0635\u0627\u0644 \u0628\u0647 OMERTA \u0628\u0627 <code>OMERTA_GATEWAY_URL</code> \u0648 \u062a\u0648\u06a9\u0646 dev \u0627\u0632 \u0645\u062d\u06cc\u0637 \u06cc\u0627 <code>.env</code> \u0627\u0646\u062c\u0627\u0645 \u0634\u0648\u062f.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u06af\u0627\u0645 \u06f3: manifest \u0648 ODR \u0631\u0648\u06cc \u0648\u06cc\u0646\u062f\u0648\u0632</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>\u062f\u0631 <code>manifests/omertaos-wsl.mcp.json</code> \u0645\u0633\u06cc\u0631 <code>wsl.exe</code> \u0648 \u062f\u0633\u062a\u0648\u0631 \u0631\u0627\u0647\u200c\u0627\u0646\u062f\u0627\u0632\u06cc \u067e\u0644 \u0631\u0627 \u062a\u0646\u0638\u06cc\u0645 \u06a9\u0646\u06cc\u062f.</li>
            <li>\u0627\u0632 PowerShell\u060c \u0641\u0627\u06cc\u0644 \u0631\u0627 \u0628\u0627 <code>odr.exe mcp add</code> \u062b\u0628\u062a \u06a9\u0646\u06cc\u062f \u0648 \u0628\u0627 <code>odr.exe mcp list</code> \u0635\u062d\u062a \u062b\u0628\u062a \u0631\u0627 \u0628\u0628\u06cc\u0646\u06cc\u062f.</li>
            <li>\u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f <code>scripts/check-bridge.ps1</code> \u0631\u0627 \u0628\u0631\u0627\u06cc \u0633\u0644\u0627\u0645\u062a \u0627\u0648\u0644\u06cc\u0647 \u0627\u062c\u0631\u0627 \u06a9\u0646\u06cc\u062f.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u06af\u0627\u0645 \u06f4: Agent Host \u0646\u0645\u0648\u0646\u0647</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>\u06cc\u06a9 Agent \u0633\u0627\u062f\u0647 \u0628\u0627 Microsoft Agent Framework \u0628\u0633\u0627\u0632\u06cc\u062f \u06a9\u0647 \u0627\u0628\u0632\u0627\u0631\u0647\u0627\u06cc <code>omerta_run_task</code> \u0648 <code>omerta_list_agents</code> \u0631\u0627 \u0645\u0635\u0631\u0641 \u06a9\u0646\u062f.</li>
            <li>\u067e\u0627\u06cc\u0627\u0646 \u06a9\u0627\u0631: \u0627\u0632 \u0648\u06cc\u0646\u062f\u0648\u0632 \u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f \u0648 \u062e\u0631\u0648\u062c\u06cc \u0631\u0627 \u0627\u0632 Agent \u0631\u0648\u06cc WSL \u062f\u0631\u06cc\u0627\u0641\u062a \u06a9\u0646\u06cc\u062f \u062a\u0627 \u0645\u0633\u06cc\u0631 end-to-end \u062a\u0627\u06cc\u06cc\u062f \u0634\u0648\u062f.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u0645\u0646\u0627\u0628\u0639 \u0648 \u0645\u0633\u06cc\u0631\u0647\u0627</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm leading-6 text-white/80">
          <p>\u06a9\u062f \u0648 \u0645\u0633\u062a\u0646\u062f\u0627\u062a \u067e\u0644 \u062f\u0631 \u0645\u062e\u0632\u0646 \u0627\u0635\u0644\u06cc:</p>
          <ul className="list-disc space-y-2 pl-5">
            <li>
              \u067e\u0644 MCP \u0648 UI: <code>integrations/windows-agentic-bridge/bridge-server</code> \u0648 <code>integrations/windows-agentic-bridge/bridge-ui</code>
            </li>
            <li>manifest \u0648 \u0627\u0633\u06a9\u0631\u06cc\u067e\u062a\u200c\u0647\u0627: <code>integrations/windows-agentic-bridge/manifests</code> \u0648 <code>integrations/windows-agentic-bridge/scripts</code></li>
            <li>
              \u0631\u0627\u0647\u0646\u0645\u0627\u06cc \u06a9\u0627\u0645\u0644: <Link
                href="https://github.com/omertaos/omertaos/blob/main/integrations/windows-agentic-bridge/docs/README.md"
                className="text-emerald-300 underline"
                target="_blank"
                rel="noreferrer"
              >
                docs/README.md
              </Link>
            </li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>\u0646\u0645\u0648\u062f\u0627\u0631 ASCII \u0645\u0633\u06cc\u0631 \u0627\u062a\u0635\u0627\u0644</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-6 text-white/80">
          <pre className="whitespace-pre overflow-x-auto rounded-md bg-black/40 p-4 text-xs leading-6 text-emerald-100">
{`+-----------------------------+
|  Windows Agent (Copilot)    |
+--------------+--------------+
               |
               |  MCP over stdio via ODR
               v
+-----------------------------+
|  wsl.exe launches bridge    |
+--------------+--------------+
               |
               v
+-----------------------------+
|  WSL2                       |
|  OMERTA MCP Bridge (Node)   |
+--------------+--------------+
               |
               |  HTTP (local)
               v
+------------------+   +------------------+
| OMERTA Gateway   |   | OMERTA Control   |
+------------------+   +------------------+`}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
