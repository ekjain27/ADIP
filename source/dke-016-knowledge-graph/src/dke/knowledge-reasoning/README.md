# DKE-017 Knowledge Graph Reasoning Engine

DKE-017 is the read-only reasoning layer for DecisionOS. It consumes the DKE-016 knowledge graph through public read exports adapted into `GraphReadPort`; it never mutates nodes, edges, evidence, repositories, or entity identity.

## Architecture

The module follows Clean Architecture with ports, adapters, dependency injection, and controller delegation:

- `domain`: strongly typed reasoning models and errors.
- `ports`: graph read, rules, ontology, cache, logging, metrics, and events.
- `services`: deterministic reasoning logic for paths, rules, ontology, time, confidence, conflicts, missing links, ranking, and explanations.
- `adapters`: DKE-016 read adapter, in-memory graph/rules/cache/metrics/logger/events.
- `api`: controller handlers for the public POST endpoints.
- `composition`: dependency injection root.

## Reasoning Flow

1. Validate `ReasoningQuery`.
2. Resolve the source node through `GraphReadPort`.
3. Traverse accessible graph paths up to `maxDepth`.
4. Prune cycles, expired edges, inaccessible nodes/evidence, and low-confidence paths.
5. Apply configurable deterministic rules.
6. Apply ontology inheritance for `IS_A` paths.
7. Detect conflicts.
8. Apply confidence propagation and conflict penalties.
9. Suggest missing links when strong inferred relationships lack direct accessible edges.
10. Rank paths and generate an explanation trace.

## Rule Engine

Rules are data, not hardcoded service branches:

```json
{
  "id": "rule_supplies_produces_affects",
  "name": "Supplier production impact",
  "when": { "path": ["SUPPLIES", "PRODUCES"] },
  "then": { "relationshipType": "AFFECTS" },
  "confidenceModifier": 0.95,
  "enabled": true
}
```

The engine returns a `ReasoningConclusion`; it does not create an `AFFECTS` graph edge.

## Temporal Reasoning

Queries may include `reasoningDate`. Edges outside `validFrom` and `validTo` are ignored. Edges where `validFrom` is after `validTo` raise `TemporalReasoningError`.

## Confidence Model

```text
FinalConfidence = PathConfidence * RuleModifier * EvidenceConfidence * TemporalValidity * ConflictPenalty
```

All values are clamped between `0` and `1`.

## Conflict Detection

The engine detects contradictory relationships, overlapping contradiction windows, ontology mismatches, confidence disagreements, and circular dependencies. Conflicts are returned as data; the graph is never modified.

## API Endpoints

- `POST /knowledge-graph/reason`
- `POST /knowledge-graph/reason/paths`
- `POST /knowledge-graph/reason/rules`
- `POST /knowledge-graph/reason/conflicts`
- `POST /knowledge-graph/reason/missing-links`
- `POST /knowledge-graph/reason/explain`

## Example Request

```json
{
  "sourceNodeId": "supplier",
  "maxDepth": 2,
  "minConfidence": 0.4,
  "reasoningDate": "2026-06-28T00:00:00.000Z",
  "includeConflicts": true,
  "includeMissingLinkSuggestions": true,
  "visibility": {
    "roles": ["analyst"],
    "allowedEvidenceIds": ["ev1", "ev2"]
  }
}
```

## Example Response

```json
{
  "paths": [
    {
      "id": "path_e1_e2",
      "relationshipTypes": ["SUPPLIES", "PRODUCES"],
      "confidence": 0.72
    }
  ],
  "conclusions": [
    {
      "relationshipType": "AFFECTS",
      "sourceNodeId": "supplier",
      "targetNodeId": "product",
      "confidence": 0.49248,
      "ruleId": "rule_supplies_produces_affects"
    }
  ],
  "missingLinkSuggestions": [
    {
      "relationshipType": "AFFECTS",
      "sourceNodeId": "supplier",
      "targetNodeId": "product",
      "reason": "Strong inferred relationship exists, but no accessible direct edge exists."
    }
  ]
}
```

## Events And Metrics

Events: `ReasoningStarted`, `ReasoningCompleted`, `ReasoningFailed`, `ConflictDetected`, `MissingLinkSuggested`, and `RuleApplied`.

Metrics: `reasoningRequests`, `reasoningSuccesses`, `reasoningFailures`, `averageReasoningTime`, `pathsEvaluated`, `rulesApplied`, `conflictsDetected`, `missingLinksSuggested`, and `averageConfidence`.

## Limitations

DKE-017 is deterministic and read-only. It does not perform recommendations, predictions, simulations, autonomous decisions, entity merges, evidence updates, repository writes, or graph mutation.

## Future Extensions

Future modules can add richer ontology adapters, external rule repositories, distributed cache adapters, and larger graph traversal optimizations without changing the service boundary.
