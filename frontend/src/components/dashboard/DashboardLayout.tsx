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
      <div className="flex h-screen bg-slate-50 dark:bg-ocean-950 transition-colors duration-300">
        <Sidebar />

        <div className="flex-1 flex flex-col overflow-hidden">
          <Topbar title={title} />

          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
