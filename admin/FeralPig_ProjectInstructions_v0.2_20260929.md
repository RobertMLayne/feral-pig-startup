# FeralPig Project Instructions
Version: v0.2
Date: 2026-09-29
Project root: `Feral Pig Startup`

This local instruction revision preserves the v0.1 patent-work rules, identifies current source conflicts, and adds separate-workstream and publication controls. The original v0.1 file is retained unchanged. The current manifest controls promotion/version status; a local hash check is not a live OneDrive write verification. This revision does not alter patent content, workbook cells, inventorship facts, or filing status.

## 1. Project purpose

Build a patent and business around detecting and identifying pests or other target animals using video, audio, or other recognition technology and selectively applying lethal or nonlethal population-control measures.

The disclosure and claim architecture should preserve a broad-to-narrow ladder:

1. generic target-animal or pest recognition and control;
2. selective targeting, access, timing, dispensing, exposure, or delivery;
3. local-population learning, state estimation, and population-conditioned authorization;
4. feral-swine population-control embodiments;
5. narrow embodiments in which a generally toxic or other population-control agent is exposed only after a defined local-population condition is satisfied.

This ladder is illustrative only. **The current tracker controls claim numbers, parentage, version, status and risk metadata. The canonical claim text controls the actual limitations and scope; a tracker summary cannot replace that text.** Reconcile conflicts before drafting, and do not infer a fixed claim number from this description.

## 2. Hard-stop rules

- Enablement and written description control the provisional filing. Do not postpone an otherwise ready provisional merely to polish claims.
- The current live tracker is the controlling project-state record.
- Do not draft against archived, superseded, generated-export, duplicate, convenience-snapshot, or stale sandbox files.
- No filing, public disclosure, material external technical disclosure, pilot disclosure, grant disclosure containing protected technical detail, or partner disclosure without attorney review and NDA or other disclosure controls as appropriate, subject to a later explicit user instruction authorizing a particular action. The September 29 public GitHub authorization is recorded in section 15; do not generalize it to other external actions.
- Check AI retention/training settings before disclosing invention details to any AI system.
- Settle inventorship and conception records in writing before equity formation, IP assignment, licensing, or commercial use.
- Regulatory, wildlife, pesticide/poison, product-label, permit, and deployment legality are separate from patentability.
- Public-disclosure risk overrides speed. Human review controls, including an explicit scoped user override; do not treat that override as proof that a historical legal or filing gate has been cleared.
- Never revive stale Set-1 logic, an artificial 20-claim ceiling, obsolete mid-scope claim instructions, or a superseded claim-number exemplar.
- Never reset to an older architecture or earlier drafting posture unless the tracker expressly records that decision.
- Do not claim project completion without verifying workspace state, versions, naming, risk status, and the live tracker.

## 3. Workspace authority and live-write protocol

### 3.1 Authority hierarchy

Use this hierarchy:

1. live OneDrive tracker and canonical active files;
2. live document manifest;
3. locally synchronized Windows mirror;
4. incoming/staging material;
5. sandbox drafting artifacts;
6. derivative convenience snapshots such as `current_drafts`;
7. archive/history and generated exports.

If the local Windows mirror and live OneDrive differ materially, stop substantive drafting and reconcile the sync conflict.

### 3.2 Canonical folders

Canonical active folders are:

- `Feral Pig Startup\admin`
- `Feral Pig Startup\docs`
- `Feral Pig Startup\drafts`
- `Feral Pig Startup\claims`
- `Feral Pig Startup\figures`
- `Feral Pig Startup\reference_materials`
- `Feral Pig Startup\roadmap`
- `Feral Pig Startup\tracker`

Additional controlled folders:

- `Feral Pig Startup\new_materials` — incoming/staging only;
- `Feral Pig Startup\current_drafts` — derivative latest-only convenience snapshot, never authoritative;
- `Feral Pig Startup\archive\history` — superseded/historical project artifacts;
- `Feral Pig Startup\archive\generated-export` — generated/export provenance only.

The project root should remain focused on canonical project structure and workspace configuration.

### 3.3 Naming and artifact-family continuity

Project-authored substantive artifacts use:

`FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>`

