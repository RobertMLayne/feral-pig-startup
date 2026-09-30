# Startup Project Archive Deep-Research Review and Canonicalization Report

## Executive assessment

I decompressed and reviewed the attached `Startup.zip` as a **workspace**, not merely as a single canonical filing package. The archive is substantially complete and contains the patent work, project-control materials, historical versions, generated exports, the current claim universe, the current specification, figures, MPEP materials, and the business/funding skeleton. I also ingested the project instructions before evaluating the contents.

The archive contains **67 physical files at the top workspace level/tree**, spanning Markdown, DOCX, PDF, XLSX, CSV, JSON, PowerShell, ZIP, CSS, text, log, workspace, and image formats. I also recursively inspected the embedded ZIP packages. Most importantly, `Startup\reference_materials\MPEP\e9r-01-2024.zip` contains the full **43-PDF MPEP Ninth Edition, Revision 01.2024** package. The USPTO currently confirms that Ninth Edition, Revision 01.2024, published in November 2024, remains the current MPEP as of September 3, 2026; the USPTO expressly cautions that it incorporates policy only through January 31, 2024, so post-January-2024 notices and memoranda must be tracked separately. citeturn5search0turn5search4turn5search12

That means the project's basic authority architecture is correct: **retain the full Revision 01.2024 MPEP locally, then overlay intervening USPTO guidance.** The USPTO's current examiner-memoranda page contains post-MPEP developments through 2026, including the July 17, 2026 foreign-applicant-practitioner material, December 2025 eligibility developments, and other post-revision guidance. citeturn6search1 The project should therefore never treat `e9r-01-2024.zip` by itself as the complete contemporary examination rule set.

The review uncovered several material organizational discrepancies. The most important are:

**The active project instructions are stale and conflict with your current instructions.** `Startup\.github\copilot-instructions.md` still imposes a 20-claim-set architecture, says only Set 1 is active, and says a claim set must contain exactly three independent and seventeen dependent claims. That is directly superseded by your later direction and by the current project status itself, which establishes **135 exemplary claims, 14 independent families, and no claim-count ceiling**.

**The active tracker is the wrong copy.** `Startup\tracker\FeralPig_Tracker_v0.1_20260903.xlsx` is an older approximately 78 KB workbook with 13 sheets and about 45 populated Task Register entries. A newer approximately 104 KB copy is sitting in `Startup\archive\duplicates\FeralPig_Tracker_v0.1_20260903_584751.xlsx`; that newer copy matches the tracker packaged in the canonical v0.5 archive and contains **17 sheets and 58 task entries**, including the Figure Numerals, Independent Family Audit, Figure-Spec Audit, and Detailed Claim-Spec Audit sheets. The newer workbook—not the smaller active copy—should occupy the canonical tracker path.

**Some superseded versions remain in active directories**, contrary to the workspace's own rule that active folders contain only the current canonical version. Examples include Master Control v0.4 alongside v0.5, Status Protocol v0.4 alongside v0.5, and Figures v0.1 alongside v0.2.

**Two previously produced project artifacts are missing from `Startup.zip` as standalone historical artifacts:** the unrestricted exemplary claims v0.1 and the canonical v0.4 project ZIP. Both still exist among the project files available in this session and should ultimately be placed in the historical archive.

The patent itself is much healthier than the administration layer. The current substantive patent set is coherent: **specification v0.4, claims v0.4, figures v0.2, support audit v0.2, master control v0.5, status protocol v0.5, inventor questionnaire v0.1, roadmap v0.4, and the newer tracker.** The current specification contains the broad technical disclosure we have been building toward, and the support audit properly identifies unresolved §112(a) branches rather than pretending that the mere presence of claim words proves adequate written description or enablement. That caution is exactly consistent with current MPEP §§ 2161, 2163, and 2164. citeturn5search10turn5search2turn5search6

My present estimate is that the **patent subproject is approximately 72% complete at the first-draft level**, while the **entire patent/business/funding/regulatory/commercialization project is approximately 40% complete at the first-draft level**. The distinction matters: most of the detailed patent documents exist, while most of the eventual business, grant, procurement, regulatory, partnership, jurisdictional, financial, and international documents exist only as roadmap/tracker skeletons.

## What is actually in the archive

The workspace root is structurally sensible:

```text
Startup\
├── .github\
├── .vscode\
├── admin\
├── archive\
├── claims\
├── docs\
├── drafts\
├── figures\
├── reference_materials\
├── roadmap\
├── tracker\
├── README.md
└── Startup.code-workspace
```

This should remain the basic architecture. The key distinction going forward should be:

> **Active directories contain one current canonical version per artifact. `Startup\archive\...` preserves every superseded version, old package, duplicate, generated export, and historical snapshot.**

