import { Request, Response } from 'express';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'ultracore-dev-secret-change-in-production';

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'user';
}

export interface Context {
  req: Request;
  res: Response;
  user: User | null;
}

export function createContext({ req, res }: { req: Request; res: Response }): Context {
  const authHeader = req.headers.authorization;
  let user: User | null = null;

  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    try {
      const decoded = jwt.verify(token, JWT_SECRET) as User;
      user = decoded;
    } catch (error) {
      // Invalid token, user remains null
    }
  }

  return { req, res, user };
}
