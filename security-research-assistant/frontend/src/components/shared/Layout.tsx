/** Main application layout — top bar, sidebar, content area. */

import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { ConnectionBanner } from "./StatusIndicator";
import { TopBar } from "./TopBar";

export function Layout() {
  return (
    <div className="h-screen flex flex-col bg-sra-bg text-sra-text overflow-hidden">
      <TopBar />
      <ConnectionBanner />
      <div className="flex flex-1 min-h-0">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4">
          <Outlet />
        </main>
      </div>
      {/* Classification marking */}
      <footer className="h-6 bg-sra-sidebar border-t border-sra-border flex items-center justify-center shrink-0">
        <span className="text-[10px] font-semibold tracking-widest text-sra-muted uppercase">
          OFFICIAL
        </span>
      </footer>
    </div>
  );
}
