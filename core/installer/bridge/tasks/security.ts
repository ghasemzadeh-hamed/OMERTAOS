import fs from 'node:fs';
import path from 'node:path';
import { appendLog, runCommand } from './utils';

type SecurityOptions = {
  refreshInstaller?: boolean;
};

function resolveInstallerRoot() {
  if (process.env.AIONOS_INSTALLER_ROOT) {
    return process.env.AIONOS_INSTALLER_ROOT;
  }
  return path.resolve(__dirname, '../../../..');
}

async function maybeRefreshInstaller(enabled?: boolean) {
  if (!enabled) {
    return;
  }
  const root = resolveInstallerRoot();
  if (!fs.existsSync(root)) {
    appendLog(`skip refresh-installer: missing root ${root}`);
    return;
  }
  if (!fs.existsSync(path.join(root, '.git'))) {
    appendLog(`skip refresh-installer: ${root} is not a git repo`);
    return;
  }
  await runCommand('git', ['-C', root, 'pull', '--ff-only'], { ignoreFailure: true });
}

export async function applySecurity(options: SecurityOptions = {}) {
  appendLog('security task start');
  await runCommand('apt-get', ['update']);
  await runCommand('apt-get', ['-y', 'upgrade']);
  await runCommand('sh', ['-c', 'command -v snap >/dev/null 2>&1 && snap refresh || true'], { ignoreFailure: true });
  await maybeRefreshInstaller(options.refreshInstaller);
  appendLog('security task end');
  return { ok: true };
}
