import type { ReasoningEvent } from "../domain/models.js";
import type { EventPublisherPort } from "../ports/index.js";

export class InMemoryEventPublisher implements EventPublisherPort {
  readonly events: ReasoningEvent[] = [];

  async publish(event: ReasoningEvent): Promise<void> {
    this.events.push(event);
  }
}
