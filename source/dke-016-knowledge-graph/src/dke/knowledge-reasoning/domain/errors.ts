export class ReasoningValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ReasoningValidationError";
  }
}

export class RuleEvaluationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RuleEvaluationError";
  }
}

export class ReasoningConflictError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ReasoningConflictError";
  }
}

export class OntologyReasoningError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "OntologyReasoningError";
  }
}

export class TemporalReasoningError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TemporalReasoningError";
  }
}

export class ReasoningDepthExceededError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ReasoningDepthExceededError";
  }
}

export class GraphReadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GraphReadError";
  }
}
