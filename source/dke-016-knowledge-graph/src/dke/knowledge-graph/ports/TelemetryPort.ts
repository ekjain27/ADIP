export interface TelemetrySpan {
  name: string;
  attributes?: Record<string, string | number | boolean>;
}

export interface TelemetryPort {
  startSpan(span: TelemetrySpan): { end(): void; recordException?(error: unknown): void };
}
