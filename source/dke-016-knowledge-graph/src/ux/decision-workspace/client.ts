import type {
  DecisionAlternative,
  DecisionContext,
  DecisionHistoryItem,
  DecisionSession,
  DecisionWorkspaceClient,
  DecisionWorkspaceSnapshot,
  DecisionWorkspaceSummary,
  EvaluationResult,
  RankingResult,
  WorkspaceTimelineEvent,
} from "./types.js";

export const DECISION_WORKSPACE_STORAGE_KEY = "project1.ux002.decision-workspace.snapshots.v1";
const DECISION_HISTORY_LIMIT = 10;

const FALLBACK_WORKSPACE: DecisionWorkspaceSnapshot = {
  summary: {
    workspaceTitle: "Enterprise Expansion Decision",
    status: "ranked",
    decisionId: "DEC-2026-001",
    sessionId: "SESSION-UX2-001",
    updatedAt: "2026-07-01T09:30:00.000Z",
  },
  sessions: [
    { id: "SESSION-UX2-001", title: "Enterprise Expansion Decision", status: "ranked", updatedAt: "2026-07-01T09:30:00.000Z" },
    { id: "SESSION-UX2-002", title: "Platform Consolidation Review", status: "evaluated", updatedAt: "2026-06-30T16:15:00.000Z" },
  ],
  context: {
    objective: "Select the best enterprise expansion path while preserving governance, reliability, and commercial readiness.",
    domain: "Enterprise decision intelligence",
    constraints: ["Maintain backend freeze", "Use approved governance controls", "Keep rollout under two quarters"],
    stakeholders: ["Executive sponsor", "Risk office", "Platform operations", "Product leadership"],
    riskPreference: "Moderate",
    governanceMode: "Policy-gated recommendation",
  },
  alternatives: [
    { id: "ALT-A", title: "Phased regional rollout", summary: "Launch by region with progressive control gates.", expectedImpact: "High adoption with managed operational risk.", riskLevel: "medium", status: "recommended" },
    { id: "ALT-B", title: "Single enterprise launch", summary: "Launch to all business units at once after central readiness review.", expectedImpact: "Fast time-to-value with higher change-management load.", riskLevel: "high", status: "evaluated" },
    { id: "ALT-C", title: "Pilot-first rollout", summary: "Run a controlled pilot before scaling to enterprise users.", expectedImpact: "Lower risk with slower commercial impact.", riskLevel: "low", status: "evaluated" },
  ],
  evaluationResults: [
    {
      alternativeId: "ALT-A",
      score: 88,
      confidence: 0.91,
      criteria: [
        { name: "Strategic fit", score: 92, weight: 0.3 },
        { name: "Operational readiness", score: 86, weight: 0.25 },
        { name: "Governance fit", score: 90, weight: 0.25 },
        { name: "Time-to-value", score: 82, weight: 0.2 },
      ],
      strengths: ["Strong governance alignment", "Balanced delivery risk", "Clear rollout checkpoints"],
      weaknesses: ["Requires regional coordination"],
      warnings: ["Monitor dependency readiness before each phase"],
    },
    {
      alternativeId: "ALT-B",
      score: 74,
      confidence: 0.84,
      criteria: [
        { name: "Strategic fit", score: 88, weight: 0.3 },
        { name: "Operational readiness", score: 68, weight: 0.25 },
        { name: "Governance fit", score: 72, weight: 0.25 },
        { name: "Time-to-value", score: 80, weight: 0.2 },
      ],
      strengths: ["Fast commercial signal", "Unified launch messaging"],
      weaknesses: ["Elevated support burden", "Limited correction window"],
      warnings: ["Governance review should precede launch approval"],
    },
    {
      alternativeId: "ALT-C",
      score: 79,
      confidence: 0.88,
      criteria: [
        { name: "Strategic fit", score: 78, weight: 0.3 },
        { name: "Operational readiness", score: 84, weight: 0.25 },
        { name: "Governance fit", score: 86, weight: 0.25 },
        { name: "Time-to-value", score: 66, weight: 0.2 },
      ],
      strengths: ["Strong operational control", "Low rollout risk", "Clear validation window"],
      weaknesses: ["Slower commercial scale"],
      warnings: ["Pilot success criteria should be approved before expansion"],
    },
  ],
  rankingResults: [
    { rank: 1, alternativeId: "ALT-A", alternativeTitle: "Phased regional rollout", score: 88, explanationSummary: "Best balance of impact, governance fit, and rollout control.", recommended: true },
    { rank: 2, alternativeId: "ALT-C", alternativeTitle: "Pilot-first rollout", score: 79, explanationSummary: "Safest option, but slower path to commercial scale.", recommended: false },
    { rank: 3, alternativeId: "ALT-B", alternativeTitle: "Single enterprise launch", score: 74, explanationSummary: "Higher launch risk offsets faster time-to-value.", recommended: false },
  ],
  timeline: [
    { id: "created", label: "Decision created", status: "complete", timestamp: "2026-07-01T08:00:00.000Z" },
    { id: "context", label: "Context loaded", status: "complete", timestamp: "2026-07-01T08:20:00.000Z" },
    { id: "alternatives", label: "Alternatives generated", status: "complete", timestamp: "2026-07-01T08:45:00.000Z" },
    { id: "evaluation", label: "Evaluation completed", status: "complete", timestamp: "2026-07-01T09:05:00.000Z" },
    { id: "ranking", label: "Ranking completed", status: "complete", timestamp: "2026-07-01T09:20:00.000Z" },
    { id: "governance", label: "Governance checked", status: "current", timestamp: "2026-07-01T09:30:00.000Z" },
  ],
};

