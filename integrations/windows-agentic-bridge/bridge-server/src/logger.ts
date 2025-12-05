/* eslint-disable no-console */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

function shouldLog(level: LogLevel, current: LogLevel): boolean {
  const weights: Record<LogLevel, number> = { debug: 10, info: 20, warn: 30, error: 40 };
  return weights[level] >= weights[current];
}

export class Logger {
  constructor(private level: LogLevel = 'info') {}

  debug(message: string, meta: Record<string, unknown> = {}) {
    if (shouldLog('debug', this.level)) console.log(JSON.stringify({ level: 'debug', message, ...meta }));
  }

  info(message: string, meta: Record<string, unknown> = {}) {
    if (shouldLog('info', this.level)) console.log(JSON.stringify({ level: 'info', message, ...meta }));
  }

  warn(message: string, meta: Record<string, unknown> = {}) {
    if (shouldLog('warn', this.level)) console.warn(JSON.stringify({ level: 'warn', message, ...meta }));
  }

  error(message: string, meta: Record<string, unknown> = {}) {
    if (shouldLog('error', this.level)) console.error(JSON.stringify({ level: 'error', message, ...meta }));
  }
}