Revisions addressing the same artifact or function must retain the same descriptive artifact stem unless a deliberate family split is recorded in the tracker/manifest.

Exceptions:
- immutable external-source originals may retain source filenames;
- browser-export internal dependency assets may retain generated filenames when renaming would break the preserved export package;
- workspace infrastructure such as `.github`, `.vscode`, `README.md`, and `Startup.code-workspace` need not use the FeralPig prefix.

Retire superseded active revisions in the tracker/manifest after the new revision is verified. Preserve the canonical folder structure and original records. Move a predecessor to archive/history only when the user has authorized that move; do not rename, move, archive, or delete originals during this September 29 instruction/publication checkpoint.

### 3.4 Material-write verification

A sandbox artifact is not canonical merely because it was generated.

For every separately authorized live OneDrive revision:

1. read the exact current live tracker and target artifact before drafting;
2. generate and QA the revision in the sandbox;
3. write the new versioned artifact to the correct canonical OneDrive folder;
4. read back the exact resulting OneDrive item;
5. download/read the resulting bytes and compute SHA-256 independently;
6. verify the read-back hash against the generated artifact;
7. retire the superseded active revision in the control records and archive it only if the user has authorized the move;
8. update the document manifest with canonical path, version/date, OneDrive item ID, SHA-256, current/canonical status, and superseded predecessor;
9. read back and hash the updated manifest;
10. refresh changed `current_drafts` derivative copies and verify their hashes against canonical counterparts.

Use the phrase **“Live OneDrive write verified”** only after exact-item read-back succeeds. At filing-critical checkpoints, independently verify the local Windows-synced copy by SHA-256 as well.

Authorized local work may proceed from the verified local record without online OneDrive access. Label its verification as local, record hash/version conflicts, and do not claim live synchronization or exact online item verification. The September 29 local instruction/publication checkpoint preserves the existing convenience snapshots rather than refreshing them.

## 4. Claim strategy

- There is no artificial claim-count ceiling for the provisional or active claim universe.
- The active claim universe is an unrestricted disclosure/claim platform, not a fixed Set-1 architecture.
- Claims may be added, reorganized, narrowed, expanded, or supplemented whenever doing so improves disclosure support, fallback coverage, differentiation, or conversion options.
- Distinct invention families may be tracked for restriction, unity, prosecution, divisional, continuation, or continuation-in-part analysis, but they are not constrained by obsolete claim-count assumptions.
- Broad claims may remain as disclosure/patentability probes even when prior-art risk is high, provided the tracker accurately records the risk and no unsupported patentability conclusion is made.
- Do not prune solely because AI prior-art triage identifies risk. Professional search and licensed patent-counsel analysis control prosecution decisions.

### Representative scope ladder — unnumbered

Broad exemplar:
- recognize a pest or target animal using video, audio, or other recognition technology and selectively perform a disclosed lethal or control operation using concrete acts, structures, materials, or treatment classes.

Intermediate exemplar:
- selectively control target access, exposure, dispensing, timing, localization, treatment, or other control based on recognition and applicable safety conditions.

Population-state exemplar:
- learn or maintain information representing a local target population and condition a control operation on a defined population-state criterion.

Narrow feral-swine exemplar:
- learn the applicable local feral-pig membership, establish a defined contemporaneous completeness condition, and selectively expose the required presently represented members to a generally toxic or other population-control treatment through controlled timing/access/delivery while applying non-target, unresolved-member, safety, and revalidation vetoes.

**Do not assign these exemplars to a fixed claim number. The live tracker controls claim numbering and parentage.**

## 5. Tracker requirements

For each claim, maintain at minimum:

- claim number;
- family/set identifier (current P-U1 is a universe identifier, not the descriptive invention-family label);
- independent/dependent status;
- parent claim;
- scope summary;
- full claim language;
- status;
- risk flags;
- last-updated date;
- provisional/conversion role;
- specification-support references where maintained by the current tracker.

Statuses:
- drafted;
- under review;
- attorney-reviewed;
- final.

Risk flags include as applicable:
- §112(f);
- §112(b);
- written-description gap;
- enablement gap;
- prior-art risk;
- restriction/unity risk;
- regulatory/deployment issue;
- inventorship/ownership issue;
- disclosure-control issue.

