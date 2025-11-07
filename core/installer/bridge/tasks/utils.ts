import fs from 'node:fs';
import path from 'node:path';
import { execFile } from 'node:child_process';

const LOG_PATH = '/var/log/aionos-installer.log';

function writeLog(line: string) {
  const timestamp = new Date().toISOString();
  const message = `[bridge] ${timestamp} ${line}\n`;
  try {
    const dir = path.dirname(LOG_PATH);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.appendFileSync(LOG_PATH, message, 'utf8');
  } catch (error) {
    // ignore logging failures (read-only filesystem, etc.)
  }
}

export function appendLog(message: string) {
  writeLog(message);
}

export async function runCommand(
  cmd: string,
  args: string[] = [],
  options: { ignoreFailure?: boolean } = {},
) {
  appendLog(`exec ${cmd} ${args.join(' ')}`.trim());
  return new Promise<{ stdout: string; stderr: string }>((resolve, reject) => {
    execFile(
      cmd,
      args,
      {
        encoding: 'utf8',
        env: {
          ...process.env,
          DEBIAN_FRONTEND: 'noninteractive',
        },
      },
      (error, stdout, stderr) => {
        if (error) {
          appendLog(`fail ${cmd}: ${error.message}`);
          if (options.ignoreFailure) {
            return resolve({ stdout: stdout ?? '', stderr: stderr ?? '' });
          }
          return reject(error);
        }
        appendLog(`done ${cmd}`);
        return resolve({ stdout: stdout ?? '', stderr: stderr ?? '' });
      },
    );
  });
}
