import { ReasoningValidationError } from "../domain/errors.js";
import type {
  MissingLinkSuggestion,
  ReasoningConclusion,
  ReasoningConflict,
  ReasoningMetrics,
  ReasoningPath,
  ReasoningQuery,
  ReasoningResult
} from "../domain/models.js";
import type {
  EventPublisherPort,
  GraphReadPort,
  LoggerPort,
  MetricsPort,
  ReasoningCachePort,
  RuleRepositoryPort
} from "../ports/index.js";
import { ConflictDetectionService } from "./conflict-detection.service.js";
import { MissingLinkPredictionService } from "./missing-link-prediction.service.js";
import { OntologyReasoningService } from "./ontology-reasoning.service.js";
import { PathReasoningService } from "./path-reasoning.service.js";
import { clampConfidence, ReasoningConfidenceService } from "./reasoning-confidence.service.js";
import { ReasoningExplanationService } from "./reasoning-explanation.service.js";
import { ReasoningRankingService } from "./reasoning-ranking.service.js";
import { RuleReasoningService } from "./rule-reasoning.service.js";
import { dateValue, TemporalReasoningService } from "./temporal-reasoning.service.js";

const DEFAULT_METRICS: ReasoningMetrics = {
  reasoningRequests: 0,
  reasoningSuccesses: 0,
  reasoningFailures: 0,
  averageReasoningTime: 0,
  pathsEvaluated: 0,
  rulesApplied: 0,
  conflictsDetected: 0,
  missingLinksSuggested: 0,
  averageConfidence: 0
};

export interface GraphReasoningServiceDependencies {
  graph: GraphReadPort;
  rules: RuleRepositoryPort;
  cache: ReasoningCachePort;
  logger: LoggerPort;
  metrics: MetricsPort;
  events: EventPublisherPort;
  temporal?: TemporalReasoningService;
  confidence?: ReasoningConfidenceService;
  pathReasoning?: PathReasoningService;
  ruleReasoning?: RuleReasoningService;
  ontologyReasoning?: OntologyReasoningService;
  conflictDetection?: ConflictDetectionService;
  missingLinks?: MissingLinkPredictionService;
  explanations?: ReasoningExplanationService;
  ranking?: ReasoningRankingService;
}

export class GraphReasoningService {
  private readonly temporal: TemporalReasoningService;
  private readonly confidence: ReasoningConfidenceService;
  private readonly pathReasoning: PathReasoningService;
  private readonly ruleReasoning: RuleReasoningService;
  private readonly ontologyReasoning: OntologyReasoningService;
  private readonly conflictDetection: ConflictDetectionService;
  private readonly missingLinks: MissingLinkPredictionService;
  private readonly explanations: ReasoningExplanationService;
  private readonly ranking: ReasoningRankingService;

  constructor(private readonly deps: GraphReasoningServiceDependencies) {
    this.temporal = deps.temporal ?? new TemporalReasoningService();
    this.confidence = deps.confidence ?? new ReasoningConfidenceService();
    this.pathReasoning = deps.pathReasoning ?? new PathReasoningService(deps.graph, this.temporal, this.confidence);
    this.ruleReasoning = deps.ruleReasoning ?? new RuleReasoningService(deps.rules, this.confidence);
    this.ontologyReasoning = deps.ontologyReasoning ?? new OntologyReasoningService(deps.graph, this.temporal);
    this.conflictDetection = deps.conflictDetection ?? new ConflictDetectionService();
    this.missingLinks = deps.missingLinks ?? new MissingLinkPredictionService(deps.graph);
    this.explanations = deps.explanations ?? new ReasoningExplanationService();
    this.ranking = deps.ranking ?? new ReasoningRankingService();
  }

