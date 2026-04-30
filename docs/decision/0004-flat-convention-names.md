# Decision 0004: Keep shared convention files flat and scope-prefixed

Date: 2026-04-29

## Context

Shared convention markdown files are tagged for multiple concerns, which makes directory-based grouping ambiguous.
For example, a file tagged with both `github` and `kotlin` could plausibly live in either a GitHub-focused or Kotlin-focused
repository. A nested directory structure pushes that decision into the path and creates avoidable debate.

## Decision

Keep `.agents/conventions/` flat by default.

Use the primary scope in both of these places:

- the markdown file name
- the `id` field

Examples:

- `github-gh-auth-bootstrap.md`
- `id: github-gh-auth-bootstrap`

Use tags only as metadata for secondary classification.

Add subdirectories only when the convention library grows enough that a flat layout becomes harder to navigate than a scoped one.

## Consequences

- Convention discovery stays simple and predictable.
- File names communicate the primary scope without relying on directory placement.
- Multi-tag conventions no longer force a folder choice before the content is read.
- Future convention additions should follow the same naming pattern unless the flat layout stops scaling.
