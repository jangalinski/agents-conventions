# import-shared-conventions

Composite GitHub Action for consuming repositories.

## Purpose

Read the consuming repo's `.agents/.shared.yml` or `.agents/.shared.yaml`, resolve the listed convention `id`s from this repository, copy the matching markdown files into `.agents/shared/<id>.md`, always include `general.md`, push a feature branch, and open a pull request.

## Usage

```yaml
- uses: jangalinski/agents-conventions/.github/actions/import-shared-conventions@main
```

The consuming workflow should already check out the consumer repository before invoking the action.
To test a branch of this action repository, change the ref in `uses:` to that branch name.
The optional `source_ref` input stays available for workflows that need to import from a different branch than the action ref itself.

## Workflow permissions

The consuming workflow needs at least:

- `contents: write`
- `pull-requests: write`

The workflow should also provide `actions/checkout` for the consumer repository before invoking this action.
GitHub Actions must be allowed to create pull requests in the consumer repo or organization, otherwise the final PR creation step will fail.
If the repository-level toggle is greyed out, enable **Allow GitHub Actions to create and approve pull requests** at the organization level.
The implementation logic lives in `scripts/import_shared_conventions.py`.