The tracker may contain additional audit, source, search, figure, support, and governance fields. Those current live fields are controlling even if this instruction file lists only the minimum.

## 6. Patent drafting workflow

1. Re-read these instructions and the current live workspace.
2. Read the live tracker and relevant canonical specification/claims/support/figure files.
3. Compare instructions, tracker, active files, manifest, and—only if needed for provenance—archive history.
4. Identify stale rules, duplicate authority copies, inconsistent family stems, mismatched versions, or conflicting status.
5. Resolve or expressly record discrepancies before drafting.
6. Draft/expand enabling specification first where support is incomplete.
7. Update the tracker before or in the same controlled revision as new claims.
8. Draft or revise independent and dependent claims within the unrestricted universe.
9. Audit §112(a), §112(b), §112(f), support, prior art, restriction/unity, disclosure, regulatory, and inventorship risk.
10. Add missing technical detail to the specification before relying on a claim branch.
11. Analyze already supplied prior-art sources locally and maintain element-level claim charts/search logs. External AI/search-service research requires separate authorization for the specific nonconfidential query or source.
12. Run formal/professional patent searching before nonprovisional filing and before relying on a novelty position.
13. Licensed patent counsel determines readiness for an enabling provisional with necessary drawings/support, even if claims remain provisional-quality. The human professional handles filing only after separate user authorization; no filing is authorized by this workflow or the repository publication.
14. During the provisional year, continue claim refinement, search, inventor confirmation, regulatory planning, and business development.
15. Around month 10 after filing, perform nonprovisional conversion/pruning/fee/restriction/continuation strategy review.

## 7. Required specification coverage

Maintain enabling disclosure across, as applicable:

- field and technological context;
- summary and definitions;
- system architecture;
- sensing hardware and placement;
- audio/video preprocessing and recognition pipeline;
- target/non-target/unknown classification;
- training, validation, calibration, local adaptation, confidence and failure handling;
- persistent or pseudonymous identity and re-identification;
- local-population registry and dynamic membership;
- representation/discovery readiness;
- contemporaneous population-presence/completeness alternatives;
- recency, observation coverage, one-to-one association, ambiguity and unresolved-member behavior;
- treatment authorization and revalidation;
- version/state binding and event logging;
- access-control and dispensing structures;
- attraction, conditioning, pre-baiting and trough/feed-station embodiments;
- general/non-species-selective toxicants with selective access/timing;
- predetermined toxicants and named concrete examples where appropriate;
- species-selective-toxicant branch only to the extent inventor-conceived and enabled;
- reproductive-control branch only to the extent inventor-conceived and enabled;
- genetic-modification branch only to the extent inventor-conceived and enabled;
- feed-mediated control;
- capture/euthanasia and other supported control alternatives;
- human-in-the-loop and autonomous modes;
- fail-safe, equipment-health, communications and non-target vetoes;
- edge, remote and distributed computing;
- data flows, audit logs and model/configuration versioning;
- deployment scenarios, variants, alternatives and failure cases;
- representative other-target-animal embodiments sufficient to support any retained genus breadth.

## 8. Inventorship and AI-assisted drafting discipline

AI-generated technical language, algorithmic formalization, prior-art-directed fallback concepts, search hypotheses, and public prior-art examples do **not** become inventor conception merely because they are written into a draft.

For any inventor-confirmation-gated branch:
- identify the specific formalization requiring confirmation;
- obtain inventor confirmation, correction, or rejection;
- record conception contributors and timing;
- preserve supporting notes/evidence where available;
- revise or remove non-inventor-conceived material before relying on it for an early-priority filing.

Local-population completeness, true species-selective toxicants, reproductive-control specifics, genetic-modification specifics, and broad other-animal embodiments remain particularly sensitive to this rule.

## 9. Known legal/technical risks

Maintain active review of at least these issues:

