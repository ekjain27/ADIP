export interface GraphSummary {
  readonly title: string;
  readonly status: "ready" | "refreshed" | "provenance-loaded";
  readonly selectedSource: string;
  readonly lastRefreshedAt: string;
  readonly nodeCount: number;
  readonly edgeCount: number;
}

export interface GraphNode {
  readonly id: string;
  readonly label: string;
  readonly type: "decision" | "evidence" | "criterion" | "governance" | "recommendation";
  readonly confidence: number;
  readonly sourceModule: string;
  readonly governanceStatus: "approved" | "review" | "pending";
  readonly relatedDecisions: readonly string[];
  readonly metadata: Record<string, string>;
  readonly x: number;
  readonly y: number;
}

export interface GraphEdge {
  readonly id: string;
  readonly sourceNodeId: string;
  readonly targetNodeId: string;
  readonly relationshipType: "supports" | "derived-from" | "governed-by" | "ranked-by" | "traces-to";
  readonly confidence: number;
  readonly provenanceReference: string;
  readonly timestamp: string;
  readonly label: string;
}

export interface ProvenanceEvent {
  readonly id: string;
  readonly title: string;
  readonly type: "extraction" | "fusion" | "state-update" | "evaluation" | "ranking" | "governance" | "recommendation";
  readonly timestamp: string;
  readonly sourceModule: string;
  readonly detail: string;
}

export interface GraphFilters {
  readonly nodeType: string;
  readonly relationshipType: string;
  readonly confidenceRange: string;
  readonly governanceStatus: string;
  readonly timePeriod: string;
  readonly provenanceSource: string;
}

export interface KnowledgeGraphSnapshot {
  readonly summary: GraphSummary;
  readonly nodes: readonly GraphNode[];
  readonly edges: readonly GraphEdge[];
  readonly timeline: readonly ProvenanceEvent[];
  readonly filters: GraphFilters;
}

export interface KnowledgeGraphProvenanceClient {
  getGraphSummary(): Promise<GraphSummary>;
  getGraphData(): Promise<{ readonly nodes: readonly GraphNode[]; readonly edges: readonly GraphEdge[] }>;
  getProvenanceTimeline(): Promise<readonly ProvenanceEvent[]>;
  getNodeDetails(nodeId: string): Promise<GraphNode | undefined>;
  getEdgeDetails(edgeId: string): Promise<GraphEdge | undefined>;
  refreshGraph(): Promise<KnowledgeGraphSnapshot>;
  loadDecisionProvenance(decisionId: string): Promise<KnowledgeGraphSnapshot>;
}
