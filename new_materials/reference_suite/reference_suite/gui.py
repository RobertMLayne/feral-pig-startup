"""Local catalog-driven job builder and review surface."""
from __future__ import annotations

import json
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from .catalog import OPERATIONS
from .engine import execute
from .model import Job
from .providers import plan
from .storage import Library


def job_from_form(data: dict) -> Job:
    """Convert the desktop controls to the same complete contract as CLI jobs."""
    values = dict(data)
    values["allow_hosts"] = tuple(host.strip() for host in values["allow_hosts"].split(",") if host.strip())
    for key in ("max_results", "citation_depth", "max_depth"):
        values[key] = int(values[key])
    return Job(**values)


def launch(root: Path) -> None:
    app = tk.Tk()
    app.title("Reference Suite")
    app.geometry("960x720")
    defaults = {"provider": "openalex", "operation": "search", "value": "", "dataset": "references", "max_results": "25", "citation_depth": "0", "max_depth": "1", "allow_hosts": "", "content_selector": ""}
    values = {key: tk.StringVar(value=value) for key, value in defaults.items()}
    values["download_files"] = tk.BooleanVar(value=False)
    values["render_js"] = tk.BooleanVar(value=False)
    values["render_pdf"] = tk.BooleanVar(value=False)
    form = ttk.Frame(app, padding=12)
    form.pack(fill="x")
    labels = (("Provider", "provider"), ("Operation", "operation"), ("Identifier, query, or URL", "value"), ("Dataset", "dataset"), ("Maximum results", "max_results"), ("Citation depth", "citation_depth"), ("Mirror depth", "max_depth"), ("Allowed hosts (comma separated)", "allow_hosts"), ("Rendered content CSS selector (optional)", "content_selector"))
    widgets = {}
    for row, (label, key) in enumerate(labels):
        ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=3)
        if key in {"provider", "operation"}:
            choices = list(OPERATIONS) if key == "provider" else list(OPERATIONS["openalex"])
            widget = ttk.Combobox(form, textvariable=values[key], values=choices, state="readonly")
        else:
            widget = ttk.Entry(form, textvariable=values[key])
        widget.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        widgets[key] = widget
    ttk.Checkbutton(form, text="Download available files", variable=values["download_files"]).grid(row=len(labels), column=1, sticky="w")
    ttk.Checkbutton(form, text="Render JavaScript page", variable=values["render_js"]).grid(row=len(labels) + 1, column=1, sticky="w")
    ttk.Checkbutton(form, text="Save rendered PDF", variable=values["render_pdf"]).grid(row=len(labels) + 2, column=1, sticky="w")
    form.columnconfigure(1, weight=1)
    description = ttk.Label(app, padding=(12, 0), wraplength=900)
    description.pack(fill="x")
    output = tk.Text(app, wrap="word")
    output.pack(fill="both", expand=True, padx=12, pady=8)

    def describe(*_):
        description.configure(text=OPERATIONS.get(values["provider"].get(), {}).get(values["operation"].get(), "Choose an operation."))

    def provider_changed(*_):
        options = list(OPERATIONS[values["provider"].get()])
        widgets["operation"].configure(values=options)
        values["operation"].set(options[0])

    values["provider"].trace_add("write", provider_changed)
    values["operation"].trace_add("write", describe)
    describe()

    def show(value):
        output.delete("1.0", "end")
        output.insert("end", json.dumps(value, ensure_ascii=False, indent=2))

    def get_job() -> Job:
        return job_from_form({key: value.get() for key, value in values.items()})

    def preview():
        try:
            job = get_job()
            from .local_intake import preview_local
            show({"job": job.asdict(), "requests": [x.asdict() for x in plan(job)], "local_input": preview_local(job, root) if job.provider == "local" else None})
        except Exception as exc:
            show({"error": str(exc)})

    def run():
        try:
            job = get_job()
            show({"status": "running", "plan": [x.asdict() for x in plan(job)]})
        except Exception as exc:
            show({"error": str(exc)})
            return

        def worker():
            try:
                result = execute(job, root)
            except Exception as exc:
                result = {"status": "failed", "error": str(exc)}
            app.after(0, lambda: show(result))

        threading.Thread(target=worker, daemon=True).start()

    def search():
        lib = Library(root)
        try:
            show(lib.search(values["value"].get()))
        finally:
            lib.close()

    def review():
        lib = Library(root)
        try:
            show(lib.review(values["value"].get().strip()))
        except Exception as exc:
            show({"error": str(exc)})
        finally:
            lib.close()

    def export_library():
        from .library_export import export_library as build_export
        try:
            show(build_export(root))
        except Exception as exc:
            show({"error": str(exc)})

    def save_preset():
        try:
            job = get_job()
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON preset", "*.json")])
            if path:
                Path(path).write_text(json.dumps(job.asdict(), ensure_ascii=False, indent=2), encoding="utf-8")
                show({"saved_preset": path})
        except Exception as exc:
            show({"error": str(exc)})

    def load_preset():
        path = filedialog.askopenfilename(filetypes=[("JSON preset", "*.json")])
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            data["allow_hosts"] = tuple(data.get("allow_hosts") or ())
            job = Job(**data)
            for key, value in job.asdict().items():
                if key == "schema_version":
                    continue
                values[key].set(", ".join(value) if key == "allow_hosts" else value)
            show({"loaded_preset": path, "job": job.asdict()})
        except Exception as exc:
            show({"error": str(exc)})

    buttons = ttk.Frame(app, padding=12)
    buttons.pack(fill="x")
    for label, command in (("Preview plan", preview), ("Run acquisition", run), ("Search library", search), ("Review record", review), ("Export library", export_library), ("Load preset", load_preset), ("Save preset", save_preset)):
        ttk.Button(buttons, text=label, command=command).pack(side="left", padx=4)
    app.mainloop()
