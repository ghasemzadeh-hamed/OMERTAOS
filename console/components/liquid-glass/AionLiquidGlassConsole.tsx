'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Bot,
  ChevronLeft,
  ChevronRight,
  Cpu,
  DownloadCloud,
  Globe,
  HardDrive,
  LayoutDashboard,
  MessageSquare,
  Moon,
  Plug,
  RefreshCcw,
  Server,
  Settings,
  ShieldCheck,
  Sun,
  Database,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';

const glass =
  'backdrop-blur-xl bg-white/10 dark:bg-white/5 border border-white/20 dark:border-white/10 shadow-[0_8px_30px_rgb(0,0,0,0.12)]';

const navItems = [
  { key: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-5 w-5" /> },
  { key: 'chat', label: 'Chat', icon: <MessageSquare className="h-5 w-5" /> },
  { key: 'updates', label: 'Updates', icon: <RefreshCcw className="h-5 w-5" /> },
  { key: 'config', label: 'Configuration', icon: <Settings className="h-5 w-5" /> },
  { key: 'install', label: 'Installers', icon: <DownloadCloud className="h-5 w-5" /> },
  { key: 'health', label: 'Health', icon: <ShieldCheck className="h-5 w-5" /> },
] as const;

const THEME_STORAGE_KEY = 'aion-liquid-theme';

type ActiveTab = (typeof navItems)[number]['key'];

type ChatMessage = {
  role: 'assistant' | 'user';
  text: string;
};

export default function AionLiquidGlassConsole(): JSX.Element {
  const [active, setActive] = useState<ActiveTab>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [dark, setDark] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', text: 'Hello! How can I help you today?' },
  ]);
  const [input, setInput] = useState('');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === 'light') {
      setDark(false);
    } else if (storedTheme === 'dark') {
      setDark(true);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(THEME_STORAGE_KEY, dark ? 'dark' : 'light');
  }, [dark]);

  const themeClasses = useMemo(
    () => `${dark ? 'dark' : ''} bg-gradient-to-br from-[#0f172a] via-[#111827] to-[#030712]`,
    [dark],
  );

  const toggleTheme = () => setDark((prev) => !prev);

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((prev) => [...prev, { role: 'user', text: input }]);
    setInput('');
    // TODO: wire up Gateway chat streaming endpoint
  };

  return (
    <div dir="ltr" className={`min-h-screen ${themeClasses} text-white`}>
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-24 h-[32rem] w-[32rem] rounded-full bg-fuchsia-500/10 blur-3xl" />
      </div>

      <div className="relative z-10 flex">
        <motion.aside
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: 'spring', stiffness: 60, damping: 12 }}
          className={`${glass} ${sidebarOpen ? 'w-72' : 'w-18'} m-4 flex flex-col gap-3 rounded-2xl p-3`}
        >
          <div className="flex items-center justify-between px-2 py-1">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6" />
              {sidebarOpen && <span className="font-bold">AION-OS</span>}
            </div>
            <Button size="icon" variant="ghost" onClick={() => setSidebarOpen((prev) => !prev)}>
              {sidebarOpen ? <ChevronRight /> : <ChevronLeft />}
            </Button>
          </div>

          <div className="px-2">
            <Select>
              <SelectTrigger className={`${glass} h-10`}>
                <SelectValue placeholder="Choose project" />
              </SelectTrigger>
              <SelectContent align="end">
                <SelectItem value="default">Default project</SelectItem>
                <SelectItem value="doko">Doko (Commerce)</SelectItem>
                <SelectItem value="sobhan">Sobhan (FMCG)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <nav className="mt-2 flex flex-col gap-1">
            {navItems.map((item) => {
              const isActive = active === item.key;
              return (
                <Button
                  key={item.key}
                  variant={isActive ? 'default' : 'ghost'}
                  className={`justify-start ${isActive ? 'bg-white/20' : 'hover:bg-white/10'}`}
                  onClick={() => setActive(item.key)}
                >
                  <span className="ml-3">{item.icon}</span>
                  {sidebarOpen && <span>{item.label}</span>}
                </Button>
              );
            })}
          </nav>

          <div className="mt-auto px-2">
            <Card className={`${glass} rounded-xl`}>
              <CardContent className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  <span className="text-sm">Service status</span>
                </div>
                <div className="flex gap-1">
                  <Badge className="bg-emerald-500/80">Gateway</Badge>
                  <Badge className="bg-emerald-500/80">Control</Badge>
                  <Badge className="bg-amber-500/80">Vector</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.aside>

        <main className="m-4 mr-0 flex-1">
          <div className={`${glass} mb-4 flex items-center justify-between rounded-2xl px-4 py-3`}>
            <div className="flex items-center gap-3">
              <span className="font-semibold">Operations overview</span>
              <Badge className="bg-sky-500/80">Beta</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" onClick={toggleTheme} className="gap-2">
                {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                <span>Theme</span>
              </Button>
              <Button variant="secondary" className="bg-white/20 hover:bg-white/30">
                Sign out
              </Button>
            </div>
          </div>

          {active === 'dashboard' && <DashboardSection />}
          {active === 'chat' && (
            <ChatSection
              input={input}
              messages={messages}
              onInputChange={setInput}
              onSend={sendMessage}
            />
          )}
          {active === 'updates' && <UpdatesSection />}
          {active === 'config' && <ConfigSection />}
          {active === 'install' && <InstallSection />}
          {active === 'health' && <HealthSection />}
        </main>
      </div>
    </div>
  );
}

