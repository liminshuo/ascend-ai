#!/usr/bin/env python3
"""Align doc-structure / metadata principle pages with robots.txt page IA + styles."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRS = [ROOT / "docs", ROOT / "report-serve"]

PAGES = {
    "principles-hierarchy.html": {
        "skip": True,
    },
    "principles-noise.html": {
        "overview2": (
            "推荐内容后置原则旨在确保安装、教程等主任务步骤在正文中连续可跟，"
            "推荐、广告与相关阅读置于页末并明确标识，避免被 Agent 当成规格或下一步正文。"
        ),
        "principles": [
            "相关文章、推荐阅读、广告不得插进步骤或主任务中间；次要内容须收到页末并标明推荐。",
            "相关阅读标题勿用「下一步」「继续安装」等操作口吻，避免与步骤正文混淆。",
        ],
        "expected": [
            "主任务步骤可从头到尾连贯跟完，不被营销或推荐内容切断。",
            "推荐与广告可被识别为次要内容，入库时不会与安装规格或步骤正文混为一体。",
        ],
        "notes": [
            "步骤编号或顺序应保持连续；中间插入推荐会导致 Agent 误判步骤总数或遗漏步骤。",
            "页末推荐区应使用「相关文章」「推荐阅读」等栏目名，而非步骤式标题。",
            "侧边栏或弹窗中的推广若含操作指引，仍须在正文中保留完整主路径。",
        ],
        "body_agent": False,
    },
    "principles-timeliness.html": {
        "overview2": (
            "版本号外显原则旨在确保列表与详情均写明具体软件或文档版本（如 v8.0.0），"
            "帮助 AI Agent 定位主推版本与历史版本，而不依赖「新」「旧」等模糊标签。"
        ),
        "principles": [
            "列表与详情均写明具体版本（如 v8.0.0），「新」色标与排序仅作辅助，不能替代版本号。",
            "页头、列表条目与 Frontmatter / meta 中的版本字段应保持一致，避免人机两套说法。",
        ],
        "expected": [
            "回答能落到具体版本号，不会把「新 / 旧」标签或列表第一条误当成当前版本。",
            "检索命中的版本与用户所见页头、列表标注一致，便于核对主推版本。",
        ],
        "notes": [
            "仅有「旧版」字样而未写出版本号时，Agent 无法判断对应哪一发行线。",
            "色标「新」会随运营策略变化，不能作为唯一时效或主推依据。",
            "多版本并列时，每个条目都应带独立版本号，而非共用标题仅靠标签区分。",
        ],
        "body_agent": False,
    },
    "principles-date-modified.html": {
        "overview2": (
            "更新日期外显原则旨在确保列表与详情写出具体更新日期（如 更新时间：2026/03/12），"
            "帮助 AI Agent 判断稿面时效，而不只依赖版本号或「新」标签。"
        ),
        "principles": [
            "列表与详情中均写出具体更新日期（如 更新时间：2026/03/12）；有版本号也不能省略日期。",
            "可见更新日期与 Frontmatter / meta 中的 date_modified 等字段保持同一事实。",
        ],
        "expected": [
            "回答能落到具体更新日期，不会把「新」标签或列表排序误当成最近更新。",
            "检索与页面展示的更新时间一致，便于判断内容是否仍适用。",
        ],
        "notes": [
            "版本号表示发行线，更新日期表示稿面修订时间，二者应同时外显。",
            "日期格式宜全站统一（如 YYYY/MM/DD），避免混用相对时间「上周更新」。",
            "仅写在不可抓取的交互或图片中不算外显，须在正文或页头文本节点可见。",
        ],
        "body_agent": False,
    },
    "principles-a2.html": {
        "overview2": (
            "生命周期状态显化原则旨在明确文档或版本是否仍适用、是否已被取代，"
            "帮助 AI Agent 区分现行版与已废弃版，并在必要时引导至最新版本。"
        ),
        "principles": [
            "主推或现行版本无需特别标注；已废弃、即将下线等非现行状态需明确写出（如「已废弃」）。",
            "若文档已被取代，详情页须提供指向最新版本的链接（如：查看最新版本 v8.0.0）；列表中若最新版已并列展示，可不再重复跳转。",
        ],
        "expected": [
            "历史或废弃版本不会被 Agent 当作当前权威文档引用。",
            "阅读旧版详情时能直达现行版本，减少误用过时规格的风险。",
        ],
        "notes": [
            "仅有版本号与日期仍无法表达「已废弃」；状态须用文字或机器字段写明。",
            "「已废弃」与「维护中」等状态用语应全站统一，并与视觉标签语义一致。",
            "跳转最新版的链接文案应写出目标版本号，避免泛化的「点击查看」。",
        ],
        "body_agent": False,
    },
    "principles-structure-metadata.html": {
        "overview2": (
            "元数据丰富化原则旨在补全文档身份、时效与适用范围等字段，"
            "使页头、正文分节与 Frontmatter / meta 同源，便于 AI Agent 判断能否引用该页。"
        ),
        "principles": [
            "核心身份信息（标题、版本、更新日期等）置于页头；关键内容概述、适用产品等在正文中独立成节。",
            "其余补充元数据（语言、关键词、文档类型、发布方等）统一写入 Frontmatter / meta，避免重复堆砌可见区块。",
            "Frontmatter / meta 与可见文案保持同一套事实，避免页面展示与机器字段出现两套说法。",
        ],
        "expected": [
            "Agent 能根据页头、正文分节与机器字段确认文档身份与适用范围，不单靠标题猜测。",
            "版本、日期与生命周期写入机器字段后，检索与引用更有依据，减少误用过期内容。",
        ],
        "notes": [
            "页头可见信息应在 Frontmatter 中有对应字段，便于切片与整页抓取一致。",
            "「概要」「适用产品」等宜为正文标题节，不宜只出现在 tooltip 或折叠默认隐藏区。",
            "不宜为追求版面简洁而删除机器可读字段，导致 Agent 只能读到残缺标题。",
        ],
        "body_agent": False,
    },
    "principles-link.html": {
        "overview2": (
            "链接去向可自描述原则旨在确保链接与菜单的可见文案写出跳转目标或栏目全称，"
            "使切片脱离上下文后，AI Agent 仍能识别站内外去向。"
        ),
        "principles": [
            "链接、菜单的可见文案须写出目标或栏目全称；站外来源须可识别。",
            "禁止 chunk 里只剩「点击这里」「了解更多」「LINK」等泛化锚文本；页内锚点若邻近标题已写出对象名，仍忌泛词锚文本。",
        ],
        "expected": [
            "锚文本带走目标名或栏目名，切片仍可知跳转去向。",
            "导航与页脚链接可被 Agent 映射到具体栏目，减少「未知链接」实体。",
        ],
        "notes": [
            "图标按钮须提供 aria-label 或可见文字说明目标，不能仅有图形。",
            "站外链接宜在文案或邻近句中注明来源站点或文档类型。",
            "同一 URL 在全站宜使用一致的描述性锚文本，避免同链不同名造成实体分裂。",
        ],
        "body_agent": False,
    },
    "principles-term.html": {
        "overview2": (
            "内容表述清晰可指代原则旨在确保关键信息表达完整、逻辑关系明确、指代对象清晰，"
            "并在相同语境下保持术语一致，帮助 AI Agent 准确理解和使用页面内容。"
        ),
        "principles": [
            "核心结论应明确表达。重要结论、适用条件和关键限制应在相关内容附近完整说明，避免依赖上下文补全关键信息。",
            "逻辑关系应明确呈现。对因果、条件、转折、递进等关系，应使用明确的连接词表达，避免省略关键逻辑导致语义不完整。",
            "指代对象应清晰可定位。使用「它」「该功能」「上述内容」等指代时，应确保对象在当前语境中明确；涉及多个对象时，应直接写出具体名称，避免歧义。",
            "同一概念应保持术语一致。同一页面及相关页面中，同一概念应使用统一名称；确需使用简称、别名或英文术语时，应明确其对应关系。",
        ],
        "expected": [
            "帮助 AI Agent 准确识别核心结论、适用条件及信息之间的逻辑关系。",
            "减少因指代不明、语义省略或术语混用造成的理解偏差。",
            "提高内容检索、跨段落关联和知识引用的准确性。",
        ],
        "notes": [
            "无需消除所有代词或简称；只需确保其指代对象在当前语境中明确。",
            "术语统一不代表必须统一所有表达方式，必要时可保留别名、缩写及中英文对照。",
            "结论前置不应改变原有语义，也不应省略必要的推导过程、条件或限制。",
        ],
        "body_agent": False,
    },
}

SECTION_CSS = """
  #mechanism > p.page-lead,
  #practices > p.page-lead {
    margin: 0;
    font-size: var(--text-body);
    line-height: var(--text-body-lh, 22px);
    color: var(--color-text-secondary);
  }
  #mechanism > h2 + .page-lead,
  #detail-principles > h2 + .bg-list,
  #expected-effect > h2 + .bg-list,
  #notes > h2 + .bg-list {
    margin-top: 0;
  }
  #mechanism > p.page-lead {
    margin-bottom: var(--space-stack, 16px);
  }
  #mechanism > p.page-lead + p.page-lead {
    margin-top: 0;
    margin-bottom: 0;
  }
  #mechanism,
  #detail-principles,
  #practices,
  #expected-effect,
  #notes {
    margin-bottom: 32px;
  }
  .bg-list {
    margin: 0;
    padding-left: 1.25em;
    font-size: var(--text-body);
    line-height: 22px;
    list-style: disc;
    color: var(--color-text-secondary);
  }
  #detail-principles .bg-list li + li,
  #expected-effect .bg-list li + li,
  #notes .bg-list li + li { margin-top: 16px; }
  #detail-principles ol.bg-list,
  #expected-effect ol.bg-list,
  #notes ol.bg-list {
    list-style: decimal;
    list-style-position: inside;
    padding-left: 0;
    margin-left: 0;
  }
