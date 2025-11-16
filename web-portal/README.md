# UltraCore Operations Portal

Standalone operations dashboard for UltraCore wealth management platform with **complete independence from Manus infrastructure**.

## Features

✅ **Standalone JWT Authentication** - No Manus OAuth dependency  
✅ **Direct OpenAI Integration** - GPT-4o for Larry AI assistant  
✅ **Type-Safe API** - tRPC for end-to-end type safety  
✅ **Modern Stack** - React 18 + Vite + Express + TypeScript  

## Quick Start

```bash
# Install dependencies
npm install

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export JWT_SECRET="your-secret-key"

# Start development server
npm run dev
```

The portal will run on:
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001

## Project Structure

```
web-portal/
├── client/          # React frontend
│   └── src/
│       ├── pages/   # Page components
│       ├── lib/     # tRPC client
│       └── App.tsx  # Main app
├── server/          # Express + tRPC backend
│   ├── index.ts     # Server entry
│   ├── router.ts    # tRPC routes
│   └── context.ts   # Auth context
└── shared/          # Shared types
```

## Authentication

The portal uses JWT tokens for authentication. Default quick-login creates an admin user:
- Email: admin@ultracore.com
- Role: admin

## Integration with UltraCore Backend

The portal can connect to the UltraCore FastAPI backend (port 8000) for:
- Portfolio data
- Securities information
- ESG metrics
- RL agent monitoring
- Kafka event streams

## Deployment

1. Build the project: `npm run build`
2. Serve the `dist` folder
3. Ensure environment variables are set
4. Backend runs on port 3001

## License

Part of the UltraCore wealth management platform.
