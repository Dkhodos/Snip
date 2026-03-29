import { Outlet } from "@tanstack/react-router";
import { Header } from "./header";
import { Sidebar } from "./sidebar";

export function AppShell() {
  return (
    <div className="flex h-screen">
      <aside className="hidden lg:flex">
        <Sidebar />
      </aside>
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex min-h-0 flex-1 flex-col p-6">
          <div className="min-h-0 flex-1 animate-in fade-in duration-200">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
