/** Transient UI state — not persisted. */

import { create } from "zustand";

type ActiveView = "chat" | "library" | "architecture" | "reports" | "settings";

interface UiState {
  isSourcePanelOpen: boolean;
  isImportModalOpen: boolean;
  activeView: ActiveView;
  toggleSourcePanel: () => void;
  toggleImportModal: () => void;
  setActiveView: (view: ActiveView) => void;
}

export const useUiStore = create<UiState>()((set) => ({
  isSourcePanelOpen: false,
  isImportModalOpen: false,
  activeView: "chat",
  toggleSourcePanel: () => set((s) => ({ isSourcePanelOpen: !s.isSourcePanelOpen })),
  toggleImportModal: () => set((s) => ({ isImportModalOpen: !s.isImportModalOpen })),
  setActiveView: (view) => set({ activeView: view }),
}));
