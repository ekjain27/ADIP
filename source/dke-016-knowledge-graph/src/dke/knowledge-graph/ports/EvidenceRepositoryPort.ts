import type { GraphEvidence } from "../domain/index.js";

export interface EvidenceRepositoryPort {
  createEvidence(evidence: GraphEvidence): Promise<GraphEvidence>;
  getEvidenceById(id: string): Promise<GraphEvidence | null>;
  listEvidence(): Promise<GraphEvidence[]>;
}
