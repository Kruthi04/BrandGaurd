import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Monitoring from "./pages/Monitoring";
import GraphExplorer from "./pages/GraphExplorer";
import Threats from "./pages/Threats";
import AgentChat from "./pages/AgentChat";
import Settings from "./pages/Settings";
import Corrections from "./pages/Corrections";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <BrowserRouter>
        <Routes>
          <Route path="/"            element={<Dashboard />} />
          <Route path="/monitoring"  element={<Monitoring />} />
          <Route path="/graph"       element={<GraphExplorer />} />
          <Route path="/threats"     element={<Threats />} />
          <Route path="/corrections" element={<Corrections />} />
          <Route path="/agent"       element={<AgentChat />} />
          <Route path="/settings"    element={<Settings />} />
          <Route path="*"            element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
