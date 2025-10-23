import { FastifyInstance, FastifyRequest } from 'fastify';

export interface AuthUser {
  sub: string;
  role: 'admin' | 'manager' | 'user';
  email: string;
}

export const registerAuth = async (app: FastifyInstance, secret: string) => {
  app.register(import('@fastify/jwt'), {
    secret,
    sign: { algorithm: 'HS256' }
  });

  app.decorate(
    'authenticate',
    async (request: FastifyRequest): Promise<void> => {
      try {
        await request.jwtVerify<AuthUser>();
      } catch (err) {
        throw app.httpErrors.unauthorized('Invalid token');
      }
    }
  );
};

declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: FastifyRequest) => Promise<void>;
  }
  interface FastifyRequest {
    user: AuthUser;
  }
}
