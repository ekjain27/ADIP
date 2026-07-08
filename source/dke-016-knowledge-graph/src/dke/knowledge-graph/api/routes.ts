import type { KnowledgeGraphController } from "./KnowledgeGraphController.js";

export interface RouteDefinition {
  method: "GET" | "POST" | "DELETE";
  path: string;
  handlerName: keyof KnowledgeGraphController;
}

export function createKnowledgeGraphRoutes(): RouteDefinition[] {
  return [
    { method: "POST", path: "/knowledge-graph/construct", handlerName: "construct" },
    { method: "POST", path: "/knowledge-graph/nodes", handlerName: "createNode" },
    { method: "GET", path: "/knowledge-graph/nodes/:id", handlerName: "getNode" },
    { method: "GET", path: "/knowledge-graph/nodes/:id/neighbors", handlerName: "getNeighbors" },
    { method: "POST", path: "/knowledge-graph/edges", handlerName: "createEdge" },
    { method: "GET", path: "/knowledge-graph/path?source=&target=", handlerName: "findPath" },
    { method: "POST", path: "/knowledge-graph/nodes/merge", handlerName: "mergeNodes" },
    { method: "DELETE", path: "/knowledge-graph/nodes/:id", handlerName: "deleteNode" },
    { method: "DELETE", path: "/knowledge-graph/edges/:id", handlerName: "deleteEdge" },
  ];
}
