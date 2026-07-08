import type { DocumentationGenerationClient, DocumentationGenerationSnapshot, DocumentationGenerationSummary, GeneratedAsset, GeneratedDocument, GenerationActivity } from "./types.js";

const initialGeneratedAt = new Date().toISOString();

function minutesBefore(timestamp: string, minutes: number): string {
  return new Date(Date.parse(timestamp) - minutes * 60 * 1000).toISOString();
}

const summary: DocumentationGenerationSummary = {
  generatorStatus: "ready",
  currentProject: "AI Decision Intelligence Platform",
  lastGenerationAt: initialGeneratedAt,
  packageVersion: "UX-005-preview.1",
};

const documentation: readonly GeneratedDocument[] = [
  { id: "doc-architecture", title: "Architecture", status: "ready", version: "DOC-001", lastGeneratedAt: initialGeneratedAt, summary: "Architecture overview generated from backend documentation outputs." },
  { id: "doc-api", title: "API", status: "ready", version: "DOC-002", lastGeneratedAt: initialGeneratedAt, summary: "API reference package consumed from backend documentation services." },
  { id: "doc-user-guide", title: "User Guide", status: "review", version: "DOC-003", lastGeneratedAt: initialGeneratedAt, summary: "Enterprise user workflow guide prepared for review." },
  { id: "doc-technical-guide", title: "Technical Guide", status: "ready", version: "DOC-004", lastGeneratedAt: initialGeneratedAt, summary: "Technical implementation guide snapshot." },
  { id: "doc-deployment-guide", title: "Deployment Guide", status: "ready", version: "DOC-005", lastGeneratedAt: initialGeneratedAt, summary: "Deployment and release guide package." },
];

const patent: readonly GeneratedAsset[] = [
  { id: "patent-draft", title: "Patent Draft", status: "ready", version: "PAT-001", lastGeneratedAt: initialGeneratedAt, summary: "Patent draft package consumed through adapter boundary." },
  { id: "patent-claims", title: "Claims", status: "ready", version: "PAT-002", lastGeneratedAt: initialGeneratedAt, summary: "Claims matrix output prepared by backend patent layer." },
  { id: "patent-figures", title: "Figures", status: "review", version: "PAT-003", lastGeneratedAt: initialGeneratedAt, summary: "Figure package ready for preview." },
  { id: "patent-prior-art", title: "Prior Art Summary", status: "ready", version: "PAT-004", lastGeneratedAt: initialGeneratedAt, summary: "Prior art comparison summary." },
  { id: "patent-filing", title: "Filing Status", status: "filed", version: "PAT-004", lastGeneratedAt: initialGeneratedAt, summary: "Filing readiness status from patent preparation outputs." },
];

const researchPaper: readonly GeneratedAsset[] = [
  { id: "research-abstract", title: "Abstract", status: "ready", version: "RP-001", lastGeneratedAt: initialGeneratedAt, summary: "Abstract generated from research paper preparation outputs." },
  { id: "research-introduction", title: "Introduction", status: "ready", version: "RP-002", lastGeneratedAt: initialGeneratedAt, summary: "Introduction section package." },
  { id: "research-methodology", title: "Methodology", status: "ready", version: "RP-003", lastGeneratedAt: initialGeneratedAt, summary: "Methodology section package." },
  { id: "research-experiments", title: "Experiments", status: "review", version: "RP-004", lastGeneratedAt: initialGeneratedAt, summary: "Experiment summary package." },
  { id: "research-results", title: "Results", status: "ready", version: "RP-005", lastGeneratedAt: initialGeneratedAt, summary: "Results section package." },
  { id: "research-references", title: "References", status: "ready", version: "RP-005", lastGeneratedAt: initialGeneratedAt, summary: "Reference package." },
];

const activity: readonly GenerationActivity[] = [
  { id: "documentation-initial", title: "Documentation Generated", type: "documentation", timestamp: minutesBefore(initialGeneratedAt, 20), detail: "Documentation package available from backend documentation outputs." },
  { id: "patent-initial", title: "Patent Generated", type: "patent", timestamp: minutesBefore(initialGeneratedAt, 15), detail: "Patent preparation package available from backend patent outputs." },
  { id: "research-initial", title: "Research Generated", type: "research", timestamp: minutesBefore(initialGeneratedAt, 10), detail: "Research paper package available from backend research outputs." },
  { id: "package-initial", title: "Package Exported", type: "package", timestamp: minutesBefore(initialGeneratedAt, 5), detail: "Combined package export snapshot available." },
];

