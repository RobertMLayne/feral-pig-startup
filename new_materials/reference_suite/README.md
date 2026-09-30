# Reference Suite

A local implementation of the consolidated reference-management, citation, and source-acquisition workflow. The core uses the Python standard library; rendered capture, PDF text extraction, and OCR are optional local adapters. It combines ideas from the source repositories listed below. No patent matter data is bundled or sent to a service by installation or planning.

## What works

- One validated job contract for OpenAlex lookup/search, USPTO application/documents/search/petition/bulk/PTAB searches and a constrained GET composer, allowlisted HTTPS web capture or bounded mirroring, selected local files and folders, and offline RIS import.
- Offline request preview before any acquisition. Live network requests occur only with `run` or the GUI/browser **Run acquisition** action.
- Exact HTTPS host controls, cross-host redirect rejection, robots checks for web capture, response size caps, bounded retries, and an opt-in resumable file download switch.
- Per-run raw captures, record-level raw JSON, normalized records, diagnostic/event logs, sidecars, RIS/BibTeX, SHA-256 artifact manifest, and a latest-successful pointer.
- SQLite library with all run versions retained and searchable by citation metadata, record review with citation previews and field conflicts, reviewed metadata corrections with append-only history, a source procurement queue with local file fulfillment evidence, and bounded retrieval of OpenAlex referenced and citing works when requested.
- Local Tk GUI and a Chrome extension that sends jobs to a token-protected loopback server.
- Offline URL extraction, prevalidated URL batches, raw capture regeneration, artifact inspection, and web URL/sitemap/CSV reports.
- Optional Playwright rendered-page HTML and screenshot capture, main-content selection, and rendered PDF; optional local PDF text extraction and OCR.
- Reusable validated job presets with immutable revisions, review reasons, and explicit preview/run commands.
- Offline OpenAPI/Swagger JSON snapshots with retained source files, endpoint inventories, integrity verification, and added/removed/changed endpoint comparisons.

## Quick start

Run from this directory with Python 3.12 or newer:

```powershell
python -m reference_suite plan openalex lookup 10.1038/nature12373
python -m reference_suite run openalex lookup 10.1038/nature12373
python -m reference_suite search nature
python -m reference_suite library-export
python -m reference_suite inventory
python -m reference_suite requests
python -m reference_suite gui
```

USPTO calls require `USPTO_ODP_API_KEY` in the environment:

```powershell
$env:USPTO_ODP_API_KEY = '<your key>'
python -m reference_suite plan uspto application 14412875
python -m reference_suite run uspto application 14412875
```

Web capture requires an explicit exact host:

```powershell
python -m reference_suite plan web capture https://example.org/ --allow-host example.org
python -m reference_suite run web capture https://example.org/ --allow-host example.org
python -m reference_suite plan web mirror https://example.org/ --allow-host example.org --max-results 10 --max-depth 2
```

Selected local files use the same run, citation, and provenance pipeline without network access:

```powershell
python -m reference_suite run local ingest path/to/saved-page.html
python -m reference_suite plan local ingest_tree path/to/saved-folder --max-results 500
python -m reference_suite run local ingest_tree path/to/saved-folder --max-results 500
python -m reference_suite run local import_ris path/to/existing-library.ris --max-results 10000
python -m reference_suite extract-urls path/to/notes --out path/to/urls.txt
python -m reference_suite batch-urls path/to/urls.txt --allow-host example.org
```

`batch-urls` only previews by default. Add `--execute` to acquire every URL in the validated batch. Every URL must be on an explicitly allowed HTTPS host before the first request.

Folder intake previews the selected file list, excludes the suite's `out/` tree, symlinks, and Windows junctions, and stops scanning when the `--max-results` limit is exceeded. It accepts up to 10,000 supported files and rejects files above 100 MiB. RIS import retains the original file and each raw record, maps citation fields, and keeps `L1` paths as unverified links; it does not open them. RIS files are capped at 25 MiB, and preview and execution both enforce `--max-results` (25 by default, up to 10,000). Generic RIS `M1`/`M2`/`M3` values remain raw fields unless the record is a patent.

For a previously created run:

```powershell
python -m reference_suite inspect-export path/to/run --fail-on-missing
python -m reference_suite normalize-export path/to/run
python -m reference_suite normalize-export path/to/run --split-chars 12000
python -m reference_suite web-report path/to/web-run
```

