import { useCallback, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface GraphNode {
  id: string;
  label: string;
  type: "brand" | "platform" | "mention" | "source" | "correction";
  x?: number;
  y?: number;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  relationship: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphVisualizationProps {
  data?: GraphData;
}

const NODE_COLORS: Record<string, string> = {
  brand:      "#3b82f6",
  platform:   "#22c55e",
  mention:    "#ef4444",
  source:     "#f59e0b",
  correction: "#a855f7",
};

const NODE_SIZE: Record<string, number> = {
  brand:      10,
  platform:   8,
  mention:    6,
  source:     6,
  correction: 6,
};

function NodePanel({ node, onClose }: { node: GraphNode; onClose: () => void }) {
  const typeLabel = node.type.charAt(0).toUpperCase() + node.type.slice(1);
  return (
    <div className="absolute top-4 right-4 w-64 rounded-lg border bg-background/95 backdrop-blur shadow-lg p-4 space-y-3 z-10">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold text-sm">{node.label}</p>
          <Badge
            variant={node.type as "critical"}
            style={{ backgroundColor: NODE_COLORS[node.type], color: "#fff", border: "none" }}
            className="mt-1"
          >
            {typeLabel}
          </Badge>
        </div>
        <button className="text-muted-foreground hover:text-foreground text-xs" onClick={onClose}>✕</button>
      </div>
      <div className="text-xs text-muted-foreground space-y-1">
        <p><span className="font-medium">ID:</span> {node.id}</p>
        <p><span className="font-medium">Type:</span> {typeLabel}</p>
        {node.type === "mention" && (
          <p className="text-red-500 font-medium">⚠ Potential misinformation detected</p>
        )}
        {node.type === "correction" && (
          <p className="text-purple-500 font-medium">✓ Correction submitted</p>
        )}
        {node.type === "brand" && (
          <p className="text-blue-500 font-medium">Primary monitored entity</p>
        )}
      </div>
    </div>
  );
}

export default function GraphVisualization({ data }: GraphVisualizationProps) {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const paintNode = useCallback((node: GraphNode, ctx: CanvasRenderingContext2D) => {
    const size = NODE_SIZE[node.type] ?? 6;
    ctx.beginPath();
    ctx.arc(node.x ?? 0, node.y ?? 0, size, 0, 2 * Math.PI);
    ctx.fillStyle = NODE_COLORS[node.type] ?? "#888";
    ctx.fill();

    // Label
    ctx.font = "4px sans-serif";
    ctx.fillStyle = "#fff";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    const short = node.label.length > 12 ? node.label.slice(0, 10) + "…" : node.label;
    ctx.fillText(short, node.x ?? 0, (node.y ?? 0) + size + 5);
  }, []);

  if (!data) {
    return (
      <Card className="h-[600px]">
        <CardHeader><CardTitle className="text-lg">Knowledge Graph</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-center h-full">
          <p className="text-sm text-muted-foreground">No graph data available.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="relative h-[600px] overflow-hidden">
      <CardHeader>
        <CardTitle className="text-lg">Knowledge Graph</CardTitle>
      </CardHeader>
      <CardContent className="p-0 h-[calc(100%-64px)]" ref={containerRef}>
        <ForceGraph2D
          graphData={data}
          nodeLabel="label"
          nodeCanvasObject={paintNode as never}
          nodeCanvasObjectMode={() => "replace"}
          linkLabel={(link: GraphLink) => link.relationship}
          linkColor={() => "#94a3b8"}
          linkWidth={1}
          onNodeClick={(node) => setSelectedNode(node as GraphNode)}
          backgroundColor="transparent"
          width={containerRef.current?.clientWidth ?? 800}
          height={containerRef.current?.clientHeight ?? 536}
          cooldownTicks={100}
        />
        {selectedNode && (
          <NodePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
        )}
      </CardContent>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 flex flex-wrap gap-3 text-xs bg-background/80 rounded p-2">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1">
            <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </span>
        ))}
      </div>
    </Card>
  );
}