type StatProps = {
  title: string;
  value: string;
  sub?: string;
};

function Stat({ title, value, sub }: StatProps) {
  return (
    <div className={`${glass} rounded-xl p-4`}>
      <div className="text-sm opacity-80">{title}</div>
      <div className="mt-1 text-3xl font-extrabold">{value}</div>
      {sub && <div className="mt-1 text-xs opacity-70">{sub}</div>}
    </div>
  );
}

type KeyValueProps = {
  k: string;
  v: string;
  icon?: React.ReactNode;
};

function KeyValue({ k, v, icon }: KeyValueProps) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <div className="flex items-center gap-2 opacity-90">
        {icon}
        <span className="text-sm">{k}</span>
      </div>
      <div className="text-sm opacity-80">{v}</div>
    </div>
  );
}

function DashboardSection() {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <Card className={`${glass} rounded-2xl xl:col-span-2`}>
        <CardHeader>
          <CardTitle>Project summary</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <Stat title="Requests today" value="12,457" sub="+8% vs yesterday" />
          <Stat title="Monthly spend" value="$142.8" sub="Budget: $200" />
          <Stat title="Average latency" value="612ms" sub="p95: 1.3s" />
        </CardContent>
      </Card>
      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Current router</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <KeyValue k="Policy" v="auto (fa->local, long->api)" />
          <KeyValue k="Local Provider" v="Ollama (llama3.2:3b)" />
          <KeyValue k="API Provider" v="OpenAI (gpt-4o)" />
          <Button className="w-full bg-white/20 hover:bg-white/30">Edit policy</Button>
        </CardContent>
      </Card>
    </div>
  );
}

type ChatSectionProps = {
  input: string;
  messages: ChatMessage[];
  onInputChange: (value: string) => void;
  onSend: () => void;
};

