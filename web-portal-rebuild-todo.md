# Operations Portal Rebuild TODO

## Phase 1: Initialize Project
- [x] Create /web-portal directory in UltraCore repo
- [x] Initialize package.json with dependencies
- [x] Set up React + Vite frontend
- [x] Set up Express + tRPC backend
- [x] Configure TypeScript
- [x] Verify dev server starts successfully

## Phase 2: Standalone Authentication
- [x] Create JWT implementation in context.ts
- [x] Create auth router in router.ts
- [x] JWT authentication working (no Manus OAuth)
- [x] Create Login.tsx page
- [x] Authentication flow complete

## Phase 3: OpenAI Integration
- [ ] Install openai npm package
- [ ] Create openai-client.ts wrapper
- [ ] Update larry-openai.ts to use direct OpenAI SDK
- [ ] Configure OPENAI_API_KEY environment variable
- [ ] Test OpenAI API connection

## Phase 4: UI Components
- [ ] Create FloatingLarryButton.tsx component
- [ ] Add floating button to App.tsx
- [ ] Create conversations and messages database tables
- [ ] Test conversation creation
- [ ] Test message sending with Larry AI

## Phase 5: Finalize & Commit
- [x] Remove debug logging
- [x] Code committed to GitHub
- [x] Pushed to TuringDynamics3000/UltraCore
- [x] Available in /web-portal directory
- [x] PowerShell setup script created
- [x] Ready for local deployment
- [x] Successfully deployed on Windows
- [x] Frontend running on port 3001
- [x] Backend running on port 3002
- [x] Login page verified working
- [x] Standalone JWT authentication confirmed
- [x] CORS issue identified and fixed
- [x] Awaiting user to pull fix and test login


## Restore Full Portal Features
- [x] Add beautiful dashboard with KPIs and charts
- [x] Add Portfolio management module (placeholder)
- [x] Add Securities universe module (placeholder)
- [x] Add ESG scoring module (placeholder)
- [x] Add UltraGrow loans module (placeholder)
- [x] Add RL Agents monitoring module (placeholder)
- [x] Add Kafka streaming module (placeholder)
- [x] Add Data Mesh module (placeholder)
- [x] Add MCP integration module (placeholder)
- [x] Add Larry AI page (placeholder)
- [ ] Implement Larry AI chat interface with OpenAI
- [ ] Add onboarding tour
- [ ] Add floating Larry button
- [ ] Improve UI/UX with modern design
