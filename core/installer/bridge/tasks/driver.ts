import { appendLog, runCommand } from './utils';

type HardwareProbe = {
  hasNvidia: boolean;
  hasAmd: boolean;
  hasIntelGpu: boolean;
  hasIntelWifi: boolean;
  hasRealtek: boolean;
  hasMellanox: boolean;
};

async function readPciInventory() {
  const { stdout } = await runCommand('sh', ['-c', 'lspci | tr A-Z a-z || true'], { ignoreFailure: true });
  return stdout || '';
}

function detectHardware(raw: string): HardwareProbe {
  const normalized = raw.toLowerCase();
  return {
    hasNvidia: normalized.includes('nvidia'),
    hasAmd: normalized.includes('advanced micro devices') || normalized.includes('amd/ati'),
    hasIntelGpu: normalized.includes('intel corporation uhd') || normalized.includes('intel corporation iris') || normalized.includes('intel corporation arc'),
    hasIntelWifi: normalized.includes('network controller: intel corporation') || normalized.includes('wireless: intel corporation'),
    hasRealtek: normalized.includes('realtek'),
    hasMellanox: normalized.includes('mellanox') || normalized.includes('mlx5'),
  };
}

async function installPackages(packages: string[], optional = false) {
  if (!packages.length) {
    return;
  }
  try {
    await runCommand('apt-get', ['install', '-y', ...packages]);
  } catch (error) {
    if (!optional) {
      throw error;
    }
    appendLog(`warn apt-get install ${packages.join(' ')}: ${(error as Error).message}`);
  }
}

async function installNvidiaStack() {
  await installPackages(['ubuntu-drivers-common'], true);
  await runCommand(
    'sh',
    [
      '-c',
      'ubuntu-drivers autoinstall || apt-get install -y nvidia-driver-535 || apt-get install -y nvidia-driver-525 || true',
    ],
    { ignoreFailure: true },
  );
}

async function installAmdStack() {
  await installPackages(['firmware-amd-graphics'], true);
  await installPackages(['amdgpu-dkms'], true);
}

async function installIntelGpuStack() {
  await installPackages(['intel-media-va-driver-non-free'], true);
}

export async function applyDrivers() {
  appendLog('driver task start');
  await runCommand('apt-get', ['update']);
  const inventory = await readPciInventory();
  const probe = detectHardware(inventory);

  const basePackages = new Set<string>();
  basePackages.add('linux-firmware');
  if (probe.hasIntelWifi) {
    basePackages.add('firmware-iwlwifi');
  }
  if (probe.hasRealtek) {
    basePackages.add('firmware-realtek');
  }
  if (probe.hasMellanox) {
    basePackages.add('mlx5-tools');
  }

  await installPackages([...basePackages]);

  if (probe.hasNvidia) {
    await installNvidiaStack();
  }
  if (probe.hasAmd) {
    await installAmdStack();
  }
  if (probe.hasIntelGpu) {
    await installIntelGpuStack();
  }

  appendLog('driver task end');
  return { ok: true, probe };
}
