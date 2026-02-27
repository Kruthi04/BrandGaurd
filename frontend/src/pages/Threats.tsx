import { useState } from "react";
import { toast } from "sonner";
import AppLayout from "@/components/layout/AppLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { mockAlerts, type MockAlert, type AlertSeverity, type AlertStatus } from "@/lib/mockData";

function relativeTime(iso: string) {
  const h = Math.floor((Date.now() - new Date(iso).getTime()) / 3_600_000);
  if (h < 1) return "< 1h ago";
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

const SEVERITY_ORDER: AlertSeverity[] = ["critical", "high", "medium", "low"];

function AccuracyBar({ score }: { score: number }) {
  const color = score >= 70 ? "bg-green-500" : score >= 45 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">Accuracy score</span>
        <span className="font-medium">{score}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }} />
      </div>
    </div>
  );
}

function AlertCard({ alert, onStatusChange }: {
  alert: MockAlert;
  onStatusChange: (id: string, status: AlertStatus) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [investigating, setInvestigating] = useState(false);
  const [correcting, setCorrecting] = useState(false);

  async function handleInvestigate() {
    setInvestigating(true);
    await new Promise((r) => setTimeout(r, 1500));
    onStatusChange(alert.id, "investigating");
    toast.success("Investigation started — Tavily is tracing sources…");
    setInvestigating(false);
  }

  async function handleAutoCorrect() {
    setCorrecting(true);
    await new Promise((r) => setTimeout(r, 2000));
    onStatusChange(alert.id, "corrected");
    toast.success("Correction generated and submitted via Senso GEO");
    setCorrecting(false);
  }

  return (
    <Card className={`transition-all ${alert.severity === "critical" ? "border-red-300" : ""}`}>
      <CardContent className="pt-4 space-y-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 min-w-0">
            <Badge variant={alert.severity as AlertSeverity}>{alert.severity}</Badge>
            <div className="min-w-0">
              <p className="text-sm font-medium leading-snug">{alert.claim}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-muted-foreground">{alert.platform}</span>
                <span className="text-xs text-muted-foreground">·</span>
                <span className="text-xs text-muted-foreground">{relativeTime(alert.detected_at)}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Badge variant={alert.status as AlertStatus}>{alert.status}</Badge>
            <button
              className="text-xs text-muted-foreground hover:text-foreground"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? "▲" : "▼"}
            </button>
          </div>
        </div>

        <AccuracyBar score={alert.accuracy_score} />

        {/* Expanded detail */}
        {expanded && (
          <div className="space-y-3 pt-2 border-t">
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Context</p>
              <p className="text-sm">{alert.context}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">Suggested correction</p>
              <p className="text-sm text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/30 rounded p-2">
                {alert.suggested_correction}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                disabled={investigating || alert.status === "investigating" || alert.status === "corrected"}
                onClick={handleInvestigate}
              >
                {investigating ? "Investigating…" : "Investigate"}
              </Button>
              <Button
                size="sm"
                disabled={correcting || alert.status === "corrected"}
                onClick={handleAutoCorrect}
              >
                {correcting ? "Correcting…" : "Auto-Correct"}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Threats() {
  const [alerts, setAlerts] = useState(
    [...mockAlerts].sort(
      (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity)
    )
  );
  const [filterSeverity, setFilterSeverity] = useState<AlertSeverity | "all">("all");
  const [filterStatus, setFilterStatus]     = useState<AlertStatus | "all">("all");

  function updateStatus(id: string, status: AlertStatus) {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, status } : a)));
  }

  const filtered = alerts.filter(
    (a) =>
      (filterSeverity === "all" || a.severity === filterSeverity) &&
      (filterStatus   === "all" || a.status   === filterStatus)
  );

  const openCount     = alerts.filter((a) => a.status === "open").length;
  const criticalCount = alerts.filter((a) => a.severity === "critical").length;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Threat Monitor</h1>
            <p className="text-muted-foreground">Track and respond to brand reputation threats.</p>
          </div>
          <div className="flex gap-3 text-sm">
            <div className="rounded-lg border px-3 py-2 text-center">
              <div className="text-2xl font-bold text-red-600">{openCount}</div>
              <div className="text-xs text-muted-foreground">Open</div>
            </div>
            <div className="rounded-lg border px-3 py-2 text-center">
              <div className="text-2xl font-bold text-orange-600">{criticalCount}</div>
              <div className="text-xs text-muted-foreground">Critical</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-3 flex-wrap">
          <select
            className="rounded-md border px-3 py-1.5 text-sm"
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value as AlertSeverity | "all")}
          >
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            className="rounded-md border px-3 py-1.5 text-sm"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as AlertStatus | "all")}
          >
            <option value="all">All statuses</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="corrected">Corrected</option>
            <option value="dismissed">Dismissed</option>
          </select>
        </div>

        {/* Alert list */}
        {filtered.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">No threats match your filters.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {filtered.map((alert) => (
              <AlertCard key={alert.id} alert={alert} onStatusChange={updateStatus} />
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
