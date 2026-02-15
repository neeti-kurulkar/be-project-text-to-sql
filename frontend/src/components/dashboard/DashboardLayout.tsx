import { type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { SidebarProvider } from '../../hooks/useSidebar';

interface DashboardLayoutProps {
  children: ReactNode;
  title: string;
}

export function DashboardLayout({ children, title }: DashboardLayoutProps) {
  return (
    <SidebarProvider>
      <div className="dashboard-3d-root flex h-screen transition-smooth">
        <div className="dashboard-3d-surface flex flex-1 min-w-0">
          <Sidebar />

          <div className="flex-1 flex flex-col overflow-hidden dashboard-3d-main">
            <Topbar title={title} />

            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
}
