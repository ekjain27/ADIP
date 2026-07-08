import type { GraphNodeType, GraphRelationType } from "../domain/index.js";

export interface OntologyPort {
  isAllowedNodeType(type: GraphNodeType): Promise<boolean>;
  isAllowedRelationType(type: GraphRelationType): Promise<boolean>;
  relationMatchScore(type: GraphRelationType): Promise<number>;
}
