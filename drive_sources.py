"""Read the Structural Analysis working sources and project their publication fields."""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


SHEET = "application/vnd.google-apps.spreadsheet"
DOC = "application/vnd.google-apps.document"
REGISTER_TITLE = "JP Structural Analysis — Narayani Inputs and Review — LIVE"
GUIDE_TITLE = "00 START HERE — Structural Sources and GitHub Migration"
DRIVE = "https://www.googleapis.com/drive/v3/files"
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
SCHEMA = "jp.structural.drive-source-status.v1"
PROJECTS = ("Narayani", "Harisharan", "Sabitri Giri", "Kharika Paudel", "Rohini")
NATIVE = {
    "basis-guide": ("Narayani", "Doc"),
    "nar-stair-qa": ("Narayani", "Doc"),
    "har-aad": ("Harisharan", "Doc"),
    "har-stage": ("Harisharan", "Sheet"),
    "har-rebar": ("Harisharan", "Sheet"),
}
SOURCE_HEADERS = ("Key", "Project", "Source role", "Type", "Original Drive link",
                  "Review note", "Read mode")
INPUT_HEADERS = ("Key", "Topic", "Source observation", "Unit", "Evidence keys",
                 "Source section", "Review status", "Public summary", "Publish")
FILE_ID = r"[A-Za-z0-9_-]{20,160}"
LOCATORS = {
    "Sheet": rf"https://docs\.google\.com/spreadsheets/d/({FILE_ID})/edit",
    "Doc": rf"https://docs\.google\.com/document/d/({FILE_ID})/edit",
    "PDF": rf"https://drive\.google\.com/file/d/({FILE_ID})/view",
    "Folder": rf"https://drive\.google\.com/drive/folders/({FILE_ID})",
}
STATES = {"Review hold", "Source observation", "Research reference"}
PRIVATE = re.compile(r"https?://|(?:docs|drive)\.google|ya29\.|access_token|\b\S+@\S+|\b1[A-Za-z0-9_-]{22,}\b",
                     re.IGNORECASE)


class SourceError(ValueError):
    """A source could not be read or failed its publication contract."""


def fetch(token, url, params, operation, *, raw=False):
    url = url + ("?" + urlencode(params, doseq=True) if params else "")
    request = Request(url, headers={"Authorization": "Bearer " + token})
    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read(2_000_001)
    except HTTPError as exc:
        raise SourceError(f"{operation}: HTTP {exc.code}") from None
    except (TimeoutError, URLError):
        raise SourceError(f"{operation}: Google source unavailable") from None
    if len(payload) > 2_000_000:
        raise SourceError(f"{operation}: source exceeds the allowed read size")
    return payload.decode("utf-8-sig") if raw else json.loads(payload)


def discover(token, title, mime):
    result = fetch(token, DRIVE, {
        "q": f"name = '{title}' and mimeType = '{mime}' and trashed = false",
        "fields": "files(id),nextPageToken",
        "pageSize": 100,
    }, "Discover registered structural source")
    files = result.get("files", [])
    if (len(files) != 1 or result.get("nextPageToken") or
            not re.fullmatch(FILE_ID, files[0].get("id", ""))):
        raise SourceError("Expected exactly one matching source visible to the Google reader")
    return files[0]["id"]


def revision(token, file_id, mime):
    info = fetch(token, f"{DRIVE}/{file_id}",
                 {"fields": "mimeType,version,trashed", "supportsAllDrives": "true"},
                 "Read source revision")
    version = str(info.get("version", ""))
    if info.get("trashed") or info.get("mimeType") != mime or not version.isdecimal():
        raise SourceError("Source type, archive state or Drive revision is invalid")
    return version


def cells(token, file_id, a1):
    return fetch(token, f"{SHEETS}/{file_id}/values/{quote(a1, safe='')}",
                 {"valueRenderOption": "UNFORMATTED_VALUE"}, "Read structural Sheet").get("values", [])


def document(token, file_id):
    return fetch(token, f"{DRIVE}/{file_id}/export", {"mimeType": "text/plain"},
                 "Read structural Doc", raw=True)


def records(values, headers):
    if not values or tuple(values[0]) != headers:
        raise SourceError("Structural register headers changed")
    result = {}
    for row in values[1:]:
        if not any(value not in ("", None) for value in row):
            continue
        key = row[0]
        if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,44}", key) or key in result:
            raise SourceError("Missing or duplicate structural source key")
        result[key] = (row + [""] * len(headers))[1:len(headers)]
    return result


def public_text(value, limit):
    if (not isinstance(value, str) or not value.strip() or len(value) > limit
            or PRIVATE.search(value) or any(ord(char) < 32 for char in value)):
        raise SourceError("A public structural field contains unsupported or private content")
    return value.strip()


