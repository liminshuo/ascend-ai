#!/usr/bin/env python3
"""用组件实测标准刷新索引页 / reachability 的「读的懂」列。"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from html_readability import (  # noqa: E402
    attr_esc,
    build_case_index,
    format_auto_tip,
    format_tip,
    load_cases,
    norm_url,
    pending_tip,
    resolve_case,
    score_floors,
    wrap_html_cell,
)

ROOT = Path(__file__).resolve().parents[2]
AUTO_PATH = ROOT / "data/html_readability_auto.json"

HEADER_TIP = attr_esc(
    "按组件楼层聚合（与 citability-html 案例同标尺）："
    "完整=全可抓或橙标均可不解决；部分=有蓝楼层且存在橙标需改；缺失=无蓝楼层。"
    "优先组件细测案例；其余为批量 HTML 探测。悬停看楼层统计。"
)

WHY_TIP_PATCH = """
  .domain-table .why-tip {
    position: relative;
    cursor: help;
  }
  .domain-table a.res-tip,
  .domain-table .why-tip {
    position: relative;
    text-decoration: none;
  }
  .domain-table a.res-tip::after,
  .domain-table .why-tip::after {
    content: attr(data-tip);
    position: absolute;
    left: 50%;
    bottom: calc(100% + 8px);
    transform: translateX(-50%) translateY(4px);
    min-width: 180px;
    max-width: 360px;
    padding: 8px 10px;
    border-radius: 6px;
    background: #0f172a;
    color: #f8fafc;
    font-size: 11px;
    font-weight: 500;
    line-height: 1.45;
    letter-spacing: 0;
    text-transform: none;
    white-space: pre-wrap;
    word-break: break-all;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.18);
    opacity: 0;
    pointer-events: none;
    transition: opacity .12s ease, transform .12s ease;
    z-index: 40;
  }
  .domain-table a.res-tip::before,
  .domain-table .why-tip::before {
    content: "";
    position: absolute;
    left: 50%;
    bottom: calc(100% + 2px);
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-top-color: #0f172a;
    opacity: 0;
    pointer-events: none;
    transition: opacity .12s ease;
    z-index: 40;
  }
  .domain-table a.res-tip:hover::after,
  .domain-table a.res-tip:focus-visible::after,
  .domain-table .why-tip:hover::after,
  .domain-table .why-tip:focus-visible::after {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
  .domain-table a.res-tip:hover::before,
  .domain-table a.res-tip:focus-visible::before,
  .domain-table .why-tip:hover::before,
  .domain-table .why-tip:focus-visible::before {
    opacity: 1;
  }
"""

PATH_RE = re.compile(
    r'<td class="path"><a href="([^"]+)"[^>]*>.*?</a>.*?</td>\s*'
    r"<td>.*?</td>\s*"
    r"<td>.*?</td>\s*"
    r"<td>.*?</td>",
    re.S,
)
TR_RE = re.compile(r"<tr>.*?</tr>", re.S)
NAME_RE = re.compile(
    r'<span class="mn-sub">([^<]+)</span>|<div class="nav-src">([^<]+)</div>'
)

TARGETS = [
    {
        "site": "ascend",
        "doc": "reachability.html",
        "cases": "assets/cases-html-ascend/cases-data.json",
        "case_page": "citability-html-ascend-case.html?case={key}",
        "case_hint": "citability-html-ascend",
        "scope": "panel-ascend",
    },
    {
        "site": "nvidia",
        "doc": "nvidia-index.html",
        "cases": "assets/cases-html-nvidia/cases-data.json",
        "case_page": "citability-html-nvidia-case.html?case={key}",
        "case_hint": "citability-html-nvidia",
        "scope": "all",
    },
    {
        "site": "mintlify",
        "doc": "mintlify-index.html",
        "cases": "assets/cases-html/cases-data.json",
        "case_page": "citability-html-mintlify-case.html?case={key}",
        "case_hint": "citability-html-mintlify",
        "scope": "all",
    },
]


def load_auto_site(site: str) -> dict[str, dict]:
    if not AUTO_PATH.exists():
        return {}
    data = json.loads(AUTO_PATH.read_text(encoding="utf-8"))
    entries = data.get(site, {})
    by_norm: dict[str, dict] = {}
    for url, rec in entries.items():
        by_norm[norm_url(url)] = rec
    return by_norm


def page_label(tr: str) -> str | None:
    m = NAME_RE.search(tr)
    if not m:
        return None
    return (m.group(1) or m.group(2) or "").strip() or None


def add_pending_css(text: str) -> str:
    if ".tag-pending" in text:
        return text
    needle = "  .tag-miss { background: #fde8e8; color: #8b1a1a; }"
    if needle not in text:
        return text
    return text.replace(
        needle,
        needle
        + "\n  .tag-pending { background: #f3f4f6; color: #64748b; border: 1px dashed #cbd5e1; }",
        1,
    )


def ensure_why_tip_css(text: str) -> str:
    if ".domain-table .why-tip" in text:
        return text
    anchor = "  .domain-table a.res-tip {"
    if anchor not in text:
        anchor = "  /* 收录列：hover 显示文件名与地址 */"
        if anchor not in text:
            return text + WHY_TIP_PATCH
    return text.replace(anchor, WHY_TIP_PATCH + "\n" + anchor, 1)


def patch_html(
    text: str,
    cases: dict,
    auto_by_url: dict[str, dict],
    *,
    case_page: str,
    case_hint: str,
    scope: str,
) -> tuple[str, dict]:
    by_url, by_path = build_case_index(cases)
    stats = {"manual": 0, "inherited": 0, "auto": 0, "pending": 0}

    text = re.sub(
        r'<th class="th-group th-group-html(?: why-tip)?"[^>]*>读的懂</th>',
        f'<th class="th-group th-group-html why-tip" data-tip="{HEADER_TIP}" title="{HEADER_TIP}">读的懂</th>',
        text,
    )

    def repl_tr(m: re.Match) -> str:
        tr = m.group(0)
        if 'class="path"' not in tr:
            return tr
        pm = PATH_RE.search(tr)
        if not pm:
            return tr
        url = pm.group(1)
        page_name = page_label(tr)
        nurl = norm_url(url)

        resolved = resolve_case(url, by_url, by_path)
        manual_exact = False
        if resolved:
            (case_key, case), inherited = resolved
            manual_exact = nurl == norm_url(case.get("leftUrl", ""))
            if manual_exact:
                inherited = False

        auto = auto_by_url.get(nurl)

        if resolved and manual_exact:
            case_key, case = resolved[0]
            floors = case.get("floors", [])
            status = score_floors(floors)
            tip = format_tip(
                status,
                floors,
                case_key=case_key,
                case_page=case_page,
                page_name=case.get("pageName") or page_name,
                inherited=False,
            )
            stats["manual"] += 1
        elif auto:
            floors = auto.get("floors", [])
            status = score_floors(floors)
            tip = format_auto_tip(
                status,
                floors,
                page_name=auto.get("pageName") or page_name,
                html_note=auto.get("html_note"),
                source=auto.get("source"),
            )
            stats["auto"] += 1
        elif resolved:
            case_key, case = resolved[0]
            inherited = True
            floors = case.get("floors", [])
            status = score_floors(floors)
            tip = format_tip(
                status,
                floors,
                case_key=case_key,
                case_page=case_page,
                page_name=case.get("pageName") or page_name,
                inherited=True,
            )
            stats["inherited"] += 1
        else:
            status = "待实测"
            tip = pending_tip(page_name, case_page_hint=case_hint)
            stats["pending"] += 1

        new_td = wrap_html_cell(status, tip)
        start_in_tr = pm.start() + pm.group(0).rfind("<td>")
        end_in_tr = pm.end()
        return tr[:start_in_tr] + new_td + tr[end_in_tr:]

    if scope == "panel-ascend":
        panel_m = re.search(
            r'(<div[^>]*id="panel-ascend"[^>]*>)(.*?)(</div>\s*</div>\s*<!-- /\.peer-main -->)',
            text,
            re.S,
        )
        if not panel_m:
            raise SystemExit("panel-ascend not found")
        panel_new = TR_RE.sub(repl_tr, panel_m.group(2))
        text = text[: panel_m.start(2)] + panel_new + text[panel_m.end(2) :]
    else:
        text = TR_RE.sub(repl_tr, text)
    return text, stats


def sync_target(target: dict) -> dict:
    doc_path = ROOT / "docs" / target["doc"]
    cases_path = ROOT / "docs" / target["cases"]
    cases = load_cases(cases_path)
    auto_by_url = load_auto_site(target["site"])
    text = doc_path.read_text(encoding="utf-8")
    text = add_pending_css(text)
    text = ensure_why_tip_css(text)
    text, stats = patch_html(
        text,
        cases,
        auto_by_url,
        case_page=target["case_page"],
        case_hint=target["case_hint"],
        scope=target["scope"],
    )
    doc_path.write_text(text, encoding="utf-8")
    report_path = ROOT / "report-serve" / target["doc"]
    shutil.copy2(doc_path, report_path)
    return stats


def main() -> None:
    for target in TARGETS:
        stats = sync_target(target)
        print(target["doc"], stats)


if __name__ == "__main__":
    main()