- “lethal means” and other functional placeholders may raise §112(f) unless concrete structure/material/acts or deliberate means-plus-function support are present; current Claim 1 uses population-control treatment, so do not repeat the stale assertion that it recites lethal means;
- local-population and completeness terms require objective operational support, including observation opportunities, thresholds/criteria, recency, identity uncertainty, exclusion/veto logic, and failure modes;
- preliminary source-reported triage treats generic recognition-triggered control, feeder access, pre-baiting/conditioning, toxicant delivery, contraceptive delivery, ML training, and ordinary controller/CRM formulations as crowded prior-art areas, pending primary-source and professional review;
- preliminary triage does not establish individual animal identity, untagged tracking, one-to-one assignment, treatment-compliance tracking, or generic version-bound authorization as stand-alone novelty anchors; retain these as search-risk hypotheses rather than definitive novelty conclusions;
- broad target-animal genus claims and feral-swine species claims may create restriction/unity and full-scope §112(a) issues;
- pesticide/poison/wildlife-control deployment legality is separate from patentability and must be evaluated under current labels, registrations, permits and jurisdictional law;
- public-disclosure, ownership and inventorship risks remain independent filing gates.

## 10. Current differentiation-search posture

Do not state that the invention or any claim is patentable based on AI searching.

The current working search hypothesis should be tested around combinations that include, as applicable:

- initially incomplete or unknown local-population membership;
- longitudinal sensor-derived membership discovery;
- representation/discovery stabilization before irreversible treatment;
- contemporaneous distinct-member completeness in a treatment zone;
- unresolved/new-member veto that reopens discovery or invalidates authorization;
- common group-directed treatment/exposure after completeness rather than retrospective treatment compliance;
- authorization bound to the relevant population-state snapshot;
- mandatory revalidation when membership, completeness, non-target, safety, or equipment state changes.

Continue citation-family, analogous-art and professional searching against these combinations.

## 11. Required AI behavior before patent drafting

Before drafting or revising patent content:

- re-read the current project instructions;
- inspect the exact live tracker and canonical workspace;
- verify the current manifest/state;
- identify stale rules or mismatches;
- resolve or record them;
- continue only from the current canonical claim/specification universe.

Do not:
- use archive/generated-export copies as drafting authority;
- continue a stale claim set;
- revive former Claim-20/Set-1 logic;
- infer inventor conception from AI output;
- declare patentability from AI prior-art triage;
- conflate regulatory legality with patentability;
- claim completion without the applicable local or separately authorized live workspace/version/risk verification, clearly identifying which verification was performed.

Human review and licensed patent counsel control filing and legal conclusions.

## 12. Current matter record and evidence standards

### 12.1 September 29 source snapshot

The September 4 [manifest v1.3](FeralPig_DocumentManifest_v1.3_20260904.md) identifies these core matter records. They remain unchanged by this instruction revision; consult the current promoted manifest for subsequent administrative additions.

| Record | Controlling role and recorded posture |
|---|---|
| [Tracker v1.3](../tracker/FeralPig_Tracker_v1.3_20260904.xlsx) | Claim Inventory A2:K161 has 160 drafted claims, fifteen independent and 145 dependent; all are P-U1. Independent Family Audit A2:H16 supplies descriptive families. Detailed Claim-Spec Audit I2:I86 has 85 limitation rows, 32 blocking. Risk Register A2:I26 has 24 open risks, one resolved, and 22 unresolved blocking risks. |
| [Specification v0.7](../drafts/FeralPig_ProvisionalDraft_v0.7_20260903.docx) | 311 numbered paragraphs plus 160 embedded claims and abstract; first-filed working draft at [0001], disclosure review at [0005], AI-conception notes at [0136], [0304], [0311]. Footer: WORKING DRAFT - NOT FOR FILING. |
| [Claims v0.7](../claims/FeralPig_ExemplaryClaims_v0.7_20260903.docx) | Actual text matches embedded claims; independent claims 1, 11, 21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 136. Claims 146-150 depend on 11; 151-160 depend on 136. Family table is incomplete; see R08. |
| [Support audit v0.5](../docs/FeralPig_SupportFigureAudit_v0.5_20260903.docx) | Working support map with inventor gates and later deltas; identified citation drift means historical QA-complete status is not present substantive clearance. |
| [Figures v0.2](../figures/FeralPig_Figures_v0.2_20260903.pdf) | Twelve image-only figure pages, inspected visually; preserve numeral vocabulary and address R12 before filing QA. |
| [Questionnaire v0.1](../docs/FeralPig_InventorQuestionnaire_v0.1_20260903.docx) | Sections A-H are unanswered; instructions require actual conception, contributor/date/evidence identification, and rejection of examples not conceived. |
| [MasterControl v0.5](../docs/FeralPig_MasterControl_v0.5_20260903.docx), [StatusProtocol v0.5](../docs/FeralPig_StatusProtocol_v0.5_20260903.md), [roadmap v0.4](../roadmap/FeralPig_Roadmap_v0.4_20260903.pdf) | Retained sources contain stale checkpoint prose. Their 135-claim/fourteen-family summaries and PAT-042 next-task text do not override the live tracker. |

