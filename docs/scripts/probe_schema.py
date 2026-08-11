#!/usr/bin/env python3
"""批量探测友商索引页 URL 是否含 Schema.org（JSON-LD / microdata），并写入「HTML 可读」列第二绿标。"""
from __future__ import annotations

import json
import re
import shutil
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "data/html_schema_probe.json"

UA = "Mozilla/5.0 (compatible; GEO-SchemaProbe/1.0)"
CTX = ssl.create_default_context()

LDJSON_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)
ITEMTYPE_RE = re.compile(r'itemtype=["\']https?://schema\.org/[^"\']+["\']', re.I)
TYPE_RE = re.compile(r'"@type"\s*:\s*"([^"]+)"')

INDEX_TARGETS = [
    ("mintlify", ROOT / "docs/mintlify-index.html"),
    ("nvidia", ROOT / "docs/nvidia-index.html"),
]

SCHEMA_TAG = (
    '<span class="tag tag-yes why-tip tag-schema" '
    'data-tip="{tip}" title="{tip}">Schema</span>'
)

STACK_CSS = """
  .domain-table td.html-stack {
    vertical-align: middle;
  }
  .domain-table td.html-stack {
    line-height: 1.35;
  }
  .domain-table td.html-stack > .tag {
    display: inline-block;
  }
  .domain-table td.html-stack > .tag + .tag {
    display: block;
    margin-top: 4px;
    width: fit-content;
  }
  #panel-ascend .domain-table td.html-stack > .tag + .tag {
    display: block;
    margin-top: 4px;
    width: fit-content;
  }
"""

TR_RE = re.compile(r"<tr>.*?</tr>", re.S)
PATH_RE = re.compile(
    r'<td class="path"><a href="([^"]+)"[^>]*>.*?</a>.*?</td>\s*'
    r"<td>.*?</td>\s*"
    r"<td>.*?</td>\s*"
    r"<td(?:\s+class=\"[^\"]*\")?>.*?</td>",
    re.S,
)
HTML_TD_RE = re.compile(
    r'(<td(?:\s+class="[^"]*")?>)(.*?)(</td>)\s*$',
    re.S,
)


def norm_url(url: str) -> str:
    p = urlsplit(url.strip())
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, "", ""))


def attr_esc(s: str) -> str:
    return escape(s, quote=True).replace("\n", "&#10;")


def fetch(url: str, timeout: int = 18) -> tuple[int | None, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, body
    except Exception as e:
        return None, str(e).encode()


def detect_schema(raw: str) -> dict:
    types: list[str] = []
    methods: list[str] = []
    for m in LDJSON_RE.finditer(raw):
        body = m.group(1).strip()
        if not body:
            continue
        if "schema.org" in body.lower() or '"@type"' in body:
            methods.append("json-ld")
            types.extend(TYPE_RE.findall(body))
    if ITEMTYPE_RE.search(raw):
        methods.append("microdata")
        types.extend(re.findall(r'itemtype=["\']https?://schema\.org/([^"\']+)["\']', raw, re.I))
    # de-dupe preserve order
    seen = set()
    uniq_types = []
    for t in types:
        if t not in seen:
            seen.add(t)
            uniq_types.append(t)
    methods = list(dict.fromkeys(methods))
    return {
        "has_schema": bool(methods),
        "methods": methods,
        "types": uniq_types[:12],
    }


def urls_from_index(html_path: Path) -> list[str]:
    t = html_path.read_text(encoding="utf-8")
    return list(dict.fromkeys(re.findall(r'<td class="path"><a href="([^"]+)"', t)))


def probe_one(url: str) -> dict:
    st, body = fetch(url)
    if st is None or not isinstance(body, bytes) or st != 200:
        err = body.decode("utf-8", "ignore")[:80] if isinstance(body, bytes) else "fail"
        return {
            "url": url,
            "ok": False,
            "status": st,
            "has_schema": False,
            "error": err,
        }
    raw = body.decode("utf-8", "ignore")
    det = detect_schema(raw)
    return {
        "url": url,
        "ok": True,
        "status": st,
        "bytes": len(body),
        **det,
    }


def build_probe(*, workers: int = 12, sites: list[str] | None = None) -> dict:
    out: dict = {"sites": {}}
    if OUT_PATH.exists():
        try:
            prev = json.loads(OUT_PATH.read_text(encoding="utf-8"))
            if isinstance(prev, dict):
                out["sites"] = dict(prev.get("sites") or {})
        except Exception:
            pass
    targets = INDEX_TARGETS
    if sites:
        want = set(sites)
        targets = [(s, p) for s, p in INDEX_TARGETS if s in want]
    for site, path in targets:
        urls = urls_from_index(path)
        rows = []
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(probe_one, u): u for u in urls}
            done = 0
            for fut in as_completed(futs):
                rows.append(fut.result())
                done += 1
                if done % 20 == 0 or done == len(urls):
                    print(f"  {site} progress {done}/{len(urls)}", flush=True)
        rows.sort(key=lambda r: r["url"])
        out["sites"][site] = {
            "index": str(path.relative_to(ROOT)),
            "count": len(rows),
            "with_schema": sum(1 for r in rows if r.get("has_schema")),
            "rows": rows,
        }
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"{site}: {out['sites'][site]['with_schema']}/{len(rows)} have schema",
            flush=True,
        )
    return out


