"""Bounded provider plans and loss-preserving normalization."""
from __future__ import annotations

import re
from urllib.parse import quote, urlencode, urlparse

from .model import Job, Reference, RequestPlan, stable_id


def plan(job: Job) -> list[RequestPlan]:
    value = job.value.strip()
    if job.provider == "local":
        return []
    if job.provider == "openalex":
        host = "api.openalex.org"
        if job.operation == "search":
            url = "https://api.openalex.org/works?" + urlencode({"search": value, "per-page": job.max_results})
        else:
            v = value.removeprefix("doi:").strip()
            if re.fullmatch(r"10\.\d{4,9}/\S+", v, re.I):
                token = "https://doi.org/" + v
                url = "https://api.openalex.org/works/" + quote(token, safe="")
            elif re.fullmatch(r"W\d+", v, re.I):
                url = "https://api.openalex.org/works/" + v.upper()
            else:
                # Other identifiers use a bounded search; matching is verified after fetch.
                url = "https://api.openalex.org/works?" + urlencode({"search": value, "per-page": job.max_results})
        return [RequestPlan("GET", url, "academic metadata", host)]
    if job.provider == "uspto":
        host = "api.uspto.gov"
        base = "https://api.uspto.gov/api/v1"
        if job.operation == "get":
            if not value.startswith("/api/v1/") or value.startswith("//") or "#" in value or "@" in value:
                raise ValueError("USPTO GET composer requires a /api/v1/ path without credentials or fragment")
            return [RequestPlan("GET", "https://api.uspto.gov" + value, "USPTO custom GET", host, auth_env="USPTO_ODP_API_KEY")]
        if job.operation in {"application", "documents"}:
            if not re.fullmatch(r"\d{7,9}", value):
                raise ValueError("USPTO application number must be 7-9 digits")
            path = f"/patent/applications/{value}" + ("/documents" if job.operation == "documents" else "")
            return [RequestPlan("GET", base + path, "PFW " + job.operation, host, auth_env="USPTO_ODP_API_KEY")]
        if job.operation == "search":
            path = "/patent/applications/search"
            body = {"q": value, "pagination": {"offset": 0, "limit": job.max_results}}
            return [RequestPlan("POST", base + path, "USPTO application search", host, body, "USPTO_ODP_API_KEY")]
        search_paths = {
            "petition": "/petition/decisions/search",
            "ptab_trials": "/patent/trials/proceedings/search",
            "ptab_documents": "/patent/trials/documents/search",
            "ptab_decisions": "/patent/trials/decisions/search",
            "ptab_appeals": "/patent/appeals/decisions/search",
            "ptab_interferences": "/patent/interferences/decisions/search",
        }
        if job.operation in search_paths:
            url = base + search_paths[job.operation] + "?" + urlencode({"q": value, "limit": job.max_results, "offset": 0})
            return [RequestPlan("GET", url, "USPTO " + job.operation, host, auth_env="USPTO_ODP_API_KEY")]
        if value not in {"PTFWPRE", "PTFWPRD"}:
            raise ValueError("bulk product must be PTFWPRE or PTFWPRD")
        return [RequestPlan("GET", base + f"/datasets/products/{value}?latest=true", "bulk product manifest", host, auth_env="USPTO_ODP_API_KEY")]
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() not in [h.lower() for h in job.allow_hosts]:
        raise ValueError("web URL must be HTTPS on an explicitly allowed host")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("web URL cannot contain credentials or fragment")
    return [RequestPlan("GET", value, "permitted web " + job.operation, parsed.hostname.lower())]


def _str(value) -> str:
    return "" if value is None else str(value)


def _abstract_from_index(index: object) -> str:
    if not isinstance(index, dict):
        return ""
    words: dict[int, str] = {}
    for word, positions in index.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for pos in positions:
            if isinstance(pos, int) and 0 <= pos < 10000:
                words.setdefault(pos, word)
    return " ".join(words[pos] for pos in sorted(words))


def normalize_openalex(raw: dict, source_url: str, retrieved_at: str, sha: str, raw_path: str) -> Reference:
    ids = raw.get("ids") or {}
    identifier = _str(raw.get("id") or ids.get("openalex") or raw.get("doi"))
    if not identifier:
        identifier = sha
    authors = []
    for item in raw.get("authorships") or []:
        name = (item.get("author") or {}).get("display_name")
        if name:
            authors.append(name)
    dates = {"publication": _str(raw.get("publication_date"))} if raw.get("publication_date") else {}
    identifiers = {k: _str(v) for k, v in ids.items() if v}
    if raw.get("doi") or ids.get("doi"):
        identifiers["doi"] = _str(raw.get("doi") or ids.get("doi")).removeprefix("https://doi.org/")
    used = {"id", "ids", "doi", "title", "display_name", "authorships", "publication_date", "abstract_inverted_index", "best_oa_location", "referenced_works", "cited_by_count"}
    location = raw.get("best_oa_location") or raw.get("primary_location") or {}
    primary_location = raw.get("primary_location") or {}
    publication_source = (primary_location.get("source") or location.get("source") or {}) if isinstance(primary_location, dict) and isinstance(location, dict) else {}
    biblio = raw.get("biblio") or {}
    citation = {}
    for label, value in (
        ("container_title", publication_source.get("display_name") if isinstance(publication_source, dict) else None),
        ("volume", biblio.get("volume") if isinstance(biblio, dict) else None),
        ("issue", biblio.get("issue") if isinstance(biblio, dict) else None),
        ("start_page", biblio.get("first_page") if isinstance(biblio, dict) else None),
        ("end_page", biblio.get("last_page") if isinstance(biblio, dict) else None),
    ):
        if value is not None and str(value).strip():
            citation[label] = str(value).strip()
    landing_url = _str(location.get("landing_page_url") or raw.get("doi") or raw.get("id"))
    rights = {"license": location.get("license"), "is_oa": raw.get("open_access", {}).get("is_oa") if isinstance(raw.get("open_access"), dict) else None}
    return Reference("openalex", "article", stable_id("openalex", identifier), _str(raw.get("title") or raw.get("display_name") or "Untitled"), landing_url, retrieved_at, sha, raw_path, authors, identifiers, dates, abstract=_abstract_from_index(raw.get("abstract_inverted_index")), extras={k: v for k, v in raw.items() if k not in used}, source_paths={"title": "title|display_name", "creators": "authorships[].author.display_name", "dates.publication": "publication_date", "abstract": "abstract_inverted_index", "citation": "primary_location.source|biblio"}, retrieval_url=source_url, rights=rights, citation=citation)