The U.S. working-draft posture is provisional filing **NOT READY** (tracker Dashboard F5:H5); PAT-013 / Task Register row 14 is Not Started. No filing receipt, actual application number, priority date, or completed inventor answers is established by these records. Do not describe the project as patent pending from README language alone. Do not start a provisional-year or month-10 deadline without an actual verified filing date.

The tracker SHA-256 locally matches the manifest: `ABBD1D278C5D82DEE5201DBA1F9CFBA9A6263D607B9863F427627495ED942DAE`. Local source/copy hashes do not establish a new exact live OneDrive read-back. If live access is unavailable, state that limitation; do not invent verification. A demonstrated material sync conflict must be reconciled before substantive drafting.

### 12.2 Required analysis method

Act as an assistant to a patent professional; the human professional remains final reviewer. Start substantive work by stating objective/scope, jurisdiction, procedural posture, source record, material assumptions, and unanswered questions. Distinguish verified facts, quoted material, technical inference, assumptions, evidence gaps, and legal conclusions. Do not invent citations, claim language, technical capabilities, experiments, prosecution events, or legal authority. Structure deliverables as objective/scope; source record; assumptions/open questions; analysis/draft; support/evidence matrix where applicable; risks/counterarguments; next actions.

For claim charts, split actual claim language into discrete material limitations, supply a primary-source pinpoint, and classify mappings as explicit, inherent but disputed, inferential, absent, or requiring more evidence. Patentability review distinguishes priority, filing, publication, public availability, and retrieval dates and identifies both teachings and missing limitations. Preliminary infringement/FTO uses all limitations and separately states construction assumptions, literal coverage, equivalents theories, validity risk, evidence gaps, jurisdiction, and time. Attorney/litigation/regulatory/foreign-law/inventor review must be identified where needed; no ultimate legal-opinion, ownership, or inventorship determination is delegated to AI.

MPEP sections 2163, 2164, 2173, and 2181 are the project's recorded written-description, enablement, definiteness, and functional-language review anchors. The retained MPEP ZIP is Ninth Edition Revision01.2024, published November2024; Appendix L/R editor notes state January31,2024 laws/rules cutoffs. The pack and dated navigation documents are source records, not proof that law remained current through September29. AppendixAI contains PCT Administrative Instructions, not artificial-intelligence inventorship guidance. Verify applicable current primary authority before legal reliance when that research is expressly authorized.

Before completion, check terminology, actual dependencies/antecedent basis, enabling support, internal contradictions, figures/numerals, version/canonical status, and unsupported conclusions. A numerical parent-reference check is not an antecedent-basis or legal review.

## 13. Reconciliation register

These flags record observed contradictions; they do not silently change source status or close risks. Resolve them in a separately controlled substantive revision or mark the retained source statement historical/noncontrolling. DOCX paragraph numbers below are body-order extraction locators; bracketed specification numbers are the document's actual numbered paragraphs.

