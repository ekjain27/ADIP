import type { GraphEdge, GraphNode, GraphSummary, KnowledgeGraphProvenanceClient, KnowledgeGraphSnapshot, ProvenanceEvent } from "./types.js";

export const PROVENANCE_TIMELINE_STORAGE_KEY = "project1.ux003.provenance.timeline.v1";

const fallbackNodes: readonly GraphNode[] = [
  { id: "NODE-DEC-001", label: "Enterprise Expansion Decision", type: "decision", confidence: 0.96, sourceModule: "DIE Core", governanceStatus: "approved", relatedDecisions: ["DEC-2026-001"], metadata: { owner: "Strategy Office", state: "ranked" }, x: 50, y: 45 },
  { id: "NODE-EVD-001", label: "Regional adoption evidence", type: "evidence", confidence: 0.9, sourceModule: "DKE Evidence Audit", governanceStatus: "approved", relatedDecisions: ["DEC-2026-001"], metadata: { source: "market-readiness", freshness: "current" }, x: 245, y: 30 },
  { id: "NODE-CRT-001", label: "Governance fit criterion", type: "criterion", confidence: 0.88, sourceModule: "DIE Evaluation", governanceStatus: "review", relatedDecisions: ["DEC-2026-001"], metadata: { weight: "25%", policy: "enterprise-governance" }, x: 250, y: 160 },
  { id: "NODE-GOV-001", label: "Policy-gated governance mesh", type: "governance", confidence: 0.93, sourceModule: "DIE Governance", governanceStatus: "approved", relatedDecisions: ["DEC-2026-001"], metadata: { control: "approval-gate", status: "checked" }, x: 455, y: 92 },
  { id: "NODE-REC-001", label: "Phased rollout recommendation", type: "recommendation", confidence: 0.91, sourceModule: "DIE Recommendation Service", governanceStatus: "approved", relatedDecisions: ["DEC-2026-001"], metadata: { rank: "1", alternative: "ALT-A" }, x: 650, y: 92 },
];

const fallbackEdges: readonly GraphEdge[] = [
  { id: "EDGE-001", sourceNodeId: "NODE-EVD-001", targetNodeId: "NODE-DEC-001", relationshipType: "supports", confidence: 0.9, provenanceReference: "PROV-EVD-001", timestamp: "2026-07-01T08:15:00.000Z", label: "supports" },
  { id: "EDGE-002", sourceNodeId: "NODE-DEC-001", targetNodeId: "NODE-CRT-001", relationshipType: "traces-to", confidence: 0.88, provenanceReference: "PROV-CRT-001", timestamp: "2026-07-01T08:40:00.000Z", label: "traces to" },
  { id: "EDGE-003", sourceNodeId: "NODE-CRT-001", targetNodeId: "NODE-GOV-001", relationshipType: "governed-by", confidence: 0.93, provenanceReference: "PROV-GOV-001", timestamp: "2026-07-01T09:05:00.000Z", label: "governed by" },
  { id: "EDGE-004", sourceNodeId: "NODE-GOV-001", targetNodeId: "NODE-REC-001", relationshipType: "ranked-by", confidence: 0.91, provenanceReference: "PROV-RNK-001", timestamp: "2026-07-01T09:20:00.000Z", label: "ranked by" },
];

const fallbackTimeline: readonly ProvenanceEvent[] = [
  { id: "PROV-EXT-001", title: "Evidence extraction event", type: "extraction", timestamp: "2026-07-01T08:10:00.000Z", sourceModule: "DKE Evidence Audit", detail: "Regional adoption evidence extracted for decision context." },
  { id: "PROV-FUS-001", title: "Knowledge fusion event", type: "fusion", timestamp: "2026-07-01T08:25:00.000Z", sourceModule: "DKE Knowledge Retrieval", detail: "Evidence and criteria relationships fused into graph snapshot." },
  { id: "PROV-STA-001", title: "Decision state update", type: "state-update", timestamp: "2026-07-01T08:45:00.000Z", sourceModule: "DIE Core", detail: "Decision state linked to alternatives and criteria." },
  { id: "PROV-EVL-001", title: "Evaluation event", type: "evaluation", timestamp: "2026-07-01T09:05:00.000Z", sourceModule: "DIE Evaluation", detail: "Backend evaluation outputs attached to criterion nodes." },
  { id: "PROV-RNK-001", title: "Ranking event", type: "ranking", timestamp: "2026-07-01T09:20:00.000Z", sourceModule: "DIE Ranking", detail: "Alternative ranking connected to recommendation node." },
  { id: "PROV-GOV-001", title: "Governance check", type: "governance", timestamp: "2026-07-01T09:30:00.000Z", sourceModule: "DIE Governance", detail: "Policy gate validated recommendation readiness." },
  { id: "PROV-REC-001", title: "Recommendation event", type: "recommendation", timestamp: "2026-07-01T09:35:00.000Z", sourceModule: "DIE Recommendation Service", detail: "Recommendation delivery package emitted by backend service." },
];

