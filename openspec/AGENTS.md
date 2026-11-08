# OpenSpec Instructions

Use OpenSpec to plan significant capabilities, breaking changes, and
architectural changes. Routine bug fixes, documentation updates, and tests for
existing behavior can be handled directly.

## Before proposing a change

- Read `project.md` for repository context.
- Check current specs and active changes with `openspec list --specs` and
  `openspec list`.
- Search the relevant source and specs for existing behavior before proposing
  a duplicate capability.

## Workflow

- Use the GitHub Copilot `/opsx:propose` prompt to create a proposal and its
  artifacts.
- Use `/opsx:apply` to implement a proposal once its scope is ready.
- Use `/opsx:sync` to synchronize specs and `/opsx:archive` after a change is
  complete.
- Validate changes with `openspec validate <change-name>` before archiving.
- Keep proposals and specs focused on behavior and requirements; do not copy
  unrelated changes from other repository checkouts.
