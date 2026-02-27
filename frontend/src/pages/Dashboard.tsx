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
  MOCK_BRAND_NAME,
} from "@/lib/mockData";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true" || true; // default to mocks

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
  const { data: health, isLoading } = useQuery({
    queryKey: ["brandHealth"],
    queryFn: () => api.get<typeof mockBrandHealth>("/graph/brand/default/health"),
    enabled: !USE_MOCKS,
    retry: false,
  });

  const healthData = USE_MOCKS ? mockBrandHealth : (health ?? mockBrandHealth);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Brand reputation overview at a glance.</p>
        </div>

        {/* Top row: Health Score + Platform Breakdown + Active Scouts */}
        <div className="grid gap-4 md:grid-cols-3">
          {isLoading ? (
            <>
              <Skeleton className="h-64" />
              <Skeleton className="h-64" />
              <Skeleton className="h-64" />
            </>
          ) : (
            <>
              <BrandHealthCard
                score={healthData.reputation_score}
                brandName={MOCK_BRAND_NAME}
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
          <RecentAlerts alerts={mockAlerts} />
        </div>
      </div>
    </AppLayout>
  );
}
