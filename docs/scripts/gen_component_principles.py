#!/usr/bin/env python3
"""Generate principles-component-guide HTML pages for community UI catalog."""

from __future__ import annotations

import importlib.util
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REPORT = ROOT / "report-serve"

# Load probe catalog from sibling generator
_probe_spec = importlib.util.spec_from_file_location(
    "gen_component_probes",
    Path(__file__).parent / "gen_component_probes.py",
)
_probe_mod = importlib.util.module_from_spec(_probe_spec)
assert _probe_spec and _probe_spec.loader
_probe_spec.loader.exec_module(_probe_mod)

GROUPS = _probe_mod.GROUPS
PROBES: dict[str, dict] = _probe_mod.PROBES
all_components = _probe_mod.all_components

OCAROUSEL_CANONICAL = DOCS / "principles-affinity.html"
SKIP_BODY = {"ocarousel"}

CSS = OCAROUSEL_CANONICAL.read_text(encoding="utf-8").split("<style>")[1].split("</style>")[0]

TOC_SCRIPT = """
<script>
(function () {
  var main = document.querySelector('.main-content');
  var tocList = document.getElementById('page-toc-list');
  var used = {};
  function slugify(text) {
    var base = (text || '').trim().toLowerCase()
      .replace(/[^\\w\\u4e00-\\u9fff]+/g, '-')
      .replace(/^-+|-+$/g, '');
    if (!base) base = 'section';
    var slug = base, n = 2;
    while (used[slug]) slug = base + '-' + n++;
    used[slug] = true;
    return slug;
  }
  var headings = main ? main.querySelectorAll('h2, h3') : [];
  var tocItems = [];
  headings.forEach(function (el) {
    var text = el.textContent.replace(/\\s+/g, ' ').trim();
    if (!text) return;
    if (!el.id) el.id = slugify(text);
    tocItems.push({ id: el.id, text: text, level: el.tagName === 'H3' ? 3 : 2, el: el });
  });
  if (tocList) {
    tocList.innerHTML = tocItems.map(function (item) {
      var cls = item.level === 3 ? ' class="toc-h3"' : '';
      return '<li><a href="#' + item.id + '"' + cls + ' data-toc-link>' + item.text + '</a></li>';
    }).join('');
  }
  var tocLinks = document.querySelectorAll('[data-toc-link]');
  function setTocActive(id) {
    tocLinks.forEach(function (a) {
      a.classList.toggle('active', a.getAttribute('href') === '#' + id);
    });
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      var visible = entries
        .filter(function (e) { return e.isIntersecting; })
        .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
      if (visible.length) setTocActive(visible[0].target.id);
    }, { rootMargin: '-20% 0px -60% 0px', threshold: [0, 0.25, 0.5] });
    tocItems.forEach(function (item) { io.observe(item.el); });
  }
  function syncHash() {
    var id = (location.hash || '').replace('#', '');
    if (id) setTocActive(id);
  }
  window.addEventListener('hashchange', syncHash);
  syncHash();
})();
</script>
"""

NAV_SLUGS = {
    "omenu", "obreadcrumb", "oanchor", "opagination", "ostep",
    "onavigation", "ofooternav", "otrees", "osearch",
}
HIDDEN_SLUGS = {"otab", "odialog", "opopover", "odropdown", "ocarousel"}
TABLE_SLUGS = {"odatetable"}

DESIGN_KW = (
    "设计", "版式", "稿面", "视觉", "标注", "UI", "组件", "颜色", "图标",
    "悬停", "tooltip", "折叠", "Tab", "面板", "步骤", "布局", "清单",
)
CONTENT_KW = (
    "MD", "llms", "正文", "文档", "摘要", "锚文本", "入库", "白名单", "文案",
    "sitemap", "规格", "说明", "旁注", "段落", "FAQ", "清单", "图意", "alt",
    "营销", "口号", "噪声", "版本", "定义",
)
FRONTEND_KW = (
    "SSR", "HTML", "href", "DOM", "管道", "chunk", "display", "JS", "首包",
    "链接", "aria", "data-llm", "button", "a[", "懒加载", "客户端", "渲染",
    "option", "table", "th", "id", "hash", "rel=", "figure", "pre>", "details",
)


