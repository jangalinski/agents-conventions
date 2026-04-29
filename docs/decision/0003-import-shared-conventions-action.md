# Decision 0003: Provide a reusable import-shared-conventions GitHub Action

Date: 2026-04-29

## Context

Consuming repositories need a lightweight, reusable way to import selected shared conventions from this repository.
The first selector model is a flat list of unique convention `id` values.

## Decision

Provide a composite GitHub Action named `import-shared-conventions`.

The action:

- reads `.agents/.shared.yml` or `.agents/.shared.yaml` from the consuming repository
- checks out this repository at a configured ref
- resolves the requested convention ids
- copies the matching markdown files into `.agents/shared/<id>.md`
- commits the changes on a feature branch
- opens a pull request against the consumer's default branch

## Consequences

- Consumer repos can import conventions without reimplementing the lookup/copy/PR flow.
- The action keeps the current selection model simple and id-based.
- The source repository is implicit; consumers only override the ref when they need to test a branch.
- Later versions can extend the selector logic to tags, agents, or other criteria without changing the basic workflow shape.