const fallbackSnapshot: KnowledgeGraphSnapshot = {
  summary: {
    title: "Knowledge Graph & Provenance Explorer",
    status: "ready",
    selectedSource: "Decision Provenance Graph",
    lastRefreshedAt: "2026-07-01T09:35:00.000Z",
    nodeCount: fallbackNodes.length,
    edgeCount: fallbackEdges.length,
  },
  nodes: fallbackNodes,
  edges: fallbackEdges,
  timeline: fallbackTimeline,
  filters: {
    nodeType: "all",
    relationshipType: "all",
    confidenceRange: "0.80-1.00",
    governanceStatus: "all",
    timePeriod: "last-24h",
    provenanceSource: "all",
  },
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isProvenanceEvent(value: unknown): value is ProvenanceEvent {
  if (!isRecord(value)) return false;
  return (
    typeof value.id === "string"
    && typeof value.title === "string"
    && typeof value.type === "string"
    && typeof value.timestamp === "string"
    && typeof value.sourceModule === "string"
    && typeof value.detail === "string"
  );
}

function getProvenanceTimelineStorage(): Storage | null {
  try {
    if (typeof localStorage !== "undefined") return localStorage;
  } catch {
    return null;
  }
  return null;
}

function readStoredProvenanceTimeline(): readonly ProvenanceEvent[] | null {
  const storage = getProvenanceTimelineStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(PROVENANCE_TIMELINE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed) || !parsed.every(isProvenanceEvent)) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeStoredProvenanceTimeline(timeline: readonly ProvenanceEvent[]): void {
  const storage = getProvenanceTimelineStorage();
  if (!storage) return;
  try {
    storage.setItem(PROVENANCE_TIMELINE_STORAGE_KEY, JSON.stringify(timeline));
  } catch {
    // localStorage persistence is optional for the UX preview.
  }
}

function createLoadedProvenanceTimeline(timestamp: string): readonly ProvenanceEvent[] {
  return [
    { id: "PROV-LOAD-ACTION", title: "Full Provenance Path Loaded", type: "state-update", timestamp, sourceModule: "UX Adapter", detail: "Full provenance path loaded from current graph snapshot." },
    { id: "PROV-DEC-CREATED", title: "Decision created", type: "state-update", timestamp, sourceModule: "DIE Core", detail: "Decision node is included in the provenance path." },
    { id: "PROV-EVD-LINKED", title: "Evidence linked", type: "extraction", timestamp, sourceModule: "DKE Evidence Audit", detail: "Evidence node is linked to the decision through the supports relationship." },
    { id: "PROV-CRT-TRACED", title: "Governance criterion traced", type: "evaluation", timestamp, sourceModule: "DIE Evaluation", detail: "Governance criterion is traced from the decision context." },
    { id: "PROV-MESH-APPLIED", title: "Governance mesh applied", type: "governance", timestamp, sourceModule: "DIE Governance", detail: "Governance mesh node is applied to the criterion path." },
    { id: "PROV-RANK-COMPLETED", title: "Ranking completed", type: "ranking", timestamp, sourceModule: "DIE Ranking", detail: "Ranking relationship connects governance output to the recommendation node." },
    { id: "PROV-REC-GENERATED", title: "Recommendation generated", type: "recommendation", timestamp, sourceModule: "DIE Recommendation Service", detail: "Recommendation node completes the visible provenance path." },
  ];
}

export class DeterministicKnowledgeGraphProvenanceClient implements KnowledgeGraphProvenanceClient {
  private timeline: readonly ProvenanceEvent[] = readStoredProvenanceTimeline() ?? fallbackTimeline;

  async getGraphSummary(): Promise<GraphSummary> {
    return this.timeline !== fallbackTimeline
      ? { ...fallbackSnapshot.summary, status: "provenance-loaded", selectedSource: "Decision Provenance Graph: DEC-2026-001", lastRefreshedAt: this.timeline[0]?.timestamp ?? fallbackSnapshot.summary.lastRefreshedAt }
      : fallbackSnapshot.summary;
  }

  async getGraphData(): Promise<{ readonly nodes: readonly GraphNode[]; readonly edges: readonly GraphEdge[] }> {
    return { nodes: fallbackSnapshot.nodes, edges: fallbackSnapshot.edges };
  }

  async getProvenanceTimeline(): Promise<readonly ProvenanceEvent[]> {
    return this.timeline;
  }

  async getNodeDetails(nodeId: string): Promise<GraphNode | undefined> {
    return fallbackSnapshot.nodes.find((node) => node.id === nodeId);
  }

  async getEdgeDetails(edgeId: string): Promise<GraphEdge | undefined> {
    return fallbackSnapshot.edges.find((edge) => edge.id === edgeId);
  }

  async refreshGraph(): Promise<KnowledgeGraphSnapshot> {
    return { ...fallbackSnapshot, timeline: this.timeline, summary: { ...fallbackSnapshot.summary, status: "refreshed", lastRefreshedAt: new Date().toISOString() } };
  }

  async loadDecisionProvenance(decisionId: string): Promise<KnowledgeGraphSnapshot> {
    const timestamp = new Date().toISOString();
    this.timeline = createLoadedProvenanceTimeline(timestamp);
    writeStoredProvenanceTimeline(this.timeline);
    return {
      ...fallbackSnapshot,
      summary: { ...fallbackSnapshot.summary, status: "provenance-loaded", selectedSource: `Decision Provenance Graph: ${decisionId}`, lastRefreshedAt: timestamp },
      timeline: this.timeline,
    };
  }
}

export function createKnowledgeGraphProvenanceClient(): KnowledgeGraphProvenanceClient {
  return new DeterministicKnowledgeGraphProvenanceClient();
}

export async function getKnowledgeGraphSnapshot(client: KnowledgeGraphProvenanceClient): Promise<KnowledgeGraphSnapshot> {
  const [summary, graphData, timeline] = await Promise.all([client.getGraphSummary(), client.getGraphData(), client.getProvenanceTimeline()]);
  return { summary, nodes: graphData.nodes, edges: graphData.edges, timeline, filters: fallbackSnapshot.filters };
}
