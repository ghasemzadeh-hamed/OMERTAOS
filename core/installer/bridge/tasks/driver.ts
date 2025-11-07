import { execFile } from 'node:child_process';

function run(cmd: string, args: string[] = []) {
  return new Promise<void>((resolve, reject) => {
    execFile(cmd, args, (error) => {
      if (error) {
        reject(error);
      } else {
        resolve();
      }
    });
  });
}

export async function applyDrivers() {
  await run('apt', ['update']);
  await run('sh', ['-c', "lspci | grep -qi nvidia && apt -y install nvidia-driver || true"]);
  return { ok: true };
}