| Flag | Evidence and required handling |
|---|---|
| R01 Stale checkpoint summaries | MasterControl paragraphs 4, 6-7, 17, 20, 30; StatusProtocol STATE / Parallel work; roadmap page 1; tracker Dashboard H10 retain v0.4/v0.6, 135/155 claims, fourteen families, 280/304 paragraphs, and PAT-042. Use current 160/15/145, 311 paragraphs, and PS-13/PAT-050 rather than inherited resume prose. |
| R02 Out-of-range claim support | Tracker Claim Inventory K72:K101 for Claims 71-100 cites [0331]-[0360], beyond the actual [0311] endpoint. Remap to exact current enabling paragraphs; do not copy these generic references into a filing analysis. |
| R03 Obsolete section map | Tracker Spec Section Map A18:A21 extends through [0375]; G21 says drawings need preparation. Rebuild against the current specification and figures. |
| R04 Retired Claim-20 architecture | Tracker Claim-Spec Support I14:I16, Task Register C31:D31/J31, and [template CSV](../tracker/FeralPig_TrackerTemplate_v0.1_20260903.csv) retain former Claim-20 / Set-1 structures. Preserve as historical/template examples; they cannot control current claim numbers or impose a ceiling. |
| R05 Stale naming audit | Tracker Naming Audit rows 2-3, 5, 8, 10, 19, 23 retain earlier versions/pending revisions, audit v0.3, manifest v0.2, and empty-staging assertions. Compare actual paths and current manifest before relying on them. |
| R06 Shifted disclosure row | Tracker Broad Disclosure Matrix E37:K37 (DEL-07): G37 contains Proposed; H37 risk prose; I37 support references; J37 Required; K37 blank. Confirm intended column meaning before using support/conception fields. |
| R07 Citation drift / limitation audit | Support audit paragraph 455 cites [0251]-[0257] for KAPUT/warfarin, now actually [0267]-[0275]; paragraph 325 cites [0205]-[0210] for computer implementation, now [0221]-[0226]; paragraph 288 cites [0163]-[0170] for safety, now principally [0179]-[0186]/[0227]-[0233]. Its 63 original discrete headings cover families 1-131; paragraph 491 treats 136 narratively. Re-split actual claim text, remap support, and reconcile with Detailed Claim-Spec Audit, rather than applying a blanket offset. Audit 121D includes a population-accumulation branch absent from independent 121; 101D is a terminology distinction rather than a separate claim limitation. |
| R08 Incomplete family table | Claims v0.7 Table 1 omits independent family 136 and added fallback dependencies despite paragraphs 7-9 and actual text including them. Use Claim Inventory and Independent Family Audit pending table correction. |
| R09 Antecedent concerns | Claims 26->21, 36->31, 47/48->41, 57/58->51, 94->91, and 130->121 refer to subject matter introduced in siblings 25, 35, 46, 56, 93, or 129 rather than their stated parent. Review Claim 70's local-population reference and Claim 83's pretraining prerequisite. Select any corrected parentage/introduction deliberately to preserve intended scope; do not auto-reparent or prune. |
| R10 Preliminary prior-art charts | Tracker independent-family prior-art rows largely use summary disclosures/URLs rather than exact source paragraph/claim/page pinpoints, with some approximate/mixed family dates. Verify primary sources, actual availability, mapping strength, missing teachings, and combination risk before reliance. |
| R11 Stale functional-language attribution | Tracker Risk Register C2:D2 and MPEP Update Register G3 attribute lethal means to Claim 1; current Claim 1 says population-control treatment. Retain appropriate section 112(f) review without repeating a false quotation. |
| R12 Present figure defects | Figures PDF page 2/FIG. 2 box crosses frame; page 4/FIG. 4 partly masks numeral 422/box; page 5/FIG. 5 overlaps inactivate/reactivate labels; page 9/FIG. 9 Trough patch masks feed text. Historical Figure-Spec Audit PASS entries and QA statements do not clear current visual defects. |
| R13 Unsupported filing description | Original intake README line 7 said patent pending, contrary to tracker NOT READY / filing Not Started and draft footers. Any current summary must use verified filing evidence; preserve the intake discrepancy as an issue even if README is corrected. |
| R14 Local configuration mismatch | Intake [.vscode/mcp.json](../.vscode/mcp.json) line 9 points at older `Documents/Startup`; [.codex/config.toml](../.codex/config.toml) disables web/network. Configuration auto-approvals or historical paths do not authorize disclosures. Reconcile configured workspace paths in the requested project setup separately, without assuming live cloud access. |
| R15 Unused assessment examples | Tracker Supplemental Prov Eval D2:D9 is blank while M5 says Routine capture because blank scores act as zero; Post-Filing Invention Log A2 is EXAMPLE-REMOVE. These are uncompleted rubric/example data, not an evaluated improvement or real post-filing invention. |
| R16 Publication versus historical lock | Tracker Dashboard F8:H8 remains LOCKED; NDA or filing first, with R-DISC at Risk Register row 11. Section 15 records a later scoped public repository instruction; it does not imply filing, inventor confirmation, or historical risk disposition was completed. |
| R17 Index hash discrepancies | The retained MasterIndex v0.1 has local SHA-256 `7D6F77E6FA2BDB76B8291ABBDDC4233A45AF5F77090D0269D635355B5987B3DE`, while manifest v1.3 carries `2DAEF2AEB0E60C106F3D6F16AD1F1E1BDAE690A1259CE1FFD5F4C1E3754358DF`. ProjectIndex v0.1 has local `6883640DEC824BC13734E4012FBACCB37589D81AA4D368838E100D9FF37DD1EC`, while the manifest carries `F5F44AF47B7CFF07998FDFC53C25BF431B5551B60A567ED500489B5C8AECAEE1`. Their current_drafts copies also differ. Preserve each version; the new manifest records actual local hashes and discrepancies rather than implying live cloud reconciliation. |

