import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import type { NextAuthOptions } from 'next-auth';

async function fetchGateway<T>(path: string, init?: RequestInit): Promise<T> {
  const base = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080';
  const response = await fetch(`${base}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`Gateway request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export const authOptions: NextAuthOptions = {
  session: {
    strategy: 'jwt',
    maxAge: 60 * 60,
  },
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials.password) {
          throw new Error('Missing credentials');
        }
        const result = await fetchGateway<{ token: string; role: string; tenantId?: string }>(
          '/v1/auth/login',
          {
            method: 'POST',
            body: JSON.stringify({ email: credentials.email, password: credentials.password }),
          }
        );
        return {
          id: credentials.email,
          email: credentials.email,
          role: result.role,
          token: result.token,
          tenantId: result.tenantId,
        } as any;
      },
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? '',
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.role = (user as any).role ?? 'user';
        token.tenantId = (user as any).tenantId;
        token.accessToken = (user as any).token ?? token.accessToken;
      }
      if (account?.provider === 'google' && account.access_token) {
        token.accessToken = account.access_token;
      }
      return token;
    },
    async session({ session, token }) {
      session.user = {
        ...session.user,
        role: (token as any).role ?? 'user',
        tenantId: (token as any).tenantId,
      } as any;
      (session as any).accessToken = (token as any).accessToken;
      return session;
    },
  },
  pages: {
    signIn: '/sign-in',
  },
  events: {
    async signOut({ token }) {
      if (token?.accessToken) {
        try {
          await fetchGateway('/v1/auth/logout', {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${token.accessToken}`,
            },
          });
        } catch (error) {
          console.warn('Failed to notify gateway logout', error);
        }
      }
    },
  },
};
