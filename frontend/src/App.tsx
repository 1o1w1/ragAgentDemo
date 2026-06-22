import { useState } from "react";
import { ChatWindow } from "./components/Chat";
import { Sidebar } from "./components/Sidebar";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui, sans-serif" }}>
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <main style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <ChatWindow />
      </main>
    </div>
  );
}
