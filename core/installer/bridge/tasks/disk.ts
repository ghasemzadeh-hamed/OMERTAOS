import { appendLog, runCommand } from './utils';

export async function probeHw() {
  const { stdout: lsblkOut } = await runCommand('lsblk', ['-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT']);
  const { stdout: lspciOut } = await runCommand('sh', ['-c', 'lspci || true'], { ignoreFailure: true });
  const parsed = JSON.parse(lsblkOut || '{"blockdevices": []}');
  return { disks: parsed.blockdevices ?? [], pci: lspciOut };
}

export function allowDiskMode(mode?: string) {
  return mode === 'native' || mode === 'image';
}

export async function planPartition(payload: Record<string, unknown> = {}) {
  const mode = typeof payload.mode === 'string' ? payload.mode : undefined;
  appendLog(`plan.partition mode=${mode ?? 'unknown'}`);
  return {
    mode,
    plan: allowDiskMode(mode) ? 'apply-available' : 'preview-only',
  };
}

export async function applyPartition(payload: Record<string, unknown> = {}) {
  const mode = typeof payload.mode === 'string' ? payload.mode : undefined;
  if (!allowDiskMode(mode)) {
    throw new Error('unsupported-mode');
  }
  appendLog(`apply.partition mode=${mode}`);
  // Disk operations are gated; this placeholder only acknowledges the request.
  return { ok: true, mode, applied: false };
}
