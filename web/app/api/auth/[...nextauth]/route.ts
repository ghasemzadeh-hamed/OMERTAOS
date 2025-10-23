import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import Google from 'next-auth/providers/google';
import { NextAuthOptions } from 'next-auth';

const authOptions: NextAuthOptions = {
  providers: [
    Credentials({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'text', placeholder: 'you@example.com' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (credentials?.email && credentials.password) {
          return {
            id: 'user-1',
            email: credentials.email,
            name: 'Commander'
          };
        }
        return null;
      }
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID ?? 'placeholder',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? 'placeholder'
    })
  ],
  session: { strategy: 'jwt' },
  pages: { signIn: '/login' },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = 'admin';
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.role = token.role as string;
      }
      return session;
    }
  }
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
