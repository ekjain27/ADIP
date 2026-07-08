# DIE-015 Temporal Decision Lineage & Versioning Engine

DIE-015 consumes a `GovernanceDecisionPackage` from DIE-014 and produces a `TemporalDecisionPackage`.

## Temporal Decision Lineage Ledger

The Temporal Decision Lineage Ledger, or TDLL, records how decisions evolve across their lifecycle: decision versions, governance decisions, policy changes, learning updates, confidence changes, rollback points, and the active decision version.

## Architecture

- `VersionManager` creates ordered versions, parent references, metadata, and active version selection.
- `ChangeTracker` records governance, policy, confidence, learning, planning, optimization, and provenance changes.
- `TimelineBuilder` creates chronological events for versions, governance updates, learning updates, rollback points, confidence updates, and policy updates.
- `RollbackManager` creates rollback points and validates rollback targets.
- `LineageLedger` assembles immutable in-memory ledgers.
- `TemporalValidator` validates version ordering, timeline ordering, rollback references, unique versions, no version cycles, and active version existence.
- `TemporalPackageBuilder` assembles timestamped temporal decision packages.
- `TemporalDecisionEngine` coordinates end-to-end temporal tracking.

Future persistent ledgers, distributed ledgers, blockchain adapters, event sourcing, and temporal graph engines can plug in by replacing managers, builders, validators, or package components without changing the public API.