const DRAFT_VARIANTS = [
  {
    title: "Supply Chain Optimization Decision",
    objective: "Select the best supply chain resilience plan for multi-region fulfillment continuity.",
    domain: "Supply chain optimization",
    riskPreference: "Medium operational risk tolerance",
    governanceMode: "Procurement and continuity review pending",
    alternatives: [
      { id: "SC-OPT-1A", title: "Dual-source critical components", summary: "Split critical component sourcing across two qualified suppliers.", expectedImpact: "Higher continuity with moderate qualification effort.", riskLevel: "medium", status: "candidate" },
      { id: "SC-OPT-1B", title: "Regional buffer inventory", summary: "Place safety stock close to high-volatility regions.", expectedImpact: "Fast resilience gain with working-capital tradeoff.", riskLevel: "low", status: "candidate" },
      { id: "SC-OPT-1C", title: "Expedited supplier consolidation", summary: "Consolidate suppliers to one preferred global provider.", expectedImpact: "Lower coordination cost with concentration exposure.", riskLevel: "high", status: "candidate" },
    ],
  },
  {
    title: "Healthcare Resource Allocation Decision",
    objective: "Allocate scarce clinical staffing capacity across care programs without reducing governance visibility.",
    domain: "Healthcare resource allocation",
    riskPreference: "Low patient-safety risk tolerance",
    governanceMode: "Clinical governance approval required",
    alternatives: [
      { id: "HC-RES-2A", title: "Prioritize critical-care coverage", summary: "Shift available staff to critical-care demand bands first.", expectedImpact: "Protects high-acuity service levels.", riskLevel: "low", status: "candidate" },
      { id: "HC-RES-2B", title: "Expand tele-triage rotation", summary: "Use cross-trained clinicians for tele-triage overflow windows.", expectedImpact: "Improves access while preserving escalation paths.", riskLevel: "medium", status: "candidate" },
      { id: "HC-RES-2C", title: "Defer elective program capacity", summary: "Temporarily reduce elective program staffing allocation.", expectedImpact: "Frees capacity with patient-experience tradeoffs.", riskLevel: "medium", status: "candidate" },
    ],
  },
  {
    title: "Financial Risk Mitigation Decision",
    objective: "Choose a mitigation path for portfolio exposure while preserving audit-ready risk governance.",
    domain: "Financial risk mitigation",
    riskPreference: "Conservative downside protection",
    governanceMode: "Risk committee review pending",
    alternatives: [
      { id: "FIN-RISK-3A", title: "Hedge downside exposure", summary: "Apply targeted hedging to the highest-volatility exposure band.", expectedImpact: "Reduces downside risk with premium cost.", riskLevel: "medium", status: "candidate" },
      { id: "FIN-RISK-3B", title: "Rebalance toward liquid assets", summary: "Shift allocation toward more liquid instruments.", expectedImpact: "Improves liquidity and reduces volatility.", riskLevel: "low", status: "candidate" },
      { id: "FIN-RISK-3C", title: "Maintain position with monitoring", summary: "Keep current allocation and increase review cadence.", expectedImpact: "Avoids transaction cost but leaves exposure open.", riskLevel: "high", status: "candidate" },
    ],
  },
  {
    title: "Hiring Workforce Planning Decision",
    objective: "Choose a workforce plan for delivery capacity while protecting budget and role coverage.",
    domain: "Hiring and workforce planning",
    riskPreference: "Balanced talent and budget risk",
    governanceMode: "People operations approval pending",
    alternatives: [
      { id: "WF-PLAN-4A", title: "Hire critical specialists", summary: "Prioritize senior specialist roles for the highest delivery bottlenecks.", expectedImpact: "High delivery leverage with longer hiring cycle.", riskLevel: "medium", status: "candidate" },
      { id: "WF-PLAN-4B", title: "Reskill internal teams", summary: "Invest in targeted upskilling and internal mobility.", expectedImpact: "Improves retention with slower capacity gain.", riskLevel: "low", status: "candidate" },
      { id: "WF-PLAN-4C", title: "Use short-term contractors", summary: "Add temporary capacity for urgent delivery windows.", expectedImpact: "Fast capacity with continuity risk.", riskLevel: "high", status: "candidate" },
    ],
  },
  {
    title: "Sustainability Investment Decision",
    objective: "Select a sustainability investment path with credible impact, governance evidence, and financial discipline.",
    domain: "Sustainability investment",
    riskPreference: "Moderate financial risk with high evidence quality",
    governanceMode: "ESG investment review pending",
    alternatives: [
      { id: "SUS-INV-5A", title: "Facility energy retrofit", summary: "Upgrade lighting and controls across high-consumption facilities.", expectedImpact: "Measurable efficiency improvement with capital spend.", riskLevel: "medium", status: "candidate" },
      { id: "SUS-INV-5B", title: "Renewable power contract", summary: "Commit to a renewable power purchase agreement.", expectedImpact: "Large sustainability signal with contract exposure.", riskLevel: "high", status: "candidate" },
      { id: "SUS-INV-5C", title: "Waste reduction program", summary: "Deploy operational waste reduction and supplier packaging controls.", expectedImpact: "Moderate impact with low capital requirement.", riskLevel: "low", status: "candidate" },
    ],
  },
  {
    title: "Customer Retention Decision",
    objective: "Choose a retention intervention for priority customer segments while protecting margin and trust.",
    domain: "Customer retention",
    riskPreference: "Moderate churn risk tolerance",
    governanceMode: "Commercial policy review pending",
    alternatives: [
      { id: "CUST-RET-6A", title: "Targeted success outreach", summary: "Prioritize high-risk accounts for proactive success engagement.", expectedImpact: "Trust-building intervention with moderate operating cost.", riskLevel: "low", status: "candidate" },
      { id: "CUST-RET-6B", title: "Contract renewal incentives", summary: "Offer structured incentives for renewal commitments.", expectedImpact: "Fast retention signal with margin tradeoff.", riskLevel: "medium", status: "candidate" },
      { id: "CUST-RET-6C", title: "Product adoption accelerator", summary: "Fund onboarding support for under-adopting customer teams.", expectedImpact: "Improves usage depth with delivery effort.", riskLevel: "medium", status: "candidate" },
    ],
  },
] satisfies ReadonlyArray<{
  readonly title: string;
  readonly objective: string;
  readonly domain: string;
  readonly riskPreference: string;
  readonly governanceMode: string;
  readonly alternatives: readonly DecisionAlternative[];
}>;

