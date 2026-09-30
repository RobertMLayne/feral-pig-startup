---
applyTo: "**/*.{md,py,ts,js,json,yml,yaml,ps1,sh,txt}"
description: "Use when setting up or adjusting local developer tooling, environment configuration, Docker, WSL, Python, Node, or project infrastructure."
---

# Local development and infrastructure guidance

- Prefer reproducible machine-level configuration over ad hoc one-off commands.
- Use WSL2 + Ubuntu for Linux-native tooling, Docker, and shell-based automation where practical.
- Keep Windows host setup minimal and stable; use the WSL environment for package-heavy Linux work.
- Install and verify tools with version checks before relying on them for automation.
- Keep environment variables and PATH configuration explicit and well documented.
- Prefer `uv` for Python package and tool management when available.
- Prefer `npm` or `npx` only when a package is required; avoid unnecessary global installs.
- For Docker, prefer the Desktop daemon on Windows and use Linux containers by default.
- When a tool fails due to path issues, re-check PATH and tool availability rather than guessing.
- Keep workspace customizations in the repo, and machine-level settings in the user profile or OS-level config.