def principles_href(slug: str) -> str:
    return "principles-affinity.html" if slug == "ocarousel" else f"principles-{slug}.html"


def principles_out_path(slug: str) -> Path:
    if slug == "ocarousel":
        return OCAROUSEL_CANONICAL
    return DOCS / f"principles-{slug}.html"


def node_for(slug: str) -> str:
    if slug in HIDDEN_SLUGS or slug in TABLE_SLUGS:
        return "读的懂"
    if slug in NAV_SLUGS:
        return "找的到"
    return "社区 UI"


def classify_column(title: str, desc: str, fix: str) -> str:
    blob = f"{title} {desc} {fix}"
    scores = {
        "design": sum(1 for k in DESIGN_KW if k in blob),
        "content": sum(1 for k in CONTENT_KW if k in blob),
        "frontend": sum(1 for k in FRONTEND_KW if k in blob),
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "frontend"
    return best


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def li_items(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'        <li><strong>{esc(t)}</strong>：{esc(d)}。</li>' for t, d in items
    )


def compare_block(
    example_title: str,
    before_label: str,
    before_body: str,
    after_label: str,
    after_body: str,
    *,
    before_is_frame: bool = False,
    after_is_frame: bool = False,
) -> str:
    def col(is_frame: bool, body: str) -> str:
        inner = f'<div class="render-frame">{body}</div>' if is_frame else f'<pre class="arch-diagram">{esc(body)}</pre>'
        return f'          <div class="compare-col machine">\n            {inner}\n          </div>'

    def col_human(is_frame: bool, body: str) -> str:
        inner = f'<div class="render-frame">{body}</div>' if is_frame else f'<pre class="arch-diagram">{esc(body)}</pre>'
        return f'          <div class="compare-col human">\n            {inner}\n          </div>'

    return f"""      <div class="principle-example">
        <h4>1. {esc(example_title)}</h4>
        <div class="compare-grid compare-grid--stack compare-grid--no-mid-divider">
          <h4 class="compare-label compare-label--machine">Before · {esc(before_label)}</h4>
{col(before_is_frame, before_body)}
          <h4 class="compare-label compare-label--human">After · {esc(after_label)}</h4>
{col_human(after_is_frame, after_body)}
        </div>
      </div>"""


def render_sidebar(active: str | None) -> str:
    lines = [
        '  <aside class="comp-sidebar" aria-label="组件列表">',
        '    <div class="comp-sidebar-title">组件列表</div>',
        '    <nav class="comp-nav">',
    ]
    for group, items in GROUPS:
        lines.append(f'      <div class="comp-group-label">{group}</div>')
        lines.append("      <ul>")
        for slug, name in items:
            href = principles_href(slug)
            cls = ' class="active"' if active == slug else ""
            lines.append(f'        <li><a href="{href}"{cls}>{name}</a></li>')
        lines.append("      </ul>")
    lines.extend(["    </nav>", "  </aside>"])
    return "\n".join(lines)


def principle_title(probe: dict, name: str, slug: str) -> str:
    if probe.get("no_aff"):
        comp = name.split()[0] if name else slug
        return f"{comp} · 无需亲和改造"
    overrides = {
        "omenu": "侧栏目录 SSR 可爬",
        "otab": "Tab 隐藏语义全量展开",
        "obreadcrumb": "面包屑路径可链回溯",
        "oanchor": "锚点目录与正文 id 对齐",
        "opagination": "分页深页 URL 可爬",
        "ostep": "步骤流程文本平铺",
        "onavigation": "主导航子级 SSR 可发现",
        "ofooternav": "页脚链接全量可抓",
        "obutton": "跳转按钮链接化",
        "olink": "链接 href 真实可跟",
        "odropdown": "下拉子项进首包",
        "otrees": "文档树节点 SSR 可链",
        "osearch": "搜索补充不可替 URL",
        "oselect": "选型选项文本可证伪",
        "otoggle": "Toggle 入口与筛选分流",
        "orate": "评分数字与 CTA 分流",
        "ocascader": "级联路径选项可读",
        "otag": "标签语义与装饰分流",
        "odialog": "对话框关键说明双写",
        "ocard": "卡片三要素文本化",
        "odatetable": "表格语义化可问答",
        "opopover": "气泡说明正文 duplicate",
    }
    return overrides.get(slug, probe["title_short"])


def principle_one_liner(probe: dict, slug: str) -> str:
    if probe.get("no_aff"):
        return (
            f"<strong>{probe['term']}</strong>——{probe['definition']}。"
            "本组件<strong>无需亲和改造</strong>；规格说明应写在旁侧正文/文档页，管道可跳过纯控件 DOM。"
        )
    fixes = {
        "omenu": "文档侧栏/层级菜单须在首包输出<strong>完整可爬目录树</strong>，每个节点为真实 <code>a[href]</code>；勿把发现层绑在前端注入的 OMenu 上。",
        "otab": "关键步骤不得只放在交互切换的面板里；<strong>各 Tab 面板须 SSR 全量输出</strong>，禁 JS 抓取仍得全面板正文，视觉隐藏不得删除文本节点。",
        "obreadcrumb": "面包屑须把<strong>祖先页输出为可爬链接</strong>，当前页为纯文本；路径文案与 sitemap 保持一致。",
        "oanchor": "长文锚点目录须用<strong>真实 #id 与 href 对齐正文标题</strong>；禁 javascript: 或仅 JS 生成目录。",
        "opagination": "列表分页须为<strong>带 query 的真实 URL</strong>；禁纯 button/onClick 翻页导致深页不可达。",
        "ostep": "流程步骤的<strong>标题与说明须写入 HTML 文本</strong>；状态勿只靠颜色，进行中/完成须文本可引用。",
        "onavigation": "顶栏/主导航<strong>全部层级 a[href] 进首包</strong>；纯交互（换肤/语言）标注排除，勿当知识正文。",
        "ofooternav": "页脚各列导航<strong>SSR 全量链接</strong>，列名稳定；作为顶栏之外的第二发现层写入 llms/sitemap。",
        "obutton": "跳转型 CTA 一律用<strong>可抓链接</strong>；纯提交/关闭类按钮文案管道宜剥离。",
        "olink": "正文与导航链接必须带<strong>真实 href</strong>；禁 javascript:void、空链或 span 冒充链接。",
        "odropdown": "下拉菜单内导航项须在<strong>源码可读</strong>；勿悬停/portal 延迟挂载导致子链丢失。",
        "otrees": "文档树节点须<strong>链接+标题进 HTML</strong>；懒加载子树须 SSR 当前分支或提供 MD 平行轨。",
        "osearch": "搜索是补充发现层，<strong>不能替代可爬 URL 与 sitemap</strong>；检索范围说明写文档而非 placeholder。",
        "oselect": "若选项映射文档/版本，<strong>选项文本与落地页须可证伪</strong>；纯表单 select 管道可跳过。",
        "otoggle": "区分 Toggle 的<strong>导航入口</strong>与<strong>纯 UI 筛选</strong>；映射分类页则每项须可链。",
        "orate": "评分数字若 SSR 可作社会证明；<strong>「我要评分」等操作 CTA 宜剥离</strong>，勿与官方认证混淆。",
        "ocascader": "级联若代表内容路径，<strong>各级 option 文本须可读</strong>；纯地址表单不必入库。",
        "otag": "版本/状态类标签须<strong>可读文本进 HTML</strong>；装饰性营销 tag 管道宜剥离。",
        "odialog": "含安装步骤等<strong>关键说明须在正文 duplicate 或 dialog DOM 进首包</strong>；纯确认框可忽略。",
        "ocard": "卡片须静态输出<strong>标题 + 摘要 + a[href]</strong>；封面图补 alt，禁整卡 onclick。",
        "odatetable": "规格表用<strong>真实 table/th/td</strong>，禁截图表或 div 伪表；md 平行表可问答。",
        "opopover": "字段规格<strong>勿只放悬停气泡</strong>；正文须 duplicate 或 popover 内容 SSR 进首包。",
    }
    if slug in fixes:
        return fixes[slug]
    rc = probe["root_cause"]
    return f"针对<strong>{probe['term']}</strong>：{rc}。改造方向见下方三栏建议与示例。"


def probe_to_principles(slug: str, name: str, probe: dict) -> dict[str, Any]:
    design: list[tuple[str, str]] = []
    content: list[tuple[str, str]] = []
    frontend: list[tuple[str, str]] = []

    for title, desc, fix in probe.get("subcauses", []):
        col = classify_column(title, desc, fix)
        item = (title, fix.rstrip("。"))
        {"design": design, "content": content, "frontend": frontend}[col].append(item)

    for title, desc in probe.get("insights", []):
        if title.startswith("结论"):
            continue
        col = classify_column(title, desc, desc)
        item = (title, desc.rstrip("。"))
        target = {"design": design, "content": content, "frontend": frontend}[col]
        if not any(t == title for t, _ in target):
            target.append(item)

    if not design:
        design.append(("本原则无独立设计改动", "以内容/前端交付面为主；设计稿标注组件角色即可"))
    if not content:
        content.append(("正文承载规格", "关键说明写入可引用文档页或旁注段落，勿绑在交互态"))
    if not frontend:
        frontend.append(("HTML 结构实现", "关键文本与链接 SSR 进首包；管道按组件语义切片或跳过"))

    comp = name.split()[0] if name else slug
    term = probe["term"]

    design_b = f"{comp} 交互态/视觉壳；规格说明缺失或绑在点击/hover 上。"
    design_a = f"稿面预留可见文案位；{design[0][1]}。"
    content_b = f"（无）关键说明只在 {term} 交互态或 UI 文案中。"
    content_a = f"规格写入正文/MD；{content[0][1]}。"
    frontend_b = f"&lt;div class=\"o-{slug.lstrip('o')}\"&gt;…&lt;/div&gt;\n&lt;!-- 关键文本未 SSR / 无 href --&gt;"
    frontend_a = f"&lt;!-- SSR 全量文本 + 真实链接 --&gt;\n&lt;!-- {frontend[0][1]} --&gt;"

    acceptance = [
        ("静态可达", f"禁 JS 抓取后，{term}相关关键文本/链接仍在首包 HTML 中。"),
        ("可证伪", f"对探针问句的回答可引用具体 href/段落，与 <a href=\"problems-{slug}.html\">问题实测</a> 失败判据互斥。"),
        ("管道", "Chunk 规则明确：该收录的文本/链接进库，纯 UI 控件/瞬时态可跳过。"),
    ]
    if probe.get("no_aff"):
        acceptance = [
            ("无需改造", "组件本身不承载官网知识正文；Agent 不应把控件态解释成规格。"),
            ("旁注优先", "规格说明须在旁侧正文/文档页可引用，而非 placeholder/label/角标数字。"),
            ("管道跳过", "构建管道默认跳过该组件 DOM 或标记 data-llm-exclude，不产生噪声 chunk。"),
        ]

    return {
        "title": principle_title(probe, name, slug),
        "one_liner": principle_one_liner(probe, slug),
        "node": node_for(slug),
        "symptom": probe["title_short"],
        "design": design[:4],
        "content": content[:5],
        "frontend": frontend[:4],
        "design_example": ("交付稿对比", "仅交互壳/视觉态", design_b, "可见文案位 + 角色标注", design_a, False, False),
        "content_example": ("正文/MD 对比", "说明绑在 UI 态", content_b, "规格进可引用正文", content_a, False, False),
        "frontend_example": ("HTML/管道对比", "首包缺文本/链接", frontend_b, "SSR + 管道规则", frontend_a, False, False),
        "acceptance": acceptance,
        "no_aff": probe.get("no_aff", False),
    }


# Rich overrides for high-traffic / benchmark components
PRINCIPLES_OVERRIDES: dict[str, dict[str, Any]] = {
    "otab": {
        "design": [
            ("面板标题入稿", "每个 Tab 面板在稿面有独立 H3 标题位，维度名（在线/离线/型号）须可见"),
            ("平铺备用轨", "提供「展开全部」或预展开 MD 安装页链接，不依赖点击切换"),
            ("多轴勿叠隐藏", "选型×Tab 叠加时，各轴选项仍须在稿面列表化，避免只显示默认组合"),
        ],
        "content": [
            ("核心步骤不进唯一面板", "安装命令、下载说明等须写入可引用正文或独立文档页"),
            ("Tab 维度写进标题", "面板标题含维度名，抓取后可区分「Atlas 800 离线安装」等"),
            ("MD 平行轨", "CANN 下载等页提供预展开 MD，RAG 优先读平铺轨"),
        ],
        "frontend": [
            ("SSR 全量面板", "各 tab-panel 完整输出 DOM；视觉层叠用位移/透明度，禁 display:none 删文本"),
            ("语义结构", "tablist + tab + tabpanel，panel 以 section/h3 标题开头"),
            ("Chunk 切片", "按 panel 拆 chunk，字段含「Tab 名 + 正文」；非激活 panel 同样入库"),
        ],
        "design_example": (
            "Tab 稿面：隐藏 → 全量可见",
            "仅默认面板有正文位",
            '<p class="rf-muted">稿面只画「当前 Tab」内容区，其余面板标注「交互出现」。</p>',
            "每面板独立标题+正文块",
            '<p><strong>在线安装</strong> / <strong>离线安装</strong> 各有正文区与 CTA 位。</p>',
            True,
            True,
        ),
        "content_example": (
            "安装命令：单面板 → 平铺 MD",
            "命令只在非默认 Tab",
            "Atlas 800 离线命令：（仅在「离线安装」Tab，HTML 未输出）",
            "MD 预展开全部组合",
            "## 在线安装\\n…\\n## 离线安装（Atlas 800）\\nwget …",
            False,
            False,
        ),
        "frontend_example": (
            "DOM：隐藏面板 → SSR 全量",
            "display:none 删正文",
            '&lt;div role="tabpanel" hidden&gt;…安装命令…&lt;/div&gt;',
            "全量 panel 进首包",
            '&lt;section role="tabpanel" id="panel-offline"&gt;\\n  &lt;h3&gt;离线安装&lt;/h3&gt;\\n  &lt;pre&gt;wget …&lt;/pre&gt;\\n&lt;/section&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("全量面板", "禁 JS 抓取仍得全部 Tab 面板正文，不得只剩默认 panel。"),
            ("维度可辨", "抓取后 panel 标题含 Tab 维度名，能回答「离线安装命令在哪」。"),
            ("互斥探针", "与 CANN 下载页探针失败判据互斥——能给出完整命令原文。"),
        ],
    },
}


def merge_principles(slug: str, name: str, probe: dict) -> dict[str, Any]:
    base = probe_to_principles(slug, name, probe)
    override = PRINCIPLES_OVERRIDES.get(slug, {})
    for key, val in override.items():
        base[key] = val
    return base


def no_aff_skip_example(comp: str) -> tuple[str, str, str, str]:
    before = f"{comp} DOM 被送入知识库 pipeline\n→ 选项/placeholder/角标数字 产生噪声 chunk"
    after = f"pipeline: skip .o-{comp.lower().replace(' ', '-')} , [data-llm-exclude]\n→ 规格从正文/文档页收录"
    return ("控件态进库", before, "管道跳过", after)


def render_principles_body(data: dict[str, Any], slug: str) -> str:
    d = data
    de = d["design_example"]
    ce = d["content_example"]
    fe = d["frontend_example"]

    design_cmp = compare_block(de[0], de[1], de[2], de[3], de[4], before_is_frame=de[5], after_is_frame=de[6])
    content_cmp = compare_block(ce[0], ce[1], ce[2], ce[3], ce[4], before_is_frame=ce[5], after_is_frame=ce[6])
    frontend_cmp = compare_block(fe[0], fe[1], fe[2], fe[3], fe[4], before_is_frame=fe[5], after_is_frame=fe[6])

    accept_html = "\n".join(
        f'        <li><strong>{esc(t)}</strong>：{esc(d)}。</li>' for t, d in d["acceptance"]
    )

    return f"""    <div class="page-header">
      <h1>{esc(d["title"])}</h1>
      <p class="page-desc page-desc--split">
        <span class="page-desc-line">{d["one_liner"]}</span>
        <span class="page-desc-line">{esc(d["node"])} · 社区 UI · 对应 <a href="problems-{slug}.html">问题实测 · {esc(d["symptom"])}</a>。</span>
      </p>
    </div>

    <section class="section" id="design-ui">
      <h2>设计UI调整</h2>
      <h3 id="design-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["design"])}
      </ul>
      <h3 id="design-example">调整示例</h3>
{design_cmp}
    </section>

    <section class="section" id="content-adjust">
      <h2>文档内容调整</h2>
      <h3 id="content-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["content"])}
      </ul>
      <h3 id="content-example">调整示例</h3>
{content_cmp}
    </section>

    <section class="section" id="frontend-adjust">
      <h2>前端调整</h2>
      <h3 id="frontend-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["frontend"])}
      </ul>
      <h3 id="frontend-example">调整示例</h3>
{frontend_cmp}
    </section>

    <section class="section" id="acceptance">
      <h2>验收标准</h2>
      <ul class="accept-list">
{accept_html}
      </ul>
    </section>"""


def render_no_aff_body(data: dict[str, Any], slug: str, name: str) -> str:
    comp = name.split()[0] if name else slug
    skip = no_aff_skip_example(comp)
    skip_cmp = compare_block("管道：收录 → 跳过", skip[0], skip[1], skip[2], skip[3])

    skip_items = [("无独立改动，管道可跳过", "控件态/placeholder/角标等非知识正文，设计交付无需额外亲和标注")]

    return f"""    <div class="page-header">
      <h1>{esc(data["title"])}</h1>
      <p class="page-desc page-desc--split">
        <span class="page-desc-line">{data["one_liner"]}</span>
        <span class="page-desc-line">{esc(data["node"])} · 社区 UI · 对应 <a href="problems-{slug}.html">问题实测 · {esc(data["symptom"])}</a>。</span>
      </p>
    </div>

    <section class="section" id="design-ui">
      <h2>设计UI调整</h2>
      <h3 id="design-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(skip_items)}
      </ul>
      <h3 id="design-example">调整示例</h3>
{skip_cmp}
    </section>

    <section class="section" id="content-adjust">
      <h2>文档内容调整</h2>
      <h3 id="content-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(skip_items)}
      </ul>
      <h3 id="content-example">调整示例</h3>
{skip_cmp}
    </section>

    <section class="section" id="frontend-adjust">
      <h2>前端调整</h2>
      <h3 id="frontend-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
        <li><strong>管道跳过</strong>：构建时跳过 {esc(comp)} 相关 DOM，或根节点标记 <code>data-llm-exclude="true"</code>。</li>
      </ul>
      <h3 id="frontend-example">调整示例</h3>
{skip_cmp}
    </section>

    <section class="section" id="acceptance">
      <h2>验收标准</h2>
      <ul class="accept-list">
{li_items(data["acceptance"])}
      </ul>
    </section>"""


def render_page(slug: str, name: str, data: dict[str, Any]) -> str:
    body = render_no_aff_body(data, slug, name) if data.get("no_aff") else render_principles_body(data, slug)
    sidebar = render_sidebar(slug)
    phref = principles_href(slug)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(data["title"])} · 亲和原则 · 昇腾社区 AI 亲和原则</title>
