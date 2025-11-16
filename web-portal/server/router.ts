import { initTRPC, TRPCError } from '@trpc/server';
import { z } from 'zod';
import jwt from 'jsonwebtoken';
import type { Context } from './context.js';

const JWT_SECRET = process.env.JWT_SECRET || 'ultracore-dev-secret-change-in-production';

const t = initTRPC.context<Context>().create();

const isAuthed = t.middleware(({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED', message: 'Please login' });
  }
  return next({ ctx: { ...ctx, user: ctx.user } });
});

export const publicProcedure = t.procedure;
export const protectedProcedure = t.procedure.use(isAuthed);

export const appRouter = t.router({
  auth: t.router({
    me: publicProcedure.query(({ ctx }) => ctx.user),
    
    quickLogin: publicProcedure.mutation(() => {
      const user = {
        id: 1,
        email: 'admin@ultracore.com',
        name: 'Admin',
        role: 'admin' as const,
      };
      
      const token = jwt.sign(user, JWT_SECRET, { expiresIn: '7d' });
      return { token, user };
    }),
    
    logout: publicProcedure.mutation(() => {
      return { success: true };
    }),
  }),
  
  larry: t.router({
    test: protectedProcedure.query(() => {
      return { message: 'Larry AI is ready!' };
    }),
  }),
});

export type AppRouter = typeof appRouter;
