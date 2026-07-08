export class KnowledgeGraphError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

export class GraphValidationError extends KnowledgeGraphError {}
export class DuplicateEntityError extends KnowledgeGraphError {}
export class NodeNotFoundError extends KnowledgeGraphError {}
export class EdgeNotFoundError extends KnowledgeGraphError {}
export class GraphConsistencyError extends KnowledgeGraphError {}
export class GraphRepositoryError extends KnowledgeGraphError {}
export class GraphConstructionError extends KnowledgeGraphError {}

export class ValidationError extends GraphValidationError {}
export class NotFoundError extends KnowledgeGraphError {}
export class ConflictError extends KnowledgeGraphError {}
