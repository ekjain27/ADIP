import {
  createDefaultRules,
  InMemoryEventPublisher,
  InMemoryGraphReadAdapter,
  InMemoryMetrics,
  InMemoryReasoningCache,
  InMemoryRuleRepository,
  NullLogger
} from "../adapters/index.js";
import { KnowledgeGraphReasoningController } from "../api/index.js";
import type { GraphEdge, GraphNode, ReasoningRule } from "../domain/models.js";
import type {
  EventPublisherPort,
  GraphReadPort,
  LoggerPort,
  MetricsPort,
  ReasoningCachePort,
  RuleRepositoryPort
} from "../ports/index.js";
import { GraphReasoningService } from "../services/index.js";

export interface KnowledgeReasoningCompositionInput {
  graph?: GraphReadPort;
  rules?: RuleRepositoryPort;
  cache?: ReasoningCachePort;
  logger?: LoggerPort;
  metrics?: MetricsPort;
  events?: EventPublisherPort;
  nodes?: readonly GraphNode[];
  edges?: readonly GraphEdge[];
  deterministicRules?: readonly ReasoningRule[];
}

export interface KnowledgeReasoningComposition {
  service: GraphReasoningService;
  controller: KnowledgeGraphReasoningController;
  graph: GraphReadPort;
  rules: RuleRepositoryPort;
  cache: ReasoningCachePort;
  logger: LoggerPort;
  metrics: MetricsPort;
  events: EventPublisherPort;
}

export function createKnowledgeReasoningModule(input: KnowledgeReasoningCompositionInput = {}): KnowledgeReasoningComposition {
  const graph = input.graph ?? new InMemoryGraphReadAdapter({ nodes: input.nodes, edges: input.edges });
  const rules = input.rules ?? new InMemoryRuleRepository(input.deterministicRules ?? createDefaultRules());
  const cache = input.cache ?? new InMemoryReasoningCache();
  const logger = input.logger ?? new NullLogger();
  const metrics = input.metrics ?? new InMemoryMetrics();
  const events = input.events ?? new InMemoryEventPublisher();
  const service = new GraphReasoningService({ graph, rules, cache, logger, metrics, events });
  return {
    service,
    controller: new KnowledgeGraphReasoningController(service),
    graph,
    rules,
    cache,
    logger,
    metrics,
    events
  };
}
