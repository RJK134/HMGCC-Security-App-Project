/** Top navigation bar with project selector, health, and theme toggle. */

import { Moon, PanelLeftClose, PanelLeftOpen, Shield, Sun } from "lucide-react";
import { useAppStore } from "../../stores/appStore";
import { ProjectSelector } from "../projects/ProjectSelector";
import { StatusIndicator } from "./StatusIndicator";

export function TopBar() {
  const { theme, setTheme, sidebarCollapsed, toggleSidebar } = useAppStore();

  return (
    <header className="h-12 border-b border-sra-border bg-sra-sidebar flex items-center px-3 gap-3 shrink-0">
      {/* Sidebar toggle */}
      <button
        onClick={toggleSidebar}
        className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {sidebarCollapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
      </button>

      {/* App title */}
      <div className="flex items-center gap-2">
        <Shield size={20} className="text-sra-accent" />
        <span className="font-semibold text-sm hidden md:inline">
          Security Research Assistant
        </span>
      </div>

      {/* Project selector - center */}
      <div className="flex-1 flex justify-center">
        <ProjectSelector />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        <StatusIndicator />
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