const DRAFT_CONTEXT_PROFILES = [
  {
    constraints: ["Maintain supplier auditability", "Avoid single-region dependency", "Keep transition under 90 days"],
    stakeholders: ["Chief operations officer", "Procurement lead", "Regional logistics owner"],
    criteria: [
      { name: "Continuity gain", weight: 0.4 },
      { name: "Cost control", weight: 0.25 },
      { name: "Governance fit", weight: 0.35 },
    ],
    scores: [87, 82, 69],
    rationale: "resilience, supplier governance, and manageable cost exposure",
  },
  {
    constraints: ["Preserve patient safety thresholds", "Maintain staffing compliance", "Avoid external data assumptions"],
    stakeholders: ["Clinical director", "Operations manager", "Compliance officer"],
    criteria: [
      { name: "Patient safety", weight: 0.5 },
      { name: "Operational feasibility", weight: 0.25 },
      { name: "Compliance fit", weight: 0.25 },
    ],
    scores: [91, 83, 75],
    rationale: "patient-safety weighting and clinical governance readiness",
  },
  {
    constraints: ["Keep exposure within board threshold", "Preserve liquidity", "Document approval evidence"],
    stakeholders: ["Risk committee", "Treasury lead", "Finance controller"],
    criteria: [
      { name: "Downside protection", weight: 0.45 },
      { name: "Liquidity impact", weight: 0.25 },
      { name: "Governance evidence", weight: 0.3 },
    ],
    scores: [86, 84, 61],
    rationale: "downside protection with audit-ready approval evidence",
  },
  {
    constraints: ["Stay within hiring budget", "Cover critical roles first", "Avoid unapproved headcount expansion"],
    stakeholders: ["People operations", "Engineering director", "Finance partner"],
    criteria: [
      { name: "Skill coverage", weight: 0.4 },
      { name: "Budget fit", weight: 0.3 },
      { name: "Time-to-capacity", weight: 0.3 },
    ],
    scores: [85, 81, 73],
    rationale: "critical role coverage while staying within workforce governance",
  },
  {
    constraints: ["Use auditable impact claims", "Stay within capital plan", "Avoid unsupported external data"],
    stakeholders: ["Sustainability lead", "Finance controller", "Facilities operations"],
    criteria: [
      { name: "Impact measurability", weight: 0.45 },
      { name: "Capital discipline", weight: 0.3 },
      { name: "Governance evidence", weight: 0.25 },
    ],
    scores: [88, 80, 77],
    rationale: "auditable sustainability impact and capital discipline",
  },
  {
    constraints: ["Protect gross margin", "Avoid unsupported customer data assumptions", "Keep offer policy auditable"],
    stakeholders: ["Customer success", "Revenue operations", "Finance partner"],
    criteria: [
      { name: "Trust impact", weight: 0.35 },
      { name: "Margin protection", weight: 0.35 },
      { name: "Execution speed", weight: 0.3 },
    ],
    scores: [86, 78, 82],
    rationale: "retention durability, customer trust, and margin protection",
  },
] satisfies ReadonlyArray<{
  readonly constraints: readonly string[];
  readonly stakeholders: readonly string[];
  readonly criteria: readonly { readonly name: string; readonly weight: number }[];
  readonly scores: readonly number[];
  readonly rationale: string;
}>;

