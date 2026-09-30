# Feral Pig Patent and Business Buildout

This project contains a working patent disclosure for recognition-gated animal population control, claim and support records, historical provenance, and separate staged reference-management and website projects. Human patent-professional review controls legal and filing decisions.

## Start here

- [Project instructions](admin/FeralPig_ProjectInstructions_v0.2_20260929.md): current operating rules and document authority.
- [Document ingestion index](admin/FeralPig_DocumentIngestionIndex_v0.1_20260929.md): file and archive-member coverage, hashes, source-derived instructions and discrepancies.
- [Resume plan](admin/FeralPig_ResumePlan_v0.1_20260929.md): verified checkpoint, evidence, open questions and next steps.
- [Current document manifest](admin/FeralPig_DocumentManifest_v1.4_20260929.md): active records, retained predecessors and local verification.
- [Codex project instructions](AGENTS.md) and [Copilot instructions](.github/copilot-instructions.md): project entry points.

## Current patent checkpoint

The controlling workbook is [tracker v1.3](tracker/FeralPig_Tracker_v1.3_20260904.xlsx), dated September 4, 2026. The current [specification](drafts/FeralPig_ProvisionalDraft_v0.7_20260903.docx) has 311 numbered paragraphs; the [claim set](claims/FeralPig_ExemplaryClaims_v0.7_20260903.docx) has 160 claims, including 15 independent claims. The [support audit](docs/FeralPig_SupportFigureAudit_v0.5_20260903.docx) is v0.5 and [figures](figures/FeralPig_Figures_v0.2_20260903.pdf) are v0.2.

The tracker records filing readiness as **NOT READY**, 22 unresolved blocking risks and inventor-confirmation dependencies. The reviewed source record contains no established filing date. Prior statements that the project is patent pending, fully QA-complete or ready for filing must not be adopted without evidence.

The last search checkpoint was PAT-049 / PS-12 first-pass work. The next queued search is PAT-050 / PS-13; PAT-051 / PS-14 awaits prosecution-record review. The resume plan records stale controls, support-citation drift, antecedent concerns and figure defects that must be reconciled before further drafting.

## Folder authority

| Folder | Role |
|---|---|
| `admin` | Instructions, indexes, manifests and project operations |
| `docs`, `drafts`, `claims`, `figures`, `roadmap`, `tracker` | Canonical patent/project records, subject to documented discrepancies |
| `reference_materials` | Retained legal/technical sources; source date does not prove current legal authority |
| `archive` | Historical, superseded and exported provenance; never current drafting authority |
| `current_drafts` | Derivative convenience copies; never authoritative |
| `new_materials` | Staged intake and separate imported software/site workstreams |

Project-authored records follow `FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>`. Immutable source names and workspace infrastructure retain existing names. This checkpoint does not move or delete retained predecessors.

## Repository publication

The two large MPEP ZIPs use Git LFS and share one content object. To obtain the actual archive bytes after cloning, use an installed Git LFS client and run `git lfs install`, then `git lfs pull`. The ingestion index records SHA-256 hashes of the original archive bytes, not the LFS pointer files. All other selected records use regular Git. LFS account capacity, upload and fresh-download verification are required before publication is reported complete.

The user expressly authorized a public [GitHub repository](https://github.com/RobertMLayne/feral-pig-startup) containing all records and source, including unpublished invention drafts, inventor materials and historical logs. Git internals, disposable Python caches, and local `.codex/` and `.vscode/` configurations are excluded. Authorization is specific to this publication and does not establish attorney clearance, patentability, inventorship, ownership, regulatory permission or filing readiness.

The repository preserves imported LayneIP working-tree files, including incomplete packaging. It does not represent a verified website build, website launch or DNS deployment. Reference Suite live integrations also remain unverified as described in the resume plan. No repository-wide license is added.
