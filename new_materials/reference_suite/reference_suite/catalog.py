"""Single operation catalog consumed by the CLI and GUI."""

OPERATIONS = {
    "openalex": {
        "lookup": "Resolve a DOI or OpenAlex ID; other academic IDs use exact-checked search.",
        "search": "Search academic works with a bounded result count.",
    },
    "uspto": {
        "application": "Look up one Patent File Wrapper application number.",
        "documents": "List one application's document metadata.",
        "search": "Search Patent File Wrapper applications.",
        "petition": "Search petition decisions.",
        "bulk": "List one PTFWPRE or PTFWPRD bulk product and optionally its files.",
        "ptab_trials": "Search PTAB trial proceedings.",
        "ptab_documents": "Search PTAB trial documents.",
        "ptab_decisions": "Search PTAB trial decisions.",
        "ptab_appeals": "Search PTAB appeal decisions.",
        "ptab_interferences": "Search PTAB interference decisions.",
        "get": "Compose a read-only GET under the USPTO /api/v1/ path.",
    },
    "web": {
        "capture": "Capture one allowlisted HTTPS page or document.",
        "mirror": "Mirror bounded pages and optional assets on allowlisted HTTPS hosts.",
    },
    "local": {
        "ingest": "Capture one selected local file and derive readable content without network access.",
        "ingest_tree": "Capture supported files from one selected local folder without following symlinks or using the network.",
        "import_ris": "Import an existing RIS citation file into versioned records without following attachment links.",
    },
}