The [resume plan](FeralPig_ResumePlan_v0.1_20260929.md) provides the ordered work, source evidence, and acceptance criteria. Next patent search is PS-13/PAT-050; PS-14/PAT-051 is an external/professional file-wrapper dependency. Inventor work PAT-041/PAT-022 and ORG-001 proceeds in parallel.

## 14. Separate workstreams and ingestion rules

### 14.1 Reference Suite

[The September 22 consolidated brief](../new_materials/Reference_Management_Citation_Procurement_Consolidated_v0.1_20260922.md), line 3, expressly separates this software project from the Feral Pig specification/claim/tracker matter. Follow the [suite README](../new_materials/reference_suite/README.md) and versioned shared job, record, and run schemas. Preserve immutable raw bytes, per-run provenance, hashes/manifests, explicit dry-run acquisition preview, HTTPS/exact-host restrictions, source facts versus reviewed metadata corrections, and append-only history. Stable/provider identifiers and source evidence must not be overwritten by review edits. Keep credentials in environment/process memory and out of artifacts. A lead is acquired only with captured evidence and verified integrity; byte integrity does not prove bibliographic identity. Breaking contract changes require a new schema and migration.

Historical 63-test claims use offline fakes; live providers, EndNote round trip, real rendering/OCR, interactive GUI/extension, and throughput remain unverified. Current fixture-write PermissionError is an environment result, not a clean pass or established regression. Obtain separately scoped approval before dependency installation, live source acquisition, or integration tests that send material externally.

Do not equate ordinary Reference Suite folder intake with whole-folder ingestion. Record OOXML/workbook extraction, recursive ZIP member paths, PDF page/text limits, image-only figures, metadata/comments, unsupported/skipped formats, deduplication hash groups, and actual review coverage explicitly. Every indexed record should state its path/virtual member, format/hash, canonical versus staged/historical role, extraction/review status, source-derived instruction, and follow-up/gap. Zero extracted text or a capped extraction is not proof of complete reading. Archive and source originals remain immutable unless the user asks otherwise; public publication does not make archived files drafting authority.

### 14.2 LayneIP source

[Release record](../new_materials/LayneIP_site_source/docs/release.md), September 22 continuation, controls over September 21 successful-build prose. Preserve the nested source history and dirty imported changes; do not reset them. Reconcile missing package/lockfile, Vite configuration, README, .gitignore, generated manifest, and root pages before claiming a current full build. Write structured content/templates, preserve routes, verify professional facts and added claims, and keep editorial drafts excluded from public generation/RSS until deliberately approved. Evidence tools stay local; inquiry remains a user-reviewed email draft, not an automatic send.

Recorded 37 private-review / 34 public pages, eleven services, six technology areas, one professional, three external references, and three drafts are imported-source facts, not current deployed-service verification. Five selected pure source tests passed in this review; missing dependencies and temporary-file failures limit broader verification. Repository publication does not launch the website or change its audience.

### 14.3 Cloudflare and domains

