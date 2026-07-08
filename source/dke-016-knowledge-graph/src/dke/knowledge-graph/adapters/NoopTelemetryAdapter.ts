import type { TelemetryPort, TelemetrySpan } from "../ports/index.js";

export class NoopTelemetryAdapter implements TelemetryPort {
  startSpan(_span: TelemetrySpan): { end(): void; recordException(error: unknown): void } {
    return {
      end(): void {},
      recordException(_error: unknown): void {},
    };
  }
}
