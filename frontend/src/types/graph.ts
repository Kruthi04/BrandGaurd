/** Node in the knowledge graph */
export interface GraphNode {
  id: string;
  label: string;
  type: "brand" | "person" | "platform" | "mention" | "threat" | "source" | "correction";
  properties?: Record<string, unknown>;
}

/** Edge in the knowledge graph */
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  properties?: Record<string, unknown>;
}

/** Graph data for visualization */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
