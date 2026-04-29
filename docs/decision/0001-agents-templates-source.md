# Decision 0001: Use `.agents/_templates` for shared convention templates

Date: 2026-04-29

## Context

This repository is the central source of truth for shared agent conventions and reusable instruction blocks.
Template-based markdown needs a stable location so future shared `.agents/**/*.md` files can be created consistently
and later analyzed or rendered as documentation.

## Decision

Use `.agents/_templates` as the source of truth for template-based file creation.

The template stored there defines the canonical structure for shared convention markdown:

- `id`
- `title`
- `tags`
- `agents`
- `prio`
- `refs`
- `status`

## Consequences

- Shared convention files under `.agents/` should be created from the template in `.agents/_templates`.
- Future docs or automation can parse `.agents/_templates` as the machine-readable template source.
