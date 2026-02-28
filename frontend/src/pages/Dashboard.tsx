import { useNavigate } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import AccuracyTrendChart from "@/components/dashboard/AccuracyTrendChart";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useActiveBrand } from "@/lib/brand";
import {
  Shield,
  TrendingUp,
  TrendingDown,
  Radar,
  AlertTriangle,
  CheckCircle,
  Activity,
  MessageSquare,
} from "lucide-react";
import type { Alert, AlertSeverity } from "@/types";

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

const PLATFORM_LABELS: Record<string, string> = {
  chatgpt: "ChatGPT",
  claude: "Claude",
  perplexity: "Perplexity",
  gemini: "Gemini",
};

export default function Dashboard() {
  const brandId = useActiveBrand();
  const navigate = useNavigate();

  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ["brandHealth", brandId],
    queryFn: () =>
      api.get<{
        overall_accuracy: number;
        total_mentions: number;
        by_platform: Record<string, { accuracy: number; mentions: number }>;
      }>(`/graph/brand/${brandId}/health`),
  });

  const { data: alertsData } = useQuery({
    queryKey: ["mentions", brandId],
    queryFn: () =>
      api.get<{
        mentions: Alert[];
      }>(`/graph/brand/${brandId}/mentions`),
  });

  const { data: scoutsData } = useQuery({
    queryKey: ["monitoringStatus", brandId],
    queryFn: () => api.get<{ scouts: unknown[] }>(`/monitoring/status?brand_name=${encodeURIComponent(brandId)}`),
  });

  const { data: trendData } = useQuery({
    queryKey: ["trend", brandId],
    queryFn: () =>
      api.get<
        Array<{
          date: string;
          chatgpt?: number;
          claude?: number;
          perplexity?: number;
          gemini?: number;
        }>
      >(`/graph/brand/${brandId}/trend`),
  });

  const reputationScore = health ? Math.round(health.overall_accuracy) : 0;
  const scoutsCount = scoutsData?.scouts?.length ?? 0;
  const alerts = alertsData?.mentions ?? [];
  const trend = trendData ?? [];
  const totalMentions = health?.total_mentions ?? 0;
  const platforms = health?.by_platform ?? {};

  const scoreColor =
    reputationScore >= 80
      ? "text-emerald-400"
      : reputationScore >= 60
        ? "text-yellow-400"
        : "text-red-400";
  const scoreLabel =
    reputationScore >= 80
      ? "Healthy"
      : reputationScore >= 60
        ? "At Risk"
        : "Critical";
  const scoreBg =
    reputationScore >= 80
      ? "bg-emerald-500/15"
      : reputationScore >= 60
        ? "bg-yellow-500/15"
        : "bg-red-500/15";

  const criticalAlerts = alerts.filter(
    (a) => a.severity === "critical" || a.severity === "high"
  ).length;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Brand reputation overview for{" "}
              <span className="font-medium text-blue-400 capitalize">
                {brandId}
              </span>
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        {healthLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-36 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Brand Health Score */}
            <div className="p-6 rounded-xl border bg-card shadow-lg shadow-blue-950/20 hover:shadow-blue-900/20 transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2 rounded-lg ${scoreBg}`}>
                  <Shield className={`h-5 w-5 ${scoreColor}`} />
                </div>
                {reputationScore >= 60 ? (
                  <TrendingUp className="h-4 w-4 text-emerald-400" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-400" />
                )}
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">
                Health Score
              </h3>
              <p className="text-2xl font-bold">{reputationScore}/100</p>
              <p className={`text-sm mt-1 ${scoreColor}`}>{scoreLabel}</p>
            </div>

            {/* Total Mentions */}
            <div className="p-6 rounded-xl border bg-card shadow-lg shadow-blue-950/20 hover:shadow-blue-900/20 transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-blue-500/15 rounded-lg">
                  <MessageSquare className="h-5 w-5 text-blue-400" />
                </div>
                <TrendingUp className="h-4 w-4 text-emerald-400" />
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">
                Total Mentions
              </h3>
              <p className="text-2xl font-bold">{totalMentions}</p>
              <p className="text-sm text-muted-foreground mt-1">
                Across all platforms
              </p>
            </div>

            {/* Active Scouts */}
            <div className="p-6 rounded-xl border bg-card shadow-lg shadow-blue-950/20 hover:shadow-blue-900/20 transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-violet-500/15 rounded-lg">
                  <Radar className="h-5 w-5 text-violet-400" />
                </div>
                <Activity className="h-4 w-4 text-emerald-400" />
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">
                Active Scouts
              </h3>
              <p className="text-2xl font-bold">{scoutsCount}</p>
              <p className="text-sm text-muted-foreground mt-1">
                Monitors running
              </p>
            </div>

            {/* Critical Alerts */}
            <div className="p-6 rounded-xl border bg-card shadow-lg shadow-blue-950/20 hover:shadow-blue-900/20 transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="p-2 bg-red-500/15 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-red-400" />
                </div>
                {criticalAlerts > 0 ? (
                  <span className="flex h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                ) : (
                  <CheckCircle className="h-4 w-4 text-emerald-400" />
                )}
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">
                Critical Alerts
              </h3>
              <p className="text-2xl font-bold">{criticalAlerts}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {criticalAlerts > 0 ? "Need attention" : "All clear"}
              </p>
            </div>
          </div>
        )}

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend Chart -- spans 2 cols */}
          <div className="lg:col-span-2">
            {trend.length > 0 ? (
              <div className="rounded-xl border bg-card p-6 shadow-lg shadow-blue-950/20">
                <h3 className="text-lg font-semibold mb-4">
                  7-Day Accuracy Trend
                </h3>
                <AccuracyTrendChart
                  data={
                    trend as Array<{
                      date: string;
                      chatgpt: number;
                      claude: number;
                      perplexity: number;
                      gemini: number;
                    }>
                  }
                />
              </div>
            ) : (
              <div className="rounded-xl border bg-card p-6 shadow-lg shadow-blue-950/20">
                <h3 className="text-lg font-semibold mb-2">
                  7-Day Accuracy Trend
                </h3>
                <p className="text-sm text-muted-foreground py-8 text-center">
                  No trend data available yet. Mentions will appear here as
                  scouts detect them.
                </p>
              </div>
            )}
          </div>

          {/* Platform Breakdown */}
          <div className="rounded-xl border bg-card p-6 shadow-lg shadow-blue-950/20">
            <h3 className="text-lg font-semibold mb-4">Platform Breakdown</h3>
            {Object.keys(platforms).length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No platform data yet.
              </p>
            ) : (
              <div className="space-y-4">
                {Object.entries(platforms).map(([key, stat]) => {
                  const barColor =
                    stat.accuracy >= 80
                      ? "bg-emerald-500"
                      : stat.accuracy >= 60
                        ? "bg-yellow-500"
                        : "bg-red-500";
                  return (
                    <div key={key}>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-muted-foreground">
                          {PLATFORM_LABELS[key] ?? key}
                        </span>
                        <span className="text-sm font-medium">
                          {stat.accuracy.toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className={`${barColor} h-2 rounded-full transition-all duration-700`}
                          style={{ width: `${stat.accuracy}%` }}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {stat.mentions} mentions
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="rounded-xl border bg-card p-6 shadow-lg shadow-blue-950/20">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Recent Alerts</h3>
            <button
              className="text-sm text-blue-400 hover:text-blue-300 font-medium transition-colors"
              onClick={() => navigate("/threats")}
            >
              View all
            </button>
          </div>
          {alerts.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              No alerts detected. Your brand looks healthy.
            </p>
          ) : (
            <div className="space-y-2">
              {alerts.slice(0, 5).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center space-x-4 p-3 rounded-lg hover:bg-accent transition-colors cursor-pointer"
                  onClick={() => navigate("/threats")}
                >
                  <div
                    className={`p-2 rounded-lg ${
                      alert.severity === "critical"
                        ? "bg-red-500/15"
                        : alert.severity === "high"
                          ? "bg-orange-500/15"
                          : alert.severity === "medium"
                            ? "bg-yellow-500/15"
                            : "bg-blue-500/15"
                    }`}
                  >
                    <AlertTriangle
                      className={`h-4 w-4 ${
                        alert.severity === "critical"
                          ? "text-red-400"
                          : alert.severity === "high"
                            ? "text-orange-400"
                            : alert.severity === "medium"
                              ? "text-yellow-400"
                              : "text-blue-400"
                      }`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{alert.claim}</p>
                    <p className="text-xs text-muted-foreground">
                      {alert.platform}
                    </p>
                  </div>
                  <Badge
                    variant={severityVariant(alert.severity)}
                    className="shrink-0"
                  >
                    {alert.severity}
                  </Badge>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {relativeTime(alert.detected_at)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