const snapshot: DocumentationGenerationSnapshot = { summary, documentation, patent, researchPaper, activity };

function markDocumentsGenerated(items: readonly GeneratedDocument[], generatedAt: string): readonly GeneratedDocument[] {
  return items.map((item) => ({ ...item, status: "generated", lastGeneratedAt: generatedAt }));
}

function markAssetsGenerated(items: readonly GeneratedAsset[], generatedAt: string): readonly GeneratedAsset[] {
  return items.map((item) => ({ ...item, status: item.status === "filed" ? item.status : "generated", lastGeneratedAt: generatedAt }));
}

function withActivity(event: GenerationActivity, events: readonly GenerationActivity[]): readonly GenerationActivity[] {
  return [event, ...events.filter((item) => item.id !== event.id && item.title !== event.title)].slice(0, 8);
}

function nextSnapshot(status: DocumentationGenerationSummary["generatorStatus"], generatedAt: string, event: GenerationActivity, updates: Partial<DocumentationGenerationSnapshot> = {}): DocumentationGenerationSnapshot {
  return {
    ...snapshot,
    ...updates,
    summary: { ...snapshot.summary, generatorStatus: status, lastGenerationAt: generatedAt },
    activity: withActivity(event, updates.activity ?? snapshot.activity),
  };
}

export class DeterministicDocumentationGenerationClient implements DocumentationGenerationClient {
  async getDocumentation(): Promise<readonly GeneratedDocument[]> { return snapshot.documentation; }
  async getPatent(): Promise<readonly GeneratedAsset[]> { return snapshot.patent; }
  async getResearchPaper(): Promise<readonly GeneratedAsset[]> { return snapshot.researchPaper; }
  async getSummary(): Promise<DocumentationGenerationSummary> { return snapshot.summary; }
  async getActivity(): Promise<readonly GenerationActivity[]> { return snapshot.activity; }
  async generateDocumentation(): Promise<DocumentationGenerationSnapshot> {
    const generatedAt = new Date().toISOString();
    return nextSnapshot("documentation-generated", generatedAt, { id: "documentation-generated-action", title: "Documentation Generated", type: "documentation", timestamp: generatedAt, detail: "Documentation generation requested through adapter." }, { documentation: markDocumentsGenerated(snapshot.documentation, generatedAt) });
  }
  async generatePatent(): Promise<DocumentationGenerationSnapshot> {
    const generatedAt = new Date().toISOString();
    return nextSnapshot("patent-generated", generatedAt, { id: "patent-generated-action", title: "Patent Generated", type: "patent", timestamp: generatedAt, detail: "Patent package generation requested through adapter." }, { patent: markAssetsGenerated(snapshot.patent, generatedAt) });
  }
  async generateResearchPaper(): Promise<DocumentationGenerationSnapshot> {
    const generatedAt = new Date().toISOString();
    return nextSnapshot("research-generated", generatedAt, { id: "research-generated-action", title: "Research Generated", type: "research", timestamp: generatedAt, detail: "Research paper generation requested through adapter." }, { researchPaper: markAssetsGenerated(snapshot.researchPaper, generatedAt) });
  }
  async refresh(): Promise<DocumentationGenerationSnapshot> {
    const generatedAt = new Date().toISOString();
    return nextSnapshot("refreshed", generatedAt, { id: "generator-refreshed-action", title: "Generator Refreshed", type: "refresh", timestamp: generatedAt, detail: "Documentation generation center refreshed through adapter." });
  }
  async exportPackage(): Promise<DocumentationGenerationSnapshot> {
    const generatedAt = new Date().toISOString();
    return nextSnapshot("package-exported", generatedAt, { id: "package-exported-action", title: "Package Exported", type: "package", timestamp: generatedAt, detail: "Combined documentation, patent, and research package exported." });
  }
}

export function createDocumentationGenerationClient(): DocumentationGenerationClient {
  return new DeterministicDocumentationGenerationClient();
}

export async function getDocumentationGenerationSnapshot(client: DocumentationGenerationClient): Promise<DocumentationGenerationSnapshot> {
  const [summary, documentation, patent, researchPaper, activity] = await Promise.all([client.getSummary(), client.getDocumentation(), client.getPatent(), client.getResearchPaper(), client.getActivity()]);
  return { summary, documentation, patent, researchPaper, activity };
}
