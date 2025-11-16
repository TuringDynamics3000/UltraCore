import express from 'express';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from './router.js';
import { createContext } from './context.js';

const app = express();
const PORT = 3001;

app.use(express.json());

// tRPC endpoint
app.use(
  '/api/trpc',
  createExpressMiddleware({
    router: appRouter,
    createContext,
  })
);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'ultracore-operations-portal' });
});

app.listen(PORT, () => {
  console.log(`🚀 UltraCore Operations Portal running on http://localhost:${PORT}`);
});
