import { useState } from "react";
import AppLayout from "@/components/layout/AppLayout";
import GraphVisualization from "@/components/graph/GraphVisualization";
import { Skeleton } from "@/components/ui/skeleton";
import { mockGraphData } from "@/lib/mockData";
import { getActiveBrand } from "@/lib/brand";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface GraphNode {
  id: string;
  label: string;
  type: "brand" | "platform" | "mention" | "source" | "correction";
}

interface GraphLink {
  source: string;
  target: string;
  relationship: string;
}

interface NetworkResponse {
  nodes: GraphNode[];
  edges: GraphLink[];
}

type NodeType = "all" | "brand" | "platform" | "mention" | "source" | "correction";

export default function GraphExplorer() {
  const brandId = getActiveBrand();
  const [filterType, setFilterType] = useState<NodeType>("all");

  const { data: networkData, isLoading, error } = useQuery({
    queryKey: ["graphNetwork", brandId],
    queryFn: async () => {
      const res = await api.get<NetworkResponse>(`/graph/brand/${brandId}/network`);
      // Backend returns { nodes, edges } but the graph component expects { nodes, links }
      return {
        nodes: res.nodes,
        links: res.edges ?? (res as unknown as { links: GraphLink[] }).links ?? [],
      };
    },
    retry: 1,
  });

  // Use real data if available, fall back to mock on error
  const graphData = (error || !networkData) ? mockGraphData : networkData;

  const filtered = {
    nodes: filterType === "all"
      ? graphData.nodes
      : graphData.nodes.filter((n) => n.type === filterType),
    links: graphData.links,
  };

  const counts = graphData.nodes.reduce<Record<string, number>>((acc, n) => {
    acc[n.type] = (acc[n.type] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Graph Explorer</h1>
            <p className="text-muted-foreground">
              Visualize brand entity relationships from the Neo4j knowledge graph.
            </p>
          </div>

          {/* Stats */}
          <div className="flex gap-3 text-sm flex-wrap">
            {Object.entries(counts).map(([type, count]) => (
              <div key={type} className="rounded-lg border px-3 py-2 text-center">
                <div className="text-xl font-bold">{count}</div>
                <div className="text-xs text-muted-foreground capitalize">{type}s</div>
              </div>
            ))}
          </div>
        </div>

        {/* Node type filter */}
        <div className="flex gap-2 flex-wrap">
          {(["all", "brand", "platform", "mention", "source", "correction"] as NodeType[]).map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors capitalize ${
                filterType === t
                  ? "bg-primary text-primary-foreground border-primary"
                  : "hover:bg-muted"
              }`}
            >
              {t === "all" ? "All nodes" : t}
            </button>
          ))}
        </div>

        {isLoading ? (
          <Skeleton className="h-[600px]" />
        ) : (
          <GraphVisualization data={filtered as never} />
        )}
      </div>
    </AppLayout>
  );
}