function createVariantEvaluationResults(
  variant: (typeof DRAFT_VARIANTS)[number],
  profile: (typeof DRAFT_CONTEXT_PROFILES)[number],
): readonly EvaluationResult[] {
  return variant.alternatives.map((alternative, index) => {
    const score = profile.scores[index] ?? 70;
    return {
      alternativeId: alternative.id,
      score,
      confidence: Math.max(0.78, 0.92 - index * 0.04),
      criteria: profile.criteria.map((criterion, criterionIndex) => ({
        name: criterion.name,
        score: Math.max(50, Math.min(96, score + (criterionIndex === 0 ? 5 : criterionIndex === 1 ? -4 : 2))),
        weight: criterion.weight,
      })),
      strengths: [`${alternative.title} aligns with ${profile.rationale}`],
      weaknesses: [`${alternative.title} carries ${alternative.riskLevel} execution tradeoffs`],
      warnings: [`Governance status: ${variant.governanceMode}`],
    };
  });
}

function createVariantRankingResults(
  variant: (typeof DRAFT_VARIANTS)[number],
  profile: (typeof DRAFT_CONTEXT_PROFILES)[number],
): readonly RankingResult[] {
  return createVariantEvaluationResults(variant, profile)
    .map((result) => {
      const alternative = variant.alternatives.find((item) => item.id === result.alternativeId) ?? variant.alternatives[0];
      return { result, alternative };
    })
    .sort((left, right) => right.result.score - left.result.score)
    .map(({ result, alternative }, index) => ({
      rank: index + 1,
      alternativeId: alternative.id,
      alternativeTitle: alternative.title,
      score: result.score,
      explanationSummary: index === 0
        ? `Recommended because it best balances ${profile.rationale}.`
        : `${alternative.title} remains viable, but its ${alternative.riskLevel} risk profile lowers its rank.`,
      recommended: index === 0,
    }));
}