def prepare_sources(values):
    source_rows = records(values, SOURCE_HEADERS)
    result = {}
    for key, (project, role, kind, url, _, mode) in source_rows.items():
        locator = re.fullmatch(LOCATORS.get(kind, r"(?!)"), url) if isinstance(url, str) else None
        if project not in PROJECTS or not role or not locator or mode not in ("Evidence link", "Native read"):
            raise SourceError("The source index has an invalid project, link, source type or read mode")
        if mode == "Native read" and NATIVE.get(key) != (project, kind):
            raise SourceError("Native reads require a registered structural source role")
        result[key] = (project, kind, locator[1], mode)
    native = {key for key, row in result.items() if row[3] == "Native read"}
    if native != NATIVE.keys() or len({row[2] for row in result.values()}) != len(result):
        raise SourceError("Missing or duplicate native source registration")
    return result


def project_inputs(values, sources):
    rows = []
    for topic, _, _, evidence, location, state, note, visibility in records(values, INPUT_HEADERS).values():
        if visibility == "No":
            continue
        if visibility != "Yes" or state not in STATES or not location or not isinstance(evidence, str):
            raise SourceError("A public structural input is missing a review state or provenance")
        if any(key.strip() not in sources for key in evidence.split("/")):
            raise SourceError("A public structural input points to unregistered evidence")
        rows.append({"topic": public_text(topic, 90), "status": state, "summary": public_text(note, 400)})
    if not rows or len({row["topic"] for row in rows}) != len(rows):
        raise SourceError("The structural input summary is empty or has duplicate topics")
    return rows


def verify_native(token, file_id, kind):
    if kind == "Doc":
        if not document(token, file_id).strip():
            raise SourceError("A registered structural Doc is empty")
        return
    book = fetch(token, f"{SHEETS}/{file_id}", {"fields": "sheets(properties(title,index,hidden))"},
                 "Locate the native summary sheet")
    tabs = sorted((s["properties"] for s in book.get("sheets", []) if not s["properties"].get("hidden")),
                  key=lambda tab: tab.get("index", 0))
    if not tabs:
        raise SourceError("A registered structural Sheet has no visible tabs")
    title = tabs[0]["title"].replace("'", "''")
    if not cells(token, file_id, f"'{title}'!A1:D12"):
        raise SourceError("A registered structural Sheet summary is empty")


def sync(token):
    register = discover(token, REGISTER_TITLE, SHEET)
    guide = discover(token, GUIDE_TITLE, DOC)
    current = {register: (SHEET, revision(token, register, SHEET)),
               guide: (DOC, revision(token, guide, DOC))}
    sources = prepare_sources(cells(token, register, "'Project Sources'!A:G"))
    if sources["basis-guide"][2] != guide:
        raise SourceError("The companion guide in the register differs from the live guide")
    inputs = project_inputs(cells(token, register, "'Inputs and Review'!A:I"), sources)
    notes = [public_text(line[len("[PUBLIC] "):], 400) for line in document(token, guide).splitlines()
             if line.startswith("[PUBLIC] ")]
    if not notes:
        raise SourceError("The structural guide has no public review notes")
    linked = Counter()
    read = Counter(Narayani=1)
    for project, kind, file_id, mode in sources.values():
        if mode == "Evidence link":
            linked[project] += 1
            continue
        mime = DOC if kind == "Doc" else SHEET
        if file_id != guide:
            current[file_id] = (mime, revision(token, file_id, mime))
            verify_native(token, file_id, kind)
        read[project] += 1
    if any(revision(token, file_id, mime) != version for file_id, (mime, version) in current.items()):
        raise SourceError("A structural source changed during import. Run the publisher again.")
    return {
        "schema": SCHEMA,
        "read_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "register_revision": current[register][1],
        "guide_revision": current[guide][1],
        "inputs": inputs,
        "notes": notes,
        "projects": [{"name": name, "native_reads": read[name], "evidence_links": linked[name]}
                     for name in PROJECTS],
        "engineering_approval": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    token = os.environ.get("GOOGLE_OAUTH_ACCESS_TOKEN")
    if not token:
        raise SystemExit("A read-only Google access token is required")
    try:
        snapshot = sync(token)
    except SourceError as exc:
        raise SystemExit(str(exc)) from None
    except (ValueError, KeyError, TypeError):
        raise SystemExit("The structural source returned an invalid payload") from None
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(f"Structural Drive read verified: {len(snapshot['inputs'])} input summaries, "
          f"{len(snapshot['notes'])} Doc notes, {sum(row['native_reads'] for row in snapshot['projects'])} "
          "native sources.")
