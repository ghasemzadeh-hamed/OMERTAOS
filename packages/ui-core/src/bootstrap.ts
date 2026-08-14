export interface BootstrapState {
  setupDone: boolean;
  authenticated: boolean;
  onboardingComplete: boolean;
}

export async function resolveBootstrapState(baseUrl?: string): Promise<BootstrapState> {
  const fallback: BootstrapState = {
    setupDone: false,
    authenticated: false,
    onboardingComplete: false,
  };

  if (!baseUrl) {
    return fallback;
  }

  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, '')}/api/bootstrap`, {
      cache: 'no-store',
    });
    if (!response.ok) {
      return fallback;
    }
    return { ...fallback, ...(await response.json()) };
  } catch {
    return fallback;
  }
}
