import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import type { NextAuthOptions } from 'next-auth';

interface ConsoleUser {
  email: string;
  password: string;
  roles: string[];
  tenant?: string;
}

const parseConsoleUsers = (): ConsoleUser[] => {
  const raw = process.env.AION_CONSOLE_USERS ?? process.env.CONSOLE_USERS;
  if (!raw) {
    return [
      {
        email: 'admin@aionos.dev',
        password: 'changeme',
        roles: ['admin', 'manager'],
        tenant: process.env.AION_CONSOLE_DEFAULT_TENANT ?? 'default',
      },
    ];
  }
  return raw
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)
    .map((entry) => {
      const [email, password, rolesPart, tenant] = entry.split(':');
      return {
        email,
        password,
        roles: (rolesPart ?? '').split('|').filter(Boolean),
        tenant: tenant || process.env.AION_CONSOLE_DEFAULT_TENANT || undefined,
      } as ConsoleUser;
    });
};

const consoleUsers = parseConsoleUsers();

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
        const user = consoleUsers.find((candidate) => candidate.email?.toLowerCase() === credentials.email.toLowerCase());
        if (!user || user.password !== credentials.password) {
          throw new Error('Invalid credentials');
        }
        return {
          id: credentials.email,
          email: credentials.email,
          roles: user.roles,
          tenantId: user.tenant,
        } as any;
      },
    }),
    ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ? [
          GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
          }),
        ]
      : []),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.roles = (user as any).roles ?? ['user'];
        token.tenantId = (user as any).tenantId;
      }
      if (account?.provider === 'google' && account.access_token) {
        token.accessToken = account.access_token;
        token.roles = ['user'];
      }
      return token;
    },
    async session({ session, token }) {
      session.user = {
        ...session.user,
        role: Array.isArray((token as any).roles) ? (token as any).roles[0] : 'user',
        roles: (token as any).roles ?? ['user'],
        tenantId: (token as any).tenantId,
      } as any;
      (session as any).accessToken = (token as any).accessToken;
      return session;
    },
  },
  pages: {
    signIn: '/sign-in',
  },
};
