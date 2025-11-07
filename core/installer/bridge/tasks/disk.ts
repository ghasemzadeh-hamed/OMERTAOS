import { execFile } from 'node:child_process';

function run(cmd: string, args: string[] = []) {
  return new Promise<string>((resolve, reject) => {
    execFile(cmd, args, { encoding: 'utf8' }, (error, stdout, stderr) => {
      if (error) {
        reject(stderr || error.message);
      } else {
        resolve(stdout);
      }
    });
  });
}

export async function probeHw() {
  const lsblk = await run('lsblk', ['-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT']);
  const lspci = await run('sh', ['-c', 'lspci || true']);
  return { disks: JSON.parse(lsblk).blockdevices, pci: lspci };
}