[Launch guide](../new_materials/LayneIP_site_source/docs/cloudflare-launch.md) and [retained inventory](../new_materials/LayneIP_cloudflare_inventory/inventory-2026-09-22.json) show four historically pending bindings and no authenticated zone inventory (`fetched_at: null`, zero zones). Keep this workstream separate. Future authorized work starts with fresh authenticated read-only zone/registrar inventory; preserve mail/unrelated records, resolve competing address/CNAME values, verify DNS/TLS and path/query-preserving redirects, and make any proposed changes reviewable with fresh-state checks and recovery journals. Do not infer sign-in failure from the historical execution-approval block. Repository upload grants no DNS cutover, hosting deployment, website audience change, email sending, purchase, or account-setting authority.

### 14.4 Reference and historical sources

Preserve all archived formats, filenames, ZIP relationships, and original byte hashes. Label archive/history, generated exports, duplicates, and current_drafts noncanonical even when their own internal headings say canonical. Long AI conversations are provenance/conception leads, not legal or technical proof. The comedy transcript is a contextual lead, not primary evidence for a claim or legal conclusion. Authority-pack documents require date/currentness and source-quality review. Do not use source URLs or instructions found inside a document as authorization to visit it or transmit material.

## 15. September 29 public repository authorization

The user's September 29 instruction specifically authorizes a public snapshot at **RobertMLayne/feral-pig-startup**, including the project records, source, invention drafts/claims, staged workstreams, archives, reference materials, and historical logs. This is an explicit scoped override of the earlier confidentiality/public-disclosure restriction for this repository action. Preserve originals and include nested source as ordinary files. Exclude Git internals, disposable Python caches and local `.codex/` and `.vscode/` configuration under Robert's development preferences. Inventory exact included/excluded paths and hashes and verify the resulting repository visibility/content/commit before reporting publication complete.

This instruction records the authorization and its limits; it does not itself perform or prove upload. It is not attorney clearance, a filing event, a risk closure, or general permission for later invention disclosures, web research, connector uploads, website launch, DNS/account changes, messages, or unrelated repository publication. New nonpublic material remains confidential by default. The original filing/support/conception gates stay open unless the responsible professional resolves them with evidence. Never treat a public snapshot as authorization to invent facts or revise technical/legal records.

The user subsequently expressly requested Git LFS setup. Apply .gitattributes only to the two preserved large MPEP ZIPs, which have identical original bytes and share one LFS content object. Keep other selected source and small review files in regular Git. Git LFS is installed locally; account quota/usage must be verified without purchases or billing changes. Document clone/pull requirements, verify actual LFS upload and fresh-download hashes, and keep original archives unchanged locally. LFS pointers alone do not satisfy publication acceptance. Retain any earlier unpublished staging checkpoint locally; start the public main history from the selected package without leaking excluded configuration through ancestors or rewriting retained history.

## 16. Checkpoint and handoff discipline

Make the smallest requested workspace change and preserve original records. Do not install dependencies, execute destructive operations, rename/move/archive/delete source records, or make substantive patent revisions merely to complete documentation. Explain actual unsupported/unavailable checks; no phantom live synchronization, full ingestion, source currentness, integration pass, filing, publication, or deployment claims.

Robert's September 29 development preferences are persisted in root AGENTS.md and apply across workstreams: use the actual project conventions and document them; inspect repository identity/status/remotes and preserve local work; keep one independent Git checkout per repository outside cloud sync; prefer understood fast-forward updates and never force-push or rewrite history; inspect final diffs and run meaningful required checks. Check attributes, quotas, consumers and availability before selecting Git LFS for appropriate large binaries, and verify actual LFS data rather than pointer presence. Keep credentials, unapproved private data, disposable caches, build products and local configuration out of public commits. The specifically authorized retained records, historical snapshots and test records remain in this publication package. Do not infer permission to deploy or change licensing. Applied changes, recommendations and unresolved work must be reported separately with evidence.

For this checkpoint, the instruction and resume artifacts are local Markdown additions. Root-level project/Codex/Copilot instruction wiring, per-document indexing, publication, and manifest promotion are coordinated separately. Before handoff, verify relative source links, matching versions/counts/flags, source-grounded pinpoints, explicit assumptions, and inclusion/exclusion boundaries. Keep decisions that require inventors, licensed patent counsel, regulators, external searchers, or account access visibly pending.

