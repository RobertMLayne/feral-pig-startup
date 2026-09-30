"""Bounded offline intake of an explicitly selected local folder."""
from __future__ import annotations

import os
from pathlib import Path

from .model import Job, Reference, digest, now, stable_id
from .offline import derive_bytes


SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".txt", ".md", ".json", ".jsonl", ".xml", ".csv", ".yaml", ".yml", ".ris", ".bib"}
MAX_TREE_FILE_BYTES = 100 * 1024 * 1024


def select_tree(source: Path, root: Path, max_files: int) -> list[Path]:
    if not 1 <= max_files <= 10000:
        raise ValueError("local tree file limit must be 1..10000")
    source = source.expanduser().resolve()
    if not source.is_dir():
        raise ValueError("local tree input is not a folder")
    output_root = (root / "out").resolve()
    if source.is_relative_to(output_root):
        raise ValueError("cannot ingest the suite output tree")
    paths: list[Path] = []
    for folder, child_folders, filenames in os.walk(source, followlinks=False):
        parent = Path(folder)
        child_folders[:] = [name for name in child_folders if not (parent / name).is_symlink() and not (parent / name).is_junction() and not (parent / name).resolve().is_relative_to(output_root)]
        for name in filenames:
            path = parent / name
            if path.suffix.lower() in SUPPORTED_SUFFIXES and not path.is_symlink() and not path.resolve().is_relative_to(output_root):
                paths.append(path)
                if len(paths) > max_files:
                    raise ValueError(f"selected folder exceeds the {max_files} supported file limit")
    paths.sort()
    if not paths:
        raise ValueError("selected folder contains no supported files")
    too_large = [path for path in paths if path.stat().st_size > MAX_TREE_FILE_BYTES]
    if too_large:
        raise ValueError("local tree file exceeds 100 MiB text-derivation cap: " + str(too_large[0]))
    return paths


def preview_local(job: Job, root: Path) -> dict:
    source = Path(job.value).expanduser().resolve()
    if job.operation == "ingest_tree":
        paths = select_tree(source, root, job.max_results)
        return {"path": str(source), "file_count": len(paths), "total_bytes": sum(path.stat().st_size for path in paths), "files": [path.relative_to(source).as_posix() for path in paths]}
    if not source.is_file():
        raise ValueError("local input is not a file")
    size = source.stat().st_size
    if size > 1024 * 1024 * 1024:
        raise ValueError("local input exceeds file size cap")
    if job.operation == "import_ris":
        if size > 25 * 1024 * 1024:
            raise ValueError("RIS input exceeds 25 MiB text size cap")
        from .ris_import import parse_ris
        return {"path": str(source), "bytes": size, "record_count": len(parse_ris(source.read_bytes(), job.max_results))}
    return {"path": str(source), "bytes": size}


def ingest_tree(source: Path, root: Path, run_dir: Path, max_files: int) -> tuple[list[Reference], dict[str, dict], list[dict]]:
    source = source.expanduser().resolve()
    paths = select_tree(source, root, max_files)
    records: list[Reference] = []
    raw_by_id: dict[str, dict] = {}
    events: list[dict] = [{"event": "local_tree_start", "source": str(source), "selected_files": len(paths), "at": now()}]
    for path in paths:
        relative = path.relative_to(source).as_posix()
        with path.open("rb") as stream:
            data = stream.read(MAX_TREE_FILE_BYTES + 1)
        if len(data) > MAX_TREE_FILE_BYTES:
            raise ValueError("local tree file grew beyond the 100 MiB cap: " + str(path))
        sha = digest(data)
        name = digest(relative.encode("utf-8"))[:12] + "_" + sha[:12]
        raw_path = run_dir / "raw" / "local" / (name + path.suffix.lower())
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(data)
        derived_text, method = derive_bytes(data, path.suffix)
        derived_path = run_dir / "derived" / (name + ".md")
        derived_path.parent.mkdir(parents=True, exist_ok=True)
        derived_path.write_text(derived_text, encoding="utf-8")
        kind = "dataset" if path.suffix.lower() in {".json", ".jsonl", ".csv"} else ("web_page" if path.suffix.lower() in {".html", ".htm"} else "document")
        record_id = stable_id("local", digest((relative + "\0" + sha).encode("utf-8")))
        rec = Reference(
            provider="local", kind=kind, stable_id=record_id, title=path.stem, source_url="", retrieved_at=now(),
            raw_sha256=sha, raw_path=str(raw_path.resolve()), identifiers={"sha256": sha},
            extras={"original_local_path": str(path.resolve()), "relative_local_path": relative, "derived_markdown": str(derived_path.resolve()), "derivation_method": method},
            attachments=[{"path": str(raw_path.resolve()), "sha256": sha, "role": "original"}], access_status="acquired",
        )
        records.append(rec)
        raw_by_id[record_id] = {"original_local_path": str(path.resolve()), "relative_local_path": relative, "raw_path": str(raw_path.resolve()), "sha256": sha}
        events.append({"event": "local_tree_file", "relative_path": relative, "raw_path": str(raw_path.resolve()), "sha256": sha, "retrieved_at": now()})
    return records, raw_by_id, events
