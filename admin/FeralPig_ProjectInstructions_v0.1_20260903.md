# FeralPig Project Instructions
Version: v0.1
Date: 2026-09-03
Project root: `Startup`

## 1. Project purpose

Build a patent and business around detecting and identifying pests or other target animals using video, audio, or other recognition technology and selectively applying lethal or nonlethal population-control measures.

The disclosure and claim architecture should preserve a broad-to-narrow ladder:

1. generic target-animal or pest recognition and control;
2. selective targeting, access, timing, dispensing, exposure, or delivery;
3. local-population learning, state estimation, and population-conditioned authorization;
4. feral-swine population-control embodiments;
5. narrow embodiments in which a generally toxic or other population-control agent is exposed only after a defined local-population condition is satisfied.

This ladder is illustrative only. **Actual claim numbers, parentage, scope, and status are always controlled by the current live tracker.** Do not infer a fixed claim number from this description.

## 2. Hard-stop rules

- Enablement and written description control the provisional filing. Do not postpone an otherwise ready provisional merely to polish claims.
- The current live tracker is the controlling project-state record.
- Do not draft against archived, superseded, generated-export, duplicate, convenience-snapshot, or stale sandbox files.
- No filing, public disclosure, material external technical disclosure, pilot disclosure, grant disclosure containing protected technical detail, or partner disclosure without attorney review and NDA or other disclosure controls as appropriate.
- Check AI retention/training settings before disclosing invention details to any AI system.
- Settle inventorship and conception records in writing before equity formation, IP assignment, licensing, or commercial use.
- Regulatory, wildlife, pesticide/poison, product-label, permit, and deployment legality are separate from patentability.
- Public-disclosure risk overrides speed. Human review controls.
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

- `Startup\admin`
- `Startup\docs`
- `Startup\drafts`
- `Startup\claims`
- `Startup\figures`
- `Startup\reference_materials`
- `Startup\roadmap`
- `Startup\tracker`

Additional controlled folders:

- `Startup\new_materials` — incoming/staging only;
- `Startup\current_drafts` — derivative latest-only convenience snapshot, never authoritative;
- `Startup\archive\history` — superseded/historical project artifacts;
- `Startup\archive\generated-export` — generated/export provenance only.

The project root should remain focused on canonical project structure and workspace configuration.

### 3.3 Naming and artifact-family continuity

Project-authored substantive artifacts use:

`FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>`

Revisions addressing the same artifact or function must retain the same descriptive artifact stem unless a deliberate family split is recorded in the tracker/manifest.

Exceptions:
- immutable external-source originals may retain source filenames;
- browser-export internal dependency assets may retain generated filenames when renaming would break the preserved export package;
- workspace infrastructure such as `.github`, `.vscode`, `README.md`, and `Startup.code-workspace` need not use the FeralPig prefix.

Superseded active revisions must be moved to archive/history after the new revision is verified.

### 3.4 Material-write verification

A sandbox artifact is not canonical merely because it was generated.

For every material OneDrive revision:

1. read the exact current live tracker and target artifact before drafting;
2. generate and QA the revision in the sandbox;
3. write the new versioned artifact to the correct canonical OneDrive folder;
4. read back the exact resulting OneDrive item;
5. download/read the resulting bytes and compute SHA-256 independently;
6. verify the read-back hash against the generated artifact;
7. archive the superseded active revision;
8. update the document manifest with canonical path, version/date, OneDrive item ID, SHA-256, current/canonical status, and superseded predecessor;
9. read back and hash the updated manifest;
10. refresh changed `current_drafts` derivative copies and verify their hashes against canonical counterparts.

Use the phrase **“Live OneDrive write verified”** only after exact-item read-back succeeds. At filing-critical checkpoints, independently verify the local Windows-synced copy by SHA-256 as well.

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
- family/set identifier;
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
11. Run AI prior-art triage and maintain element-level claim charts/search logs.
12. Run formal/professional patent searching before nonprovisional filing and before relying on a novelty position.
13. File the provisional once the disclosure is enabling and necessary drawings/support are ready, subject to attorney review and disclosure controls, even if claims remain provisional-quality.
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

- “lethal means” and other functional placeholders may raise §112(f) unless concrete structure/material/acts or deliberate means-plus-function support are present;
- local-population and completeness terms require objective operational support, including observation opportunities, thresholds/criteria, recency, identity uncertainty, exclusion/veto logic, and failure modes;
- generic recognition-triggered control, feeder access, pre-baiting/conditioning, toxicant delivery, contraceptive delivery, ML training, and ordinary controller/CRM formulations are materially crowded prior-art areas;
- individual animal identity, untagged tracking, one-to-one assignment, treatment-compliance tracking, and generic version-bound authorization are not stand-alone novelty anchors;
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
- claim completion without live workspace/version/risk verification.

Human review and licensed patent counsel control filing and legal conclusions.
