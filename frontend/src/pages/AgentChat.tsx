import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AgentChat() {
  const [input, setInput] = useState("");

  // TODO: Implement chat with agent API
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agent Chat</h1>
          <p className="text-muted-foreground">
            Interact with the BrandGuard AI agent.
          </p>
        </div>
        <Card className="h-[500px] flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg">Chat</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto mb-4">
              <p className="text-sm text-muted-foreground">
                Start a conversation with the BrandGuard agent. Ask it to scan your brand,
                assess threats, or check content compliance.
              </p>
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask the agent..."
                className="flex-1 rounded-md border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <Button>Send</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