`normalize-export` derives Markdown and metadata sidecars from retained raw captures; `--ocr` renders PDF pages locally through Tesseract. It preserves XML structure in a formatted code block and labels malformed XML as unparsed. `--split-chars` writes ordered text chunks with offsets and hashes alongside the complete derived text; concatenating the chunks reconstructs that text. The split size must be 1,000 to 1,000,000 characters. Raw bytes remain retained. `web-report` is for web runs only.

For a JavaScript-rendered single page, install the optional Playwright package in an approved environment. Use Playwright's bundled Chromium, or select an existing Chrome/Edge executable with `REFERENCE_SUITE_BROWSER` to avoid a browser download:

```powershell
$env:REFERENCE_SUITE_BROWSER = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
python -m reference_suite run web capture https://example.org/page --allow-host example.org --render-js --render-pdf --content-selector main
```

The executable override must be an absolute path to an existing executable. Leave it unset to use Playwright's bundled Chromium. A fresh browser context is created for each capture.

The full rendered HTML remains the raw source. The selector controls derived text; if omitted, common main-content selectors are tried. The screenshot and optional PDF are hashed attachments. All browser requests are restricted to the exact allowed HTTPS hosts; the initial capture also honors the web robots gate.

To acquire PDF or document files referenced by metadata, add `--download-files` and explicitly allow any non-provider file host with `--allow-host`. The selected provider's API host is automatically allowed for its own requests. A URL outside the allowed set is logged as a diagnostic rather than fetched.

An incomplete acquisition returns `partial` or `failed` and does not replace `latest.txt`. Resume it with the identical job arguments and `--resume-run <run-id>`, using the ID printed by the previous run.

## Browser intake

1. Run `python -m reference_suite serve` locally. Copy the per-launch token printed in the terminal.
2. Load the `browser/` folder as an unpacked Chrome extension. The extension is configured for port 8765.
3. Paste the token into the popup. Select a reference identifier in a web page and use **Capture in Reference Suite**, or enter it directly in the popup.
4. Preview the plan, then run it. The server binds only to `127.0.0.1`.

The token is intentionally not saved by the extension. A new token is issued each server launch.

## Saved jobs and API specifications

Save an existing job JSON file as a named preset, preview its exact settings, and explicitly run a chosen revision:

```powershell
python -m reference_suite preset-save literature path/to/job.json --reason "Reviewed acquisition settings"
python -m reference_suite preset-list
python -m reference_suite preset-history literature
python -m reference_suite preset-show literature --revision 1
python -m reference_suite preset-plan literature --revision 1
python -m reference_suite preset-run literature --revision 1
```

Saving, listing, and previewing presets never acquires source data. Saving the same name creates a new revision in the selected data root's `presets.sqlite3`; earlier jobs and review reasons remain available. Each load validates the job, provider scope, and revision hashes. API credentials remain in the normal environment variables and are never copied into a preset. Presets can contain confidential local paths or search terms, so keep their database local. Run output identifies the selected revision; the acquisition run retains its full job parameters. Existing `--job-file` inputs now use the same strict type and scope validation and are limited to 64 KiB.

For an API specification already saved locally:

```powershell
python -m reference_suite spec-import path/to/openapi.json
python -m reference_suite spec-show path/to/printed-snapshot-directory
python -m reference_suite spec-diff path/to/older-snapshot path/to/newer-snapshot
```

The importer accepts JSON OpenAPI 3.x and Swagger 2.0 specifications. It stores original bytes, hashes, provenance, a derived endpoint inventory, and a manifest under `out/specifications/spec_snapshots/`. Bounded JSON references within the selected specification directory are included; remote, escaping, missing, or recursive references remain labeled unresolved. No reference URL or declared endpoint is fetched. Importing a specification does not grant acquisition permission or change the suite's provider catalog.

Snapshot loading verifies retained files. Comparison reports added, removed, and changed HTTP path operations, including referenced parameter/schema and inherited server/security changes. It does not classify legal or API compatibility consequences, validate full schema conformance, or inventory callbacks/webhooks. Default bounds are 10 MiB per JSON file, 25 MiB total, 32 files, and 10,000 operations.

## Procurement review