That reconciles two objectives that can otherwise appear inconsistent: your earlier instruction that a **canonical delivery ZIP contain no fossil files**, and your current instruction that the broader **Startup project workspace preserve all documentation and versions produced thus far**. The solution is not to delete history; it is to keep history out of the active canonical directories and place it under clearly labeled archive paths.

### Canonical substantive patent set

Based on content, version lineage, current status documents, and the canonical v0.5 package, the active patent files should resolve to these exact locations:

| Function | Canonical destination path |
|---|---|
| Current provisional/specification draft | `Startup\drafts\FeralPig_ProvisionalDraft_v0.4_20260903.docx` |
| Current unrestricted exemplary claims | `Startup\claims\FeralPig_ExemplaryClaims_v0.4_20260903.docx` |
| Current patent figures | `Startup\figures\FeralPig_Figures_v0.2_20260903.pdf` |
| Current claim/spec/figure support audit | `Startup\docs\FeralPig_SupportFigureAudit_v0.2_20260903.docx` |
| Current inventor questionnaire | `Startup\docs\FeralPig_InventorQuestionnaire_v0.1_20260903.docx` |
| Current master drafting control | `Startup\docs\FeralPig_MasterControl_v0.5_20260903.docx` |
| Current resume/status protocol | `Startup\docs\FeralPig_StatusProtocol_v0.5_20260903.md` |
| Current patent research notes | `Startup\docs\FeralPig_ResearchNotes_v0.1_20260903.md` |
| Current roadmap | `Startup\roadmap\FeralPig_Roadmap_v0.4_20260903.pdf` |
| Current tracker | `Startup\tracker\FeralPig_Tracker_v0.1_20260903.xlsx` |

The filename pattern currently stated in the project is sensible and should remain:

```text
FeralPig_<Artifact>_v<major.minor>_<YYYYMMDD>.<ext>
```

The date segment should remain compact `YYYYMMDD`, so a file can be dropped directly into its destination without having to reconcile a second hyphenated-date naming scheme.

### Current MPEP/reference set

The official MPEP ZIP belongs at:

```text
Startup\reference_materials\MPEP\e9r-01-2024.zip
```

That is an external-source filename and therefore does **not** need to be forced into the `FeralPig_...` convention. The USPTO confirms Revision 01.2024 remains the current MPEP, while also expressly warning that post-January-31-2024 policy changes are outside that revision. citeturn5search0turn5search8

Project-created MPEP derivative/reference documents, by contrast, should use the project convention. The preferred locations are:

```text
Startup\reference_materials\MPEP\FeralPig_MPEPCoreAuthorities_v0.1_20260903.pdf
Startup\reference_materials\MPEP\FeralPig_MPEPPostRevisionUpdateRegister_v0.1_20260903.pdf
```

The post-revision register is important because there are genuinely intervening USPTO developments. For example, the Office's November 2025 revised AI-assisted-inventorship guidance **rescinded the February 2024 guidance in its entirety**, so any old project language based solely on the 2024 guidance should not be treated as current. citeturn6search0turn6search4 That is particularly relevant here because we have intentionally separated AI-assisted drafting from inventor conception.

The project's filing-format checklist should also eventually reflect the August/September 2026 Patent Center change: for DOCX submissions, Patent Center now converts the DOCX directly to TIFF for pre-submission review rather than first generating PDF in that workflow. citeturn6search2turn6search3turn6search14 This is a filing-administration change, not a reason to change the substantive invention disclosure.

## Discrepancies that should be corrected

The discrepancies fall into four categories: **instruction conflicts, canonical-version errors, administrative-document errors, and historical-completeness errors.**

### Instruction and claim-strategy conflicts

The most serious inconsistency is:

```text
Startup\.github\copilot-instructions.md
```

It presently states, among other things:

> “Total claim count must be a multiple of 20…”

> “Each 20-claim set = 3 independent + 17 dependent claims.”

> “Only Set 1 is active.”

> “Do not start Set 2 unless Set 1 is complete…”

Those provisions are obsolete. They conflict with both your explicit instructions in this conversation and the later project-control documents. The controlling project rule should instead be:

> **There is no artificial ceiling on the provisional claim universe. The provisional is being drafted as an overcomplete disclosure-and-claim platform intended to minimize the need for new subject matter during conversion to a nonprovisional. Claims may be added, reorganized, multiplied, or developed whenever doing so improves disclosure support, claim-family coverage, fallback positions, or later conversion options. Claim pruning and fee-conscious claim architecture are deferred principally to the nonprovisional preparation period, targeted around month ten after provisional filing.**

It should also expressly state:

> **The 135-claim / 14-independent-family set is the current working claim universe, not a maximum.**

And:

> **No previous 20-claim “Set 1” rule is a drafting gate, completion test, or authorization prerequisite.**

This correction should be made before relying on Copilot or any other workspace-aware drafting tool, because otherwise that tool can be affirmatively instructed to reverse the current strategy.

