<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Reusable Skills

- Use `.github/skills/openspec-epub-workflow/SKILL.md` when a user wants to package OpenSpec proposals, project files, commit ranges, diffs, specs, designs, or tasks into a mark2epub-ready folder or EPUB for ereader review.
- Use `.github/skills/dearcygui-build/SKILL.md` when a user wants to build, rebuild, or run DearCyGui after editing `.pyx`/`.pxd` sources, or when debugging Cython/SDL3/CMake build issues, the venv toolchain, or `ModuleNotFoundError` on `dearcygui`.