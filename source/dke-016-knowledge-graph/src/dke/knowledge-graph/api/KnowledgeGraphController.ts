import type { GraphConstructionInput, GraphEdge, GraphEdgeInput, GraphNode, GraphNodeInput } from "../domain/index.js";
import { EdgeService, GraphConstructionService, GraphIndexService, NodeService } from "../services/index.js";

export class KnowledgeGraphController {
  constructor(
    private readonly constructionService: GraphConstructionService,
    private readonly nodeService: NodeService,
    private readonly edgeService: EdgeService,
    private readonly indexService: GraphIndexService,
  ) {}

  construct(payload: GraphConstructionInput) {
    return this.constructionService.construct(payload);
  }

  createNode(payload: GraphNodeInput) {
    return this.nodeService.createNode(payload);
  }

  getNode(id: string) {
    return this.nodeService.getNodeById(id);
  }

  getNeighbors(id: string) {
    return this.indexService.getNeighbors(id);
  }

  createEdge(payload: GraphEdgeInput) {
    return this.edgeService.createEdge(payload);
  }

  findPath(source: string, target: string) {
    return this.indexService.findPath(source, target);
  }

  mergeNodes(targetNodeId: string, incomingNode: GraphNode) {
    return this.nodeService.mergeNodes(targetNodeId, incomingNode);
  }

  deleteNode(id: string) {
    return this.nodeService.deleteNode(id);
  }

  deleteEdge(id: string) {
    return this.edgeService.deleteEdge(id);
  }

  updateNode(payload: GraphNode) {
    return this.nodeService.updateNode(payload);
  }

  updateEdge(payload: GraphEdge) {
    return this.edgeService.updateEdge(payload);
  }
}
