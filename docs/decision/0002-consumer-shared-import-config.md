# Decision 0002: Use `.agents/.shared.yaml` for consumer import selection

Date: 2026-04-29

## Context

Consuming repositories need a simple local configuration file that tells the shared-convention import workflow
which conventions to copy from this repository.

## Decision

Use `.agents/.shared.yaml` in consuming repositories as the import configuration file.

The first version contains:

- `ids`

## Consequences

- The import workflow can resolve conventions by unique `id` values first.
- Consuming repos keep the selector local and ignored alongside their agent setup.
- The schema can later be extended to support tags, agents, or other selectors without changing the file location.
- The source repository itself is fixed by the reusable action; only the source ref stays configurable.
