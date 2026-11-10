"""Merge an inbox JSON file of job postings into data/jobs.json (deduplicated).

Usage: python scripts/merge.py data/inbox/2026-11-11.json
"""
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "jobs.json"
CSV = ROOT / "data" / "jobs.csv"
KST = timezone(timedelta(hours=9))

REGIONS = {"Korea", "Europe", "USA", "Asia", "Other"}
TYPES = {"Faculty", "Postdoc", "Industry Research", "Industry"}
FIELDS = ["id", "status", "region", "country", "position_type", "field", "title",
          "institution", "department", "deadline", "fit", "url", "source", "summary",
          "first_seen", "last_seen"]


def today():
    return datetime.now(KST).date().isoformat()


def norm_url(u):
    if not u:
        return ""
    p = urlsplit(u.strip())
    q = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith(("utm_", "ref", "fbclid", "gclid"))]
    path = p.path.rstrip("/")
    return urlunsplit((p.scheme.lower() or "https", p.netloc.lower().removeprefix("www."), path, urlencode(q), ""))


def norm_text(s):
    return re.sub(r"[^0-9a-z가-힣]+", "", (s or "").lower())


def key_of(job):
    return "t:" + norm_text(job.get("institution")) + "|" + norm_text(job.get("title"))


def make_id(job):
    base = norm_url(job.get("url")) or key_of(job)
    return hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]


def status_of(job, ref):
    d = job.get("deadline") or ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d < ref:
        return "expired"
    return "open"


def load_db():
    if DB.exists():
        return json.loads(DB.read_text(encoding="utf-8"))
    return []


def save_db(jobs):
    ref = today()
    for j in jobs:
        j["status"] = status_of(j, ref)
    jobs.sort(key=lambda j: (j["region"], j.get("deadline") or "9999", j["institution"]))
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with CSV.open("w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel reads Korean
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(jobs)


def validate(job):
    errs = []
    for k in ("title", "institution", "region", "position_type"):
        if not job.get(k):
            errs.append(f"missing {k}")
    if job.get("region") not in REGIONS:
        errs.append(f"bad region {job.get('region')!r}")
    if job.get("position_type") not in TYPES:
        errs.append(f"bad position_type {job.get('position_type')!r}")
    d = job.get("deadline") or ""
    if d and d != "rolling" and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        errs.append(f"bad deadline {d!r}")
    return errs


def merge(new_jobs):
    jobs = load_db()
    by_id = {j["id"]: j for j in jobs}
    by_key = {key_of(j): j for j in jobs}
    now = today()
    added, updated, skipped = 0, 0, 0
    for raw in new_jobs:
        errs = validate(raw)
        if errs:
            print(f"SKIP {raw.get('title')!r}: {', '.join(errs)}", file=sys.stderr)
            skipped += 1
            continue
        jid = make_id(raw)
        existing = by_id.get(jid) or by_key.get(key_of(raw))
        if existing:
            existing["last_seen"] = now
            for k, v in raw.items():
                if v not in (None, "") and not existing.get(k):
                    existing[k] = v
            updated += 1
            continue
        job = {k: raw.get(k, "") for k in FIELDS if k not in ("id", "status", "first_seen", "last_seen")}
        job.update(id=jid, first_seen=now, last_seen=now)
        jobs.append(job)
        by_id[jid] = job
        by_key[key_of(job)] = job
        added += 1
    save_db(jobs)
    print(f"added={added} updated={updated} skipped={skipped} total={len(jobs)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    merge(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
