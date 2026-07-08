import type { GraphEventPayload } from "../domain/index.js";

export function createGraphEvent(
  type: GraphEventPayload["type"],
  payload: Record<string, unknown>,
  correlationId?: string,
): GraphEventPayload {
  return {
    id: `evt_${crypto.randomUUID()}`,
    type,
    payload,
    createdAt: new Date().toISOString(),
    correlationId,
  };
}
