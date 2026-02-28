import { Component, type ReactNode } from "react";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Monitoring from "./pages/Monitoring";
import GraphExplorer from "./pages/GraphExplorer";
import Threats from "./pages/Threats";
import AgentChat from "./pages/AgentChat";
import Settings from "./pages/Settings";
import Corrections from "./pages/Corrections";
import NotFound from "./pages/NotFound";

class ErrorBoundary extends Component<
  { children: ReactNode },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, fontFamily: "monospace" }}>
          <h1 style={{ color: "red" }}>React Error</h1>
          <pre style={{ whiteSpace: "pre-wrap" }}>
            {this.state.error.message}
          </pre>
          <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, opacity: 0.7 }}>
            {this.state.error.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <Routes>
            <Route path="/"            element={<Landing />} />
            <Route path="/dashboard"   element={<Dashboard />} />
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
  </ErrorBoundary>
);

export default App;
