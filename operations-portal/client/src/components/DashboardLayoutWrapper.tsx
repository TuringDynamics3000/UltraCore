import { Layout, LayoutProps } from 'react-admin';
import DashboardLayout from './DashboardLayout';

/**
 * Wrapper to use our existing DashboardLayout with React Admin
 * 
 * React Admin expects a Layout component, but we want to use our
 * beautiful shadcn/ui sidebar layout. This wrapper bridges the two.
 */
export const DashboardLayoutWrapper = (props: LayoutProps) => {
  return <DashboardLayout>{props.children}</DashboardLayout>;
};
