import type { ReasoningEvent } from "../domain/models.js";

export interface EventPublisherPort {
  publish(event: ReasoningEvent): Promise<void>;
}
