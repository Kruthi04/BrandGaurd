import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Alert, AlertSeverity } from "@/types";

interface RecentAlertsProps {
  alerts: Alert[];
}

function severityVariant(s: AlertSeverity) {
  return s as "critical" | "high" | "medium" | "low";
}

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function RecentAlerts({ alerts }: RecentAlertsProps) {
  const navigate = useNavigate();

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Recent Alerts</CardTitle>
        <button
          className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          onClick={() => navigate("/threats")}
        >
          View all →
        </button>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <p className="text-sm text-muted-foreground">No alerts detected. Your brand is healthy.</p>
        ) : (
          <ul className="space-y-3">
            {alerts.slice(0, 5).map((alert) => (
              <li
                key={alert.id}
                className="flex items-start justify-between gap-3 border-b pb-3 last:border-0 cursor-pointer hover:bg-muted/30 rounded px-1 -mx-1 transition-colors"
                onClick={() => navigate("/threats")}
              >
                <div className="flex items-start gap-3 min-w-0">
                  <Badge variant={severityVariant(alert.severity)} className="mt-0.5 shrink-0">
                    {alert.severity}
                  </Badge>
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{alert.claim}</p>
                    <p className="text-xs text-muted-foreground">{alert.platform}</p>
                  </div>
                </div>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {relativeTime(alert.detected_at)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
