import {
  ConsoleLoggerAdapter,
  InMemoryEventPublisherAdapter,
  InMemoryMetricsAdapter,
  MemoryGraphRepository,
  NoopTelemetryAdapter,
} from "../adapters/index.js";
import { KnowledgeGraphController } from "../api/index.js";
import type { EventPublisherPort, EvidenceRepositoryPort, GraphRepositoryPort, LoggerPort, MetricsPort, TelemetryPort } from "../ports/index.js";
import {
  EdgeService,
  EntityResolutionService,
  GraphConfidenceService,
  GraphConstructionService,
  GraphEvidenceService,
  GraphIndexService,
  GraphValidationService,
  NodeService,
} from "../services/index.js";

export interface KnowledgeGraphModuleOptions {
  graphRepository?: GraphRepositoryPort & EvidenceRepositoryPort;
  logger?: LoggerPort;
  eventPublisher?: EventPublisherPort;
  metrics?: MetricsPort;
  telemetry?: TelemetryPort;
}

export interface KnowledgeGraphModule {
  repository: GraphRepositoryPort & EvidenceRepositoryPort;
  logger: LoggerPort;
  eventPublisher: EventPublisherPort;
  metrics: MetricsPort;
  telemetry: TelemetryPort;
  controller: KnowledgeGraphController;
  services: {
    validation: GraphValidationService;
    confidence: GraphConfidenceService;
    entityResolution: EntityResolutionService;
    nodes: NodeService;
    edges: EdgeService;
    evidence: GraphEvidenceService;
    index: GraphIndexService;
    construction: GraphConstructionService;
  };
}

export function createKnowledgeGraphModule(options: KnowledgeGraphModuleOptions = {}): KnowledgeGraphModule {
  const repository = options.graphRepository ?? new MemoryGraphRepository();
  const logger = options.logger ?? new ConsoleLoggerAdapter();
  const eventPublisher = options.eventPublisher ?? new InMemoryEventPublisherAdapter();
  const metrics = options.metrics ?? new InMemoryMetricsAdapter();
  const telemetry = options.telemetry ?? new NoopTelemetryAdapter();

  const validation = new GraphValidationService();
  const confidence = new GraphConfidenceService();
  const entityResolution = new EntityResolutionService();
  const nodes = new NodeService(repository, validation, entityResolution, eventPublisher, metrics, logger);
  const edges = new EdgeService(repository, validation, eventPublisher, metrics, logger);
  const evidence = new GraphEvidenceService(repository, validation, eventPublisher, metrics, logger);
  const index = new GraphIndexService(repository);
  const construction = new GraphConstructionService(repository, validation, nodes, edges, evidence, eventPublisher, metrics, logger);
  const controller = new KnowledgeGraphController(construction, nodes, edges, index);

  return {
    repository,
    logger,
    eventPublisher,
    metrics,
    telemetry,
    controller,
    services: { validation, confidence, entityResolution, nodes, edges, evidence, index, construction },
  };
}
