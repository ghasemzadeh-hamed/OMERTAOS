const resolveGatewayUrl = (): string => {
  const raw =
    process.env.GATEWAY_URL ||
    process.env.AION_GATEWAY_URL ||
    process.env.NEXT_PUBLIC_GATEWAY_URL ||
    'http://gateway:8080';

  const trimmed = raw.trim();
  if (!trimmed) {
    return 'http://gateway:8080';
  }

  // Avoid trailing slashes so callers can safely append paths.
  return trimmed.replace(/\/+$/, '') || 'http://gateway:8080';
};

export const GATEWAY_HTTP_URL = resolveGatewayUrl();
