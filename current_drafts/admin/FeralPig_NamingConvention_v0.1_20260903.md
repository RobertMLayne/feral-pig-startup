# Project Naming Convention

All working documents use the following format:

FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>

Examples:
- FeralPig_StatusProtocol_v0.4_20260903.md
- FeralPig_ProvisionalDraft_v0.3_20260903.docx
- FeralPig_ExemplaryClaims_v0.4_20260903.docx
- FeralPig_Roadmap_v0.3_20260903.pdf

## Why this convention

- The project name remains consistent across all artifacts.
- Version tracking is explicit and machine-readable.
- Date stamping supports revision history and auditability.
- The format is easy to sort by date and version.

## Usage rules

1. Use semantic-style version numbers such as v0.1, v0.2, v0.3, v0.4.
2. Use the date in YYYYMMDD format for traceability.
3. Keep the artifact name short but descriptive.
4. Archive duplicate or superseded copies rather than leaving them in the active working set.

## Rename method

Use the script at:

./rename_startup_documents.ps1

This script applies the convention across the current working folders and archives duplicate versions automatically.