"""


def ol_items(items: list[str]) -> str:
    lines = ["      <ol class=\"bg-list\">"]
    for it in items:
        lines.append(f"        <li>{it}</li>")
    lines.append("      </ol>")
    return "\n".join(lines)


def replace_core_section(html: str, principles: list[str]) -> str:
    block = (
        '    <section class="section" id="detail-principles">\n'
        "      <h2>具体原则</h2>\n"
        f"{ol_items(principles)}\n"
        "    </section>"
    )
    pat = re.compile(
        r'    <section class="section" id="core-principles">.*?</section>',
        re.DOTALL,
    )
    if not pat.search(html):
        raise SystemExit("core-principles section not found")
    return pat.sub(block, html, count=1)


def replace_benefits(html: str, expected: list[str], notes: list[str]) -> str:
    block = (
        '    <section class="section" id="expected-effect">\n'
        "      <h2>预期效果</h2>\n"
        f"{ol_items(expected)}\n"
        "    </section>\n\n"
        '    <section class="section" id="notes">\n'
        "      <h2>注意事项</h2>\n"
        f"{ol_items(notes)}\n"
        "    </section>"
    )
    pat = re.compile(
        r'    <section class="section" id="benefits">.*?</section>',
        re.DOTALL,
    )
    if not pat.search(html):
        raise SystemExit("benefits section not found")
    return pat.sub(block, html, count=1)


def patch_css(html: str) -> str:
    html = html.replace(
        "border-bottom: 2px solid var(--color-card-border);",
        "border-bottom: none;",
    )
    html = re.sub(
        r"(padding-bottom: var\(--space-h2-pad-y, 16px\);)\s*\n(\s*border-bottom: none;)",
        "padding-bottom: 0;\n    border-bottom: none;",
        html,
    )
    # Remove old problem/core-principles CSS block if present
    html = re.sub(
        r"\n  #problem > p\.page-lead,.*?#benefits \.bg-list li strong \{[^}]+\}\n",
        "\n",
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"\n  #core-principles \.principle-body[^}]+\}\n(?:  #core-principles \.principle-body[^\}]+\}\n)*",
        "\n",
        html,
        flags=re.DOTALL,
    )
    if "#mechanism > p.page-lead" not in html:
        html = html.replace("</style>", f"{SECTION_CSS}\n</style>")
    # Update section margin rules that still reference old ids
    html = html.replace("#problem,", "#mechanism,")
    html = html.replace("#core-principles,", "#detail-principles,")
    html = html.replace("#benefits .bg-list", "#expected-effect .bg-list")
    return html


def patch_overview(html: str, overview2: str) -> str:
    html = html.replace('id="problem"', 'id="mechanism"', 1)
    html = html.replace("<h2>解决什么问题</h2>", "<h2>概述</h2>", 1)
    insert = f'      <p class="page-lead">{overview2}</p>\n'
    pat = re.compile(
        r"(<section class=\"section\" id=\"mechanism\">\s*\n\s*<h2>概述</h2>\s*\n\s*<p class=\"page-lead\">.*?</p>\s*\n)",
        re.DOTALL,
    )
    m = pat.search(html)
    if not m:
        raise SystemExit("mechanism overview not found")
    return pat.sub(m.group(1) + insert, html, count=1)


def patch_body(html: str, need_agent: bool) -> str:
    if need_agent:
        html = html.replace(
            '<body class="inner-page" data-module="principles" data-page="hierarchy">',
            '<body class="inner-page agent-entry-page" data-module="principles" data-page="hierarchy" data-no-surface-tabs>',
        )
    return html


def process_file(path: Path, meta: dict) -> None:
    if meta.get("skip"):
        return
    html = path.read_text(encoding="utf-8")
    html = patch_body(html, meta.get("body_agent", False))
    html = patch_css(html)
    html = patch_overview(html, meta["overview2"])
    html = replace_core_section(html, meta["principles"])
    html = replace_benefits(html, meta["expected"], meta["notes"])
    path.write_text(html, encoding="utf-8")
    print("updated", path.relative_to(ROOT))


def main() -> None:
    for d in DIRS:
        for name, meta in PAGES.items():
            p = d / name
            if not p.is_file():
                raise SystemExit(f"missing {p}")
            process_file(p, meta)


if __name__ == "__main__":
    main()
