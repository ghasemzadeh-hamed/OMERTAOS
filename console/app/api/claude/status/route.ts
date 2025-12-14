import path from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { NextResponse } from 'next/server';

import { safeGetServerSession } from '@/lib/session';

const execFileAsync = promisify(execFile);
const marketplaceId = 'wshobson/agents';
const recommendedPlugins = [
  'python-development@wshobson/agents',
  'javascript-typescript@wshobson/agents',
  'backend-development@wshobson/agents',
  'kubernetes-operations@wshobson/agents',
  'cloud-infrastructure@wshobson/agents',
  'security-scanning@wshobson/agents',
  'code-review-ai@wshobson/agents',
  'full-stack-orchestration@wshobson/agents',
];

const installCommand = 'bash scripts/claude/install-claude-code.sh';
const bootstrapCommand = 'bash scripts/claude/bootstrap-marketplace.sh';
const marketplaceCommand = `/plugin marketplace add ${marketplaceId}`;
const pluginCommands = recommendedPlugins.map((plugin) => `/plugin install ${plugin}`);

function buildDefaultPayload() {
  return {
    claude: { installed: false, path: '', version: '' },
    settings: { present: false, valid: false, error: 'Missing settings' },
  };
}

export async function GET() {
  const session = await safeGetServerSession();
  if (!session) {
    return NextResponse.json({ error: 'unauthorized' }, { status: 401 });
  }

  const scriptPath = path.resolve(process.cwd(), '..', 'scripts', 'claude', 'status.sh');
  let payload: any = buildDefaultPayload();

  try {
    const { stdout } = await execFileAsync(scriptPath, ['--json'], { timeout: 5000 });
    const parsed = JSON.parse(stdout || '{}');
    payload = parsed;
  } catch (error: any) {
    try {
      if (error?.stdout) {
        payload = JSON.parse(String(error.stdout));
      }
    } catch (parseError) {
      payload = {
        ...payload,
        error: 'Unable to read status',
        details: error?.message ?? String(error),
      };
    }
  }

  return NextResponse.json({
    claude: {
      installed: Boolean(payload?.claude?.installed),
      path: payload?.claude?.path ?? '',
      version: payload?.claude?.version ?? '',
    },
    settings: {
      present: Boolean(payload?.settings?.present),
      valid: Boolean(payload?.settings?.valid),
      error: payload?.settings?.error ?? '',
    },
    recommendedPlugins,
    marketplace: marketplaceId,
    instructions: {
      installCommand,
      bootstrapCommand,
      marketplaceCommand,
      pluginCommands,
      note: 'Login is interactive; run claude once in a terminal to finish setup.',
    },
  });
}