function createDraftWorkspaceVariant(index: number, timestamp: string): DecisionWorkspaceSnapshot {
  const variant = DRAFT_VARIANTS[index % DRAFT_VARIANTS.length];
  const profile = DRAFT_CONTEXT_PROFILES[index % DRAFT_CONTEXT_PROFILES.length];
  const sequenceId = String(index + 1).padStart(3, "0");
  const cycle = Math.floor(index / DRAFT_VARIANTS.length);
  const title = cycle > 0 ? `${variant.title} ${cycle + 1}` : variant.title;
  return {
    ...FALLBACK_WORKSPACE,
    summary: {
      workspaceTitle: title,
      status: "draft",
      decisionId: `DEC-UX-DRAFT-${sequenceId}`,
      sessionId: `SESSION-UX-DRAFT-${sequenceId}`,
      updatedAt: timestamp,
    },
    sessions: [
      { id: `SESSION-UX-DRAFT-${sequenceId}`, title, status: "draft", updatedAt: timestamp },
      ...FALLBACK_WORKSPACE.sessions,
    ],
    context: {
      objective: variant.objective,
      domain: variant.domain,
      constraints: profile.constraints,
      stakeholders: profile.stakeholders,
      riskPreference: variant.riskPreference,
      governanceMode: variant.governanceMode,
    },
    alternatives: variant.alternatives,
    evaluationResults: createVariantEvaluationResults(variant, profile),
    rankingResults: createVariantRankingResults(variant, profile),
    timeline: [
      { id: "draft-created", label: "New decision workspace created", status: "current", timestamp },
      { id: "governance-status", label: variant.governanceMode, status: "pending", timestamp },
    ],
  };
}

const FALLBACK_LOADED_WORKSPACE: DecisionWorkspaceSnapshot = {
  ...FALLBACK_WORKSPACE,
  summary: {
    ...FALLBACK_WORKSPACE.summary,
    status: "loaded",
    updatedAt: "2026-07-01T09:45:00.000Z",
  },
  timeline: [
    { id: "workspace-loaded", label: "Decision workspace loaded", status: "current", timestamp: "2026-07-01T09:45:00.000Z" },
    ...FALLBACK_WORKSPACE.timeline,
  ],
};

