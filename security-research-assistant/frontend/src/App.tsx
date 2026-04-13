import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/shared/Layout";
import { FirstRunWizard } from "./components/setup/FirstRunWizard";
import { ChatPage } from "./pages/ChatPage";
import { LibraryPage } from "./pages/LibraryPage";
import { DocumentDetailPage } from "./pages/DocumentDetailPage";
import { ArchitecturePage } from "./pages/ArchitecturePage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";

export function App() {
  const [showWizard, setShowWizard] = useState(
    () => !localStorage.getItem("sra-setup-complete"),
  );

  if (showWizard) {
    return (
      <FirstRunWizard
        onComplete={() => {
          localStorage.setItem("sra-setup-complete", "true");
          setShowWizard(false);
        }}
      />
    );
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/library/:documentId" element={<DocumentDetailPage />} />
        <Route path="/architecture" element={<ArchitecturePage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
