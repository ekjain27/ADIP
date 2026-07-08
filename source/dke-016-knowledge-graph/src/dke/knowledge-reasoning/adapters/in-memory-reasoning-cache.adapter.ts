import type { ReasoningResult } from "../domain/models.js";
import type { ReasoningCachePort } from "../ports/index.js";

export class InMemoryReasoningCache implements ReasoningCachePort {
  private readonly values = new Map<string, { value: ReasoningResult; expiresAt?: number }>();

  async get(key: string): Promise<ReasoningResult | null> {
    const entry = this.values.get(key);
    if (!entry) {
      return null;
    }
    if (entry.expiresAt && entry.expiresAt < Date.now()) {
      this.values.delete(key);
      return null;
    }
    return entry.value;
  }

  async set(key: string, value: ReasoningResult, ttlMs?: number): Promise<void> {
    this.values.set(key, { value, expiresAt: ttlMs ? Date.now() + ttlMs : undefined });
  }

  async delete(key: string): Promise<void> {
    this.values.delete(key);
  }

  async clear(): Promise<void> {
    this.values.clear();
  }
}