interface StoredDecisionWorkspaceState {
  readonly draftSequence: number;
  readonly loadSequence: number;
  readonly savedSnapshots: readonly DecisionWorkspaceSnapshot[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isDecisionWorkspaceSnapshot(value: unknown): value is DecisionWorkspaceSnapshot {
  if (!isRecord(value) || !isRecord(value.summary) || !isRecord(value.context)) return false;
  return (
    typeof value.summary.decisionId === "string" &&
    typeof value.summary.sessionId === "string" &&
    typeof value.summary.workspaceTitle === "string" &&
    Array.isArray(value.sessions) &&
    Array.isArray(value.alternatives) &&
    Array.isArray(value.evaluationResults) &&
    Array.isArray(value.rankingResults) &&
    Array.isArray(value.timeline)
  );
}

function getDecisionWorkspaceStorage(): Storage | null {
  try {
    if (typeof localStorage !== "undefined") return localStorage;
  } catch {
    return null;
  }
  return null;
}

function readStoredDecisionWorkspaceState(): StoredDecisionWorkspaceState | null {
  const storage = getDecisionWorkspaceStorage();
  if (!storage) return null;
  try {
    const raw = storage.getItem(DECISION_WORKSPACE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed) || !Array.isArray(parsed.savedSnapshots)) return null;
    const savedSnapshots = parsed.savedSnapshots.filter(isDecisionWorkspaceSnapshot);
    return {
      draftSequence: typeof parsed.draftSequence === "number" && Number.isFinite(parsed.draftSequence) ? parsed.draftSequence : savedSnapshots.length,
      loadSequence: typeof parsed.loadSequence === "number" && Number.isFinite(parsed.loadSequence) ? parsed.loadSequence : 0,
      savedSnapshots: savedSnapshots.slice(0, DECISION_HISTORY_LIMIT),
    };
  } catch {
    return null;
  }
}

function writeStoredDecisionWorkspaceState(state: StoredDecisionWorkspaceState): void {
  const storage = getDecisionWorkspaceStorage();
  if (!storage) return;
  try {
    storage.setItem(DECISION_WORKSPACE_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // localStorage is optional UX demo persistence; unavailable storage must not break preview rendering.
  }
}

function markWorkspaceLoaded(snapshot: DecisionWorkspaceSnapshot, timestamp: string): DecisionWorkspaceSnapshot {
  return {
    ...snapshot,
    summary: { ...snapshot.summary, status: "loaded", updatedAt: timestamp },
    sessions: snapshot.sessions.map((session, index) =>
      index === 0 ? { ...session, status: "ready", updatedAt: timestamp } : session,
    ),
    timeline: [
      { id: "workspace-loaded", label: "Decision workspace loaded", status: "current", timestamp },
      ...snapshot.timeline.filter((event) => event.id !== "workspace-loaded"),
    ],
  };
}

function saveSnapshot(snapshots: readonly DecisionWorkspaceSnapshot[], snapshot: DecisionWorkspaceSnapshot): readonly DecisionWorkspaceSnapshot[] {
  return [
    snapshot,
    ...snapshots.filter((item) => item.summary.decisionId !== snapshot.summary.decisionId),
  ].slice(0, DECISION_HISTORY_LIMIT);
}

function replaceSnapshot(snapshots: readonly DecisionWorkspaceSnapshot[], snapshot: DecisionWorkspaceSnapshot): readonly DecisionWorkspaceSnapshot[] {
  const replaced = snapshots.map((item) => item.summary.decisionId === snapshot.summary.decisionId ? snapshot : item);
  return replaced.some((item) => item.summary.decisionId === snapshot.summary.decisionId)
    ? replaced
    : [snapshot, ...snapshots].slice(0, DECISION_HISTORY_LIMIT);
}

function toDecisionHistoryItem(snapshot: DecisionWorkspaceSnapshot): DecisionHistoryItem {
  return {
    decisionId: snapshot.summary.decisionId,
    sessionId: snapshot.summary.sessionId,
    title: snapshot.summary.workspaceTitle,
    status: snapshot.summary.status,
    updatedAt: snapshot.summary.updatedAt,
    domain: snapshot.context.domain,
  };
}

export class DeterministicDecisionWorkspaceClient implements DecisionWorkspaceClient {
  private draftSequence = 0;
  private loadSequence = 0;
  private savedSnapshots: readonly DecisionWorkspaceSnapshot[] = [];
  private activeSnapshot: DecisionWorkspaceSnapshot = FALLBACK_WORKSPACE;

  constructor() {
    const stored = readStoredDecisionWorkspaceState();
    if (stored) {
      this.draftSequence = stored.draftSequence;
      this.loadSequence = stored.loadSequence;
      this.savedSnapshots = stored.savedSnapshots;
      this.activeSnapshot = stored.savedSnapshots[0] ?? FALLBACK_WORKSPACE;
    }
  }

  async createDraftWorkspace(): Promise<DecisionWorkspaceSnapshot> {
    const timestamp = new Date().toISOString();
    const snapshot = createDraftWorkspaceVariant(this.draftSequence, timestamp);
    this.draftSequence += 1;
    this.savedSnapshots = saveSnapshot(this.savedSnapshots, snapshot);
    this.activeSnapshot = snapshot;
    this.loadSequence = this.savedSnapshots.length > 1 ? 1 : 0;
    writeStoredDecisionWorkspaceState({
      draftSequence: this.draftSequence,
      loadSequence: this.loadSequence,
      savedSnapshots: this.savedSnapshots,
    });
    return snapshot;
  }

  async loadDecisionWorkspace(sessionId?: string): Promise<DecisionWorkspaceSnapshot> {
    const timestamp = new Date().toISOString();
    if (this.savedSnapshots.length > 0) {
      const requested = sessionId
        ? this.savedSnapshots.find((snapshot) => snapshot.summary.sessionId === sessionId || snapshot.summary.decisionId === sessionId)
        : undefined;
      const selected = requested ?? this.savedSnapshots[this.loadSequence % this.savedSnapshots.length];
      if (!requested) this.loadSequence += 1;
      const loaded = markWorkspaceLoaded(selected, timestamp);
      this.savedSnapshots = replaceSnapshot(this.savedSnapshots, loaded);
      this.activeSnapshot = loaded;
      writeStoredDecisionWorkspaceState({
        draftSequence: this.draftSequence,
        loadSequence: this.loadSequence,
        savedSnapshots: this.savedSnapshots,
      });
      return loaded;
    }
    const loadedFallback: DecisionWorkspaceSnapshot = {
      ...FALLBACK_LOADED_WORKSPACE,
      summary: { ...FALLBACK_LOADED_WORKSPACE.summary, updatedAt: timestamp },
      sessions: FALLBACK_LOADED_WORKSPACE.sessions.map((session, index) => index === 0 ? { ...session, updatedAt: timestamp } : session),
      timeline: [
        { id: "workspace-loaded", label: "Decision workspace loaded", status: "current", timestamp },
        ...FALLBACK_WORKSPACE.timeline,
      ],
    };
    this.activeSnapshot = loadedFallback;
    return loadedFallback;
  }

  async listSavedDecisionWorkspaces(): Promise<readonly DecisionHistoryItem[]> {
    return this.savedSnapshots.map(toDecisionHistoryItem);
  }

  async getWorkspaceSummary(): Promise<DecisionWorkspaceSummary> {
    return FALLBACK_WORKSPACE.summary;
  }

  async listDecisionSessions(): Promise<readonly DecisionSession[]> {
    return FALLBACK_WORKSPACE.sessions;
  }

  async getDecisionContext(): Promise<DecisionContext> {
    return FALLBACK_WORKSPACE.context;
  }

  async listAlternatives(): Promise<readonly DecisionAlternative[]> {
    return FALLBACK_WORKSPACE.alternatives;
  }

  async runEvaluation(): Promise<readonly EvaluationResult[]> {
    return this.activeSnapshot.evaluationResults;
  }

  async runRanking(): Promise<readonly RankingResult[]> {
    return this.activeSnapshot.rankingResults;
  }

  async getWorkspaceTimeline(): Promise<readonly WorkspaceTimelineEvent[]> {
    return FALLBACK_WORKSPACE.timeline;
  }
}

export function createDecisionWorkspaceClient(): DecisionWorkspaceClient {
  return new DeterministicDecisionWorkspaceClient();
}

export async function getDecisionWorkspaceSnapshot(client: DecisionWorkspaceClient): Promise<DecisionWorkspaceSnapshot> {
  const [summary, sessions, context, alternatives, evaluationResults, rankingResults, timeline] = await Promise.all([
    client.getWorkspaceSummary(),
    client.listDecisionSessions(),
    client.getDecisionContext(),
    client.listAlternatives(),
    client.runEvaluation(),
    client.runRanking(),
    client.getWorkspaceTimeline(),
  ]);
  return { summary, sessions, context, alternatives, evaluationResults, rankingResults, timeline };
}
