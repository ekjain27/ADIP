import type { LoggerPort } from "../ports/index.js";

export class ConsoleLoggerAdapter implements LoggerPort {
  debug(message: string, context?: Record<string, unknown>): void {
    console.debug(message, context ?? {});
  }
  info(message: string, context?: Record<string, unknown>): void {
    console.info(message, context ?? {});
  }
  warn(message: string, context?: Record<string, unknown>): void {
    console.warn(message, context ?? {});
  }
  error(message: string, context?: Record<string, unknown>): void {
    console.error(message, context ?? {});
  }
}
