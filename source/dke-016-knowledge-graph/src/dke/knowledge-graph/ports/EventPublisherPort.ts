import type { GraphEventPayload } from "../domain/index.js";

export interface EventPublisherPort {
  publish(event: GraphEventPayload): Promise<void>;
  listEvents?(): Promise<GraphEventPayload[]>;
}
