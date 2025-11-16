# UltraCore Operations Portal - Setup Guide

## Overview

The UltraCore Operations Portal is a **fully standalone** financial services platform designed for bank-grade security and compliance. It runs on your own infrastructure with complete data sovereignty.

## Prerequisites

- **Node.js** 18+ and npm/pnpm
- **MySQL** 8.0+ or **TiDB** (MySQL-compatible) database
- **OpenAI API Key** (for Larry AI assistant)
- **Git** for version control

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/TuringDynamics3000/UltraCore.git
cd UltraCore/operations-portal
```

### 2. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required Configuration:**

```env
# Database - Update with your MySQL credentials
DATABASE_URL=mysql://root:password@localhost:3306/ultracore_operations

# JWT Secret - Already generated, but you can regenerate with:
# openssl rand -base64 32
JWT_SECRET=your-generated-secret

# OpenAI API Key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Setup Database

````bash
# Create the database (using MySQL command line)
mysql -u root -p -e "CREATE DATABASE ultracore_operations;"

# Run migrations
pnpm db:push
```

### 5. Start Development Server

```bash
npm run dev
# or
pnpm dev
```

The portal will be available at: **http://localhost:3001**

## First Login

1. Navigate to **http://localhost:3001/login**
2. Click **"Quick Login as Admin"** button
3. You'll be logged in as the admin user

## Production Deployment

### Security Checklist

- [ ] Use strong, randomly generated `JWT_SECRET`
- [ ] Enable MySQL SSL (add `?ssl={"rejectUnauthorized":true}` to DATABASE_URL)
- [ ] Use environment-specific `.env` files (never commit to git)
- [ ] Enable database backups and point-in-time recovery
- [ ] Configure firewall rules to restrict database access
- [ ] Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Enable audit logging for all database operations
- [ ] Implement rate limiting on API endpoints
- [ ] Use HTTPS/TLS for all connections
- [ ] Regular security audits and penetration testing

### Environment Variables for Production

```env
NODE_ENV=production
DATABASE_URL=mysql://user:password@prod-db.example.com:3306/ultracore_operations
JWT_SECRET=<strong-random-secret>
OPENAI_API_KEY=<production-api-key>
```

### Deployment Options

**Option 1: Docker (Recommended)**

```bash
# Build image
docker build -t ultracore-operations-portal .

# Run container
docker run -p 3001:3001 --env-file .env ultracore-operations-portal
```

**Option 2: Traditional Server**

```bash
# Build for production
npm run build

# Start production server
NODE_ENV=production npm start
```

**Option 3: Cloud Platforms**

- **AWS**: Deploy on EC2, ECS, or EKS with RDS MySQL or Aurora MySQL
- **Azure**: App Service with Azure Database for MySQL
- **GCP**: Cloud Run with Cloud SQL MySQL
- **TiDB Cloud**: Serverless MySQL-compatible database with HTAP capabilities
- **On-Premises**: Your own infrastructure with MySQL cluster

## Architecture

### Data Layers

1. **MySQL/TiDB** - Transactional data (portfolios, securities, users)
2. **Kafka** - Event streaming (price updates, corporate actions)
3. **Data Mesh** - Analytics layer (DuckDB WASM + Parquet files)
4. **RL Agents** - Reinforcement learning for portfolio optimization

### Security Features

- **Standalone JWT Authentication** - No external OAuth dependencies
- **Row-Level Security** - Database-enforced access controls
- **Audit Logging** - Complete audit trail of all operations
- **Encrypted Connections** - TLS/SSL for all network traffic
- **Secrets Management** - Environment-based configuration

## Modules

- **Dashboard** - Overview with KPIs and system health
- **Securities Register** - 454 global securities with real-time data
- **Portfolios** - Portfolio management and holdings tracking
- **ESG Data** - Environmental, Social, Governance metrics
- **UltraGrow Loans** - Loan applications and payment tracking
- **RL Agents** - Reinforcement learning agent monitoring
- **Kafka Events** - Real-time event streaming dashboard
- **Data Mesh** - Data product catalog and analytics
- **MCP Tools** - Model Context Protocol tools registry
- **Larry AI** - Conversational AI assistant for operations

## Database Schema

The portal uses **13 core tables**:

- `users` - User accounts and authentication
- `portfolios` - Investment portfolios
- `portfolio_holdings` - Portfolio positions
- `securities` - Global securities register
- `price_history` - Historical price data
- `esg_data` - ESG metrics
- `loan_applications` - UltraGrow loan applications
- `loan_payments` - Payment tracking
- `rl_agents` - RL agent configurations
- `rl_training_runs` - Training history
- `kafka_events` - Event sourcing
- `data_products` - Data mesh catalog
- `mcp_tools` - MCP tool registry
- `audit_logs` - Compliance audit trail

## API Documentation

### tRPC Endpoints

All API endpoints are type-safe using tRPC:

- `/api/trpc/auth.*` - Authentication
- `/api/trpc/portfolios.*` - Portfolio management
- `/api/trpc/securities.*` - Securities data
- `/api/trpc/esg.*` - ESG metrics
- `/api/trpc/loans.*` - Loan management
- `/api/trpc/agents.*` - RL agent monitoring
- `/api/trpc/kafka.*` - Event streaming
- `/api/trpc/dataMesh.*` - Data products
- `/api/trpc/mcp.*` - MCP tools
- `/api/trpc/larry.*` - AI assistant

## Troubleshooting

### Database Connection Issues

```bash
# Test MySQL connection
mysql -u root -p -e "SHOW DATABASES LIKE 'ultracore_operations';"

# Check if database exists
mysql -u root -p -e "USE ultracore_operations; SHOW TABLES;"
```

### Environment Variables Not Loading

```bash
# Verify .env file exists
ls -la .env

# Check if variables are loaded
node -e "require('dotenv').config(); console.log(process.env.DATABASE_URL)"
```

### Port Already in Use

```bash
# Find process using port 3001
lsof -i :3001

# Kill the process
kill -9 <PID>
```

## Support

For issues, questions, or contributions:

- **GitHub Issues**: https://github.com/TuringDynamics3000/UltraCore/issues
- **Documentation**: See `/docs` folder
- **Email**: support@ultracore.ai

## License

Proprietary - UltraCore Financial Services Platform
