# Agent Conventions Repository

## Purpose
Centralized, reusable, tool-agnostic engineering conventions and agent instructions.

## Structure
- conventions/: reusable rules
- stacks/: stack-specific bundles
- templates/: instruction templates
- docs/: generated documentation

## Distribution Model
- Target repos define `.agents/shared.yml`
- GitHub Action syncs selected modules into `.agents/shared/`
