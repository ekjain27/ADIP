export type GraphNodeType =
  | "unknown"
  | "organization"
  | "department"
  | "user"
  | "decision"
  | "evidence"
  | "alternative"
  | "risk"
  | "outcome"
  | "lesson"
  | "concept"
  | "custom";

export type GraphRelationType =
  | "belongs_to"
  | "created_by"
  | "supported_by"
  | "contradicts"
  | "depends_on"
  | "causes"
  | "mitigates"
  | "resulted_in"
  | "learned_from"
  | "decided"
  | "related_to"
  | "custom";

export interface TemporalScope {
  validFrom?: string;
  validTo?: string | null;
  observedAt?: string;
}

export interface GraphNode {
  id: string;
  type: GraphNodeType;
  canonicalName: string;
  aliases: string[];
  attributes: Record<string, unknown>;
  confidence: number;
  sourceIds: string[];
  embedding?: number[];
  createdAt: string;
  updatedAt: string;
  version: number;
}

export interface GraphEdge {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  relationType: GraphRelationType;
  weight: number;
  confidence: number;
  evidenceIds: string[];
  temporalScope?: TemporalScope;
  createdAt: string;
  updatedAt: string;
}

export interface GraphEvidence {
  id: string;
  sourceId: string;
  sourceType: string;
  excerpt?: string;
  confidence: number;
  createdAt: string;
}

export interface GraphEvent {
  id: string;
  type: string;
  entityId: string;
  occurredAt: string;
  payload: Record<string, unknown>;
}

export type GraphNodeInput = Omit<GraphNode, "createdAt" | "updatedAt" | "version"> &
  Partial<Pick<GraphNode, "createdAt" | "updatedAt" | "version">>;
export type GraphEdgeInput = Omit<GraphEdge, "createdAt" | "updatedAt"> & Partial<Pick<GraphEdge, "createdAt" | "updatedAt">>;
export type GraphEvidenceInput = Omit<GraphEvidence, "createdAt"> & Partial<Pick<GraphEvidence, "createdAt">>;

export interface GraphConstructionInput {
  nodes: GraphNodeInput[];
  edges: GraphEdgeInput[];
  evidence: GraphEvidenceInput[];
  allowSelfEdge?: boolean;
}

export interface GraphConstructionResult {
  nodesCreated: number;
  nodesMerged: number;
  edgesCreated: number;
  evidenceCreated: number;
  nodeIds: string[];
  edgeIds: string[];
  evidenceIds: string[];
  warnings: string[];
}

export interface RelationshipConfidenceFactors {
  sourceReliability: number;
  extractionConfidence: number;
  ontologyMatch: number;
  temporalValidity: number;
  crossSourceAgreement: number;
}

export interface GraphEventPayload {
  id: string;
  type:
    | "GraphNodeCreated"
    | "GraphNodeUpdated"
    | "GraphNodeMerged"
    | "GraphEdgeCreated"
    | "GraphEvidenceStored"
    | "GraphConstructionCompleted"
    | "GraphConstructionFailed";
  payload: Record<string, unknown>;
  createdAt: string;
  correlationId?: string;
}

export interface KnowledgeGraphMetricsSnapshot {
  nodesCreated: number;
  nodesUpdated: number;
  edgesCreated: number;
  evidenceStored: number;
  duplicatesMerged: number;
  validationFailures: number;
  constructionFailures: number;
  constructionSuccesses: number;
  averageNodeConfidence: number;
  averageEdgeConfidence: number;
}