The same stale concept appears in:

```text
Startup\README.md
```

where the instruction:

> “Do not start a new claim set until the current set is complete and justified.”

should be removed or rewritten. Distinct invention families can still be tracked for restriction, unity, budget, prosecution, and later continuation strategy, but they are **not subject to a 20-claim drafting ceiling in the provisional**.

Likewise:

```text
Startup\admin\FeralPig_ManifestChecklist_v0.1_20260903.md
```

contains:

> “Claim count matches the active set rule”

That should become something like:

> “Claim inventory matches the current unrestricted claim universe and all dependencies/family assignments reconcile to the tracker.”

### The wrong tracker is active

This is the most consequential file-placement error.

The file presently at:

```text
Startup\tracker\FeralPig_Tracker_v0.1_20260903.xlsx
```

is an older workbook. The substantively newer workbook is presently located as:

```text
Startup\archive\duplicates\FeralPig_Tracker_v0.1_20260903_584751.xlsx
```

The newer workbook corresponds to the current canonical v0.5 tracker. It contains the later patent work, including:

```text
Figure Numerals
Independent Family Audit
Figure-Spec Audit
Detailed Claim-Spec Audit
```

and the PAT-031 through PAT-042 work stream.

The correct end state is therefore:

```text
Startup\tracker\FeralPig_Tracker_v0.1_20260903.xlsx
```

= **the newer 17-sheet workbook**

while the displaced older workbook should be retained under history, for example:

```text
Startup\archive\history\tracker\FeralPig_Tracker_v0.1_prePAT031_20260903.xlsx
```

The random `_584751` suffix should not survive as a canonical filename.

Even the newer tracker needs editorial normalization because several old tasks still encode the abandoned Set-1 architecture. In particular, PAT-004 and PAT-005 still refer to a mid-scope independent claim and “17 dependent claims.” Those should be closed as superseded/completed by the unrestricted claim-universe work, or rewritten so they no longer act as requirements.

### Superseded files are incorrectly active

These should not simultaneously remain in active locations:

```text
Startup\docs\FeralPig_MasterControl_v0.4_20260903.docx
Startup\docs\FeralPig_MasterControl_v0.5_20260903.docx
```

The active one is v0.5. Therefore:

```text
Startup\docs\FeralPig_MasterControl_v0.5_20260903.docx
```

should remain active, while v0.4 should move to:

```text
Startup\archive\history\docs\FeralPig_MasterControl_v0.4_20260903.docx
```

Likewise:

```text
Startup\docs\FeralPig_StatusProtocol_v0.4_20260903.md
```

should become:

```text
Startup\archive\history\docs\FeralPig_StatusProtocol_v0.4_20260903.md
```

while:

```text
Startup\docs\FeralPig_StatusProtocol_v0.5_20260903.md
```

remains active.

Similarly:

```text
Startup\figures\FeralPig_Figures_v0.1_20260903.pdf
```

should move to:

```text
Startup\archive\history\figures\FeralPig_Figures_v0.1_20260903.pdf
```

and v0.2 remains:

```text
Startup\figures\FeralPig_Figures_v0.2_20260903.pdf
```

This is not deletion. It is proper historical segregation.

### Administrative files are stale or technically broken

The following need replacement versions.

`Startup\admin\FeralPig_ProjectIndex_v0.1_20260903.md` is substantially stale. It still identifies the v0.2 specification, v0.2 master control, and v0.2 roadmap as the canonical set and uses pre-normalization filenames. It should not continue serving as an authoritative index.

The next version should be:

```text
Startup\admin\FeralPig_ProjectIndex_v0.2_20260903.md
```

and v0.1 should move to:

```text
Startup\archive\history\admin\FeralPig_ProjectIndex_v0.1_20260903.md
```

`Startup\admin\FeralPig_MasterIndex_v0.1_20260903.md` correctly says only current canonical files belong in active folders, but then gives examples containing both current and superseded versions. That internal contradiction should be eliminated in:

```text
Startup\admin\FeralPig_MasterIndex_v0.2_20260903.md
```

`Startup\admin\FeralPig_NamingConvention_v0.1_20260903.md` references:

```text
./rename_startup_documents.ps1
```

but that file does not exist under that name. The actual script is:

```text
Startup\admin\FeralPig_RenameScript_v0.1_20260903.ps1
```

The naming document should point to the real relative location:

```text
Startup\admin\FeralPig_RenameScript_v0.2_20260903.ps1
```

The v0.1 rename script itself has two substantive defects. Its root is determined from the script's own directory, which makes `Startup\admin` the effective root and causes it to look for paths such as `Startup\admin\docs` rather than `Startup\docs`. It also contains a `20260609` date in the index-renaming operation instead of `20260903`. A v0.2 script should resolve the workspace root as the **parent of `$PSScriptRoot`** before performing operations.

