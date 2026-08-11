#!/usr/bin/env python3
"""组件楼层 → 页级 HTML 可读判定（reachability / 友商索引 / citability 案例共用）。"""
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]

STANDARD_LINES = [
    "标准：按组件楼层聚合（与 citability-html 案例同标尺）",
    "完整 = 全部楼层可抓，或橙标均为「可不解决」",
    "部分 = 有蓝楼层，且存在橙标「有必要解决」",
    "缺失 = 无蓝楼层（空壳 / 全靠注入）",
]


def norm_url(url: str) -> str:
    sp = urlsplit(url.strip())
    path = sp.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunsplit((sp.scheme.lower(), sp.netloc.lower(), path, sp.query, ""))


def path_key(url: str) -> str:
    sp = urlsplit(norm_url(url))
    return f"{sp.netloc.lower()}{sp.path.rstrip('/') or '/'}"


def path_depth(path: str) -> int:
    p = path.strip("/")
    return len(p.split("/")) if p else 0


def score_floors(floors: list[dict]) -> str:
    ins = [f for f in floors if f.get("kind") == "in"]
    must_fix = [
        f
        for f in floors
        if f.get("kind") == "warn" and f.get("fixNeeded", True)
    ]
    if not ins:
        return "缺失"
    if must_fix:
        return "部分"
    return "完整"


def floor_counts(floors: list[dict]) -> tuple[int, int, int]:
    n_in = sum(1 for f in floors if f.get("kind") == "in")
    n_must = sum(
        1
        for f in floors
        if f.get("kind") == "warn" and f.get("fixNeeded", True)
    )
    n_ok = sum(
        1
        for f in floors
        if f.get("kind") == "warn" and not f.get("fixNeeded", True)
    )
    return n_in, n_must, n_ok


def format_tip(
    status: str,
    floors: list[dict],
    *,
    case_key: str | None = None,
    case_page: str | None = None,
    page_name: str | None = None,
    inherited: bool = False,
) -> str:
    n_in, n_must, n_ok = floor_counts(floors)
    lines = [
        f"组件实测：{len(floors)} 楼层 · 蓝 {n_in} · 橙需改 {n_must} · 橙可不改 {n_ok}",
        *STANDARD_LINES,
    ]
    if inherited:
        lines.append("注：与同路径案例页同结论（子路径 / ?tag 变体）")
    if n_must:
        names = "、".join(
            f["name"]
            for f in floors
            if f.get("kind") == "warn" and f.get("fixNeeded", True)
        )
        lines.append(f"待改：{names}")
    if case_key and case_page:
        lines.append(f"案例：{case_page.format(key=case_key)}")
    elif page_name:
        lines.append(f"页面：{page_name}")
    lines.append(f"判定：{status}")
    return "\n".join(lines)


def format_auto_tip(
    status: str,
    floors: list[dict],
    *,
    page_name: str | None = None,
    html_note: str | None = None,
    source: str | None = None,
) -> str:
    n_in, n_must, n_ok = floor_counts(floors)
    lines = [
        f"批量探测：{len(floors)} 楼层 · 蓝 {n_in} · 橙需改 {n_must} · 橙可不改 {n_ok}",
        *STANDARD_LINES,
        "说明：自动抓取 HTML 生成；组件细测案例可后续覆盖",
    ]
    if html_note:
        lines.append(f"探测：{html_note}")
    if source:
        lines.append(f"来源：{source}")
    if n_must:
        names = "、".join(
            f["name"]
            for f in floors
            if f.get("kind") == "warn" and f.get("fixNeeded", True)
        )
        lines.append(f"待改：{names}")
    if page_name:
        lines.append(f"页面：{page_name}")
    lines.append(f"判定：{status}")
    return "\n".join(lines)


def pending_tip(page_name: str | None = None, *, case_page_hint: str | None = None) -> str:
    lines = [
        "尚无组件实测案例",
        *STANDARD_LINES,
        f"请补充 {case_page_hint or 'citability-html'} 案例后同步",
    ]
    if page_name:
        lines.append(f"页面：{page_name}")
    lines.append("判定：待实测")
    return "\n".join(lines)


def load_cases(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_case_index(cases: dict) -> tuple[dict[str, tuple[str, dict]], dict[str, tuple[str, dict]]]:
    by_url: dict[str, tuple[str, dict]] = {}
    by_path: dict[str, tuple[str, dict]] = {}
    for key, case in cases.items():
        url = case.get("leftUrl") or case.get("rightUrl")
        if not url:
            continue
        by_url[norm_url(url)] = (key, case)
        by_path[path_key(url)] = (key, case)
    return by_url, by_path


def resolve_case(
    url: str,
    by_url: dict[str, tuple[str, dict]],
    by_path: dict[str, tuple[str, dict]],
) -> tuple[tuple[str, dict], bool] | None:
    """Return (case_key, case), inherited_flag."""
    n = norm_url(url)
    if n in by_url:
        return by_url[n], False

    pk = path_key(url)
    if pk in by_path:
        return by_path[pk], bool(urlsplit(n).query)

    sp = urlsplit(n)
    page_path = sp.path.rstrip("/") or "/"
    best: tuple[str, dict] | None = None
    best_len = -1
    for case_url, pair in by_url.items():
        csp = urlsplit(case_url)
        if csp.netloc != sp.netloc:
            continue
        case_path = csp.path.rstrip("/") or "/"
        if path_depth(case_path) < 2:
            continue
        if page_path == case_path or page_path.startswith(case_path + "/"):
            if len(case_path) > best_len:
                best_len = len(case_path)
                best = pair
    if best:
        return best, True
    return None


def attr_esc(s: str) -> str:
    return escape(s, quote=True).replace("\n", "&#10;")


def tag_class(status: str) -> str:
    return {
        "完整": "tag-full",
        "部分": "tag-partial",
        "缺失": "tag-miss",
        "待实测": "tag-pending",
    }.get(status, "tag-no")


def wrap_html_cell(status: str, tip: str, *, schema: dict | None = None) -> str:
    cls = tag_class(status)
    esc = attr_esc(tip)
    main = (
        f'<span class="tag {cls} why-tip" data-tip="{esc}" '
        f'title="{esc}">{status}</span>'
    )
    if schema and schema.get("has_schema"):
        methods = "/".join(schema.get("methods") or ["json-ld"])
        types = schema.get("types") or []
        type_s = "、".join(types[:6]) if types else "（类型未解析）"
        st = attr_esc(f"首包 HTML 含 Schema.org（{methods}）\n类型：{type_s}")
        main += (
            f'\n          <span class="tag tag-yes why-tip tag-schema" '
            f'data-tip="{st}" title="{st}">Schema</span>'
        )
        return f'<td class="html-stack">{main}</td>'
    return f"<td>{main}</td>"


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else ROOT / "docs/assets/cases-html-ascend/cases-data.json"
    cases = load_cases(path)
    for key, case in cases.items():
        floors = case.get("floors", [])
        st = score_floors(floors)
        n_in, n_must, n_ok = floor_counts(floors)
        print(f"{key:12} {st:4}  in={n_in} must={n_must} ok={n_ok}  {case.get('pageName')}")
