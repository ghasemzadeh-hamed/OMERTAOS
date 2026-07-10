export type ProxyType = "direct" | "http" | "https" | "socks4" | "socks5" | "vless";

export type ProxyScope = "global" | "ai_providers" | "model_registry" | "agent_runtime" | "custom_domains" | "system" | "browser" | "terminal" | "docker" | "all";

export type ProxyProfile = ProxyFormState & {
  id: number;
  has_secrets?: boolean;
  is_default?: boolean;
  created_at?: string;
  updated_at?: string;
  last_used_at?: string | null;
  status?: string;
  status_message?: string;
  test_result?: string;
  [key: string]: unknown;
};

/**
 * Shared network proxy validation utilities.
 * Moved out of app/tools/network/page.tsx because Next.js App Router pages
 * cannot export arbitrary helper functions.
 */

export type SecretField = string;

export type ProxyFormState = {
  name: string;
  type: ProxyType;
  enabled: boolean;
  scope: ProxyScope;
  host: string;
  port: string;
  transport: string;
  security: string;
  sni: string;
  flow: string;
  path: string;
  fallback_direct: boolean;
  health_check_url: string;
  secrets: Record<SecretField, string>;
};

export function validateProxyForm(form: ProxyFormState, hasExistingSecrets = false): string | null {
  if (!form.name.trim()) {
    return 'Profile name is required';
  }
  if (form.type !== 'direct') {
    if (!form.host.trim()) {
      return 'Host is required for proxy profiles';
    }
    const port = Number(form.port);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      return 'Port must be between 1 and 65535';
    }
  }
  if (form.type === 'vless' && !form.secrets.uuid.trim() && !hasExistingSecrets) {
    return 'VLESS UUID is required';
  }
  return null;
}








