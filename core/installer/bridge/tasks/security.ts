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

export async function applySecurity() {
  await run('apt', ['update']);
  await run('apt', ['-y', 'upgrade']);
  await run('sh', ['-c', 'command -v snap && snap refresh || true']);
  return { ok: true };
}