function ChatSection({ input, messages, onInputChange, onSend }: ChatSectionProps) {
  return (
    <div className="grid h-[70vh] grid-rows-[1fr_auto] gap-3">
      <Card className={`${glass} rounded-2xl overflow-hidden`}>
        <CardContent className="p-0">
          <div className="h-[55vh] space-y-3 overflow-y-auto p-4">
            {messages.map((message, index) => (
              <motion.div
                key={`${message.role}-${index}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user' ? 'ml-auto bg-cyan-500/20' : 'bg-white/10'
                }`}
              >
                <div className="mb-1 text-xs opacity-70">
                  {message.role === 'user' ? 'You' : 'Assistant'}
                </div>
                <div className="whitespace-pre-wrap leading-7">{message.text}</div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center gap-2">
        <Input
          placeholder="Type your message..."
          value={input}
          onChange={(event) => onInputChange(event.target.value)}
          className={`${glass} rounded-2xl`}
        />
        <Select>
          <SelectTrigger className={`${glass} w-48`}>
            <SelectValue placeholder="Choose agent" />
          </SelectTrigger>
          <SelectContent align="end">
            <SelectItem value="sales">Sales Assistant</SelectItem>
            <SelectItem value="support">Support Bot</SelectItem>
            <SelectItem value="docs">Docs QA</SelectItem>
          </SelectContent>
        </Select>
        <Button onClick={onSend} className="bg-white/20 hover:bg-white/30">
          Send
        </Button>
      </div>
    </div>
  );
}

function UpdatesSection() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Core and console updates</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <KeyValue k="Console" v="v0.9.2" />
          <KeyValue k="Gateway" v="v0.9.1" />
          <KeyValue k="Control" v="v0.9.4" />
          <Button className="w-full bg-white/20 hover:bg-white/30">Check for Updates</Button>
        </CardContent>
      </Card>

      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Model and module updates</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              <span>Ollama (llama3.2:3b)</span>
            </div>
            <Button size="sm" variant="secondary" className="bg-white/20">
              Update
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4" />
              <span>vLLM service</span>
            </div>
            <Button size="sm" variant="secondary" className="bg-white/20">
              Restart
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Plug className="h-4 w-4" />
              <span>summarize-rs@0.3.2</span>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" className="bg-white/20">
                Upgrade
              </Button>
              <Button size="sm" variant="secondary" className="bg-white/20">
                Rollback
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ConfigSection() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className={`${glass} rounded-2xl lg:col-span-2`}>
        <CardHeader>
          <CardTitle>Router and provider settings</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm opacity-80">Routing policy</label>
            <Select>
              <SelectTrigger className={glass}>
                <SelectValue placeholder="auto" />
              </SelectTrigger>
              <SelectContent align="end">
                <SelectItem value="auto">auto</SelectItem>
                <SelectItem value="local">local</SelectItem>
                <SelectItem value="api">api</SelectItem>
                <SelectItem value="hybrid">hybrid</SelectItem>
              </SelectContent>
            </Select>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-sm">Failover</span>
              <Switch defaultChecked />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm opacity-80">Default provider</label>
            <Select>
              <SelectTrigger className={glass}>
                <SelectValue placeholder="Ollama" />
              </SelectTrigger>
              <SelectContent align="end">
                <SelectItem value="ollama">Ollama</SelectItem>
                <SelectItem value="openai">OpenAI</SelectItem>
                <SelectItem value="azure">Azure</SelectItem>
                <SelectItem value="hf">HuggingFace</SelectItem>
              </SelectContent>
            </Select>
            <label className="mt-4 block text-sm opacity-80">Monthly budget (USD)</label>
            <Input type="number" defaultValue={200} className={glass} />
          </div>

          <div className="md:col-span-2">
            <label className="text-sm opacity-80">Custom YAML rules</label>
            <Textarea
              className={`${glass} min-h-[160px]`}
              placeholder={`rules:\n  - match:\n      lang: fa\n      max_input_tokens: 2000\n    route: local\n    provider: ollama\n    model: llama3.2:3b`}
            />
            <div className="mt-3 flex gap-2">
              <Button className="bg-white/20 hover:bg-white/30">Apply and reload</Button>
              <Button variant="secondary" className="bg-white/20">
                Export
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Data and integrations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <KeyValue k="Postgres" v="postgres-main (RO)" icon={<Database className="h-4 w-4" />} />
          <KeyValue k="MinIO" v="company-docs (S3)" icon={<HardDrive className="h-4 w-4" />} />
          <KeyValue k="Odoo" v="prod@odoo.local" icon={<Globe className="h-4 w-4" />} />
          <Button className="w-full bg-white/20 hover:bg-white/30">Manage connectors</Button>
        </CardContent>
      </Card>
    </div>
  );
}

function InstallSection() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <InstallCard title="Ollama" desc="Local LLM host for lightweight models" tags={['CPU', 'Local']} />
      <InstallCard title="vLLM" desc="High-throughput model serving (GPU/TP)" tags={['GPU', 'API']} />
      <InstallCard title="Qdrant" desc="Vector database for semantic search" tags={['Vector', 'Search']} />
      <InstallCard title="ClickHouse" desc="Fast analytical data warehouse" tags={['OLAP', 'Analytics']} />
      <InstallCard title="Superset" desc="Dashboards and visualization" tags={['BI', 'Charts']} />
      <InstallCard title="Summarize-RS" desc="Rust summarization module" tags={['Module', 'Rust']} />
    </div>
  );
}

type InstallCardProps = {
  title: string;
  desc: string;
  tags?: string[];
};

function InstallCard({ title, desc, tags }: InstallCardProps) {
  return (
    <Card className={`${glass} rounded-2xl transition hover:bg-white/15`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{title}</span>
          <Button size="sm" variant="secondary" className="bg-white/20">
            Install
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="text-sm leading-7 opacity-90">{desc}</div>
        <div className="flex flex-wrap gap-1">
          {tags?.map((tag) => (
            <Badge key={tag} className="bg-white/15">
              {tag}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

type HealthState = 'healthy' | 'degraded' | 'down';

type HealthRowProps = {
  name: string;
  state: HealthState;
  latency: string;
};

function HealthRow({ name, state, latency }: HealthRowProps) {
  const color = state === 'healthy' ? 'bg-emerald-500' : state === 'degraded' ? 'bg-amber-500' : 'bg-rose-500';
  const label = state === 'healthy' ? 'Healthy' : state === 'degraded' ? 'Degraded' : 'Offline';

  return (
    <div className="flex items-center justify-between rounded-xl bg-white/10 px-3 py-2">
      <div className="flex items-center gap-2">
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />
        <span className="text-sm">{name}</span>
      </div>
      <div className="flex items-center gap-3 text-xs opacity-80">
        <span>{label}</span>
        <span className="opacity-60">{latency}</span>
      </div>
    </div>
  );
}

function HealthSection() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Service health</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <HealthRow name="Gateway" state="healthy" latency="82ms" />
          <HealthRow name="Control" state="healthy" latency="94ms" />
          <HealthRow name="Vector" state="degraded" latency="220ms" />
          <HealthRow name="DB" state="healthy" latency="15ms" />
        </CardContent>
      </Card>
      <Card className={`${glass} rounded-2xl`}>
        <CardHeader>
          <CardTitle>Recent logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="whitespace-pre-wrap text-sm/7 opacity-90">
            {["[21:03:11] router: policy reloaded (rev=17)",
              "[21:03:15] chat: route=local model=llama3.2:3b tokens=512",
              "[21:03:21] summarizer: job=92a1 done in 682ms",
              "[21:03:26] vector: p95 latency 1.2s (warning)"].join('\n')}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
