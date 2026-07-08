export type Confidence = number;

export interface VisibilityPolicy {
  hidden?: boolean;
  allowedRoles?: readonly string[];
}

export interface GraphNode {
  id: string;
  canonicalName: string;
  type: string;
  labels?: readonly string[];
  properties?: Readonly<Record<string, unknown>>;
  confidence?: Confidence;
  evidenceIds?: readonly string[];
  visibility?: VisibilityPolicy;
}

export interface GraphEdge {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  type: string;
  confidence?: Confidence;
  evidenceConfidence?: Confidence;
  validFrom?: string;
  validTo?: string;
  evidenceIds?: readonly string[];
  visibility?: VisibilityPolicy;
}

export interface ReasoningVisibilityContext {
  roles?: readonly string[];
  allowedNodeIds?: readonly string[];
  allowedEvidenceIds?: readonly string[];
}

export interface ReasoningQuery {
  sourceNodeId?: string;
  sourceCanonicalName?: string;
  targetNodeId?: string;
  targetCanonicalName?: string;
  relationshipTypes?: readonly string[];
  reasoningDate?: string;
  maxDepth?: number;
  minConfidence?: Confidence;
  includeConflicts?: boolean;
  includeMissingLinkSuggestions?: boolean;
  visibility?: ReasoningVisibilityContext;
}

export interface ReasoningPath {
  id: string;
  nodes: readonly GraphNode[];
  edges: readonly GraphEdge[];
  relationshipTypes: readonly string[];
  confidence: Confidence;
  temporalValidity: Confidence;
}

export interface ReasoningRule {
  id: string;
  name: string;
  description?: string;
  when: {
    path: readonly string[];
    sourceType?: string;
    targetType?: string;
  };
  then: {
    relationshipType: string;
  };
  confidenceModifier: Confidence;
  enabled?: boolean;
}

export interface ReasoningConclusion {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  relationshipType: string;
  confidence: Confidence;
  ruleId?: string;
  pathId?: string;
  evidenceIds: readonly string[];
  summary: string;
}

export type ReasoningConflictType =
  | "CONTRADICTORY_RELATIONSHIP"
  | "TEMPORAL_OVERLAP"
  | "ONTOLOGY_MISMATCH"
  | "CONFIDENCE_DISAGREEMENT"
  | "CIRCULAR_DEPENDENCY";

export interface ReasoningConflict {
  id: string;
  type: ReasoningConflictType;
  severity: "low" | "medium" | "high";
  nodeIds: readonly string[];
  edgeIds: readonly string[];
  description: string;
  confidence: Confidence;
}

export interface MissingLinkSuggestion {
  id: string;
  sourceNodeId: string;
  targetNodeId: string;
  relationshipType: string;
  confidence: Confidence;
  supportingPathIds: readonly string[];
  reason: string;
}

export interface ExplanationStep {
  id: string;
  kind: "path" | "rule" | "ontology" | "temporal" | "confidence" | "conflict" | "missing-link";
  description: string;
  inputConfidence?: Confidence;
  outputConfidence?: Confidence;
  evidenceIds: readonly string[];
}

export interface ExplanationTrace {
  id: string;
  summary: string;
  steps: readonly ExplanationStep[];
  appliedRuleIds: readonly string[];
  evidenceIds: readonly string[];
  confidenceEvolution: readonly Confidence[];
}

export interface ReasoningMetrics {
  reasoningRequests: number;
  reasoningSuccesses: number;
  reasoningFailures: number;
  averageReasoningTime: number;
  pathsEvaluated: number;
  rulesApplied: number;
  conflictsDetected: number;
  missingLinksSuggested: number;
  averageConfidence: Confidence;
}

export interface TemporalReasoningResult {
  reasoningDate: string;
  validEdges: readonly GraphEdge[];
  rejectedEdges: readonly { edge: GraphEdge; reason: string }[];
}

export interface ReasoningResult {
  query: ReasoningQuery;
  paths: readonly ReasoningPath[];
  conclusions: readonly ReasoningConclusion[];
  conflicts: readonly ReasoningConflict[];
  missingLinkSuggestions: readonly MissingLinkSuggestion[];
  explanation: ExplanationTrace;
  temporal: TemporalReasoningResult;
  metrics: ReasoningMetrics;
}

export type ReasoningEventName =
  | "ReasoningStarted"
  | "ReasoningCompleted"
  | "ReasoningFailed"
  | "ConflictDetected"
  | "MissingLinkSuggested"
  | "RuleApplied";

export interface ReasoningEvent {
  name: ReasoningEventName;
  occurredAt: string;
  payload: Readonly<Record<string, unknown>>;
}