def schema_tip(rec: dict) -> str:
    methods = "/".join(rec.get("methods") or ["json-ld"])
    types = rec.get("types") or []
    type_s = "、".join(types[:6]) if types else "（类型未解析）"
    return f"首包 HTML 含 Schema.org（{methods}）&#10;类型：{type_s}"


def ensure_stack_css(text: str) -> str:
    if "td.html-stack > .tag + .tag" in text:
        return text
    # insert before closing of first style block that has .tag-full
    marker = "  .tag-full { background: var(--yes-bg); color: var(--yes); }"
    if marker in text:
        return text.replace(marker, marker + "\n" + STACK_CSS, 1)
    # fallback: before </style>
    return text.replace("</style>", STACK_CSS + "\n</style>", 1)


def patch_index(html_path: Path, by_norm: dict[str, dict]) -> dict:
    text = html_path.read_text(encoding="utf-8")
    text = ensure_stack_css(text)
    stats = {"added": 0, "kept": 0, "skipped": 0}

    def repl_tr(m: re.Match) -> str:
        tr = m.group(0)
        pm = PATH_RE.search(tr)
        if not pm:
            return tr
        url = pm.group(1)
        rec = by_norm.get(norm_url(url))
        block = pm.group(0)
        # HTML 可读 = last <td…>…</td> in PATH_RE block
        last_open = block.rfind("<td")
        if last_open < 0:
            stats["skipped"] += 1
            return tr
        last_close = block.rfind("</td>")
        if last_close < last_open:
            stats["skipped"] += 1
            return tr
        td = block[last_open : last_close + 5]
        had_schema = "tag-schema" in td
        # strip prior schema tag for idempotency
        td_body = re.sub(
            r'\s*<span class="tag tag-yes why-tip tag-schema"[^>]*>Schema</span>',
            "",
            td,
        )
        # unwrap previous html-stack
        td_body = re.sub(r'^<td(?:\s+class="html-stack")?>', "<td>", td_body)

        if not (rec and rec.get("has_schema")):
            if had_schema:
                # remove schema tag only
                new_block = block[:last_open] + td_body
                stats["added"]  # no-op count
                return tr[: pm.start()] + new_block + tr[pm.end() :]
            stats["skipped"] += 1
            return tr  # unchanged — avoid rewriting

        tip = schema_tip(rec)
        # inject before closing </td>
        if td_body.endswith("</td>"):
            core = td_body[:-5].rstrip()
        else:
            stats["skipped"] += 1
            return tr
        if core.startswith("<td>"):
            core = '<td class="html-stack">' + core[4:]
        elif not core.startswith('<td class="html-stack">'):
            core = re.sub(r"^<td([^>]*)>", r'<td class="html-stack"\1>', core, count=1)
        new_td = core + "\n          " + SCHEMA_TAG.format(tip=tip) + "</td>"
        new_block = block[:last_open] + new_td
        stats["kept" if had_schema else "added"] += 1
        return tr[: pm.start()] + new_block + tr[pm.end() :]

    text = TR_RE.sub(repl_tr, text)
    html_path.write_text(text, encoding="utf-8")
    report = ROOT / "report-serve" / html_path.name
    if report.parent.exists():
        shutil.copy2(html_path, report)
    return stats


def load_probe() -> dict[str, dict]:
    if not OUT_PATH.exists():
        return {}
    data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    by_norm: dict[str, dict] = {}
    for site in (data.get("sites") or {}).values():
        for row in site.get("rows") or []:
            by_norm[norm_url(row["url"])] = row
    return by_norm


def patch_all() -> None:
    by_norm = load_probe()
    if not by_norm:
        raise SystemExit(f"missing probe data: {OUT_PATH}")
    for site, path in INDEX_TARGETS:
        st = patch_index(path, by_norm)
        print(site, path.name, st, flush=True)


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-only", action="store_true")
    ap.add_argument("--patch-only", action="store_true")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--site", action="append", dest="sites", help="mintlify and/or nvidia")
    args = ap.parse_args()
    if args.patch_only:
        patch_all()
        return
    build_probe(workers=args.workers, sites=args.sites)
    if not args.probe_only:
        patch_all()


if __name__ == "__main__":
    main()
