import { appendLog, runCommand } from './utils';

const REQUIRED_COMMANDS = ['docker', 'docker-compose', 'git', 'curl'];

async function commandExists(command: string) {
  const result = await runCommand('sh', ['-c', `command -v ${command} || true`], { ignoreFailure: true });
  return Boolean(result.stdout.trim());
}

async function maybeInstallPackages(missing: string[]) {
  if (!missing.length) return;
  appendLog(`install missing packages: ${missing.join(',')}`);
  await runCommand('apt-get', ['update'], { ignoreFailure: true });
  await runCommand('apt-get', ['-y', 'install', ...missing], { ignoreFailure: true });
}

export async function bootstrapRuntime() {
  const missing: string[] = [];
  for (const command of REQUIRED_COMMANDS) {
    if (!(await commandExists(command))) {
      missing.push(command === 'docker-compose' ? 'docker-compose-plugin' : command);
    }
  }
  await maybeInstallPackages(missing);
  await runCommand('sh', ['-c', 'docker compose -f docker-compose.quickstart.yml up -d || true'], { ignoreFailure: true });
  return { ok: true, missingInstalled: missing };
}
