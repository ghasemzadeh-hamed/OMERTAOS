import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcrypt';
import { prisma } from './prisma';

export const authOptions: NextAuthOptions = {
  session: { strategy: 'jwt' },
  pages: { signIn: '/login' },
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        identifier: { label: 'Username or Email', type: 'text' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const rawIdentifier = credentials?.identifier?.trim();
        const password = credentials?.password ?? '';
        if (!rawIdentifier || !password) {
          return null;
        }

        const identifierLower = rawIdentifier.toLowerCase();
        const candidateEmails = new Set<string>([
          rawIdentifier,
          identifierLower,
        ]);
        if (!identifierLower.includes('@')) {
          candidateEmails.add(`${identifierLower}@localhost`);
          candidateEmails.add(`${identifierLower}@aion.local`);
        }

        let user = null;
        try {
          user = await prisma.user.findFirst({
            where: {
              email: {
                in: Array.from(candidateEmails),
              },
            },
          });
        } catch (error) {
          console.error('User lookup failed', error);
          return null;
        }

        if (!user) {
          return null;
        }

        const ok = await bcrypt.compare(password, user.password);
        if (!ok) {
          return null;
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name ?? '',
          role: user.role,
        } as any;
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role ?? 'USER';
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).role = (token as any).role ?? 'USER';
      }
      return session;
    },
  },
};
