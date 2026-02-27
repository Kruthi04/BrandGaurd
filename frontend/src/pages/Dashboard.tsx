import AppLayout from "@/components/layout/AppLayout";
import BrandHealthCard from "@/components/dashboard/BrandHealthCard";
import PlatformBreakdown from "@/components/dashboard/PlatformBreakdown";
import AccuracyTrendChart from "@/components/dashboard/AccuracyTrendChart";
import RecentAlerts from "@/components/dashboard/RecentAlerts";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  mockBrandHealth,
  mockTrendData,
  mockAlerts,
} from "@/lib/mockData";
import { getActiveBrand } from "@/lib/brand";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

function ActiveScoutsCard({ count }: { count: number }) {
  return (
    <Card>
      <CardHeader><CardTitle className="text-lg">Active Scouts</CardTitle></CardHeader>
      <CardContent>
        <div className="text-4xl font-bold mt-1">{count}</div>
        <p className="text-sm text-muted-foreground mt-1">Yutori monitors running</p>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const brandId = getActiveBrand();

  const { data: rawHealth, isLoading, error } = useQuery({
    queryKey: ["brandHealth", brandId],
    queryFn: async () => {
      const res = await api.get<{
        overall_accuracy: number;
        total_mentions: number;
        accurate_mentions: number;
        threats: number;
        by_platform: Record<string, { accuracy: number; mentions: number }>;
      }>(`/graph/brand/${brandId}/health`);
      return {
        reputation_score: res.overall_accuracy ?? 0,
        total_mentions: res.total_mentions ?? 0,
        active_scouts: 0,
        by_platform: res.by_platform ?? {},
      };
    },
    enabled: !USE_MOCKS,
    retry: 1,
  });

  const healthData = (USE_MOCKS || error) ? mockBrandHealth : (rawHealth ?? mockBrandHealth);

  const { data: sourcesData } = useQuery({
    queryKey: ["brandSources", brandId],
    queryFn: async () => {
      const res = await api.get<{ sources: typeof mockAlerts } | typeof mockAlerts>(`/graph/brand/${brandId}/sources`);
      if (res && !Array.isArray(res) && Array.isArray((res as { sources: typeof mockAlerts }).sources)) {
        return (res as { sources: typeof mockAlerts }).sources;
      }
      return Array.isArray(res) ? res : [];
    },
    enabled: !USE_MOCKS,
    retry: 1,
  });

  const alertsData = (USE_MOCKS || !sourcesData) ? mockAlerts : sourcesData;

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Brand reputation overview for <strong>{brandId}</strong>.</p>
        </div>

        {/* Top row: Health Score + Platform Breakdown + Active Scouts */}
        <div className="grid gap-4 md:grid-cols-3">
          {isLoading && !USE_MOCKS ? (
            <>
              <Skeleton className="h-64" />
              <Skeleton className="h-64" />
              <Skeleton className="h-64" />
            </>
          ) : (
            <>
              <BrandHealthCard
                score={healthData.reputation_score}
                brandName={brandId}
                totalMentions={healthData.total_mentions}
              />
              <PlatformBreakdown platforms={healthData.by_platform} />
              <ActiveScoutsCard count={healthData.active_scouts} />
            </>
          )}
        </div>

        {/* Trend chart + Recent alerts */}
        <div className="grid gap-4 md:grid-cols-3">
          <AccuracyTrendChart data={mockTrendData} />
          <RecentAlerts alerts={alertsData} />
        </div>
      </div>
    </AppLayout>
  );
}