`Startup\admin\FeralPig_ContentDedup_v0.1_20260903.ps1` contains a `ferlpig_` spelling error in its ranking logic and, more importantly, automatically **deletes** duplicate files. Given your instruction to preserve all versions produced, destructive deduplication is the wrong project policy. The next script should report duplicates and, when instructed, relocate them to history; it should not silently destroy historical evidence.

`Startup\debug.log` is environment noise, and the project's own Master Index already says it is noncanonical. It should not remain in the root. The orderly location is:

```text
Startup\archive\generated-export\logs\debug.log
```

or it can be excluded from a distributed workspace if it has no evidentiary value.

### Manifest defects

The current:

```text
Startup\admin\FeralPig_DocumentManifest_v0.1_20260903.md
```

has blank `Folder` fields even though folder placement is one of the core organizational requirements. The next manifest should contain the **entire root-relative path**, for example:

```text
Startup\drafts\FeralPig_ProvisionalDraft_v0.4_20260903.docx
```

not merely a filename.

It also labels old versions “canonical” even where its own `Newest Flag` says `no`. That terminology is confusing. A stronger status vocabulary would be:

```text
active-canonical
historical-superseded
reference-external
generated-noncanonical
package-snapshot
```

The manifest's own SHA-256 field should also **not attempt to contain a final hash of itself**. Editing a manifest to insert its own hash changes the manifest and therefore changes the hash. The clean scheme is:

```text
FeralPig_DocumentManifest_v0.2_20260903.md
FeralPig_DocumentManifest_v0.2_20260903.csv
SHA256SUMS.txt
```

where the manifest marks its own hash as `SELF-EXCLUDED` and the separately generated `SHA256SUMS.txt` hashes the completed manifest and all other files.

### Missing historical project outputs

Two produced artifacts are not represented as standalone files in the supplied `Startup.zip`:

```text
Feral_Pig_Unrestricted_Exemplary_Claims_v0.1_2026-09-03.docx
Startup_Feral_Pig_Project_Canonical_v0.4_2026-09-03.zip
```

For the unified workspace, their sensible destination paths are:

```text
Startup\archive\history\claims\FeralPig_ExemplaryClaims_v0.1_20260903.docx
```

and:

```text
Startup\archive\packages\history\Startup_Feral_Pig_Project_Canonical_v0.4_2026-09-03.zip
```

The current v0.5 package can remain as a package snapshot at:

```text
Startup\archive\packages\Startup_Feral_Pig_Project_Canonical_v0.5_2026-09-03.zip
```

The old organized package belongs at:

```text
Startup\archive\packages\Startup_Feral_Pig_Project_Organized_2026-09-03.zip
```

That makes package history explicit rather than mixing ZIPs with ordinary duplicate documents.

### AI-workspace governance

`Startup\.vscode\settings.json` currently enables Copilot functionality while the project itself still has an unresolved governance item concerning AI retention/training settings.

That does not itself prove that confidential information is being trained on or retained; product/account-level settings and applicable terms matter. But because the project is handling potentially unpublished invention material, the discrepancy should stay flagged until the applicable AI settings and organizational terms have been reviewed. The project's current caution against silently treating AI-generated technical ideas as inventor conception is especially sound in view of the USPTO's November 2025 revised AI-assisted-inventorship guidance, which retains the ordinary human inventorship framework rather than creating a special AI inventor standard. citeturn6search0turn6search4

## Patent drafting assessment after ingestion

The current patent specification is:

```text
Startup\drafts\FeralPig_ProvisionalDraft_v0.4_20260903.docx
```

and it is meaningfully more developed than the administrative files suggest.

It contains the present architecture of the invention, including recognition-gated control, audio/video sensing, persistent animal identification, local-population registry concepts, population-completeness logic, treatment authorization, feed/attraction/conditioning, predetermined toxicants, species-selective toxicants, reproductive-control treatments, genetic-modification embodiments subject to support limitations, computer implementation, failure modes, other target-animal embodiments, the exemplary claim set, and an abstract.

That is the correct drafting philosophy for the filing you described. MPEP §2163 requires the original disclosure to reasonably convey possession of the claimed invention; simply adding generalized claim terminology does not necessarily establish written-description support. citeturn5search2turn5search10 MPEP §2164 likewise frames enablement around whether a person of ordinary skill can make and use the claimed subject matter without undue experimentation, with the relevant scope being the claimed invention rather than merely one successful embodiment. citeturn5search6

This is why the project was correct **not** to fabricate molecular details for the genetic-control branch merely to make the provisional look complete. An unsupported synthetic example can create a false sense of §112(a) coverage without establishing actual inventor possession.

### The unrestricted claim strategy is appropriate for this project stage

The current claims file is:

```text
Startup\claims\FeralPig_ExemplaryClaims_v0.4_20260903.docx
```

