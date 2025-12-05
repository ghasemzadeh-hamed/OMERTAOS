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
            معرفی سریع پل MCP داخل WSL برای دسترسی Agentic ویندوز به قابلیت‌های OMERTAOS.
          </p>
        </div>
        <Badge className="bg-emerald-600/80">WSL + MCP</Badge>
      </div>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>پلان اجرایی خلاصه</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ol className="list-decimal space-y-2 pl-5">
            <li>OMERTA روی WSL: نصب Docker Desktop + WSL2، کلون repo و اجرای <code>./install.sh --profile user</code> یا <code>docker compose</code>.</li>
            <li>سلامت اولیه: <code>curl http://localhost:3000/healthz</code> و <code>curl http://localhost:8000/healthz</code>.</li>
            <li>ساخت OMERTA MCP Bridge در WSL: تعریف حداقل ابزارها (<code>run_task</code>، <code>list_agents</code>، <code>get_health</code>) با <code>OMERTA_GATEWAY_URL</code> و توکن dev.</li>
            <li>Manifest و ODR روی ویندوز: ثبت JSON با <code>wsl.exe</code>، اجرای <code>odr.exe mcp add ...</code> و تست <code>odr.exe mcp list</code>.</li>
            <li>Agent Host نمونه (اختیاری): یک Agent ساده با Microsoft Agent Framework که ابزارهای <code>omerta_run_task</code> و <code>omerta_list_agents</code> را صدا بزند.</li>
          </ol>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>گام ۱: آماده‌سازی WSL و OMERTAOS</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>Docker Desktop + WSL2 را فعال کنید و توزیع Ubuntu را آماده نگه دارید.</li>
            <li>مخزن <code>OMERTAOS</code> را در WSL کلون کنید و <code>./install.sh --profile user</code> یا پروفایل <code>compose dev</code> را اجرا کنید.</li>
            <li>سلامت Gateway و Control را با <code>curl</code> روی پورت‌های 3000 و 8000 بررسی کنید.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>گام ۲: پیاده‌سازی پل MCP داخل WSL</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>در مسیر <code>integrations/windows-agentic-bridge</code> یک MCP server (Node/TypeScript یا Python) بسازید؛ نمونه TypeScript آماده است.</li>
            <li>ورودی/خروجی ابزارها را با JSON Schema تعریف کنید؛ حداقل <code>run_task</code>، <code>list_agents</code> و <code>get_health</code> را فعال کنید.</li>
            <li>اتصال به OMERTA با <code>OMERTA_GATEWAY_URL</code> و توکن dev از محیط یا <code>.env</code> انجام شود.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>گام ۳: manifest و ODR روی ویندوز</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>در <code>manifests/omertaos-wsl.mcp.json</code> مسیر <code>wsl.exe</code> و دستور راه‌اندازی پل را تنظیم کنید.</li>
            <li>از PowerShell، فایل را با <code>odr.exe mcp add</code> ثبت کنید و با <code>odr.exe mcp list</code> صحت ثبت را ببینید.</li>
            <li>می‌توانید <code>scripts/check-bridge.ps1</code> را برای سلامت اولیه اجرا کنید.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>گام ۴: Agent Host نمونه</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm leading-6 text-white/80">
          <ul className="list-disc space-y-2 pl-5">
            <li>یک Agent ساده با Microsoft Agent Framework بسازید که ابزارهای <code>omerta_run_task</code> و <code>omerta_list_agents</code> را مصرف کند.</li>
            <li>پایان کار: از ویندوز درخواست ارسال کنید و خروجی را از Agent روی WSL دریافت کنید تا مسیر end-to-end تایید شود.</li>
          </ul>
        </CardContent>
      </Card>

      <Card className="border-white/10 bg-white/5">
        <CardHeader>
          <CardTitle>منابع و مسیرها</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm leading-6 text-white/80">
          <p>کد و مستندات پل در مخزن اصلی:</p>
          <ul className="list-disc space-y-2 pl-5">
            <li>
              پل MCP و UI: <code>integrations/windows-agentic-bridge/bridge-server</code> و <code>integrations/windows-agentic-bridge/bridge-ui</code>
            </li>
            <li>manifest و اسکریپت‌ها: <code>integrations/windows-agentic-bridge/manifests</code> و <code>integrations/windows-agentic-bridge/scripts</code></li>
            <li>
              راهنمای کامل: <Link
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
          <CardTitle>نمودار ASCII مسیر اتصال</CardTitle>
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