When file acquisition is requested, each source file is tracked in `procurement_requests` as `lead`, `needs_host_approval`, `acquired`, or `failed`. A missing file URL remains a lead. Review with `python -m reference_suite requests`, or filter with `--status failed`. After manual review, update a request with `python -m reference_suite request-set <id> reviewed "review note"`. Manual status updates cannot mark a request acquired.

To link a source file obtained outside the suite, use `python -m reference_suite request-fulfill <id> path/to/file.pdf --note "why this file matches the request"`. This creates a separate local capture run, stores its SHA-256 in the procurement queue, and marks the request acquired. `python -m reference_suite request-verify <id>` rechecks the file against the stored hash and run manifest. The reviewer note asserts the source identity; the software verifies file integrity, not bibliographic identity. These commands do not purchase, request, email, or upload anything.

Verification works for both provider downloads and manually fulfilled files. Resuming an interrupted acquisition retains request IDs and verified manual fulfillment, including its review note. Linked files appear in record citation previews and combined library exports. To correct a manual match, set its status to `reviewed` with the reason, then fulfill it with the corrected source; the previous evidence file, hash, and original reviewer note remain in the request's evidence history.

## Data layout and contracts

`out/<provider>/<dataset>/<run-id>/` contains immutable raw responses, record JSON, derived Markdown for HTML, `raw_provider.jsonl` with explicit payload kinds, `normalized_canonical.jsonl`, `mapping_diagnostics.jsonl`, `acquisition.jsonl`, `relationships.jsonl`, `endnote/references.ris`, `endnote/references.bib`, sidecars, and `manifest.json`. `out/<provider>/<dataset>/latest.txt` points to the last successful run. `library.sqlite3` indexes records and procurement requests across runs.

`manifest.json` reports all artifacts and SHA-256 hashes. `raw_path` and `raw_sha256` on each record identify the exact provider record. `source_url` is the cited work's landing URL when known; `retrieval_url` is the API or capture URL. Sidecars use `reference-suite.sidecar.v1` and contain raw, normalized, and diagnostic values. The citation file uses `AN` for a stable accession ID; patent application numbers are never emitted as authors. The canonical citation field group includes journal or container title, volume, issue, pages, publisher, place, ISSN, and ISBN when present in source data. Filing, publication, priority, grant, decision, imported citation, and retrieval dates remain distinct. The versioned job, record, and run contracts are in `schemas/`; future breaking changes require a new schema file and an explicit migration.

Use `python -m reference_suite review "<stable-id-from-search>"` to inspect every saved version, changed citation fields, and a current RIS/BibTeX preview for a record.

### Reviewed metadata corrections

Use a local JSON patch to record a bibliographic correction after checking its source. For example, save this as `correction.json`:

```json
{
  "title": "Reviewed article title",
  "creators": ["Reviewed Author"],
  "citation.container_title": "Verified Journal",
  "citation.volume": "12",
  "dates.citation": "2024-03-04"
}
```

```powershell
python -m reference_suite review-correct "<stable-id>" correction.json --reason "Checked against the retained article title page"
python -m reference_suite review "<stable-id>"
python -m reference_suite library-export --include-attachments
python -m reference_suite review-revert <correction-id> --reason "Restore the previous reviewed value"
```