  async reason(query: ReasoningQuery): Promise<ReasoningResult> {
    const started = Date.now();
    this.validate(query);
    const cacheKey = JSON.stringify(query);
    const cached = await this.deps.cache.get(cacheKey);
    if (cached) {
      return cached;
    }
    this.deps.metrics.increment("reasoningRequests");
    await this.deps.events.publish({ name: "ReasoningStarted", occurredAt: new Date().toISOString(), payload: { query } });
    try {
      const paths = this.ranking.rankPaths(await this.pathReasoning.findPaths(query));
      const ruleConclusions = await this.ruleReasoning.infer(paths);
      for (const conclusion of ruleConclusions.filter((item) => item.ruleId)) {
        await this.deps.events.publish({ name: "RuleApplied", occurredAt: new Date().toISOString(), payload: { ruleId: conclusion.ruleId, conclusionId: conclusion.id } });
      }
      const ontologyConclusions = await this.ontologyReasoning.inferInheritance(query, paths);
      const conclusions = [...ruleConclusions, ...ontologyConclusions].sort((left, right) => right.confidence - left.confidence);
      const conflicts = query.includeConflicts === false ? [] : this.conflictDetection.detect(paths, conclusions);
      const conflictPenalty = conflicts.length ? 0.75 : 1;
      const penalizedConclusions = conclusions.map((conclusion) => ({ ...conclusion, confidence: clampConfidence(conclusion.confidence * conflictPenalty) }));
      const suggestions = query.includeMissingLinkSuggestions === false ? [] : await this.missingLinks.suggest(query, penalizedConclusions, query.minConfidence ?? 0.7);
      const explanation = this.explanations.create({ paths, conclusions: penalizedConclusions, conflicts, suggestions });
      const temporal = this.temporal.evaluate(paths.flatMap((path) => path.edges), query.reasoningDate ?? new Date().toISOString());
      this.recordSuccess(Date.now() - started, paths, penalizedConclusions, conflicts, suggestions);
      for (const conflict of conflicts) {
        await this.deps.events.publish({ name: "ConflictDetected", occurredAt: new Date().toISOString(), payload: { conflict } });
      }
      for (const suggestion of suggestions) {
        await this.deps.events.publish({ name: "MissingLinkSuggested", occurredAt: new Date().toISOString(), payload: { suggestion } });
      }
      const result: ReasoningResult = {
        query,
        paths,
        conclusions: penalizedConclusions,
        conflicts,
        missingLinkSuggestions: suggestions,
        explanation,
        temporal,
        metrics: this.deps.metrics.snapshot()
      };
      await this.deps.cache.set(cacheKey, result);
      await this.deps.events.publish({ name: "ReasoningCompleted", occurredAt: new Date().toISOString(), payload: { pathCount: paths.length } });
      return result;
    } catch (error) {
      this.deps.metrics.increment("reasoningFailures");
      this.deps.logger.error("Knowledge graph reasoning failed.", { error: error instanceof Error ? error.message : String(error) });
      await this.deps.events.publish({ name: "ReasoningFailed", occurredAt: new Date().toISOString(), payload: { error: error instanceof Error ? error.message : String(error) } });
      throw error;
    }
  }

  private validate(query: ReasoningQuery): void {
    if (!query.sourceNodeId && !query.sourceCanonicalName) {
      throw new ReasoningValidationError("Either sourceNodeId or sourceCanonicalName is required.");
    }
    if (query.maxDepth !== undefined && (query.maxDepth < 1 || query.maxDepth > 12)) {
      throw new ReasoningValidationError("maxDepth must be between 1 and 12.");
    }
    if (query.minConfidence !== undefined && (query.minConfidence < 0 || query.minConfidence > 1)) {
      throw new ReasoningValidationError("minConfidence must be between 0 and 1.");
    }
    if (query.reasoningDate) {
      dateValue(query.reasoningDate);
    }
  }

  private recordSuccess(
    elapsed: number,
    paths: readonly ReasoningPath[],
    conclusions: readonly ReasoningConclusion[],
    conflicts: readonly ReasoningConflict[],
    suggestions: readonly MissingLinkSuggestion[]
  ): void {
    this.deps.metrics.increment("reasoningSuccesses");
    this.deps.metrics.observe("averageReasoningTime", elapsed);
    this.deps.metrics.increment("pathsEvaluated", paths.length);
    this.deps.metrics.increment("rulesApplied", conclusions.filter((conclusion) => conclusion.ruleId).length);
    this.deps.metrics.increment("conflictsDetected", conflicts.length);
    this.deps.metrics.increment("missingLinksSuggested", suggestions.length);
    if (conclusions.length) {
      this.deps.metrics.observe("averageConfidence", conclusions.reduce((sum, conclusion) => sum + conclusion.confidence, 0) / conclusions.length);
    }
  }
}

export const defaultReasoningMetrics = (): ReasoningMetrics => ({ ...DEFAULT_METRICS });