with **135 exemplary claims across 14 independent families**.

For this project, the claims should continue to function as a **disclosure stress test and conversion map**, not as a filing-fee optimization exercise. Your current instruction is therefore controlling:

> **Do not prune merely to reduce claim count now.**

The goal is to expose every technically meaningful claim branch while there is still time to strengthen the provisional disclosure. The later nonprovisional can then select, consolidate, amend, divide, or reserve families after prior-art analysis, inventor confirmation, commercial validation, regulatory information, and budget considerations are much better developed.

### Early prior-art research materially changes how we should draft the broad claims

The preliminary patent search demonstrates that the broadest “recognize an animal and then enable a population-control action” concept is a **crowded prior-art zone**.

Most significantly, USDA's `US20210315186A1`, *Intelligent dual sensory species-specific recognition trigger system*, claims an animal-species-recognition system using combined audio and visual evidence, trained classifiers, autonomous wildlife-management-device triggering, and controlled delivery of **feed, toxicants, vaccines, contraceptives, and other species-control compositions**. Its method claims also cover detecting a target species, enabling a wildlife-management device only for the target species, and not for non-target species. citeturn9view1

Its specification is particularly relevant to our feral-swine branch because it expressly reports feral-swine testing, pre-baited feeder sites, recognition of target swine, and feeder boxes being available only when target animals were present. citeturn9view0turn9view2

That means current independent Claim 1 should **not** be treated as our likely core novelty claim merely because it combines recognition, treatment authorization, and non-target inhibition. Those components are already close to what USDA disclosed.

The older `US20140261201A1`, *Species specific feeder*, is also highly relevant. Its claims cover an animal feeder with a species-recognition device, a lock responsive to the recognition output, sound-based species recognition, intermittent dispensing, a “population controlling feed,” and a species-specific feeding method in which one species is allowed to feed while another is deterred. Its listed animal classes expressly include wild boar. citeturn9view4

`US10368539B2`, *Species specific extermination device*, similarly discloses camera-based comparison of an observed animal against stored reference images followed by selective automated euthanization, with food used to position/attract the animal; the disclosure expressly contemplates adaptation beyond birds to pigs and other animals. citeturn8view0

This does **not** mean the project lacks patentable subject matter. It means our value is increasingly likely to reside in the **specific combinations and control logic** that go beyond generic recognition-triggered treatment.

The strongest candidate differentiators remain the portions we have been deliberately developing:

**Persistent local-population discovery and re-identification.** Prior systems identify a target species or count animals in a current scene; our intended branch builds a working population set across time and then evaluates present animals against that learned local population.

Animal individual-identification technology itself is also prior art. For example, `WO2020076225A1` describes determining the identity of an individual animal within a known population using stored reference information and image-based classifiers. citeturn12view1 Earlier work likewise describes automated unique identification of subjects from a target population for population monitoring. citeturn12view0 So the claim cannot safely rest on “individual animal re-identification” alone.

The likely inventive question is therefore more specific: whether the **combination of longitudinally building a local feral-swine membership set, deciding when a population-presence/completeness condition is met from that set, and selectively authorizing a population-control treatment based on that condition** distinguishes the art.

That issue needs rigorous charting, because whole-sounder trapping is also old. `US9668467B2` expressly teaches a person viewing video and waiting until a desired number of animals, such as a feral-hog sounder, has entered before transmitting the trap-drop signal. citeturn9view5 Our claim architecture therefore needs to emphasize what the automated learned-population/completeness mechanism does that is technically different from merely “wait until the whole sounder appears.”

**Recognition-gated generally toxic bait with controlled access.** This remains commercially important, but the broad concept will face USDA and species-specific feeder art. Narrower implementation details—identity/population state, safety gating, time windows, local model adaptation, dosing/dispensing architecture, audit state, non-target handling, staged conditioning, and particular treatment integrations—will matter.

**Staged conditioning/pre-baiting followed by a treatment transition.** USDA itself expressly describes pre-baited feeder sites, so pre-baiting in isolation is not a novelty anchor. citeturn9view0 The potentially stronger branch is a machine-controlled state transition in which the same monitored station uses recognized local-population behavior to progress through discovery, conditioning, validation, treatment authorization, treatment, inhibition, and post-treatment states.

**Warfarin/KAPUT embodiments.** These remain valuable narrow commercial embodiments, but the patentability case should be based on their integration with the recognition/population-control system—not on claiming warfarin bait itself as though it were newly invented here.

**Sodium nitrite/species-selective treatment embodiments.** Sodium-nitrite feral-omnivore baits and specific feral-hog formulations already have substantial patent literature. `US8795649B2` concerns nitrite-salt baits for controlling feral omnivore populations, and `US11992013B2` describes sodium-nitrite feral-hog bait designed to target wild pigs while reducing impact on non-target species. citeturn12view2turn12view3 This reinforces the earlier drafting decision to distinguish a **predetermined toxicant** from the more demanding concept of a genuinely **species-selective toxicant**.

