# AGENTS instructions

The core instruction manual for all ai-agents. This file contains only basic instructions and project description, detailed instructions and conventions are managed under `.agents/`.

## Temporary working notes

This section is temporary memory for the current setup phase and can be removed once the repo reaches a stable state.

- `_setup/` is a staging area for brainstormed content and early structure only.
- The public README must stay high-level and should not mention `_setup/`.
- The long-term goal is to centralize shared agent instructions, conventions, workflows, and reusable blocks for GitHub-based repos.
- The current repo is intentionally Gradle/Kotlin-based so future docs or tooling can be added here if needed.
- The first reusable GitHub-specific convention block lives at `.agents/conventions/github/gh-auth.md`.

## How To Create Shared Conventions

Use this section as the source of truth for all shared `.agents/**/*.md` conventions created in this repo.

### Template

Use the structure from [.agents/_templates/shared-agent-instruction.md](/Users/jangalinski/IdeaProjects/jangalinski/agents-conventions/.agents/_templates/shared-agent-instruction.md) as the baseline and extend it with the `agents:` frontmatter field.

Required frontmatter:

- `id`
- `title`
- `tags`
- `agents`
- `prio`
- `refs`
- `status`

Recommended frontmatter shape:

```md
---
id: github-gh-auth-bootstrap
title: GitHub CLI auth bootstrap

tags:
  - github
  - gh
  - auth
  - ci

agents:
  - codex

prio: SHOULD

refs:
  - title: GitHub CLI auth login
    url: https://cli.github.com/manual/gh_auth_login
    type: public-doc
    check: periodic

status: active
---
```

### Frontmatter Semantics

- `tags` describe the technical topic or domain.
- `agents` describe which agent families the convention applies to.
- `prio` describes how strongly the convention should be followed.
- `refs` point to supporting documentation or source material.

### Current Allowed Values

Tags:

- `github`
- `gh`
- `auth`
- `ci`

Agents:

- `codex`

Priorities:

- `SHOULD`

### Change Control

- Add new tags only when you agree to them explicitly.
- Add new agent names only when you agree to them explicitly.
- Add new priority levels only when you agree to them explicitly.
- Keep shared conventions machine-readable and consistent with this template.

### Workflow And Action Implementation

When writing GitHub workflows or GitHub actions in this repository, prefer `bash` and `python` for the implementation language.

- Use `bash` for thin wrappers and shell glue.
- Use `python` for lightweight parsing and file operations.
- Avoid introducing Ruby, JVM tooling, or other heavier languages unless explicitly requested.
