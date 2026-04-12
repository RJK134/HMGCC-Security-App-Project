/** Application state — persisted to localStorage. */

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  currentProjectId: string | null;
  currentConversationId: string | null;
  sidebarCollapsed: boolean;
  theme: "light" | "dark";
  setCurrentProject: (id: string | null) => void;
  setCurrentConversation: (id: string | null) => void;
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentProjectId: null,
      currentConversationId: null,
      sidebarCollapsed: false,
      theme: "dark",
      setCurrentProject: (id) => set({ currentProjectId: id, currentConversationId: null }),
      setCurrentConversation: (id) => set({ currentConversationId: id }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setTheme: (theme) => {
        document.documentElement.classList.toggle("dark", theme === "dark");
        set({ theme });
      },
    }),
    { name: "sra-app-state" },
  ),
);