### §112(a) branches still requiring inventor-originated facts

The current questionnaire and support audit correctly identify the most important unresolved conception/support branches:

**Local-population completeness:** We need to know what the inventors actually contemplated regarding individual re-identification, population membership, when a population is considered sufficiently learned, how new/unknown pigs are treated, and what constitutes “all” or a sufficient target set.

**Species-selective toxicant:** We need an actual inventor-conceived toxicant or selectivity mechanism before relying aggressively on that genus.

**Reproductive control:** We need inventor confirmation of the reproductive treatment classes/routes actually contemplated, rather than merely cataloging technologies known in wildlife management.

**Genetic modification:** We should not present a detailed molecular implementation unless the inventors actually conceived it with sufficient technical specificity. This remains the highest-risk broad §112(a) family.

**Other target animals:** The general target-animal architecture is useful, but broad genus claims need representative support commensurate with the breadth claimed. The specification can show that the common technical core—sensing, recognition, authorization, delivery gating, non-target inhibition, data logging—translates across animal classes, but it should avoid assuming that every treatment modality is interchangeable across every animal group. That is consistent with the MPEP's full-scope enablement analysis. citeturn5search6

### Claims should remain, but patentability confidence should be differentiated

The current claim universe is useful even where a claim is probably too broad to survive examination. The purpose of an overcomplete provisional claim universe is partly to **discover where the specification needs additional support and where narrower combinations may matter**.

Accordingly, the broad claims should not simply be deleted because early art is uncomfortable. They should be categorized:

| Family | Preliminary first-pass assessment |
|---|---|
| Claim 1 broad recognition-gated control | **High prior-art risk** |
| Claim 11 learned local-population/completeness | **Potentially important differentiator; substantial search and §112 work required** |
| Claim 21 general toxicant selective access | **High prior-art/combination risk; useful as parent/support branch** |
| Claim 31 species-selective toxicant | **§112(a) and prior-art risk until concrete species identified** |
| Claim 41 reproductive control | **Integration may matter; agent itself unlikely to be novelty center** |
| Claim 51 genetic modification | **Blocking §112(a) risk without inventor-conceived implementation** |
| Claim 61 feed population-control protocol | **Crowded feed/control space; staged system logic may distinguish** |
| Claim 71 system architecture | **Likely broad combination-art exposure** |
| Claim 81 recognition-model training | **Generic ML training is crowded; local adaptation/population-specific training may be more useful** |
| Claim 91 software medium | **Will generally rise/fall with underlying method novelty** |
| Claim 101 predetermined toxicant | **Useful genus/fallback; toxicant integration rather than toxicant identity is likely key** |
| Claim 111 other target animals | **Broad disclosure value but high genus/prior-art/enablement risk** |
| Claim 121 attraction/conditioning/treatment station | **Important commercial family; should emphasize staged adaptive control, not mere pre-baiting** |
| Claim 131 warfarin/KAPUT | **Important narrow product-integration species; not a claim to newly invent warfarin bait itself** |

These are **search triage judgments**, not legal conclusions of anticipation, obviousness, validity, infringement, or freedom to operate.

## Correct canonical workspace structure

The next unified workspace should use the following structure. These are the paths I recommend treating as authoritative, with **`Startup` as the root exactly as requested**.

