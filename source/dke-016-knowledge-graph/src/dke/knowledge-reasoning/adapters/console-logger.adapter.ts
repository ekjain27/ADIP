import type { LoggerPort } from "../ports/index.js";

export class ConsoleLogger implements LoggerPort {
  debug(message: string, context?: Readonly<Record<string, unknown>>): void {
    console.debug(message, context ?? {});
  }

  info(message: string, context?: Readonly<Record<string, unknown>>): void {
    console.info(message, context ?? {});
  }

  warn(message: string, context?: Readonly<Record<string, unknown>>): void {
    console.warn(message, context ?? {});
  }

  error(message: string, context?: Readonly<Record<string, unknown>>): void {
    console.error(message, context ?? {});
  }
}

export class NullLogger implements LoggerPort {
  debug(): void {}
  info(): void {}
  warn(): void {}
  error(): void {}
}
