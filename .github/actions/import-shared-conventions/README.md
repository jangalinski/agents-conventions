# import-shared-conventions

Composite GitHub Action for consuming repositories.

## Purpose

Read the consuming repo's `.agents/.shared.yml` or `.agents/.shared.yaml`, resolve the listed convention `id`s from this repository, copy the matching markdown files into `.agents/shared/<id>.md`, push a feature branch, and open a pull request.

## Usage

```yaml
- uses: jangalinski/agents-conventions/.github/actions/import-shared-conventions@main
```

The consuming workflow should already check out the consumer repository before invoking the action.
Omit `source_ref` to import from `main`. Set it only when you want to test a branch from this repository.

## Workflow permissions

The consuming workflow needs at least:

- `contents: write`
- `pull-requests: write`

The workflow should also provide `actions/checkout` for the consumer repository before invoking this action.
The implementation logic lives in `scripts/import_shared_conventions.py`.
