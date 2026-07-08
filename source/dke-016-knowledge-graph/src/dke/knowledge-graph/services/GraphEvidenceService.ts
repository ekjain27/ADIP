import type { GraphEvidence, GraphEvidenceInput } from "../domain/index.js";
import type { EventPublisherPort, EvidenceRepositoryPort, LoggerPort, MetricsPort } from "../ports/index.js";
import { createGraphEvent } from "./EventFactory.js";
import { GraphValidationService } from "./GraphValidationService.js";

export class GraphEvidenceService {
  constructor(
    private readonly evidenceRepository: EvidenceRepositoryPort,
    private readonly validation: GraphValidationService,
    private readonly events?: EventPublisherPort,
    private readonly metrics?: MetricsPort,
    private readonly logger?: LoggerPort,
  ) {}

  async createEvidence(input: GraphEvidenceInput): Promise<GraphEvidence> {
    const evidence: GraphEvidence = {
      ...input,
      createdAt: input.createdAt ?? new Date().toISOString(),
    };
    try {
      this.validation.validateEvidence(evidence);
    } catch (error) {
      this.metrics?.increment("validationFailures");
      throw error;
    }
    const created = await this.evidenceRepository.createEvidence(evidence);
    this.metrics?.increment("evidenceStored");
    this.logger?.info("Graph evidence stored", { evidenceId: created.id });
    await this.events?.publish(createGraphEvent("GraphEvidenceStored", { evidenceId: created.id }));
    return created;
  }

  getEvidenceById(id: string): Promise<GraphEvidence | null> {
    return this.evidenceRepository.getEvidenceById(id);
  }
}
