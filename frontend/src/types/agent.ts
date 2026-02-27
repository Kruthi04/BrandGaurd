/** Agent chat message */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  actions?: AgentAction[];
}

/** An action the agent took during processing */
export interface AgentAction {
  tool: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: "running" | "completed" | "failed";
}

/** Agent task status */
export interface AgentTask {
  id: string;
  task_type: "full_scan" | "threat_assessment" | "compliance_check";
  brand_id: string;
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  completed_at?: string;
  result?: Record<string, unknown>;
}
