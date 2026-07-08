import type { GraphEventPayload } from "../domain/index.js";
import type { EventPublisherPort } from "../ports/index.js";

export class InMemoryEventPublisherAdapter implements EventPublisherPort {
  private readonly events: GraphEventPayload[] = [];

  async publish(event: GraphEventPayload): Promise<void> {
    this.events.push(event);
  }

  async listEvents(): Promise<GraphEventPayload[]> {
    return [...this.events];
  }
}
