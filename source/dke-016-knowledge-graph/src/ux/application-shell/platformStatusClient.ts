import type { BackendStatusClient, PlatformStatusSnapshot } from "./types.js";

const FALLBACK_PLATFORM_STATUS: PlatformStatusSnapshot = {
  platformStatus: [
    { id: "backend", title: "Backend Platform", status: "complete", detail: "R-001 through R-010 complete and frozen." },
    { id: "research", title: "Research Layer", status: "complete", detail: "Research foundation modules are complete." },
    { id: "dke", title: "Decision Knowledge Engine", status: "complete", detail: "DKE-001 through DKE-020 complete and frozen." },
    { id: "die", title: "Decision Intelligence Engine", status: "complete", detail: "DIE-001 through DIE-020 complete and frozen." },
    { id: "platform-integration", title: "Platform Integration", status: "complete", detail: "PI-001 through PI-008 complete." },
    { id: "validation", title: "Validation & Benchmarking", status: "complete", detail: "VB-001 through VB-005 complete." },
    { id: "documentation", title: "Documentation", status: "complete", detail: "DOC-001 through DOC-005 complete." },
    { id: "patent", title: "Patent Preparation", status: "complete", detail: "PAT-001 through PAT-004 complete." },
    { id: "research-paper", title: "Research Paper Preparation", status: "complete", detail: "RP-001 through RP-005 complete." },
    { id: "commercial-release", title: "Commercial Release", status: "complete", detail: "REL-001 through REL-005 complete." },
  ],
  mechanisms: [
    { id: "decision-provenance-graph", title: "Decision Provenance Graph", backendModule: "DIE provenance", description: "Surfaces immutable decision evidence and provenance paths." },
    { id: "dynamic-governance-mesh", title: "Dynamic Decision Governance Mesh", backendModule: "DIE governance", description: "Presents policy, compliance, and governance readiness signals." },
    { id: "temporal-lineage-ledger", title: "Temporal Decision Lineage Ledger", backendModule: "DIE temporal", description: "Exposes decision versioning and time-aware lineage records." },
    { id: "adaptive-behavior-model", title: "Adaptive Decision Behavior Model", backendModule: "DIE adaptive", description: "Displays learned behavior state without reimplementing adaptation logic." },
    { id: "adaptive-workflow-graph", title: "Adaptive Decision Workflow Graph", backendModule: "DIE workflow", description: "Frames workflow stages and routing for future UX modules." },
    { id: "health-monitoring-fabric", title: "Decision Health Monitoring Fabric", backendModule: "DIE monitoring", description: "Shows health and drift monitoring as backend-owned signals." },
    { id: "recommendation-interface-fabric", title: "Decision Recommendation Interface Fabric", backendModule: "DIE recommendation service", description: "Prepares recommendation delivery surfaces for later modules." },
    { id: "enterprise-orchestration-fabric", title: "Enterprise Decision Orchestration Fabric", backendModule: "DIE enterprise orchestrator", description: "Connects lifecycle, readiness, and orchestration views." },
  ],
  regressionBaseline: { passing: 606, total: 606 },
  releaseTags: ["v1.0.0-pre-release", "v1.0.1-commercial-progress", "v1.0.2-backend-complete"],
};

export class DeterministicBackendStatusClient implements BackendStatusClient {
  async getPlatformStatus(): Promise<PlatformStatusSnapshot> {
    return FALLBACK_PLATFORM_STATUS;
  }
}

export function createBackendStatusClient(): BackendStatusClient {
  return new DeterministicBackendStatusClient();
}
