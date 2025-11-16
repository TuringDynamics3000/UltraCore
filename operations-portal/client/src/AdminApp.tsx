import { Admin, Resource, CustomRoutes } from 'react-admin';
import { Route } from 'react-router-dom';
import { authProvider } from './providers/authProvider';
import { compositeDataProvider } from './providers/compositeDataProvider';

// Import existing pages (will be converted to React Admin resources)
import Home from './pages/Home';
import Portfolios from './pages/Portfolios';
import Securities from './pages/Securities';
import ESG from './pages/ESG';
import Loans from './pages/Loans';
import Agents from './pages/Agents';
import Kafka from './pages/Kafka';
import DataMesh from './pages/DataMesh';
import MCP from './pages/MCP';
import Larry from './pages/Larry';
import Login from './pages/Login';

// Custom layout with shadcn/ui
import { DashboardLayoutWrapper } from './components/DashboardLayoutWrapper';

/**
 * Main Admin App Component
 * 
 * This combines React Admin's architecture with shadcn/ui components
 * - React Admin handles: data providers, routing, auth
 * - shadcn/ui handles: visual design, components, UX
 */
export default function AdminApp() {
  return (
    <Admin
      dataProvider={compositeDataProvider}
      authProvider={authProvider}
      layout={DashboardLayoutWrapper}
      loginPage={Login}
      dashboard={Home}
      disableTelemetry
    >
      {/* Core Resources (PostgreSQL via tRPC) */}
      <Resource
        name="portfolios"
        list={Portfolios}
        // edit={PortfolioEdit}
        // show={PortfolioShow}
        // create={PortfolioCreate}
      />
      
      <Resource
        name="securities"
        list={Securities}
        // edit={SecurityEdit}
        // show={SecurityShow}
      />
      
      <Resource
        name="esg"
        list={ESG}
      />
      
      <Resource
        name="loans"
        list={Loans}
        // edit={LoanEdit}
        // show={LoanShow}
      />
      
      <Resource
        name="agents"
        list={Agents}
        // show={AgentShow}
      />
      
      {/* Kafka Resources (Event Streams) */}
      <Resource
        name="kafka-events"
        list={Kafka}
        options={{ label: 'Kafka Events' }}
      />
      
      {/* Data Mesh Resources (S3/Parquet) */}
      <Resource
        name="data-products"
        list={DataMesh}
        options={{ label: 'Data Mesh' }}
      />
      
      {/* MCP Resources */}
      <Resource
        name="mcp-tools"
        list={MCP}
        options={{ label: 'MCP Tools' }}
      />
      
      {/* Custom Routes (non-CRUD pages) */}
      <CustomRoutes>
        <Route path="/larry" element={<Larry />} />
      </CustomRoutes>
    </Admin>
  );
}
