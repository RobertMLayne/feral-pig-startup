from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .citation import endnote_type_table
from .catalog import OPERATIONS
from .engine import execute
from .model import Job, now
from .providers import plan
from .storage import Library


def _job_file(path: Path) -> Job:
    from .presets import job_from_dict
    with Path(path).open("rb") as stream:
        raw = stream.read(65537)
    if len(raw) > 65536:
        raise ValueError("job file exceeds 64 KiB")
    return job_from_dict(json.loads(raw.decode("utf-8-sig")))


def _job(args) -> Job:
    if args.job_file:
        return _job_file(Path(args.job_file))
    return Job(args.provider, args.operation, args.value, args.dataset, args.max_results, args.citation_depth, args.download_files, tuple(args.allow_host or ()), args.max_depth, render_js=args.render_js, render_pdf=args.render_pdf, content_selector=args.content_selector)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reference-suite")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="local data root; defaults to current directory")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run"):
        cmd = sub.add_parser(name)
        cmd.add_argument("provider", nargs="?", choices=("openalex", "uspto", "web", "local"))
        cmd.add_argument("operation", nargs="?")
        cmd.add_argument("value", nargs="?")
        cmd.add_argument("--job-file")
        cmd.add_argument("--dataset", default="references")
        cmd.add_argument("--max-results", type=int, default=25)
        cmd.add_argument("--citation-depth", type=int, default=0)
        cmd.add_argument("--download-files", action="store_true")
        cmd.add_argument("--allow-host", action="append", default=[])
        cmd.add_argument("--max-depth", type=int, default=1)
        cmd.add_argument("--render-js", action="store_true")
        cmd.add_argument("--render-pdf", action="store_true")
        cmd.add_argument("--content-selector", default="", help="CSS selector for rendered page text")
        if name == "run":
            cmd.add_argument("--resume-run", help="resume an incomplete run with the same job")
    search = sub.add_parser("search")
    search.add_argument("query")
    review = sub.add_parser("review", help="show every saved version, field conflicts, and citation previews")
    review.add_argument("stable_id")
    correct = sub.add_parser("review-correct", help="append reviewed bibliographic corrections from a local JSON patch")
    correct.add_argument("stable_id")
    correct.add_argument("patch_file", type=Path)
    correct.add_argument("--reason", required=True, help="reviewer's source or basis for the correction")
    revert = sub.add_parser("review-revert", help="append a reversal of a metadata correction without deleting its history")
    revert.add_argument("correction_id", type=int)
    revert.add_argument("--reason", required=True)
    library_export = sub.add_parser("library-export", help="export the latest complete version of each stable reference ID")
    library_export.add_argument("--provider", choices=("openalex", "uspto", "web", "local"))
    library_export.add_argument("--dataset")
    library_export.add_argument("--include-attachments", action="store_true")
    sub.add_parser("inventory")
    spec_import = sub.add_parser("spec-import", help="snapshot a selected local JSON OpenAPI/Swagger specification without network access")
    spec_import.add_argument("source", type=Path)
    spec_show = sub.add_parser("spec-show", help="verify and show a saved API endpoint inventory")
    spec_show.add_argument("snapshot", type=Path)
    spec_diff = sub.add_parser("spec-diff", help="compare verified API snapshots for added, removed, and changed operations")
    spec_diff.add_argument("before", type=Path)
    spec_diff.add_argument("after", type=Path)
    preset_save = sub.add_parser("preset-save", help="save an immutable revision of a validated local job configuration")
    preset_save.add_argument("name")
    preset_save.add_argument("job_file", type=Path)
    preset_save.add_argument("--reason", required=True)
    preset_save.add_argument("--description", default="")
    preset_save.add_argument("--reviewer", default="")
    sub.add_parser("preset-list", help="list saved job presets")
    preset_history = sub.add_parser("preset-history", help="show all verified revisions of a preset")
    preset_history.add_argument("name")
    for command in ("preset-show", "preset-plan", "preset-run"):
        preset = sub.add_parser(command, help={"preset-show": "show a saved preset revision", "preset-plan": "preview a saved job without acquisition", "preset-run": "explicitly execute a saved job"}[command])
        preset.add_argument("name")
        preset.add_argument("--revision", type=int, help="use this saved revision; defaults to latest")
        if command == "preset-run":
            preset.add_argument("--resume-run", help="resume an incomplete run with the identical saved job")
    requests = sub.add_parser("requests", help="list source procurement requests")
    requests.add_argument("--status")
    request_set = sub.add_parser("request-set", help="update a procurement request after review")
    request_set.add_argument("id", type=int)
    request_set.add_argument("status", choices=("lead", "needs_host_approval", "failed", "reviewed"))
    request_set.add_argument("reason")
    request_fulfill = sub.add_parser("request-fulfill", help="capture a selected local file as evidence for a procurement request")
    request_fulfill.add_argument("id", type=int)
    request_fulfill.add_argument("file", type=Path)
    request_fulfill.add_argument("--note", required=True, help="reviewer's basis for linking this file to the request")
    request_verify = sub.add_parser("request-verify", help="verify linked procurement file and run manifest hash")
    request_verify.add_argument("id", type=int)
    extract = sub.add_parser("extract-urls", help="extract URLs from selected local files or folders")
    extract.add_argument("paths", nargs="+", type=Path)
    extract.add_argument("--out", type=Path)
    normalize = sub.add_parser("normalize-export", help="regenerate readable variants from saved raw artifacts")
    normalize.add_argument("run_dir", type=Path)
    normalize.add_argument("--ocr", action="store_true")
    normalize.add_argument("--max-pdf-pages", type=int, default=25)
    normalize.add_argument("--split-chars", type=int, default=0, help="also write exact text chunks of this many characters")
    inspect = sub.add_parser("inspect-export", help="verify every manifest artifact hash and path")
    inspect.add_argument("run_dir", type=Path)
    inspect.add_argument("--fail-on-missing", action="store_true")
    web_report = sub.add_parser("web-report", help="write sitemap, URL list, and crawl CSV from a web run")
    web_report.add_argument("run_dir", type=Path)
    batch = sub.add_parser("batch-urls", help="plan or run a selected local URL list")
    batch.add_argument("source", type=Path)
    batch.add_argument("--allow-host", action="append", default=[])
    batch.add_argument("--max-urls", type=int, default=100)
    batch.add_argument("--dataset", default="references")
    batch.add_argument("--execute", action="store_true", help="perform the planned network acquisitions")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8765)
    sub.add_parser("gui")
    template = sub.add_parser("endnote-template")
    template.add_argument("template", type=Path)
    template.add_argument("destination", type=Path)
    template.add_argument("--label", default="Reference Suite")
    template.add_argument("--base-type", default="Generic")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command in {"plan", "run", "preset-plan", "preset-run"}:
            preset_info = None
            if args.command.startswith("preset-"):
                from .presets import load_preset, job_from_dict
                selected = load_preset(root, args.name, args.revision)
                job = job_from_dict(selected["job"])
                preset_info = {key: selected[key] for key in ("name", "revision", "job_sha256")}
            else:
                if not args.job_file and (not args.provider or not args.operation or not args.value):
                    parser.error("provider, operation, and value are required unless --job-file is given")
                if args.job_file and any((args.provider, args.operation, args.value)):
                    parser.error("positional job fields cannot be combined with --job-file")
                job = _job(args)
            if args.command in {"plan", "preset-plan"}:
                if job.provider == "local":
                    from .local_intake import preview_local
                    local_input = preview_local(job, root)
                else:
                    local_input = None
                output = {"job": job.asdict(), "requests": [r.asdict() for r in plan(job)], "local_input": local_input}
                if preset_info:
                    output["preset"] = preset_info
                print(json.dumps(output, indent=2))
            else:
                result = execute(job, root, resume_run_id=args.resume_run)
                if preset_info:
                    result["preset"] = preset_info
                print(json.dumps(result, indent=2))
                return 0 if result["status"] == "complete" else 1
        elif args.command == "search":
            lib = Library(root)
            try:
                print(json.dumps(lib.search(args.query), ensure_ascii=False, indent=2))
            finally:
                lib.close()
        elif args.command == "review":
            lib = Library(root)
            try:
                print(json.dumps(lib.review(args.stable_id), ensure_ascii=False, indent=2))
            finally:
                lib.close()
        elif args.command == "review-correct":
            with args.patch_file.open("rb") as stream:
                patch_data = stream.read(128 * 1024 + 1)
            if len(patch_data) > 128 * 1024:
                raise ValueError("metadata correction file exceeds 128 KiB")
            patch = json.loads(patch_data.decode("utf-8-sig"))
            lib = Library(root)
            try:
                print(json.dumps(lib.correct_metadata(args.stable_id, patch, args.reason), ensure_ascii=False, indent=2))
            finally:
                lib.close()
        elif args.command == "review-revert":
            lib = Library(root)
            try:
                print(json.dumps(lib.revert_metadata(args.correction_id, args.reason), ensure_ascii=False, indent=2))
            finally:
                lib.close()
        elif args.command == "library-export":
            from .library_export import export_library
            print(json.dumps(export_library(root, provider=args.provider, dataset=args.dataset, include_attachments=args.include_attachments), ensure_ascii=False, indent=2))
        elif args.command == "inventory":
            print(json.dumps(OPERATIONS, indent=2))
        elif args.command == "spec-import":
            from .spec_inventory import import_spec
            result = import_spec(args.source, root / "out" / "specifications")
            summary = {key: result[key] for key in ("snapshot_id", "snapshot_path", "source_sha256", "endpoint_count", "info")}
            summary.update(document_count=len(result["documents"]), unresolved_ref_count=len(result["unresolved_refs"]))
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        elif args.command == "spec-show":
            from .spec_inventory import load_snapshot
            print(json.dumps(load_snapshot(args.snapshot), ensure_ascii=False, indent=2))
        elif args.command == "spec-diff":
            from .spec_inventory import diff_snapshots
            print(json.dumps(diff_snapshots(args.before, args.after), ensure_ascii=False, indent=2))
        elif args.command == "preset-save":
            from .presets import save_preset
            result = save_preset(root, args.name, _job_file(args.job_file), reason=args.reason,
                                 description=args.description, reviewer=args.reviewer,
                                 source=str(args.job_file.resolve()))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == "preset-list":
            from .presets import list_presets
            print(json.dumps(list_presets(root), ensure_ascii=False, indent=2))
        elif args.command == "preset-history":
            from .presets import list_revisions
            print(json.dumps(list_revisions(root, args.name), ensure_ascii=False, indent=2))
        elif args.command == "preset-show":
            from .presets import load_preset
            print(json.dumps(load_preset(root, args.name, args.revision), ensure_ascii=False, indent=2))
        elif args.command == "requests":
            lib = Library(root)
            try:
                print(json.dumps(lib.list_procurement(args.status), ensure_ascii=False, indent=2))
            finally:
                lib.close()
        elif args.command == "request-set":
            lib = Library(root)
            try:
                lib.set_procurement_status(args.id, args.status, args.reason, now())
                print(json.dumps({"id": args.id, "status": args.status}))
            finally:
                lib.close()
        elif args.command == "request-fulfill":
            from .procurement import fulfill_request
            result = fulfill_request(root, args.id, args.file, args.note)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if result["status"] != "acquired":
                return 1
        elif args.command == "request-verify":
            lib = Library(root)
            try:
                result = lib.verify_procurement(args.id)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                if not result["valid"]:
                    return 1
            finally:
                lib.close()
        elif args.command == "extract-urls":
            from .offline import extract_urls
            urls = extract_urls(args.paths)
            if args.out:
                args.out.parent.mkdir(parents=True, exist_ok=True)
                args.out.write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
                print(json.dumps({"count": len(urls), "out": str(args.out.resolve())}))
            else:
                print("\n".join(urls))
        elif args.command == "normalize-export":
            from .offline import normalize_export
            print(json.dumps(normalize_export(args.run_dir, ocr=args.ocr, max_pdf_pages=args.max_pdf_pages, split_chars=args.split_chars), indent=2))
        elif args.command == "inspect-export":
            from .offline import inspect_export
            result = inspect_export(args.run_dir)
            print(json.dumps(result, indent=2))
            if args.fail_on_missing and not result["valid"]:
                return 1
        elif args.command == "web-report":
            from .offline import write_web_reports
            print(json.dumps(write_web_reports(args.run_dir), indent=2))
        elif args.command == "batch-urls":
            from .offline import batch_urls
            result = batch_urls(args.source, root, tuple(args.allow_host), max_urls=args.max_urls, execute_jobs=args.execute, dataset=args.dataset)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if result.get("status") == "partial":
                return 1
        elif args.command == "serve":
            from .server import serve
            serve(root, args.port)
        elif args.command == "gui":
            from .gui import launch
            launch(root)
        elif args.command == "endnote-template":
            endnote_type_table(args.template, args.destination, args.label, args.base_type)
            print(str(args.destination.resolve()))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