def normalize_uspto(raw: dict, source_url: str, retrieved_at: str, sha: str, raw_path: str, kind: str = "patent") -> Reference:
    meta = raw.get("applicationMetaData") or raw.get("patentApplicationData") or {}
    number = _str(raw.get("applicationNumberText") or meta.get("applicationNumberText") or raw.get("petitionDecisionRecordIdentifier") or raw.get("trialNumber") or raw.get("appealNumber") or raw.get("interferenceNumber") or sha)
    title = _str(meta.get("inventionTitle") or raw.get("inventionTitle") or raw.get("decisionTypeCode") or raw.get("documentDescription") or number)
    inventors = raw.get("inventorBag") or raw.get("inventors") or []
    creators = []
    if isinstance(inventors, list):
        for person in inventors:
            if isinstance(person, dict):
                name = person.get("inventorNameText") or person.get("name") or " ".join(_str(person.get(k)) for k in ("firstName", "lastName")).strip()
                if name:
                    creators.append(_str(name))
    number_key = "application_number"
    if raw.get("trialNumber"):
        number_key = "trial_number"
    elif raw.get("appealNumber"):
        number_key = "appeal_number"
    elif raw.get("interferenceNumber"):
        number_key = "interference_number"
    elif raw.get("petitionDecisionRecordIdentifier"):
        number_key = "petition_decision_id"
    identifiers = {number_key: number}
    document_id = _str(raw.get("documentIdentifier") or raw.get("documentId") or raw.get("decisionIdentifier") or raw.get("documentCode"))
    if document_id:
        identifiers["document_id"] = document_id
    record_key = number + ":" + document_id if document_id and kind in {"document", "decision"} else number
    if kind in {"document", "decision"} and not document_id and number_key != "petition_decision_id":
        record_key = number + ":" + sha[:16]
    for key, label in (("patentNumber", "patent_number"), ("publicationNumber", "publication_number")):
        if raw.get(key) or meta.get(key):
            identifiers[label] = _str(raw.get(key) or meta.get(key))
    dates = {}
    for key, label in (("filingDate", "filing"), ("publicationDate", "publication"), ("priorityDate", "priority"), ("grantDate", "grant"), ("decisionDate", "decision")):
        if raw.get(key) or meta.get(key):
            dates[label] = _str(raw.get(key) or meta.get(key))
    used = {"applicationNumberText", "applicationMetaData", "patentApplicationData", "inventorBag", "inventors"}
    landing_url = _str(raw.get("url") or raw.get("documentURI") or (source_url if "/search" not in source_url else ""))
    return Reference("uspto", kind, stable_id("uspto", record_key), title, landing_url, retrieved_at, sha, raw_path, creators, identifiers, dates, extras={k: v for k, v in raw.items() if k not in used}, source_paths={"title": "applicationMetaData.inventionTitle|inventionTitle|decisionTypeCode|documentDescription", "identifiers." + number_key: "applicationNumberText|petitionDecisionRecordIdentifier|trialNumber|appealNumber|interferenceNumber"}, retrieval_url=source_url)


def extract_records(job: Job, payload: object) -> list[dict]:
    if not isinstance(payload, dict):
        raise ValueError("provider response must be a JSON object")
    if job.provider == "openalex":
        items = payload.get("results") if job.operation == "search" or "results" in payload else [payload]
    elif job.operation == "application":
        items = payload.get("patentFileWrapperDataBag") or [payload]
    elif job.operation == "documents":
        items = payload.get("documentBag") or payload.get("documents") or [payload]
    elif job.operation == "search":
        items = payload.get("patentFileWrapperDataBag") or []
    elif job.operation == "petition":
        items = payload.get("petitionDecisionDataBag") or []
    elif job.operation == "ptab_trials":
        items = payload.get("patentTrialProceedingDataBag") or []
    elif job.operation == "ptab_documents":
        items = payload.get("patentTrialDocumentDataBag") or []
    elif job.operation == "ptab_decisions":
        items = payload.get("patentTrialDocumentDataBag") or []
    elif job.operation == "ptab_appeals":
        items = payload.get("patentAppealDataBag") or []
    elif job.operation == "ptab_interferences":
        items = payload.get("patentInterferenceDataBag") or []
    elif job.operation == "get":
        items = [payload]
    else:
        items = payload.get("bulkDataProductBag") or [payload]
    if not isinstance(items, list):
        raise ValueError("provider response bag must be a list")
    return [x for x in items[:job.max_results] if isinstance(x, dict)]


def exact_openalex_match(value: str, raw: dict) -> bool:
    v = value.strip().lower().removeprefix("doi:").removeprefix("pmid:").removeprefix("pmcid:").removeprefix("arxiv:").removeprefix("openalex:")
    ids = raw.get("ids") or {}
    candidates = [raw.get("id"), raw.get("doi"), *ids.values()]
    return any(v == _str(x).lower() or _str(x).lower().rstrip("/").endswith("/" + v) for x in candidates if x)
