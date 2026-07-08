export interface DecisionSession {
  readonly id: string;
  readonly title: string;
  readonly status: "draft" | "ready" | "evaluated" | "ranked";
  readonly updatedAt: string;
}

export interface DecisionWorkspaceSummary {
  readonly workspaceTitle: string;
  readonly status: "draft" | "ready" | "loaded" | "evaluated" | "ranked";
  readonly decisionId: string;
  readonly sessionId: string;
  readonly updatedAt: string;
}

export interface DecisionContext {
  readonly objective: string;
  readonly domain: string;
  readonly constraints: readonly string[];
  readonly stakeholders: readonly string[];
  readonly riskPreference: string;
  readonly governanceMode: string;
}

export interface DecisionAlternative {
  readonly id: string;
  readonly title: string;
  readonly summary: string;
  readonly expectedImpact: string;
  readonly riskLevel: "low" | "medium" | "high";
  readonly status: "candidate" | "evaluated" | "recommended";
}

export interface EvaluationCriterion {
  readonly name: string;
  readonly score: number;
  readonly weight: number;
}

export interface EvaluationResult {
  readonly alternativeId: string;
  readonly score: number;
  readonly confidence: number;
  readonly criteria: readonly EvaluationCriterion[];
  readonly strengths: readonly string[];
  readonly weaknesses: readonly string[];
  readonly warnings: readonly string[];
}

export interface RankingResult {
  readonly rank: number;
  readonly alternativeId: string;
  readonly alternativeTitle: string;
  readonly score: number;
  readonly explanationSummary: string;
  readonly recommended: boolean;
}

export interface WorkspaceTimelineEvent {
  readonly id: string;
  readonly label: string;
  readonly status: "complete" | "current" | "pending";
  readonly timestamp: string;
}

export interface DecisionHistoryItem {
  readonly decisionId: string;
  readonly sessionId: string;
  readonly title: string;
  readonly status: DecisionWorkspaceSummary["status"];
  readonly updatedAt: string;
  readonly domain: string;
}

export interface DecisionWorkspaceSnapshot {
  readonly summary: DecisionWorkspaceSummary;
  readonly sessions: readonly DecisionSession[];
  readonly context: DecisionContext;
  readonly alternatives: readonly DecisionAlternative[];
  readonly evaluationResults: readonly EvaluationResult[];
  readonly rankingResults: readonly RankingResult[];
  readonly timeline: readonly WorkspaceTimelineEvent[];
}

export interface DecisionWorkspaceClient {
  createDraftWorkspace?(): Promise<DecisionWorkspaceSnapshot>;
  loadDecisionWorkspace?(sessionId?: string): Promise<DecisionWorkspaceSnapshot>;
  listSavedDecisionWorkspaces?(): Promise<readonly DecisionHistoryItem[]>;
  getWorkspaceSummary(): Promise<DecisionWorkspaceSummary>;
  listDecisionSessions(): Promise<readonly DecisionSession[]>;
  getDecisionContext(): Promise<DecisionContext>;
  listAlternatives(): Promise<readonly DecisionAlternative[]>;
  runEvaluation(): Promise<readonly EvaluationResult[]>;
  runRanking(): Promise<readonly RankingResult[]>;
  getWorkspaceTimeline(): Promise<readonly WorkspaceTimelineEvent[]>;
}
