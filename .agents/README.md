# `.agents` Layout

This directory contains the shared instruction catalogue for this repository and for downstream consumer repos.

## Structure

- `.agents/conventions/` contains shared convention documents.
- `.agents/_templates/` contains authoring templates and supporting scaffolding.
- `.agents/.catalog.yml` contains the machine-readable registry of allowed tags, agents, and priorities.

## Reading Order

1. Read [conventions/general.md](conventions/general.md) first.
1. Read any more specific convention files that apply to the task.
1. Use the refs in each convention for supporting background only.

## Rules

- Treat all `.agents/**/*.md` files as one catalogue.
- Treat local `.agents/**/*.md` files and shared `.agents/shared/**/*.md` files as a combined set when a consumer repo uses both.
- Prefer the convention markdown over references when there is a conflict.
- Use hidden files for machine-readable metadata that should not be considered public documentation.

## Authoring

- Keep new convention files flat by default.
- Encode the primary scope in the filename and in the `id` field.
- Use tags for classification, agents for applicability, and prio for strength of requirement.
