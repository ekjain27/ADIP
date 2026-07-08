import type { ReasoningResult } from "../domain/models.js";

export interface ReasoningCachePort {
  get(key: string): Promise<ReasoningResult | null>;
  set(key: string, value: ReasoningResult, ttlMs?: number): Promise<void>;
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
}