Corrections support `title`, the complete `creators` list, `abstract`, and these individual fields: `citation.container_title`, `citation.volume`, `citation.issue`, `citation.start_page`, `citation.end_page`, `citation.publisher`, `citation.place`, `citation.issn`, `citation.isbn`; `dates.publication`, `dates.grant`, `dates.decision`, `dates.citation`, `dates.filing`, and `dates.priority`. Dates use `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. Set an individual citation/date field to JSON `null` to remove it. Unsupported fields, including stable/provider identifiers, source URLs, raw paths, and hashes, are rejected.

Each correction requires a reviewer reason and records its source run/hash, previous values, and timestamp in an append-only SQLite event history. A later correction supersedes the affected fields; reverting adds an event that restores the most recent remaining correction or current source value. Original raw captures, normalized run records, sidecars, and per-run citations remain intact. Library search, the desktop/CLI review preview, and combined exports use the effective corrected metadata. Exported citations link a hashed review sidecar, and export provenance includes the full correction history.

Corrections persist for the stable ID when a new source version arrives. Review and export metadata flag corrected fields whose source hash changed after review. Re-submit those values with a new reviewer reason to confirm them against the refreshed source, or revert the correction. Source versions remain independently visible; this workflow does not automatically merge different source IDs.

### Combined library export

`python -m reference_suite library-export` writes one combined RIS, BibTeX, JSONL, provenance file, and SHA-256 manifest using the latest **complete** run for each stable ID. It checks each distinct source run once before export. Add `--provider openalex` or `--dataset references` to narrow the set. Add `--include-attachments` to copy the records' raw files, attached files, sidecars, and derived Markdown into a bounded local bundle; without that option, citation links retain their original local paths. Verified manual procurement files are linked to their bibliographic records even with a provider filter; their separate source runs and reviewer assertions are recorded in export provenance. Sidecars retain their original source paths as provenance even when copied. BibTeX keys remain unique when different stable IDs would otherwise collapse to the same sanitized or shortened key.

To adapt an actual EndNote Reference Types export, run:

```powershell
python -m reference_suite endnote-template path/to/exported-template.xml path/to/reference-suite-types.xml
```

That operation copies a real type's field layout into one existing `Unused` slot and relabels it. Use `--base-type Patent` if the provider bucket should start from the exported Patent layout. It does not invent a new EndNote schema.

## Source lineage

- `reference-harvester`: provider/run/output contracts, raw and canonical records, sidecars, EndNote strategy, and NiceGUI direction.
- `pro-ref`: USPTO PFW application/document/bulk descriptors, read-only composer, and desktop workflow.
- `open-alex`: identifier intake, browser capture, optional citation network, RIS and PDF acquisition.
- `pyUSPTO`: petition and PTAB API paths and response bags.
- `doc-harvester-pro`: web document acquisition and derived Markdown concept.
- `extract-ocr`: offline raw/export normalization, manifest inspection, PDF/OCR, and append-only provenance concepts.
- `content-extractor-pro`: URL batch intake, rendered page capture, and split derived text concepts.
- `openai-url-harvester`: local URL extraction, bounded crawling, robots checks, and sitemap/CSV report concepts.
- `url-to-pdf-toolkit`: rendered PDF capture and content-selector concepts.

`url-processing-toolkit`, `medium-harvester-pro`, and `jpeg-downloader` were reviewed as adjacent or placeholder repositories; they added no distinct implemented workflow here.

The original repositories are sources of ideas and endpoint descriptions. This project has its own implementation and does not silently depend on their code or installed packages.

## Provider notes and limits

- OpenAlex DOI and OpenAlex work IDs use direct lookup. PMID, PMCID, and arXiv inputs use bounded search followed by exact ID matching. If OpenAlex does not expose the identifier in `ids`, no record is accepted as an exact match.
- Set `OPENALEX_EMAIL` to add polite `mailto` and `From` request headers for OpenAlex.
- OpenAlex citation depth `1` fetches at most `max_results` referenced works and `max_results` citing works for a single lookup, then records relationship edges. Citation expansion is not enabled for broad searches.
- USPTO application and bulk paths derive from the `pro-ref` provider descriptors reviewed on 2026-09-22. Petition and PTAB search paths derive from `pyUSPTO` client code. The two repositories disagreed on the petition path; this build uses `pyUSPTO`'s `/api/v1/petition/decisions/search`. Live API behavior and field variations require verification against current USPTO responses. A failed request is preserved in the run manifest and event log.
- Static HTML capture uses the standard library. JavaScript rendering, PDF text extraction, and OCR require the optional packages in `pyproject.toml`; real integrations were not exercised in this environment because they are not installed.
- Metadata responses larger than 25 MiB and files larger than 1 GiB are rejected. Downloads stream into a `.part` file and resume when the source accepts HTTP Range requests.
- EndNote import/export has not been tested against a live EndNote 25 installation. The XML helper requires a real exported template.
- No live provider acquisition or real browser capture was run during the offline checks. API and website behavior can change and should be verified with approved, nonconfidential examples before production use.

## Tests

```powershell
python -m unittest discover -s tests -v
```

All 63 offline tests pass as of 2026-09-22. They cover desktop job controls, browser executable validation, bounded RIS intake, citation key collisions, acquisition resume, manifest verification, manual fulfillment replacement/history, combined export links, metadata correction/reversal and source immutability, XML derivation, text reconstruction, preset revisions, API snapshot comparisons, and complete CLI workflows. The tests use temporary local files, a fake transport, and a fake renderer; they do not contact providers or disclose workspace contents. An actual desktop session and browser extension session remain untested.
