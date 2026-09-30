---
mode: agent
description: "Use for repo planning, environment diagnostics, implementation work, and safe AI-assisted changes in this project. Optimized for patent-project workflow, canonical file discipline, WSL/Docker tooling, and verification-first execution."
---

# Project mode for this repository

Use this prompt when working on the Startup workspace, especially for:
- repo operations and directory hygiene
- infrastructure or environment setup
- project planning and implementation tasks
- drafting, editing, or reviewing canonical project files
- diagnosing toolchain or MCP issues
- safe AI-assisted work that must stay aligned with the project rules

Operating rules:
1. Treat the canonical project folders as the source of truth. Do not continue stale or archived logic.
2. Before changing files, confirm the active tracker/instructions are current and relevant.
3. Archive, generated-export, and duplicate content are noncanonical reference material only.
4. Prefer minimal, root-cause fixes over broad or speculative edits.
5. Verify tool availability and command results before reporting success.
6. Keep environment changes reproducible and explicit.
7. For development tasks, prefer WSL Ubuntu + Docker for Linux-native workflows and keep Windows host config minimal.
8. For final output, cite actual validation evidence rather than assumptions.

Execution flow:
1. Review the active project instructions and workspace state.
2. Identify the task type: project planning, environment, code fix, or infrastructure.
3. Determine what is repo-local versus machine-local.
4. Make the smallest correct change.
5. Validate with direct command output or a narrow proof step.
6. Report what was validated and any follow-up requirements.

Repository-specific focus:
- Keep the work aligned with the patent/business buildout goals.
- Preserve the naming convention, canonical folder discipline, and tracker-first workflow.
- Treat legal/public-disclosure risk as higher priority than speed.
- Use attorney review and human confirmation for material filings or disclosures.
