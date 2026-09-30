# Feral Pig Startup Master Index

This document describes the current canonical working structure for the Startup project. The project is organized into active working folders, archive folders, and admin/support files. The root remains focused on current work and does not hold superseded or generated-export content.

## Root structure

- [admin](../admin)
  - Project operations content, naming conventions, scripts, manifest records, and project indexes.

- [archive](../archive)
  - Superseded versions, generated exports, packaged archives, and working extraction outputs.

- [claims](../claims)
  - Active claim drafting and claim-related documents.

- [docs](../docs)
  - Core project control documents, inventor materials, research notes, and legal process documents.

- [drafts](../drafts)
  - Current patent specification and provisional application files.

- [figures](../figures)
  - Patent figures and figure-related support material.

- [reference_materials](../reference_materials)
  - External legal and technical reference materials.

- [roadmap](../roadmap)
  - Product, patent, and project roadmap files.

- [tracker](../tracker)
  - Business tracker, project-status tracking files, and operating metrics.

- [new_materials](../new_materials)
  - Staging folder for newly generated project content awaiting canonical review.

- [Startup.code-workspace](../Startup.code-workspace)
  - Workspace configuration for the project.

## Active working folders

### admin
Contains:
- naming rules and standards
- project index files
- cleanup and manifest scripts
- project-maintenance documentation

Current examples:
- FeralPig_ContentDedup_v0.1_20260903.ps1
- FeralPig_DocumentManifest_v0.1_20260903.md
- FeralPig_ManifestChecklist_v0.1_20260903.md
- FeralPig_MasterIndex_v0.1_20260903.md
- FeralPig_NamingConvention_v0.1_20260903.md
- FeralPig_ProjectIndex_v0.1_20260903.md
- FeralPig_RenameScript_v0.1_20260903.ps1

### docs
Contains current control, legal-operational, and support documents.

Current examples:
- FeralPig_StatusProtocol_v0.5_20260903.md
- FeralPig_MasterControl_v0.5_20260903.docx
- FeralPig_ResearchNotes_v0.1_20260903.md
- FeralPig_InventorQuestionnaire_v0.1_20260903.docx
- FeralPig_SupportFigureAudit_v0.3_20260903.docx

### drafts
Contains the active patent drafting versions and working provisional drafts.

Current example:
- FeralPig_ProvisionalDraft_v0.5_20260903.docx

### claims
Contains the current claims set for the active patent drafting workflow.

Current example:
- FeralPig_ExemplaryClaims_v0.5_20260903.docx

### roadmap
Contains the current roadmap and milestone planning artifacts.

Current example:
- FeralPig_Roadmap_v0.4_20260903.pdf

### tracker
Contains current operational tracking files.

Current examples:
- FeralPig_Tracker_v0.2_20260903.xlsx
- FeralPig_TrackerTemplate_v0.1_20260903.csv

### figures
Contains current figures used in the patent or invention support package.

Current example:
- FeralPig_Figures_v0.2_20260903.pdf

### reference_materials
Contains external or background reference documents that support the patent process.

Current example:
- MPEP reference archive under the reference_materials folder

## Archive folders

### archive/duplicates
Stores superseded or redundant copies no longer part of the canonical working set.

### archive/generated-export
Stores exported browser or rendered versions of working sessions, including generated AI/browser export assets.

### archive/working
Stores extracted or unpacked archive outputs used for review or reference.

### archive/history
Stores older versioned snapshots retained for provenance and audit.

## Operational rules

1. Keep only the current canonical files in active folders.
2. Preserve historical or superseded versions in archive folders.
3. Use the naming convention:
   FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>
4. Keep the root clean and free of source-document clutter.
5. Treat archive folders as read-only reference/history storage unless intentionally updating a working version.
6. Treat [new_materials](../new_materials) as a staging area and route content into canonical folders only after review.
