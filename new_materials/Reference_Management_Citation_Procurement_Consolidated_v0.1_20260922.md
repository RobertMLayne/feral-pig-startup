# Reference management, citation, and source procurement: consolidated project brief

**Status:** source synthesis, version 0.1 (2026-09-22), with a working implementation at [reference_suite/README.md](reference_suite/README.md). This is a cross-repository software brief staged in `new_materials`; it is not a Feral Pig patent specification, claim set, legal conclusion, or replacement for the matter tracker.

## Objective and scope

Create one coherent system for discovering references, obtaining permitted source files, preserving provenance, managing records, and exporting citations. This brief consolidates the accessible GitHub repositories whose principal purpose is reference management or citation capture, with adjacent acquisition components identified separately. “Procurement” here means lawful acquisition of reference metadata and source documents, not purchasing goods or services. No live source acquisition or external publication was performed for this brief.

**Jurisdiction and posture:** software implementation across academic and United States patent data; no application or claim is being drafted or analyzed. **Implementation choice:** one local Python core with command line, desktop GUI, and browser intake surfaces. Live provider and EndNote behavior still require environment-specific verification.

## Repository inventory and source record

The accessible GitHub account was inventoried on 2026-09-22. These are the repositories directly dedicated to the requested functions:

| Repository | Primary role | Verified basis | Treatment |
|---|---|---|---|
| [`reference-harvester`](https://github.com/RobertMLayne/reference-harvester) | Multi-provider harvesting, normalization, provenance, EndNote export | [README](https://github.com/RobertMLayne/reference-harvester/blob/main/README.md), [plan](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/PLAN.md), [audit](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/audit_pack.md) | Proposed core engine and record contract |
| [`pro-ref`](https://github.com/RobertMLayne/pro-ref) | USPTO Patent File Wrapper GUI, document browser, EndNote output | [docs README](https://github.com/RobertMLayne/pro-ref/blob/main/docs/README.md), [exporter](https://github.com/RobertMLayne/pro-ref/blob/main/src/api_gui/export/endnote_export.py) | Reuse its USPTO interaction concepts after mapping and export review |
| [`open-alex`](https://github.com/RobertMLayne/open-alex) | Academic identifier lookup, RIS/PDF capture, browser workflow | [README](https://github.com/RobertMLayne/open-alex/blob/main/README.md) | Browser intake concept and identifier parser |

Adjacent repositories that can supply bounded components, but are not themselves reference-management systems:

| Repository | Relevant component | Evidence |
|---|---|---|
| [`pyUSPTO`](https://github.com/RobertMLayne/pyUSPTO) | Typed clients for USPTO patent, bulk, petition, and PTAB APIs | [README](https://github.com/RobertMLayne/pyUSPTO/blob/main/README.md) |
| [`doc-harvester-pro`](https://github.com/RobertMLayne/doc-harvester-pro) | HTML and rendered-page capture to Markdown | [docs README](https://github.com/RobertMLayne/doc-harvester-pro/blob/main/docs/README.md) |
| [`extract-ocr`](https://github.com/RobertMLayne/extract-ocr) | Offline raw-export normalization, append-only manifest, URL intake, PDF/OCR, and export inspection ideas | [README](https://github.com/RobertMLayne/extract-ocr/blob/main/README.md), [architecture](https://github.com/RobertMLayne/extract-ocr/blob/main/ARCHITECTURE.md) |
| [`content-extractor-pro`](https://github.com/RobertMLayne/content-extractor-pro) | URL batches, rendered HTML, Markdown and PDF capture ideas | [README](https://github.com/RobertMLayne/content-extractor-pro/blob/main/README.md) |
| [`openai-url-harvester`](https://github.com/RobertMLayne/openai-url-harvester) | Bounded URL crawling, robots checks, local URL extraction, and CSV/sitemap output | [README](https://github.com/RobertMLayne/openai-url-harvester/blob/main/README.md) |
| [`url-to-pdf-toolkit`](https://github.com/RobertMLayne/url-to-pdf-toolkit) | Rendered PDF and main-content selector ideas | [`url_to_pdf.py`](https://github.com/RobertMLayne/url-to-pdf-toolkit/blob/main/url_to_pdf.py), [`url_extraction.py`](https://github.com/RobertMLayne/url-to-pdf-toolkit/blob/main/url_extraction.py) |

`doc-harvester-pro-v2` and `doc-harvester-pro-unified` contain related or duplicated document-harvesting files, so they are variant references rather than additional product ideas. `url-processing-toolkit` and `medium-harvester-pro` have only a single placeholder file, and `jpeg-downloader` has a placeholder README; these did not yield a distinct feature. Patent analysis repositories are outside this software project's scope. Empty repositories do not contribute implementable ideas.

## Consolidated product concept

### User journey

1. **Capture a lead:** paste a DOI, PMID, PMCID, arXiv or OpenAlex ID, USPTO application/patent identifier, search query, or permitted URL. A browser action can send the same structured lead as the desktop or command line interface.
2. **Resolve and plan:** classify the identifier, select the provider, preview endpoints/files, show the allowed host and expected data, and produce a dry-run procurement plan.
3. **Acquire:** fetch metadata and available source documents within provider terms and user-selected scope; respect rate limits, robots rules where applicable, retries, timeouts, and resumable downloads. Record inaccessible or paywalled items as requests or leads, never as acquired files.
4. **Preserve evidence:** store raw responses and downloaded bytes, retrieval time, source URL, content hash, license/access notes, request parameters, provider version, and any response or validation errors. Keep raw captures immutable per run.
5. **Normalize and reconcile:** map provider fields to a small common record, retain provider-specific fields in versioned sidecars, log coercions/collisions, and deduplicate by stable identifiers and hashes without discarding distinct versions.
6. **Review:** show metadata, source attachments, provenance, citation preview, conflicts, missing fields, and acquisition status before export.
7. **Export:** produce RIS and BibTeX; optionally EndNote reference-type XML and attachment bundles. Verify import with the target EndNote version and preserve round-trip links to sidecars.

### Canonical record and artifact contract

Use a versioned provider-neutral envelope with `provider`, `source_kind`, `stable_id`, `retrieved_at`, `source_url`, `raw_payload_ref`, `content_sha256`, `canonical`, `extras`, `source_paths`, `mapping_diagnostics`, `attachments`, `access_status`, and `schema_version`. The canonical fields should include title, creators, dates with date type, publication or patent identifiers, URL/DOI, abstract, source type, and relationships to cited/citing works. Preserve publication, priority, filing, and retrieval dates as distinct fields; do not infer one from another.

Separate **reference records** from **acquisition events** and **bulk manifests**. A bulk snapshot has its own manifest reference with file list, hashes, counts, source, and retrieval interval; individual items retain their own records. Store outputs beneath `out/<provider>/<dataset>/<run-id>/`, with a run manifest and a stable pointer to the latest successful run. Minimum artifacts: raw payloads or file references, normalized records, mapping diagnostics, acquisition log, citation exports, and a machine-readable manifest. The current `reference-harvester` implementation is only partly run-scoped, and its USPTO `raw_provider.jsonl` can contain manifest-style entries rather than full API payloads; the contract must label those record types explicitly. [Output contract](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/outputs.md); [audit](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/audit_pack.md).

### Provider and interface plan

- **OpenAlex:** combine the existing works search, raw/canonical logs, RIS, and JSON sidecars in `reference-harvester` with `open-alex`'s identifier intake and optional cited/citing network capture. The latter is a browser feature concept, not evidence that the core engine already supports network crawling. [Provider notes](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/openalex.md); [extension README](https://github.com/RobertMLayne/open-alex/blob/main/README.md).
- **USPTO:** expose PFW search, application lookup, document listing and download, bulk data, petitions, and PTAB through a provider adapter. Reconcile `reference-harvester`'s provider logic, `pro-ref`'s schema-driven GUI/presets, and `pyUSPTO` clients behind one API contract; avoid duplicate network implementations where one maintained client suffices. [pro-ref docs](https://github.com/RobertMLayne/pro-ref/blob/main/docs/README.md); [pyUSPTO README](https://github.com/RobertMLayne/pyUSPTO/blob/main/README.md).
- **Web documents:** use explicit host allowlists, captured URL manifests, and optional HTML-to-Markdown extraction from `doc-harvester-pro`. Preserve the original capture alongside derived Markdown. [Document harvester docs](https://github.com/RobertMLayne/doc-harvester-pro/blob/main/docs/README.md).
- **Interfaces:** define one job schema shared by CLI, GUI, and browser intake. The browser extension submits identifiers/jobs and displays status; it should not become a separate citation database. The NiceGUI path is present but minimal and the Streamlit path is a fallback per the existing audit. [Audit](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/audit_pack.md).

### Citation and EndNote rules

Keep citation type mappings explicit by source kind; validate RIS tags against actual import behavior. `reference-harvester`'s generic citation utility currently emits `TY  - GEN`, while `pro-ref`'s patent exporter emits `TY  - PAT` and places an application number in an `AU` author field. The latter needs correction before adoption because application number is not an author. [Generic serializer](https://github.com/RobertMLayne/reference-harvester/blob/main/src/reference_harvester/citations.py); [patent exporter](https://github.com/RobertMLayne/pro-ref/blob/main/src/api_gui/export/endnote_export.py).

Use built-in EndNote types when they match a record (Patent, Case, Web Page, Dataset). Keep first-class searchable fields intentionally small; attach versioned JSON sidecars containing the full raw/canonical/mapping/provenance data, anchored by a stable ID and hash. The repository's EndNote mapping document states a limited field/type budget and recommends repurposing only the three `Unused` slots. Treat those figures as project-supplied constraints to verify against the installed EndNote version and its exported reference-type table. [EndNote mapping strategy](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/endnote_mapping.md).

## Prioritized build plan and acceptance criteria

Implementation status on 2026-09-22: the local [Reference Suite](reference_suite/README.md) implements the common job contract, OpenAlex/USPTO/web/local adapters, bounded mirroring and citation-network intake, run isolation and resume, artifact hashes, SQLite library and procurement queue with reviewer-linked local file evidence, version/conflict review with citation previews and reviewed metadata corrections, RIS import and RIS/BibTeX/sidecar export with richer citation fields, deduplicated library-wide citation export and optional local attachment bundle, an EndNote template adapter, CLI, desktop GUI, browser intake, immutable job preset revisions, offline OpenAPI/Swagger snapshots and endpoint diffs, offline file-folder and URL-batch intake, raw-export regeneration and inspection, XML formatting, ordered text splitting, web reports, and optional rendered HTML/screenshot/PDF and PDF/OCR adapters. All 63 offline tests pass, including complete CLI workflows, fake transport, and fake renderer checks. Live USPTO/OpenAlex behavior, a real EndNote import round trip, real Playwright/Chrome capture, Tesseract OCR, interactive desktop/browser-extension sessions, and large-file throughput remain unverified. Playwright and Tesseract were not present in the local environment, and no dependencies were installed. The installed Chrome/Edge browsers can be selected once the optional Playwright package is approved. These integrations must not be represented as verified.

The latest correctness review fixed desktop controls that were omitted from submitted jobs, enforced RIS record limits in both preview and execution, kept generic RIS fields from being mislabeled as patent identifiers, and prevented BibTeX key collisions. Provider downloads and manually fulfilled sources now share manifest-backed verification. Manual fulfillment retains its request ID across acquisition resume, appears in combined citations and attachment bundles, and preserves prior file evidence and its original reviewer note when a match is corrected. Combined exports check each distinct source run once.

### Source-to-feature implementation map

| Consolidated function | Source ideas | Working implementation | Verification boundary |
|---|---|---|---|
| Shared jobs, raw/canonical records, manifests, sidecars, RIS/BibTeX | `reference-harvester`, `pro-ref`, `open-alex` | `reference_suite/model.py`, `engine.py`, `citation.py`, `storage.py` | Fake-provider tests; no live EndNote round trip |
| Offline RIS import and citation detail mapping | `reference-harvester`, `pro-ref`, `open-alex` | `ris_import.py`, `providers.py`, `citation.py` | Record-limit, type mapping, duplicate-key, local RIS, and OpenAlex fixture tests; EndNote import still unverified |
| Deduplicated library-wide citation export and local file bundle | `reference-harvester`, `pro-ref`, `open-alex` | `library_export.py`, `storage.py` | Latest-version, procurement-link, and artifact-hash tests; exported citations still need EndNote verification |
| OpenAlex identifier intake and bounded citation relationships | `open-alex`, `reference-harvester` | `providers.py`, `engine.py`, CLI/browser intake | Exact-ID and bounded-network tests; live API unverified |
| USPTO application, document, bulk, petition, and PTAB routes | `pro-ref`, `pyUSPTO` | `providers.py` adapter and common run pipeline | Route planning tests; live API and credentials unverified |
| Web capture, bounded mirror, robots and host gates | `doc-harvester-pro`, `openai-url-harvester` | `engine.py`, `transport` logic, `offline.py` reports | Fake transport tests; live site policy and behavior unverified |
| Offline URL batch, folder intake, XML/text regeneration, splitting and inspection | `extract-ocr`, `content-extractor-pro`, `openai-url-harvester` | `offline.py`, `local_intake.py`, and CLI commands | Local fixtures, bounded file selection, XML fallback, and exact chunk reconstruction; large real exports unverified |
| Rendered HTML, main-content text, screenshot, optional PDF | `content-extractor-pro`, `url-to-pdf-toolkit` | `rendered.py`, `engine.py`, shared job/UI fields | Fake renderer test; Playwright/Chromium unavailable locally |
| Local PDF text and OCR derivation | `extract-ocr` | Optional `pypdf` or Tesseract/PyMuPDF/Pillow adapters in `offline.py` | Dependencies absent; real PDF/OCR results unverified |
| Citation review and source procurement status | `reference-harvester`, `pro-ref` | `storage.py` review and procurement queue; `procurement.py` local fulfillment; CLI operations and GUI record review | Provider/manual integrity, resume, replacement/history, and export-link tests; human source and citation review still required |
| Reviewed metadata corrections and reconciliation | `reference-harvester`, `pro-ref` | `reconciliation.py`, append-only SQLite events, `review-correct`/`review-revert`, effective previews and exports | Corrected export, protected source IDs, immutable source artifacts, supersession/reversal history, and source-refresh review tests; human review remains required |
| Shared desktop job controls and reusable presets | `pro-ref`, `reference-harvester` | `gui.py`, common `Job` contract, `presets.py`, immutable configuration revisions, `preset-save`/`preset-plan`/`preset-run` and history commands | Host/file/depth options, typed job validation, revisions, concurrent saves, integrity checks, and explicit local CLI execution; interactive desktop behavior unverified |
| OpenAPI bundles, endpoint inventories, and specification diffs | `reference-harvester` | `spec_inventory.py`, hashed local JSON bundles, `spec-import`/`spec-show`/`spec-diff` | OpenAPI 3.x/Swagger 2.0 fixture snapshots, bounded local refs, source integrity, inherited settings/schema changes, and CLI workflows; no automatic API execution or complete schema conformance check |

The single project keeps all functions under `reference_suite/`. Optional adapters run through the same job and artifact contracts; they do not create separate reference libraries. `request-set` cannot label a lead acquired without a captured file. `request-fulfill` can label a lead acquired only after a selected local file has a complete capture run, a matching hash, and a reviewer note. The browser HTTP surface does not accept local paths.

Conflict review now supports explicit canonical-field corrections with a reviewer reason, original source run/hash, previous values, and an append-only correction/reversal history. The effective metadata is used in search, desktop/CLI citation previews, and combined exports; exports include a hashed review sidecar and the correction history. Original source/run records and stable/provider identifiers remain intact. Corrections persist for the stable ID across source refreshes and flag fields requiring renewed review when the source hash changes. New correction and reversal commands complete the local reviewed metadata reconciliation step.

The implementation is not a claim that every proposed product capability is finished. Deduplication uses stable IDs, with no automatic cross-provider bibliographic identity decision. Procurement fulfillment, status changes, and metadata correction entry are CLI operations; the desktop surface provides record review and citation previews. RIS/BibTeX exports are data interchange formats, and no general citation-style renderer or bidirectional EndNote synchronization is implemented. These boundaries remain separate from the external integration checks below.

| Priority | Work package | Done when |
|---|---|---|
| P0 | Inventory and contract freeze | Provider/job/record/run schemas are versioned; each field has a definition, source, and migration rule; existing outputs are classified as raw payload, manifest entry, or derived record. |
| P0 | Procurement safety and provenance | Dry run shows host, endpoint, file, and purpose; acquisition honors explicit allowlists and access status; each successful artifact has URL, time, hash, and source; failures remain visible. |
| P0 | Run isolation and resume | Two runs cannot overwrite one another; interrupted downloads resume or restart deterministically; a latest-successful pointer is maintained; the manifest reconciles files and record counts. |
| P0 | Citation correctness | Fixtures for patent, academic work, decision, web page, and dataset import into RIS/BibTeX with identifiers in the proper fields; unsupported fields are retained in sidecars. |
| P1 | Provider consolidation | OpenAlex and USPTO run through the same job and artifact contracts; provider-specific behavior remains in adapters; source documents and metadata link by stable ID. |
| P1 | EndNote verification | Real EndNote import/export round trip preserves record type, stable ID, citation fields, attachment association, and sidecar hash for representative fixtures. |
| P1 | Review UI and browser intake | GUI and CLI produce identical provider-scoped run paths; browser lead capture uses the same job schema and displays reviewable results. |
| P2 | Citation network and additional providers | Bounded cited/citing traversal logs relationship source and depth; a new provider can be added without changing canonical records or existing exports. |

## Evidence and risk matrix

| Finding | Classification | Source and consequence |
|---|---|---|
| Multi-provider raw/canonical logging and EndNote sidecars exist | Verified repository documentation | [Reference Harvester README](https://github.com/RobertMLayne/reference-harvester/blob/main/README.md), [OpenAlex notes](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/openalex.md). Reuse after contract tests. |
| USPTO harvesting is only partly complete; `harvest` has placeholder behavior and run IDs are not the final layout | Verified repository audit | [Audit pack](https://github.com/RobertMLayne/reference-harvester/blob/main/docs/audit_pack.md). Do not call the combined product production-ready. |
| One shared job schema and a single core engine would reduce duplicated workflows | Technical inference | Based on the overlapping CLI, GUI, and extension roles; implementation choice requires architecture review. |
| Live download access, current API limits, provider terms, and EndNote 25 field behavior | Open verification | Repository documentation is not a current external-service test. Verify before live procurement and release. |
| Patent or case citation accuracy | Open verification | Test actual exports and source metadata; do not treat normalized fields as legally authoritative facts. |

## Recommended next actions

1. In an approved environment, run public OpenAlex and USPTO fixture acquisitions and compare returned fields with the local mappings; update an adapter only where the live response shows a mismatch.
2. With the target EndNote installation, import representative RIS exports and verify type, stable ID, attachments, and sidecar hashes; use a real Reference Types export to exercise the XML adapter.
3. Install and exercise the optional browser/PDF/OCR tools only with the workspace owner's approval, then check rendered HTML, screenshot, PDF, extracted text, and artifact hashes on permitted public pages and local sample PDFs.
4. Have the responsible professional review provider access rules and any intended use of patent records in matter work.

**Consistency check:** this brief identifies current repositories separately from proposed capabilities; it uses “reference” for a managed source record, “artifact” for captured bytes or derived output, and “run” for a bounded acquisition/export execution. No claims, matter status, inventorship, or legal opinion are changed here.
