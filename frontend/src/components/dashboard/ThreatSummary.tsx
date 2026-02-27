import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Threat } from "@/types";

interface ThreatSummaryProps {
  threats: Threat[];
}

export default function ThreatSummary({ threats }: ThreatSummaryProps) {
  const active = threats.filter((t) => !t.resolved);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Active Threats</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{active.length}</div>
        <p className="text-sm text-muted-foreground">
          {active.filter((t) => t.threat_level === "critical").length} critical
        </p>
      </CardContent>
    </Card>
  );
}
