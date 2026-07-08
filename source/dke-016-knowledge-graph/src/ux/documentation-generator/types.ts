export interface DocumentationGenerationSummary {
  readonly generatorStatus: "ready" | "documentation-generated" | "patent-generated" | "research-generated" | "refreshed" | "package-exported";
  readonly currentProject: string;
  readonly lastGenerationAt: string;
  readonly packageVersion: string;
}

export interface GeneratedDocument {
  readonly id: string;
  readonly title: "Architecture" | "API" | "User Guide" | "Technical Guide" | "Deployment Guide";
  readonly status: "ready" | "generated" | "review";
  readonly version: string;
  readonly lastGeneratedAt: string;
  readonly summary: string;
}

export interface GeneratedAsset {
  readonly id: string;
  readonly title: string;
  readonly status: "ready" | "generated" | "review" | "filed";
  readonly version: string;
  readonly lastGeneratedAt: string;
  readonly summary: string;
}

export interface GenerationActivity {
  readonly id: string;
  readonly title: "Documentation Generated" | "Patent Generated" | "Research Generated" | "Package Exported" | "Generator Refreshed";
  readonly type: "documentation" | "patent" | "research" | "package" | "refresh";
  readonly timestamp: string;
  readonly detail: string;
}

export interface DocumentationGenerationSnapshot {
  readonly summary: DocumentationGenerationSummary;
  readonly documentation: readonly GeneratedDocument[];
  readonly patent: readonly GeneratedAsset[];
  readonly researchPaper: readonly GeneratedAsset[];
  readonly activity: readonly GenerationActivity[];
}

export interface DocumentationGenerationClient {
  getDocumentation(): Promise<readonly GeneratedDocument[]>;
  getPatent(): Promise<readonly GeneratedAsset[]>;
  getResearchPaper(): Promise<readonly GeneratedAsset[]>;
  getSummary(): Promise<DocumentationGenerationSummary>;
  getActivity(): Promise<readonly GenerationActivity[]>;
  generateDocumentation(): Promise<DocumentationGenerationSnapshot>;
  generatePatent(): Promise<DocumentationGenerationSnapshot>;
  generateResearchPaper(): Promise<DocumentationGenerationSnapshot>;
  refresh(): Promise<DocumentationGenerationSnapshot>;
  exportPackage(): Promise<DocumentationGenerationSnapshot>;
}
