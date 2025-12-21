export type DatabaseDiagnostics = {
  provider: 'postgresql' | 'sqlite' | 'unknown';
  rawUrl: string;
  redactedUrl: string;
  enforced: boolean;
};

export const detectDatabaseProvider = (rawUrl: string | undefined): DatabaseDiagnostics['provider'] => {
  if (!rawUrl) {
    return 'unknown';
  }
  const lower = rawUrl.toLowerCase();
  if (lower.startsWith('postgres')) {
    return 'postgresql';
  }
  if (lower.startsWith('file:')) {
    return 'sqlite';
  }
  return 'unknown';
};

export const redactDatabaseUrl = (rawUrl: string | undefined): string => {
  if (!rawUrl) {
    return '';
  }
  try {
    const parsed = new URL(rawUrl);
    if (parsed.password) {
      parsed.password = '***';
    }
    if (parsed.username) {
      parsed.username = '***';
    }
    return parsed.toString();
  } catch {
    return rawUrl.replace(/:[^:@/]+@/, '://***@');
  }
};

export const getDatabaseDiagnostics = (
  rawUrl: string | undefined,
  enforced: boolean,
): DatabaseDiagnostics => {
  const provider = detectDatabaseProvider(rawUrl);
  const redactedUrl = redactDatabaseUrl(rawUrl);

  return {
    provider,
    rawUrl: rawUrl ?? '',
    redactedUrl,
    enforced,
  };
};

export const requirePostgresUrl = (databaseUrl: string | undefined, enforced: boolean) => {
  if (!databaseUrl) {
    if (enforced) {
      throw new Error('[console] DATABASE_URL is required when running in docker/production.');
    }
    throw new Error('[console] DATABASE_URL must be set to a Postgres DSN.');
  }

  const diagnostics = getDatabaseDiagnostics(databaseUrl, enforced);
  if (diagnostics.provider !== 'postgresql') {
    throw new Error('[console] DATABASE_URL must point to a Postgres database.');
  }
};