```text
Startup\
│
├── .github\
│   └── copilot-instructions.md
│
├── .vscode\
│   └── settings.json
│
├── admin\
│   ├── FeralPig_ArchiveAudit_v0.1_20260903.md
│   ├── FeralPig_ContentDedup_v0.2_20260903.ps1
│   ├── FeralPig_DocumentManifest_v0.2_20260903.md
│   ├── FeralPig_DocumentManifest_v0.2_20260903.csv
│   ├── FeralPig_ManifestChecklist_v0.2_20260903.md
│   ├── FeralPig_MasterIndex_v0.2_20260903.md
│   ├── FeralPig_NamingConvention_v0.2_20260903.md
│   ├── FeralPig_ProjectIndex_v0.2_20260903.md
│   ├── FeralPig_RenameScript_v0.2_20260903.ps1
│   └── SHA256SUMS.txt
│
├── claims\
│   └── FeralPig_ExemplaryClaims_v0.4_20260903.docx
│
├── docs\
│   ├── FeralPig_InventorQuestionnaire_v0.1_20260903.docx
│   ├── FeralPig_MasterControl_v0.5_20260903.docx
│   ├── FeralPig_PriorArtClaimChart_v0.1_20260903.docx
│   ├── FeralPig_ResearchNotes_v0.1_20260903.md
│   ├── FeralPig_StatusProtocol_v0.5_20260903.md
│   └── FeralPig_SupportFigureAudit_v0.2_20260903.docx
│
├── drafts\
│   └── FeralPig_ProvisionalDraft_v0.4_20260903.docx
│
├── figures\
│   └── FeralPig_Figures_v0.2_20260903.pdf
│
├── reference_materials\
│   ├── MPEP\
│   │   ├── e9r-01-2024.zip
│   │   ├── FeralPig_MPEPCoreAuthorities_v0.1_20260903.pdf
│   │   └── FeralPig_MPEPPostRevisionUpdateRegister_v0.1_20260903.pdf
│   │
│   └── prior_art\
│       └── [patent/reference source copies added as research progresses]
│
├── roadmap\
│   └── FeralPig_Roadmap_v0.4_20260903.pdf
│
├── tracker\
│   ├── FeralPig_Tracker_v0.1_20260903.xlsx
│   └── FeralPig_TrackerTemplate_v0.2_20260903.csv
│
├── archive\
│   ├── generated-export\
│   │   ├── [ChatGPT/browser exports]
│   │   └── logs\
│   │       └── debug.log
│   │
│   ├── history\
│   │   ├── admin\
│   │   ├── claims\
│   │   ├── docs\
│   │   ├── drafts\
│   │   ├── figures\
│   │   ├── roadmap\
│   │   └── tracker\
│   │
│   ├── packages\
│   │   ├── Startup_Feral_Pig_Project_Organized_2026-09-03.zip
│   │   ├── Startup_Feral_Pig_Project_Canonical_v0.5_2026-09-03.zip
│   │   └── history\
│   │       └── Startup_Feral_Pig_Project_Canonical_v0.4_2026-09-03.zip
│   │
│   └── working\
│       └── [temporary extraction/reference material only]
│
├── README.md
└── Startup.code-workspace
```

The important historical placements should include at least:

```text
Startup\archive\history\claims\FeralPig_ExemplaryClaims_v0.1_20260903.docx

Startup\archive\history\docs\FeralPig_MasterControl_v0.2_20260903.docx
Startup\archive\history\docs\FeralPig_MasterControl_v0.4_20260903.docx
Startup\archive\history\docs\FeralPig_StatusProtocol_v0.2_20260903.md
Startup\archive\history\docs\FeralPig_StatusProtocol_v0.4_20260903.md

Startup\archive\history\drafts\FeralPig_ProvisionalDraft_v0.2_20260903.docx
Startup\archive\history\drafts\FeralPig_ProvisionalDraft_v0.3_20260903.docx

Startup\archive\history\figures\FeralPig_Figures_v0.1_20260903.pdf

Startup\archive\history\roadmap\FeralPig_Roadmap_v0.2_20260903.pdf
Startup\archive\history\roadmap\FeralPig_Roadmap_v0.3_20260903.pdf

Startup\archive\history\tracker\FeralPig_Tracker_v0.1_prePAT031_20260903.xlsx
```

