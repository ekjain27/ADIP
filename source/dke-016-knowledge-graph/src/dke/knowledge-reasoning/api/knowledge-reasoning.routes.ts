export const knowledgeGraphReasoningRoutes = [
  { method: "POST", path: "/knowledge-graph/reason", handler: "reason" },
  { method: "POST", path: "/knowledge-graph/reason/paths", handler: "paths" },
  { method: "POST", path: "/knowledge-graph/reason/rules", handler: "rules" },
  { method: "POST", path: "/knowledge-graph/reason/conflicts", handler: "conflicts" },
  { method: "POST", path: "/knowledge-graph/reason/missing-links", handler: "missingLinks" },
  { method: "POST", path: "/knowledge-graph/reason/explain", handler: "explain" }
] as const;
