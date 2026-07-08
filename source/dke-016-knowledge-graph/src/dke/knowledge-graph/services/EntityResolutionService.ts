import type { EntityResolutionPort } from "../ports/index.js";
import type { GraphNode } from "../domain/index.js";

export class EntityResolutionService implements EntityResolutionPort {
  constructor(private readonly threshold = 0.86) {}

  async findDuplicate(candidate: GraphNode, existing: GraphNode[]): Promise<GraphNode | null> {
    const candidateNames = this.names(candidate);
    for (const node of existing) {
      const existingNames = this.names(node);
      if (candidateNames.some((name) => existingNames.includes(name))) return node;
      const score = Math.max(...candidateNames.flatMap((left) => existingNames.map((right) => this.similarity(left, right))));
      if (score >= this.threshold) return node;
    }
    return null;
  }

  private names(node: GraphNode): string[] {
    return [node.canonicalName, ...node.aliases].map((name) => this.normalize(name)).filter(Boolean);
  }

  private normalize(value: string): string {
    return value.trim().toLocaleLowerCase().replace(/[^a-z0-9]+/g, " ");
  }

  private similarity(left: string, right: string): number {
    if (left === right) return 1;
    const distance = this.levenshtein(left, right);
    return 1 - distance / Math.max(left.length, right.length, 1);
  }

  private levenshtein(left: string, right: string): number {
    const rows = Array.from({ length: left.length + 1 }, (_, index) => [index]);
    for (let j = 1; j <= right.length; j += 1) rows[0][j] = j;
    for (let i = 1; i <= left.length; i += 1) {
      for (let j = 1; j <= right.length; j += 1) {
        rows[i][j] = left[i - 1] === right[j - 1]
          ? rows[i - 1][j - 1]
          : Math.min(rows[i - 1][j - 1], rows[i][j - 1], rows[i - 1][j]) + 1;
      }
    }
    return rows[left.length][right.length];
  }
}