That gives you a deterministic rule on your machine: **when I provide a file in a later response, the report should give its complete destination beginning with `Startup\`, and you can drop it there verbatim.**

## Project completion estimate and resumed drafting sequence

The project is not 70%–80% complete as a whole merely because the patent is well developed. There are really two different completion percentages.

### Patent package

**Estimated first-draft completion: approximately 72%.**

Already substantially drafted:

- unrestricted 135-claim universe;
- 14 independent claim families;
- 280-paragraph specification;
- abstract;
- FIGS. 1–12;
- 111-reference-numeral architecture;
- limitation-level claim/spec support audit;
- inventor questionnaire;
- patent master control;
- project status/resume protocol;
- broad treatment embodiments;
- warfarin/KAPUT branch;
- predetermined and species-selective toxicant branches;
- reproductive-control branch;
- genetic-control placeholder/support framework;
- attraction/prebait/conditioning/trough branch;
- broad target-animal branch;
- machine-learning training/local adaptation branch;
- safety/fault/audit architecture.

Still materially incomplete:

- inventor confirmation of the blocking conception issues;
- full formal prior-art search and claim chart;
- amendments to the specification based on that art;
- likely restructuring of certain independent claims around actual differentiators;
- deeper dependent-claim fallback ladders after the art chart;
- final §112(a), §112(b), §112(f), antecedent-basis, terminology, and dependency review;
- figure/formality filing review;
- final best-mode/conception review;
- filing metadata/forms and Patent Center preparation;
- licensed patent-counsel review.

The MPEP supports keeping §112 issues distinct: written description focuses on whether the disclosure conveys inventor possession, while enablement asks whether the claimed subject matter can be made and used without undue experimentation. citeturn5search2turn5search6 Means-plus-function and definiteness issues likewise require their own treatment rather than being collapsed into enablement. citeturn5search14turn5search32

### Entire project

**Estimated first-draft completion: approximately 40%.**

A reasonable workstream estimate is:

| Project workstream | First-draft completion |
|---|---:|
| Patent specification / claims / figures / support | ~72% |
| Patent prior-art/patentability package | ~20–25% |
| Project governance/admin/workspace | ~70% before corrections; ~85% once discrepancies above are implemented |
| Inventorship/conception/IP documentation | ~30% |
| Business model / commercialization package | ~10–15% |
| Market/customer/competitive analysis | ~10% |
| Regulatory/deployment strategy | ~10% |
| Federal funding/grant package | ~5–10% |
| State/local/tribal/territorial funding package | ~5% |
| Government procurement strategy | ~5% |
| Partnership/pilot documentation | ~5–10% |
| Financial model/unit economics | ~5% |
| Manufacturing/supply-chain/operations | ~5% |
| International patent/funding/regulatory strategy | ~5% |
| Investor/strategic-partner materials | ~5% |

A simple count of tracker rows would make the project look somewhat more complete, because many patent tasks are already marked complete or in progress. I would **not** use that as the sole metric: later business, grant, procurement, regulatory, and international workstreams currently have relatively few tracker rows even though each will require multiple substantive documents. The approximately **40%** figure is therefore a more realistic document-weighted estimate of the whole project.

### Resumed patent sequence

After the administrative discrepancies are normalized, the proper drafting sequence remains:

**First, complete PAT-042 prior-art charting.** The initial art already shows that we cannot responsibly build the patent around the proposition that audio/video species recognition plus selective feed/toxicant access is itself novel. USDA's published application expressly claims combined audio/video target-animal recognition, autonomous device activation, and delivery of feed, toxicants, vaccines, and contraceptives. citeturn9view1

**Second, sharpen the local-population architecture.** We need to determine exactly what is technically distinct about discovering/learning a local sounder across time, persistently re-identifying its members, managing active/inactive/unknown membership, and using that learned set to authorize treatment. Individual-animal visual identification is itself known, so the differentiation must arise from the larger control architecture. citeturn12view0turn12view1

**Third, sharpen the attraction/conditioning/treatment state machine.** Pre-baiting and species-specific feeders are already documented. citeturn9view0turn9view4 The more promising disclosure is a system that learns return behavior and population composition during a benign-feed phase, determines readiness from accumulated observations, and transitions the station into treatment mode only when specified recognition/population/safety criteria are met.

**Fourth, retain but clearly tier treatment families.** Warfarin/KAPUT, other predetermined toxicants, sodium nitrite, reproductive control, and genetic-control branches should all stay in the disclosure universe, but their novelty and §112 treatment should be separately assessed rather than blended together.

**Fifth, complete inventor-confirmation integration.** This is not administrative busywork. Under the USPTO's current written-description framework, a later drafter's ability to describe a plausible mechanism is not a substitute for original-filed disclosure that shows possession. citeturn5search10turn5search2 The current AI-assisted-inventorship guidance further supports keeping human conception records explicit. citeturn6search0

**Sixth, finish the filing-ready patent package before turning the drafting focus to business documentation.** Once that first-draft patent package is closed, the business documents should use the patent's actual technical architecture as the foundation for product requirements, prototype requirements, regulatory pathways, pilot design, agency/customer segmentation, grant narratives, government procurement opportunities, deployment economics, data strategy, partnerships, manufacturing, and international opportunity analysis.

## Open questions and limitations

The review found **no indication that the current substantive patent package is lost or fundamentally corrupted**. The major problems are version control and stale project-governance instructions rather than missing patent substance.

The most important unresolved technical matters remain inventor-dependent: local-population membership/completeness, the actual reproductive-control embodiments contemplated, any genuinely species-selective-toxicant mechanism, concrete genetic-modification conception, and the extent of inventor contemplation of non-swine target animals. Those should remain expressly flagged rather than “filled in” through drafting inference.

The prior-art review reported here is an **initial substantive search, not the completed PAT-042 search**. It is already sufficient to show significant risk around generic species-recognition-triggered wildlife management, species-specific feeders, recognition-triggered animal destruction, sounder trapping, animal individual identification, and feral-swine toxicant bait. citeturn8view0turn9view1turn9view4turn9view5turn12view1turn12view2 It is not yet sufficient to give a final novelty or obviousness conclusion for each of the 135 claims.

Finally, although I identified the exact corrections and target paths in this review, **I am not representing that a corrected replacement `Startup` ZIP was generated in this response**. The attached archive was ingested and audited; the discrepancies above are the change set that should govern the next canonicalized workspace revision. The next canonical workspace revision should not be labeled complete until the stale instruction set is replaced, the newer tracker is restored to the active tracker path, superseded active versions are moved to history, the missing historical artifacts are restored, the manifest is regenerated with full `Startup\...` paths and external SHA-256 verification, and the resulting tree is independently hash-checked.