<style>
{CSS}
</style>
</head>
<body data-module="principles" data-page="{slug}">
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="index.html">社区 <span>AI 亲和原则</span></a>
    <nav class="site-nav" aria-label="主导航">
      <a href="index.html">首页</a>
      <a href="mintlify.html">友商对照</a>
      <a href="reachability.html">社区诊断</a>
      <a href="community-ui.html" class="active">组件亲和</a>
    </nav>
  </div>
</div>

<div class="subnav" aria-label="组件详情二级导航">
  <div class="subnav-inner">
    <a class="subnav-back" href="community-ui.html">← 返回</a>
    <nav class="subnav-tabs">
      <a href="problems-{slug}.html">实测问题</a>
      <a href="{phref}" class="active">亲和原则</a>
    </nav>
  </div>
</div>

<div class="page-wrapper">
{sidebar}

  <main class="main-content">
{body}
  </main>

  <aside class="page-toc" id="page-toc" aria-label="本篇目录">
    <div class="page-toc-title">本篇目录</div>
    <nav class="page-toc-nav">
      <ul id="page-toc-list"></ul>
    </nav>
  </aside>
</div>
{TOC_SCRIPT}
</body>
</html>
"""


def patch_sidebar_in_file(path: Path, active: str | None) -> bool:
    text = path.read_text(encoding="utf-8")
    new_sidebar = render_sidebar(active)
    patched, n = re.subn(
        r'  <aside class="comp-sidebar" aria-label="组件列表">.*?</aside>',
        new_sidebar,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if n == 0:
        raise SystemExit(f"Could not find sidebar in {path}")
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        return True
    return False


def patch_principles_topbar(path: Path, slug: str) -> bool:
    text = path.read_text(encoding="utf-8")
    phref = principles_href(slug)
    new_tabs = (
        f'      <a href="problems-{slug}.html">实测问题</a>\n'
        f'      <a href="{phref}" class="active">亲和原则</a>'
    )
    patched, n = re.subn(
        r'      <a href="problems-[^"]+\.html">实测问题</a>\s*\n'
        r'      <a href="[^"]+" class="active">亲和原则</a>',
        new_tabs,
        text,
        count=1,
    )
    if n == 0:
        # try without active on principles
        patched, n = re.subn(
            r'      <a href="problems-[^"]+\.html">实测问题</a>\s*\n'
            r'      <a href="[^"]+">亲和原则</a>',
            new_tabs,
            text,
            count=1,
        )
    if n == 0:
        return False
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        return True
    return False


def patch_problems_topbar(path: Path, slug: str) -> bool:
    text = path.read_text(encoding="utf-8")
    phref = principles_href(slug)
    new_tabs = (
        f'      <a href="problems-{slug}.html" class="active">实测问题</a>\n'
        f'      <a href="{phref}">亲和原则</a>'
    )
    patched, n = re.subn(
        r'      <a href="problems-[^"]+\.html" class="active">实测问题</a>\s*\n'
        r'      <a href="[^"]+">亲和原则</a>',
        new_tabs,
        text,
        count=1,
    )
    if n == 0:
        return False
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        return True
    return False


def copy_to_report_serve() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    for path in DOCS.glob("problems-*.html"):
        shutil.copy2(path, REPORT / path.name)
    for path in DOCS.glob("principles-*.html"):
        shutil.copy2(path, REPORT / path.name)
    aff = DOCS / "principles-affinity.html"
    if aff.exists():
        shutil.copy2(aff, REPORT / aff.name)


def main() -> None:
    generated: list[str] = []
    skipped_body: list[str] = []

    for _, slug, name in all_components():
        if slug in SKIP_BODY:
            out = principles_out_path(slug)
            skipped_body.append(out.name)
            if out.exists():
                patch_sidebar_in_file(out, slug)
                patch_principles_topbar(out, slug)
            continue

        probe = PROBES.get(slug)
        if not probe:
            raise SystemExit(f"Missing probe data for {slug}")

        out = principles_out_path(slug)
        data = merge_principles(slug, name, probe)

        html = render_page(slug, name, data)
        out.write_text(html, encoding="utf-8")
        generated.append(out.name)

    # refresh sidebars + topbars on all principles pages (including skipped body)
    sidebars_patched = 0
    topbars_patched = 0
    for _, slug, _ in all_components():
        path = principles_out_path(slug)
        if path.exists():
            if patch_sidebar_in_file(path, slug):
                sidebars_patched += 1
            if patch_principles_topbar(path, slug):
                topbars_patched += 1

    problems_topbars = 0
    for _, slug, _ in all_components():
        ppath = DOCS / f"problems-{slug}.html"
        if ppath.exists() and patch_problems_topbar(ppath, slug):
            problems_topbars += 1

    copy_to_report_serve()

    all_principles = sorted(
        set(generated) | {OCAROUSEL_CANONICAL.name} | {"principles-affinity.html"}
    )
    print(f"Generated: {len(generated)}")
    for f in sorted(generated):
        print(f"  {f}")
    if skipped_body:
        print(f"Skipped body (preserved): {', '.join(skipped_body)}")
    print(f"Sidebars patched: {sidebars_patched}")
    print(f"Principles topbars patched: {topbars_patched}")
    print(f"Problems topbars patched: {problems_topbars}")
    print(f"Total principles files: {len(list(DOCS.glob('principles-*.html'))) + (1 if OCAROUSEL_CANONICAL.exists() else 0)}")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
