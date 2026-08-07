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

COMP_SHOT_SPECIAL = {
    "ofooternav": "o-footer-nav.png",
    "odatetable": "o-date-table.png",
}


def comp_shot_file(slug: str) -> str | None:
    if slug in COMP_SHOT_SPECIAL:
        shot = COMP_SHOT_SPECIAL[slug]
    elif slug.startswith("o") and len(slug) > 1:
        shot = f"o-{slug[1:]}.png"
    else:
        shot = f"{slug}.png"
    if (DOCS / "design-system" / "assets" / shot).exists():
        return shot
    return None


def render_comp_link(slug: str, name: str) -> str:
    shot = comp_shot_file(slug)
    if not shot:
        return ""
    return (
        f'<button type="button" class="comp-link" data-name="{esc(name)}" '
        f'data-shots="{esc(shot)}">{esc(name)}</button>'
    )


def render_page_header(title: str, one_liner: str, slug: str, name: str, data: dict[str, Any]) -> str:
    link = render_comp_link(slug, name)
    if data.get("hide_page_h1"):
        top = f'      <div class="page-header-top">\n        {link}\n      </div>\n' if link else ""
    else:
        right = f"\n        {link}" if link else ""
        top = (
            f'      <div class="page-header-top">\n'
            f'        <h1>{esc(title)}</h1>{right}\n'
            f'      </div>\n'
        )
    return f"""    <div class="page-header">
{top}      <p class="page-desc page-desc--split">
        <span class="page-desc-line">{one_liner}</span>
{principles_meta_line(data, slug)}
      </p>
    </div>"""


SHOT_MODAL_HTML = """
<div class="modal" id="shot-modal" role="dialog" aria-modal="true" aria-labelledby="shot-modal-title" hidden>
  <div class="modal-panel">
    <div class="modal-head">
      <h2 class="shot-modal-title" id="shot-modal-title">组件截图</h2>
      <button type="button" class="modal-close" id="shot-modal-close">关闭</button>
    </div>
    <div class="modal-body">
      <div class="modal-shots" id="modal-shots"></div>
    </div>
  </div>
</div>
<script>
(function () {
  var modal = document.getElementById('shot-modal');
  var titleEl = document.getElementById('shot-modal-title');
  var shotsEl = document.getElementById('modal-shots');
  var closeBtn = document.getElementById('shot-modal-close');
  if (!modal || !titleEl || !shotsEl || !closeBtn) return;
  var ASSET = 'design-system/assets/';
  function openModal(name, shotsRaw) {
    titleEl.textContent = name;
    shotsEl.innerHTML = '';
    String(shotsRaw || '').split(',').filter(Boolean).forEach(function (item) {
      var parts = item.split('|');
      var file = parts[0];
      var caption = parts[1];
      var wrap = document.createElement('div');
      if (caption) {
        var cap = document.createElement('p');
        cap.className = 'modal-caption';
        cap.textContent = caption;
        wrap.appendChild(cap);
      }
      var box = document.createElement('div');
      box.className = 'modal-shot';
      var img = document.createElement('img');
      img.src = ASSET + file;
      img.alt = name + (caption ? ' · ' + caption : '');
      box.appendChild(img);
      wrap.appendChild(box);
      shotsEl.appendChild(wrap);
    });
    modal.hidden = false;
    modal.classList.add('open');
    document.body.classList.add('modal-open');
    closeBtn.focus();
  }
  function closeModal() {
    modal.classList.remove('open');
    modal.hidden = true;
    document.body.classList.remove('modal-open');
    shotsEl.innerHTML = '';
  }
  document.querySelectorAll('.comp-link').forEach(function (btn) {
    btn.addEventListener('click', function () {
      openModal(btn.getAttribute('data-name'), btn.getAttribute('data-shots'));
    });
  });
  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
  });
})();
</script>
"""

render_nav_item = _probe_mod.render_nav_item

PRINCIPLES_CSS_EXTRA = """
  .page-header-top {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; margin-bottom: 16px;
  }
  .page-header-top h1 {
    margin: 0;
    font-size: 32px; font-weight: 800; line-height: 48px;
    letter-spacing: -0.02em; color: var(--text);
    flex: 1; min-width: 0;
  }
  .page-header .page-desc { margin-bottom: 0; }
  button.comp-link {
    appearance: none; border: 0; background: transparent;
    padding: 0; margin: 0; flex-shrink: 0;
    font: inherit; font-size: 14px; font-weight: 600;
    color: var(--accent); cursor: pointer; text-align: right;
    white-space: nowrap;
  }
  button.comp-link:hover { text-decoration: underline; }
  #shot-modal.modal {
    display: none; position: fixed; inset: 0; z-index: 100;
    background: rgba(25, 25, 25, 0.45);
    align-items: center; justify-content: center; padding: 24px;
  }
  #shot-modal.modal.open { display: flex; }
  #shot-modal .modal-panel {
    width: min(920px, 100%); max-height: min(88vh, 900px);
    background: var(--panel); border-radius: 16px;
    border: 1px solid var(--line);
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
    display: flex; flex-direction: column; overflow: hidden;
  }
  #shot-modal .modal-head {
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; padding: 16px 20px; border-bottom: 1px solid var(--line);
    flex-shrink: 0;
  }
  #shot-modal .shot-modal-title {
    margin: 0; font-size: 18px; font-weight: 650; line-height: 28px;
    color: var(--text);
  }
  #shot-modal .modal-close {
    appearance: none; border: 1px solid var(--line); background: var(--panel2);
    color: var(--text); border-radius: 8px; padding: 6px 12px;
    font-size: 13px; font-weight: 500; cursor: pointer;
  }
  #shot-modal .modal-close:hover { color: var(--accent); border-color: var(--accent); }
  #shot-modal .modal-body {
    padding: 20px; overflow: auto; background: var(--panel2);
  }
  #shot-modal .modal-shots {
    display: flex; flex-direction: column; gap: 16px;
  }
  #shot-modal .modal-shot {
    background: var(--panel); border: 1px solid var(--line);
    border-radius: 12px; padding: 16px;
    display: flex; align-items: center; justify-content: center;
  }
  #shot-modal .modal-shot img {
    max-width: 100%; height: auto; display: block;
  }
  #shot-modal .modal-caption {
    margin: 0 0 8px; font-size: 13px; color: var(--muted); font-weight: 500;
  }

  .role-split-card {
    margin: 0 0 36px;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 0;
  }
  .role-split-card .rsc-title {
    margin: 0 0 14px;
    font-size: 14px; font-weight: 700; line-height: 22px;
    color: var(--text);
  }
  .role-split-grid {
    display: grid; grid-template-columns: 1fr; gap: 14px;
  }
  .role-split-item {
    border-radius: 8px; padding: 14px 16px;
    border: 1px solid var(--line);
  }
  .role-split-item h4 {
    margin: 0 0 6px;
    display: flex; align-items: center; flex-wrap: wrap; gap: 8px;
    font-size: 13.5px; font-weight: 700; line-height: 20px;
    color: var(--text);
  }
  .rsc-verdict {
    font-size: 11.5px; font-weight: 700; line-height: 18px;
    padding: 1px 8px; border-radius: 999px;
    border: 1px solid transparent;
  }
  .rsc-verdict--keep {
    color: var(--accent); background: rgba(20, 118, 255, 0.08); border-color: rgba(20, 118, 255, 0.28);
  }
  .rsc-verdict--strip {
    color: var(--muted); background: rgba(0, 0, 0, 0.05); border-color: var(--line);
  }
  .role-split-item p {
    margin: 0;
    font-size: 13px; line-height: 21px; color: var(--muted);
  }
  .role-split-item code {
    font-family: var(--mono, ui-monospace, SFMono-Regular, Menlo, monospace);
    font-size: 12px;
    padding: 1px 5px; border-radius: 4px;
    background: rgba(0,0,0,0.05); color: var(--text);
  }
  .role-split-item--keep {
    background: rgba(20, 118, 255, 0.06); border-color: rgba(20, 118, 255, 0.25);
  }
  .role-split-item--keep h4 { color: var(--accent); }
  .role-split-item--strip {
    background: rgba(0, 0, 0, 0.03); border-color: var(--line);
  }
  .role-split-item--strip h4 { color: var(--muted); }

  .scene-judge-item {
    margin: 0 0 16px;
    font-size: var(--body-size); line-height: var(--body-lh);
    color: var(--text);
  }
  .scene-judge-item:last-child { margin-bottom: 0; }
  .scene-judge-head {
    margin: 0 0 4px;
    display: flex; align-items: center; flex-wrap: wrap; gap: 8px;
  }
  .scene-judge-head strong { font-weight: 700; color: var(--text); }
  .scene-judge-body { margin: 0; color: var(--text); }

  .principle-suggestions {
    margin: 0; padding-left: 20px;
    color: var(--muted); font-size: 14px; line-height: 22px;
  }
  .principle-suggestions li { margin-bottom: 8px; }
  .principle-lead {
    margin: 0 0 12px; font-size: 14px; line-height: 22px; color: var(--text);
  }
  .principle-subhead {
    margin: 0 0 8px; font-size: 14px; font-weight: 700; line-height: 22px; color: var(--text);
  }
  .principle-suggestions li:last-child { margin-bottom: 0; }
  .principle-suggestions li strong { color: var(--text); font-weight: 600; }

  .principle-example {
    margin-top: 16px;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: 0;
  }
  .principle-example > h4 {
    margin: 0 0 12px;
    font-size: 14px; font-weight: 700; line-height: 22px;
    color: var(--text);
  }
  .principle-example + .principle-example {
    margin-top: 28px;
    padding-top: 20px;
    border-top: 1px dashed var(--line);
  }

  .compare-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin: 0;
  }
  .compare-grid--stack { grid-template-columns: 1fr; gap: 16px; }
  .compare-grid--cols { grid-template-columns: 1fr 1fr; gap: 16px; align-items: stretch; }
  .compare-grid--cols .compare-side { display: flex; flex-direction: column; gap: 8px; min-width: 0; height: 100%; }
  .compare-grid--cols .compare-col { flex: 1; display: flex; flex-direction: column; }
  .compare-grid--cols .compare-col .render-frame,
  .compare-grid--cols .compare-col .arch-diagram { flex: 1; }
  @media (max-width: 720px) {
    .compare-grid--cols { grid-template-columns: 1fr; }
  }
  .compare-grid--stack .compare-label--human {
    margin-top: 8px;
    padding-top: 20px;
    border-top: 1px dashed var(--line);
  }
  .compare-grid--no-mid-divider .compare-label--human {
    margin-top: 8px;
    padding-top: 0;
    border-top: none;
  }
  .compare-grid--stack .compare-col.human + .compare-label.compare-label--human {
    margin-top: 4px;
  }
  .section .principle-example .compare-grid h4.compare-label {
    margin: 0;
    font-size: 13px;
    font-weight: 700;
    line-height: 20px;
  }
  .compare-label {
    margin: 0;
    font-size: 13px; font-weight: 700; line-height: 20px;
  }
  .compare-label--machine { color: var(--danger); }
  .compare-label--human { color: var(--success); }
  .cmp-mark { font-weight: 800; }
  .cmp-mark--x { color: var(--danger); }
  .cmp-mark--v { color: var(--success); }
  .compare-col {
    border-radius: 8px;
    padding: 18px 20px;
    font-size: 13.5px;
    line-height: 22px;
  }
  .compare-col.machine {
    background: var(--danger-bg);
    border: 1px solid var(--danger-border);
  }
  .compare-col.human {
    background: var(--success-bg);
    border: 1px solid var(--success-border);
  }
  .compare-col .arch-diagram { margin-top: 0; }

  .render-frame {
    background: var(--panel);
    border: 1px solid var(--card-border);
    border-radius: 6px;
    padding: 14px 16px;
    font-size: 13px;
    line-height: 1.55;
    color: var(--text);
    min-height: 48px;
  }
  .render-frame .rf-muted {
    margin: 8px 0 0;
    font-size: 12px;
    line-height: 18px;
    color: var(--muted);
  }
  .render-frame .rf-caption {
    margin: 10px 0 0;
    font-size: 12px;
    line-height: 18px;
    color: var(--muted);
  }
  .render-frame .rf-caption strong { color: var(--text); font-weight: 600; }
  .compare-col .rf-frame-caption {
    margin: 16px 0 0;
    font-size: 12.5px;
    line-height: 19px;
    color: var(--muted);
  }
  .compare-col .rf-frame-caption strong { color: var(--text); font-weight: 600; }
  .render-frame .rf-sidebar-title {
    margin: 0 0 8px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text);
  }
  .render-frame .rf-sidebar--bad {
    border: 1px dashed var(--danger-border);
    border-radius: 6px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.6);
    color: var(--muted);
    font-size: 12px;
  }
  .render-frame .rf-nav-links {
    margin: 0;
    padding-left: 18px;
    color: var(--text);
    font-size: 12px;
    line-height: 1.6;
  }
  .render-frame .rf-nav-links ul {
    margin: 4px 0 0;
    padding-left: 16px;
  }
  .render-frame .rf-nav-links a { color: var(--accent); text-decoration: none; }
  .render-frame .rf-searchbox {
    display: flex; align-items: center; gap: 8px;
    border: 1px solid var(--line); border-radius: 999px;
    padding: 7px 14px; background: #fff; color: var(--muted);
    font-size: 12.5px;
  }
  .render-frame .rf-searchbox .rf-sb-icon { color: var(--accent); font-weight: 700; }
  .render-frame .rf-searchbox .rf-sb-note { margin-left: auto; font-size: 11px; color: var(--muted); }
  .render-frame .rf-select {
    display: inline-flex; align-items: center; gap: 10px; min-width: 160px;
    border: 1px solid var(--line); border-radius: 6px;
    padding: 7px 12px; background: #fff; color: var(--text);
    font-size: 12.5px;
  }
  .render-frame .rf-select .rf-caret { margin-left: auto; color: var(--muted); }
  .render-frame table.rf-spec {
    margin: 10px 0 0; border-collapse: collapse; font-size: 12px;
  }
  .render-frame table.rf-spec th,
  .render-frame table.rf-spec td {
    border: 1px solid var(--line); padding: 4px 10px; text-align: left; color: var(--text);
  }
  .render-frame table.rf-spec th { background: #f6f8fa; font-weight: 600; }
  .render-frame pre.rf-code {
    margin: 0;
    padding: 10px 12px;
    background: #f6f8fa;
    border: 1px solid var(--line);
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--text);
  }

  .arch-diagram {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 12px;
    line-height: 1.7;
    background: rgba(255, 255, 255, 0.7);
    color: var(--text);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    padding: 14px 16px;
  }

  .accept-list {
    margin: 0;
    padding-left: 20px;
    color: var(--muted);
    font-size: 14px;
    line-height: 22px;
  }
  .accept-list li { margin-bottom: 8px; }
  .accept-list li:last-child { margin-bottom: 0; }
  .accept-list strong { color: var(--text); font-weight: 600; }

  .principles-framework {
    margin: 0 0 40px;
    padding: 14px 18px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    font-size: 14px;
    line-height: 22px;
    color: var(--muted);
  }
  .main-content > .principles-framework {
    width: 100%; max-width: var(--content-max); margin-inline: 0;
    padding-left: 0; padding-right: 0; box-sizing: border-box;
  }
  .principles-framework strong { color: var(--text); font-weight: 600; }

  .principle-none {
    margin: 0;
    font-size: 14px;
    line-height: 22px;
    color: var(--muted);
  }

  @media (max-width: 900px) {
    .compare-grid:not(.compare-grid--stack) { grid-template-columns: 1fr; }
  }
"""

CSS = _probe_mod.CSS + PRINCIPLES_CSS_EXTRA

PRINCIPLES_FRAMEWORK = (
    "本页按<strong>三交付面</strong>拆分改造信息与工作任务："
    "<strong>设计 UI</strong>（稿面/组件清单）· "
    "<strong>文档内容</strong>（正文/MD/llms）· "
    "<strong>前端</strong>（HTML 首包/管道）。"
    "以下三节各列该面职责内的建议与示例，请勿混写。"
)

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
    "onavigation", "ofooternav", "obutton", "olink", "odropdown", "otrees", "osearch",
}
HIDDEN_SLUGS = {"otab", "odialog", "opopover", "ocarousel"}
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
    before_caption: str | None = None,
    after_caption: str | None = None,
    side_by_side: bool = False,
    before_prefix: str = "错误示范",
    after_prefix: str = "推荐做法",
    before_mark: bool = True,
    after_mark: bool = True,
    after_sections: list[tuple[str, str]] | None = None,
    example_num: int = 1,
) -> str:
    def fmt(body: str) -> str:
        # Some example bodies are authored with pre-escaped HTML entities
        # (e.g. "&lt;div&gt;"); escaping again would double-encode them.
        # Only escape bodies that still contain raw angle brackets.
        if "&lt;" in body or "&gt;" in body:
            return body
        return esc(body)

    def label_head(kind: str, prefix: str, text: str, *, mark: bool) -> str:
        mark_html = ""
        if mark:
            mark_cls = "cmp-mark--x" if kind == "machine" else "cmp-mark--v"
            mark_char = "✗" if kind == "machine" else "✓"
            mark_html = f'<span class="cmp-mark {mark_cls}">{mark_char}</span> '
        return f'<h4 class="compare-label compare-label--{kind}">{mark_html}{esc(prefix)} · {esc(text)}</h4>'

    def col(kind: str, is_frame: bool, body: str, caption: str | None) -> str:
        inner = f'<div class="render-frame">{body}</div>' if is_frame else f'<pre class="arch-diagram">{fmt(body)}</pre>'
        cap = f'\n            <p class="rf-frame-caption">{caption}</p>' if caption else ""
        return f'          <div class="compare-col {kind}">\n            {inner}{cap}\n          </div>'

    def after_stack(*, is_frame: bool, caption: str | None) -> str:
        sections = after_sections or [(after_label, after_body)]
        parts: list[str] = []
        for i, section in enumerate(sections):
            label, body = section[0], section[1]
            cap = section[2] if len(section) > 2 else (caption if i == 0 else None)
            parts.append(
                f'          {label_head("human", after_prefix, label, mark=after_mark)}\n'
                f'{col("human", is_frame, body, cap)}'
            )
        return "\n".join(parts)

    if side_by_side:
        return f"""      <div class="principle-example">
        <h4>示例{example_num}. {esc(example_title)}</h4>
        <div class="compare-grid compare-grid--cols">
          <div class="compare-side">
            {label_head("machine", before_prefix, before_label, mark=before_mark)}
{col("machine", before_is_frame, before_body, before_caption)}
          </div>
          <div class="compare-side">
            {label_head("human", after_prefix, after_label, mark=after_mark)}
{col("human", after_is_frame, after_body, after_caption)}
          </div>
        </div>
      </div>"""

    return f"""      <div class="principle-example">
        <h4>示例{example_num}. {esc(example_title)}</h4>
        <div class="compare-grid compare-grid--stack compare-grid--no-mid-divider">
          {label_head("machine", before_prefix, before_label, mark=before_mark)}
{col("machine", before_is_frame, before_body, before_caption)}
{after_stack(is_frame=after_is_frame, caption=after_caption)}
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
            lines.append(render_nav_item(name, href, slug, active=active == slug))
        lines.append("      </ul>")
    lines.extend(["    </nav>", "  </aside>"])
    return "\n".join(lines)


def principle_title(probe: dict, name: str, slug: str) -> str:
    if probe.get("no_aff"):
        comp = name.split()[0] if name else slug
        return f"{comp} · 无需亲和改造"
    overrides = {
        "omenu": "侧栏菜单目录可发现",
        "otab": "标签页面板首包可抓全",
        "obreadcrumb": "面包屑路径可链回溯",
        "oanchor": "锚点目录与正文 id 对齐",
        "opagination": "列表底部分页深页可爬",
        "ostep": "流程步骤说明可逐步抓取",
        "onavigation": "顶栏主导航链接可发现",
        "ofooternav": "页脚多列链接可发现",
        "obutton": "跳转型按钮链接可发现",
        "olink": "正文导流链接须可跟",
        "odropdown": "下拉菜单子链须可抓",
        "otrees": "文档树节点 SSR 可链",
        "osearch": "可搜索 URL 全进 sitemap",
        "oselect": "选型选项文本可证伪",
        "otoggle": "Toggle 版本矩阵须进首包",
        "orate": "评分数字与 CTA 分流",
        "ocascader": "级联路径选项可读",
        "otag": "标签语义与装饰分流",
        "odialog": "对话框关键说明双写",
        "ocard": "卡片三要素文本化",
        "odatetable": "表格语义化可问答",
        "opopover": "气泡说明正文 duplicate",
        "ocarousel": "轮播帧语义隔离",
    }
    return overrides.get(slug, probe["title_short"])


def principle_one_liner(probe: dict, slug: str) -> str:
    if probe.get("no_aff"):
        return (
            f"<strong>{probe['term']}</strong>——{probe['definition']}。"
            "本组件<strong>无需亲和改造</strong>；规格说明应写在旁侧正文/文档页，管道可跳过纯控件 DOM。"
        )
    fixes = {
        "omenu": "侧栏菜单是文档的<strong>发现层</strong>：目录树须首包 SSR、每项为真实 <code>a[href]</code>，静态抓取即可列全并跟链到各章节，勿只靠前端注入。",
        "otab": "内容型标签页的各面板须<strong>首包 SSR 全量输出</strong>；可用 <code>display:none</code> 隐藏，但静态抓取仍须读到全部页签正文，禁止点击后才注入。",
        "obreadcrumb": "文档页顶栏面包屑须把<strong>每一级祖先页写成可点的链接</strong>（a[href]），当前页用纯文本即可；首包 HTML 就要输出完整路径，文案与 sitemap / 手册目录保持一致。",
        "oanchor": "长文页右侧「本篇目录」须把<strong>每一级章节写成 #hash 可点链接</strong>（a[href]），与正文 heading/section id 对齐；首包 HTML 就要输出完整目录。左侧侧栏归菜单、页底 Related 归链接，勿与本组件混测。",
        "opagination": "表格或卡片列表<strong>下方的分页</strong>若翻出公开知识深页，页码须为带 query 的真实 <code>a[href]</code>（如 <code>?page=2</code>）；禁纯 button/onClick。后台表格分页见下方场景判断。",
        "ostep": "公开流程/逐步说明块的<strong>标题与说明须为可见文本</strong>进首包；状态用文字或 aria 标注；配图内字须旁注或改文本交付。后台向导见下方场景判断。",
        "onavigation": "顶栏<strong>站点入口</strong>（文档 / 开发者 / 下载等）须为可跟 <code>a[href]</code>，下拉子项亦进首包；搜索 / 换肤 / 语言等纯操作控件见下方场景判断。",
        "ofooternav": "社区首页页脚须把<strong>五列导航与法律声明 / 联系我们等写成可跟链接</strong>（a[href]），列名稳定；并同步进 llms/sitemap，作为顶栏之外的第二发现层。",
        "obutton": "社区首页首屏 CTA（立即查看 / 了解更多等）须用<strong>可抓 a[href]</strong>；纯提交/关闭类 button 管道宜剥离（对标 Mintlify hero、NVIDIA build 列表 CTA）。",
        "olink": "正文与导航链接须带<strong>真实 a[href]</strong>；锚文本宜自描述（禁仅「软件介绍↗」）；禁 JSON/onclick/span 伪链（昇腾训练旅程矩阵须 SSR 链化）。",
        "odropdown": "下拉菜单子项须在<strong>首包 HTML 可读</strong>（a[href]+可见文案）；禁仅触发器、portal 延迟挂或外部 JSON 菜单（昇腾「更多产品」/ Mintlify Products / NVIDIA Resources 均须 SSR 链化）。",
        "otrees": "文档树节点须<strong>链接+标题进 HTML</strong>；懒加载子树须 SSR 当前分支或提供 MD 平行轨。",
        "osearch": "搜索框本身<strong>不做亲和改造</strong>（纯交互，入库剥离）；真正的硬要求是<strong>所有可搜索的 URL 都要进 sitemap / llms</strong>，让 Agent 不靠搜索也能发现全部文档。",
        "oselect": "若选项映射文档/版本，<strong>选项文本与落地页须可证伪</strong>；纯表单 select 管道可跳过。",
        "otoggle": "下载/版本页 Toggle 若映射 OS、架构、安装方式等选型，<strong>完整 option 矩阵须 SSR 或写进首包 JSON</strong>（对标 NVIDIA CUDA data-react-props）；?ids= 编码态不能替代可读矩阵；纯 UI 筛选标注 exclude。",
        "orate": "评分数字若 SSR 可作社会证明；<strong>「我要评分」等操作 CTA 宜剥离</strong>，勿与官方认证混淆。",
        "ocascader": "级联若代表内容路径，<strong>各级 option 文本须可读</strong>；纯地址表单不必入库。",
        "otag": "版本/状态类标签须<strong>可读文本进 HTML</strong>；装饰性营销 tag 管道宜剥离。",
        "odialog": "含安装步骤等<strong>关键说明须在正文 duplicate 或 dialog DOM 进首包</strong>；纯确认框可忽略。",
        "ocard": "导流卡须静态输出<strong>o-card-title + o-card-detail + a[href]</strong> 三要素；首页资讯/活动列表与卡内嵌套列表须 SSR，禁 o-card-content 空壳注入；封面补 alt，禁整卡 onclick。",
        "odatetable": "规格参数须以<strong>真实 table/th/td</strong> 写进网页源码（表头 + 单元格文本可逐行抓取）；禁截图表、div 伪表与空 td；文档页宜备 Markdown 平行表。",
        "opopover": "字段规格<strong>勿只放悬停气泡</strong>；正文须 duplicate 或 popover 内容 SSR 进首包。",
        "ocarousel": "首页/运营轮播多帧虽已写进网页源码，但<strong>运营/活动/招募口号与产品规格混层，须默认 exclude 出 llms 与知识库</strong>；人读发现归轮播，规格事实归文档。白名单产品入口帧须输出「标题 + 可引用摘要 + a[href]」，并完成图意转写；跳转型 CTA 禁 button 伪链。",
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
        "sample_url": probe.get("sample_url"),
        "sample_label": probe.get("sample_label"),
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
    "omenu": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "跳转型侧栏（换 URL 到独立页面）",
                    "要做亲和",
                    "点击侧栏项切换 URL，跳转至独立页面（如：文档手册目录）。<br>它是爬虫发现深层页面的关键入口：每项须为真实 <code>a[href]</code> 链接 + 自描述锚文本/标题，首屏 SSR 全量输出，禁用 JS 仍完整可见并可跟链。<br>对应页面：<a href=\"https://www.hiascend.com/document/detail/zh/AscendFAQ/ProduTech/productform/hardwaredesc_0001.html\" target=\"_blank\" rel=\"noopener\">Ascend FAQ 概览</a>",
                ),
                (
                    "keep",
                    "同页切换内容块（类 Tab）",
                    "要做亲和",
                    "点击侧栏不刷新 URL，仅切换右侧内容（竖向 Tab）。<br>所有内容块的文字须写入首包 HTML（SSR 全量输出），可 <code>display:none</code> 视觉隐藏、但不能靠 JS 注入才出现（详见 <a href=\"principles-otab.html\">标签页 otab</a>）。",
                ),
                (
                    "strip",
                    "后台 / 个人中心管理菜单",
                    "不做亲和 · 入库剥离",
                    "如控制台、个人中心左侧的功能操作菜单。它指向登录后的应用操作、非公开知识，入库管道宜标 <code>data-llm-exclude</code> 或直接剥离，别当可引用文档。",
                ),
            ],
        },
        "design_example_side_by_side": True,
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design": [
            (
                "跳转型侧栏文案须自描述",
                "明确文档 / 对象名（如「CANN 软件安装指南」），避免「简介 / 安装 / 更多」等泛词",
            ),
            (
                "锚文本即标题",
                "每项为真实 a[href]，锚文本即可读的文档标题本身",
            ),
        ],
        "design_example": (
            "侧栏菜单：泛词 → 自描述标题",
            "泛词菜单项",
            '<p class="rf-sidebar-title">手册目录</p>\n'
            '<ul class="rf-nav-links">\n'
            '  <li><a href="#">简介</a></li>\n'
            '  <li><a href="#">安装</a></li>\n'
            '  <li><a href="#">更多 ›</a></li>\n'
            '</ul>',
            "自描述标题",
            '<p class="rf-sidebar-title">手册目录</p>\n'
            '<ul class="rf-nav-links">\n'
            '  <li><a href="#">CANN 简介</a></li>\n'
            '  <li><a href="#">CANN 软件安装指南</a></li>\n'
            '  <li><a href="#">CANN 全部文档索引</a></li>\n'
            '</ul>',
            True,
            True,
            "「简介 / 安装 / 更多」脱离上下文说不清是哪个产品的哪篇文档，Agent 拿到锚文本也判断不了去向。",
            "<strong>要点：</strong>每项锚文本含产品 + 文档名，脱离侧栏层级也自解释；底层是真实 a[href]。",
        ),
        "content": [
            ("统一命名", "确保侧栏目录、sitemap 与手册 MD 目录中的文档标题对齐。同一文档在各处使用相同名称，避免 Agent 因名称差异而将同一页面识别为两个独立入口"),
            ("备选目录", "在 Markdown / llms.txt 中提供手册章节清单（标题 + 链接），作为侧栏的平行可达入口；即使侧栏未被抓取，也可枚举全部页面"),
            ("过渡补位", "侧栏 HTML 未达标前，用 llms.txt 临时补充关键深链；达标后以 HTML 为准，无需重复维护"),
        ],
        "content_example": (
            "手册目录 → MD / llms 平行清单",
            "只有前端注入的侧栏",
            "手册目录仅由 OMenu 前端渲染；\n没有 Markdown / llms 版章节清单，\n静态抓取时无法枚举本手册有哪些页。",
            "MD 平行目录清单",
            "## CANN 手册目录\n- [CANN 简介](/document/zh/CANN/overview.html)\n- [CANN 软件安装指南](/document/zh/CANN/install.html)\n- [CANN 全部文档索引](/document/zh/CANN/index.html)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行目录清单",
                "## CANN 手册目录\n- [CANN 简介](/document/zh/CANN/overview.html)\n- [CANN 软件安装指南](/document/zh/CANN/install.html)\n- [CANN 全部文档索引](/document/zh/CANN/index.html)",
            ),
            (
                "llms 临时补关键深链",
                "# llms.txt（过渡）\n- [CANN 软件安装指南](/document/zh/CANN/install.html)\n- [Ascend FAQ 安装部署](/document/zh/AscendFAQ/install.html)",
                "侧栏 SSR 达标后以 HTML 为准，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "侧栏（nav/aside）须在首包 HTML 中全量输出当前手册的 a[href] 目录树（对标：Mintlify 侧栏 73 链、NVIDIA 文档导航 700+ 链），确保不执行 JS 即可抓取完整章节并跟进链接。",
        "frontend": [
            ("禁用 NUXT 式 JSON 注入", "目录节点不得仅存于 __NUXT_DATA__ 等 JSON 中（Ascend FAQ 即为此类失败案例），否则静态 HTML 无可跟链的目录树"),
            ("禁用懒加载吞节点", "长目录不得使用虚拟滚动或按需渲染只输出可视区少量节点，全量 a[href] 须在首包 HTML 中一次输出"),
            ("节点须为真实链接", "每个目录项须为带 href 的 a 标签 + 可见文本，禁止用 span/div 模拟点击；须包含「安装部署」等分支章节及可跟进深层链接"),
        ],
        "frontend_example": (
            "Ascend FAQ 侧栏 html",
            "TOC 仅注入 __NUXT_DATA__，未输出真实 <a[href]>，导致静态抓取无目录可跟",
            '&lt;script id="__NUXT_DATA__"&gt;{"label":"安装部署",…}&lt;/script&gt;\n&lt;!-- 静态 HTML 无 aside/nav 内可跟链 a[href] 树 --&gt;',
            "SSR 输出全量 nav 链",
            '&lt;aside class="doc-sidebar"&gt;\n  &lt;nav aria-label="手册目录"&gt;\n    &lt;a href="/document/detail/zh/AscendFAQ/product.html"&gt;产品与技术常见问题&lt;/a&gt;\n    &lt;a href="/document/detail/zh/AscendFAQ/install.html"&gt;安装部署&lt;/a&gt;\n    &lt;a href="/document/detail/zh/AscendFAQ/install/step1.html"&gt;第一篇官方文档&lt;/a&gt;\n  &lt;/nav&gt;\n&lt;/aside&gt;',
            False,
            False,
            "目录数据只在 __NUXT_DATA__ 里，静态 HTML 的 aside/nav 内没有可跟链的 a，静态抓取拿不到章节结构。",
            "章节层级直接写成 nav 内的 a[href]，静态抓取即可列全并跟链到具体文档。",
        ),
        "acceptance": [
            ("静态可达", "静态抓取 Ascend FAQ（不执行 JS）后，侧栏仍含可跟链目录节点，能回答「安装部署下有哪些章节」等问句"),
            ("html 可抓全", "侧栏 html 可抓取达到友商文档页水准（Mintlify/NVIDIA 级：首包 70+ 条 nav 链）"),
            ("可证伪", "对「安装部署下第一篇官方文档链接」须能引用具体 href，与「问题实测」页的失败判据对应"),
        ],
    },
    "otab": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "内容型 Tab",
                    "要做亲和",
                    "每个页签面板承载独立内容（说明 / 列表 / 步骤 / 规格），切换页签即切换知识块。所有面板须 SSR 全量输出至首包 HTML，可用 <code>display:none</code> 隐藏，但禁止点击后 JS 动态注入。<br>对应页面：<a href=\"https://www.hiascend.com/developer/download\" target=\"_blank\" rel=\"noopener\">CANN 软件下载</a>",
                ),
                (
                    "strip",
                    "纯交互 / 装饰型 Tab",
                    "不做亲和 · 入库剥离",
                    "只换样式、布局或空壳，不承载可引用正文。入库管道宜标 <code>data-llm-exclude</code> 或剥离，别当知识正文。",
                ),
            ],
        },
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_none": True,
        "content": [
            (
                "面板内容须有平行持久版本",
                "每个页签的核心要点须写入 Markdown / 独立文档，不得仅存在于切换后才出现的面板中",
            ),
            (
                "MD 按页签结构平铺",
                "一级标题对应页签名，下级展开条目。例：资源下载中心 → 昇腾资源 / 三方资源 → 各软件要点与文档链",
            ),
        ],
        "frontend_lead": "内容型 Tab 的页签名与各面板正文须写入首包 HTML；静态抓取（不执行 JS）仍可读全部页签名称与面板内容。",
        "frontend": [
            (
                "页签名进首包",
                "每个页签名称写进源码（以下载中心为例：昇腾资源 / 三方资源），勿只留空的 tab nav；浏览器可见但源码读不到的页签名不算达标",
            ),
            (
                "未激活面板也进首包",
                "各 tabpanel 全量 SSR；可用 hidden / display:none 做视觉隐藏，禁止点击页签后才 JS 注入正文",
            ),
            (
                "面板内知识节点可抓",
                "卡片标题、短述、文档链等可见文本写进对应 pane（如昇腾资源下的 CANN / MindSDK）；未激活的三方资源 pane 同样须预先输出",
            ),
        ],
        "content_example": (
            "内容型 Tab：面板知识进 MD 平行轨",
            "要点只在切换后的面板里",
            "页面默认只看到「昇腾资源」下 CANN 等部分卡片短述；\n切到「三方资源」才出现该面板说明，\n且没有按页签结构写的 Markdown / 独立文档可对照。",
            "MD 按页签结构平铺",
            "## 下载资源\n### 昇腾资源\n#### CANN\n短述…\n- 安装指南：https://…/cann-install\n#### MindSDK\n短述…\n- 文档：https://…/mindsdk\n### 三方资源\n#### （三方资源面板条目）\n短述…\n- 文档：https://…",
            False,
            False,
        ),
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_example": (
            "下载中心 Tab：空 nav → 双面板进源码",
            "页签未进源码、未激活面板缺失",
            '&lt;div class="o-tab"&gt;\n  &lt;div class="o-tab-nav-list"&gt;&lt;/div&gt;\n  &lt;!-- 浏览器可见「昇腾资源 / 三方资源」，源码无页签名 --&gt;\n  &lt;div class="o-tab-pane"&gt;\n    &lt;div class="o-card-title"&gt;CANN&lt;/div&gt;\n    &lt;div class="o-card-detail"&gt;CANN作为华为昇腾…&lt;/div&gt;\n  &lt;/div&gt;\n&lt;/div&gt;',
            "页签 + 双 pane 全量 SSR",
            '&lt;div class="o-tab-nav-list"&gt;\n  &lt;span role="tab" aria-selected="true"&gt;昇腾资源&lt;/span&gt;\n  &lt;span role="tab"&gt;三方资源&lt;/span&gt;\n&lt;/div&gt;\n&lt;div role="tabpanel" id="pane-ascend"&gt;\n  &lt;div class="o-card-title"&gt;CANN&lt;/div&gt;\n  &lt;div class="o-card-detail"&gt;…&lt;/div&gt;\n  &lt;div class="o-card-title"&gt;MindSDK&lt;/div&gt;\n  &lt;div class="o-card-detail"&gt;沉淀行业能力…&lt;/div&gt;\n  &lt;a href="/document/…/cann"&gt;查看文档&lt;/a&gt;\n&lt;/div&gt;\n&lt;div role="tabpanel" id="pane-third" hidden&gt;\n  …三方资源面板条目…\n&lt;/div&gt;',
            False,
            False,
            "页签名只在浏览器里渲染，源码 tab nav 为空；未激活面板也未进首包，静态抓取列不全页签与内容。",
            "页签名与双面板均在首包；未激活 pane 可用 hidden，文本仍可抓。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "frontend_example_before_mark": True,
        "acceptance": [
            ("页签可读", "静态抓取后能读到「昇腾资源 / 三方资源」等页签名，tab nav 不为空"),
            ("面板可抓", "昇腾资源 pane 的 CANN / MindSDK 等卡片、三方资源 pane 内列表均在首包可读"),
            ("可证伪", "对「各页签有哪些内容 / 某软件卡短述」须能引用源码中的具体文本"),
        ],
    },
    "obreadcrumb": {
        "design_example_side_by_side": True,
        "design": [
            (
                "路径文案须自描述",
                "写清真实层级（如「文档中心 › CANN › 安装部署」），避免「首页 / 详情 / 当前页」等泛词",
            ),
            (
                "祖先可点、当前页纯文本",
                "上级每一级为真实 a[href]，末级当前页用纯文本（避免自链）",
            ),
        ],
        "design_example": (
            "面包屑：泛词 → 真实层级名",
            "泛词路径",
            '<nav aria-label="Breadcrumb" style="font-size:12.5px;color:var(--muted);">\n'
            '  <span>首页</span> › <span>详情</span> › <span>当前页</span>\n'
            '</nav>',
            "真实层级名 + 可跟链",
            '<nav aria-label="Breadcrumb" style="font-size:12.5px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">文档中心</a> › '
            '<a href="#" style="color:var(--accent);text-decoration:none;">CANN</a> › '
            '<a href="#" style="color:var(--accent);text-decoration:none;">安装部署</a> › '
            '<span style="color:var(--muted);">CANN 安装指南</span>\n'
            '</nav>',
            True,
            True,
            "「首页 › 详情 › 当前页」看不出在站点哪一层，也无法据此回溯到祖先页。",
            "<strong>要点：</strong>每级为真实层级名；祖先可跟链，末级当前页纯文本。",
        ),
        "content": [
            (
                "统一命名",
                "面包屑、sitemap、侧栏目录与 MD 路径链使用同一套层级名与 URL，避免同一页因名称差异被识别成多个入口",
            ),
            (
                "MD 页头写路径",
                "Markdown 版在 h1 上方用列表或一行路径链写出 ancestors（标题 + 链接）；末级当前页纯文本即可",
            ),
            (
                "过渡补位",
                "页面面包屑未达标前，用 llms.txt 临时写出关键祖先链；达标后以页面为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "昇腾产品形态说明：路径链平行轨",
            "只有 title，无路径链（连续阅读模式开启情况下）",
            "【HTML】<title>昇腾产品形态说明-产品与技术常见问题-昇腾常见问题…</title>\n"
            "【缺失】MD / llms 均无各级 ancestors 的可跟链",
            "MD 页头平铺路径链",
            "## 路径\n"
            "- [昇腾常见问题](/document/detail/zh/AscendFAQ/…)\n"
            "- [产品与技术常见问题](…)\n"
            "- 昇腾产品形态说明（当前页）\n\n"
            "# 昇腾产品形态说明\n…",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 页头平铺路径链",
                "## 路径\n"
                "- [昇腾常见问题](/document/detail/zh/AscendFAQ/…)\n"
                "- [产品与技术常见问题](…)\n"
                "- 昇腾产品形态说明（当前页）\n\n"
                "# 昇腾产品形态说明\n…",
            ),
            (
                "llms 临时补祖先链",
                "# llms.txt（过渡）\n"
                "- [昇腾常见问题](/document/detail/zh/AscendFAQ/…)\n"
                "- [产品与技术常见问题](/document/detail/zh/AscendFAQ/ProduTech/…)\n"
                "- [昇腾产品形态说明](/document/detail/zh/AscendFAQ/…/hardwaredesc_0001.html)",
                "页面面包屑达标后以 HTML 为准，llms 中重复路径可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "frontend_lead": "文档页顶栏面包屑须在首包 HTML 输出完整祖先路径；静态抓取（不执行 JS）仍能列出每一级 <code>a[href]</code> 并回溯到祖先页（对标：NVIDIA cuQuantum bd-breadcrumbs）。",
        "frontend": [
            (
                "全量祖先进首包",
                "输出与可见 UI 一致的全量路径；中间级不得缺失（Ascend FAQ 实测：server-breadcrumb 仅 2 链，缺「昇腾常见问题 / 产品与技术常见问题」）",
            ),
            (
                "祖先为真实 a[href]",
                "每一级祖先须为带真实地址的 a 标签 + 可见文案；当前页用 span 或纯文本，勿做成自链",
            ),
            (
                "禁仅 JSON/脚本补路径",
                "路径节点不得只在 __NUXT_DATA__ 或前端脚本里才出现；静态 HTML 内须已有完整可跟链",
            ),
        ],
        "frontend_example": (
            "Ascend FAQ o-breadcrumb",
            "server-breadcrumb 仅 2 链，中间级缺失",
            '&lt;div class="o-breadcrumb server-breadcrumb"&gt;\n'
            '  &lt;a href="/sitemap/sitemapdoc1.xml"&gt;文档中心&lt;/a&gt;\n'
            '  &lt;a href="…/hardwaredesc_0001.html"&gt;昇腾产品形态说明&lt;/a&gt;\n'
            '&lt;/div&gt;\n'
            '&lt;!-- 浏览器可见三级路径；中间级在 __NUXT_DATA__ --&gt;',
            "SSR 全量 ancestors 可链",
            '&lt;nav aria-label="Breadcrumb" class="o-breadcrumb"&gt;\n'
            '  &lt;a href="/document/detail/zh/AscendFAQ/…"&gt;昇腾常见问题&lt;/a&gt;\n'
            '  &lt;a href="/document/detail/zh/AscendFAQ/ProduTech/…"&gt;产品与技术常见问题&lt;/a&gt;\n'
            '  &lt;span aria-current="page"&gt;昇腾产品形态说明&lt;/span&gt;\n'
            '&lt;/nav&gt;',
            False,
            False,
            "首包只有「文档中心 → 当前页」两链；中间祖先只在 __NUXT_DATA__，静态抓取无法逐级回溯。",
            "祖先级均为真实 a[href]；末级当前页纯文本。静态抓取即可列出完整路径并跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取昇腾产品形态说明页后，面包屑仍含完整祖先可链 href，能回答「每一级祖先的可点击链接是什么」"),
            ("html 可抓全", "面包屑 html 可抓取达到友商文档页水准（NVIDIA cuQuantum：bd-breadcrumbs 祖先带 href、当前页纯文本）"),
            ("可证伪", "对探针问句须能引用具体 href，与实测失败判据互斥"),
        ],
    },
    "oanchor": {
        "design_example_side_by_side": True,
        "design": [
            (
                "目录文案勿泛指",
                "右侧「本篇目录」每项须用与正文标题一致的章节名（如「安装前提」），勿用「步骤 / 其他」等对不上的简称或泛词",
            ),
            (
                "目录与正文一一对应",
                "有目录项就有对应章节；目录文案、正文章节标题须同一套，避免目录有「安装步骤」而正文写「步骤说明」",
            ),
            (
                "标题旁可标 #",
                "章节标题旁的 # 表示节级可链（permalink），便于复制带 hash 的链接；亲和硬要求仍是标题有稳定 id + 目录可跟链，符号本身非必须",
            ),
            (
                "每项为真实链接",
                "目录每项按真实链接出、指向对应节（实现为 a[href=#id]）；勿做成纯点击滚动、无目标的伪链",
            ),
        ],
        "design_example": (
            "页内目录：泛词 → 对齐章节标题",
            "泛词 · 与正文对不上",
            '<div style="display:flex;gap:16px;align-items:flex-start;font-size:12.5px;">\n'
            '  <div style="flex:1;min-width:0;">\n'
            '    <p style="margin:0 0 10px;font-size:13px;font-weight:600;color:var(--text);">安装指南</p>\n'
            '    <p style="margin:0 0 4px;font-weight:600;color:var(--text);">安装前提</p>\n'
            '    <p class="rf-muted" style="margin:0 0 12px;">准备驱动与依赖环境…</p>\n'
            '    <p style="margin:0 0 4px;font-weight:600;color:var(--text);">安装步骤</p>\n'
            '    <p class="rf-muted" style="margin:0;">按顺序执行安装命令…</p>\n'
            '  </div>\n'
            '  <div style="flex:0 0 112px;border-left:1px solid var(--line);padding-left:12px;">\n'
            '    <p class="rf-sidebar-title">本篇目录</p>\n'
            '    <ul class="rf-nav-links">\n'
            '      <li><a href="#">简介</a></li>\n'
            '      <li><a href="#">步骤</a></li>\n'
            '      <li><a href="#">其他</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            "对齐章节标题 + #id",
            '<div style="display:flex;gap:16px;align-items:flex-start;font-size:12.5px;">\n'
            '  <div style="flex:1;min-width:0;">\n'
            '    <p style="margin:0 0 10px;font-size:13px;font-weight:600;color:var(--text);">安装指南</p>\n'
            '    <p id="install-prereq" style="margin:0 0 4px;font-weight:600;color:var(--text);">安装前提 <span style="color:var(--muted);font-weight:400;font-size:11px;">#</span></p>\n'
            '    <p class="rf-muted" style="margin:0 0 12px;">准备驱动与依赖环境…</p>\n'
            '    <p id="install-steps" style="margin:0 0 4px;font-weight:600;color:var(--text);">安装步骤 <span style="color:var(--muted);font-weight:400;font-size:11px;">#</span></p>\n'
            '    <p class="rf-muted" style="margin:0;">按顺序执行安装命令…</p>\n'
            '  </div>\n'
            '  <div style="flex:0 0 112px;border-left:1px solid var(--line);padding-left:12px;">\n'
            '    <p class="rf-sidebar-title">本篇目录</p>\n'
            '    <ul class="rf-nav-links">\n'
            '      <li><a href="#install-prereq">安装前提</a></li>\n'
            '      <li><a href="#install-steps">安装步骤</a></li>\n'
            '      <li><a href="#faq">常见问题</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "正文标题是「安装前提 / 安装步骤」，右侧目录却是「简介 / 步骤 / 其他」，对不上也点不到对应节。",
            "<strong>要点：</strong>目录文案 = 章节标题、一一对应；目录项为指向该节的真实链接；标题旁 # 表示节级可链（非必须）。",
        ),
        "content": [
            (
                "统一命名",
                "页内目录项、正文章节标题与 MD 章节名使用同一套文案；#锚点指向的 id 须与该标题对应，避免「步骤」对不上「安装步骤」",
            ),
            (
                "MD 页头写目录",
                "Markdown 版在 h1 上方用列表写出本篇章节（标题 + #锚点），作为右侧目录的平行可达入口",
            ),
            (
                "过渡补位",
                "页内章节目录未达标前，用 llms.txt 临时列出章节标题与 #id；达标后以页面为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "CANN 简介：章节目录平行轨",
            "只有正文 id，无目录清单",
            "【HTML】正文有 h4.sectiontitle + section id\n"
            "【缺失】MD / llms 均无「概述 / 使用说明 / 使用向导」章节目录",
            "MD 页头平铺章节锚点",
            "## 本篇目录\n"
            "- [概述](#ZH-CN_TOPIC_…__section10818103975019)\n"
            "- [使用说明](#…)\n"
            "- [使用向导](#…)\n\n"
            "# 简介\n…",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 页头平铺章节锚点",
                "## 本篇目录\n"
                "- [概述](#ZH-CN_TOPIC_…__section10818103975019)\n"
                "- [使用说明](#…)\n"
                "- [使用向导](#…)\n\n"
                "# 简介\n…",
            ),
            (
                "llms 临时补章节目录",
                "# llms.txt（过渡）\n"
                "- [概述](#ZH-CN_TOPIC_…__section10818103975019)\n"
                "- [使用说明](#…)\n"
                "- [使用向导](#…)",
                "页内章节目录达标后以 HTML 为准，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "frontend_lead": "长文页右侧「本篇目录」须在首包 HTML 全量输出；静态抓取（不执行 JS）仍能列出章节名与 <code>#hash</code>，并与正文 <code>id</code> 对齐（对标：Mintlify On this page、NVIDIA page-toc）。",
        "frontend": [
            (
                "目录全量进首包",
                "输出与可见 UI 一致的全量章节目录；不得只有正文 id、缺目录列表（CANN 算子库简介实测：正文 section id 在首包，右侧 nav 缺失）",
            ),
            (
                "目录项为 a[href=#id]",
                "每一项须为带 hash 的 a 标签 + 章节名；禁纯 click 滚动、无 href 的伪链",
            ),
            (
                "#hash 与正文 id 对齐",
                "hash 须指向正文标题或 section 的稳定 id；须能回答「概述对应哪一节、#id 是什么」",
            ),
        ],
        "frontend_example": (
            "CANN 本篇目录",
            "正文有 id，首包无目录 nav",
            "&lt;!-- 浏览器可见：概述 / 使用说明 / 使用向导 --&gt;\n"
            "&lt;div class=\"section\" id=\"ZH-CN_TOPIC_…__section10818103975019\"&gt;\n"
            "  &lt;h4 class=\"sectiontitle\"&gt;概述&lt;/h4&gt;\n"
            "…\n"
            "&lt;!-- 静态 HTML 无本篇目录 nav 列表 --&gt;",
            "SSR 全量本篇目录锚点",
            "&lt;nav class=\"document-anc\" aria-label=\"本篇目录\"&gt;\n"
            "  &lt;a href=\"#ZH-CN_TOPIC_…__section10818103975019\"&gt;概述&lt;/a&gt;\n"
            "  &lt;a href=\"#ZH-CN_TOPIC_…__section20972124710220\"&gt;使用说明&lt;/a&gt;\n"
            "  &lt;a href=\"#ZH-CN_TOPIC_…__section1457612184710\"&gt;使用向导&lt;/a&gt;\n"
            "&lt;/nav&gt;",
            False,
            False,
            "正文节已有 id，但首包没有右侧目录可跟链；静态抓取列不出「概述 / 使用说明 / 使用向导」。",
            "目录项均为 a[href=#id] + 章节名，hash 与正文 section id 对齐；静态抓取即可按节定位。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取 CANN 算子库简介页后，右侧本篇目录仍含可跟链 #hash，能回答「概述对应哪一节、#id 是什么」"),
            ("html 可抓全", "页内目录 html 可抓取达到友商文档页水准（Mintlify On this page、NVIDIA page-toc 首包完整）"),
            ("可证伪", "对探针问句须能引用具体 #id，与实测失败判据互斥"),
        ],
    },
    "onavigation": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "站点信息架构入口",
                    "要做亲和",
                    "顶栏「产品 / 文档 / 开发者 / 下载 / 支持」及下拉子项：须为真实 <code>a[href]</code> + 可见文案，子链首包输出，静态抓取可跟到官方落地页。<br>对应页面：<a href=\"https://www.hiascend.com/zh\" target=\"_blank\" rel=\"noopener\">社区首页</a>",
                ),
                (
                    "strip",
                    "纯操作控件",
                    "不做亲和 · 入库剥离",
                    "搜索、换肤、语言切换、登录 / 用户图标等只做当前页操作、不承载站点知识。入库管道宜标 <code>data-llm-exclude</code> 或直接剥离，别当可引用正文。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "入口文案须自描述",
                "顶栏与下拉用明确去向名（如「文档中心 / 开发资源下载」），勿用「资源 / 更多 / 了解更多 ›」等泛词",
            ),
            (
                "入口按真实链接出",
                "一级与下拉项在稿面按可点链接呈现；勿做成悬停才出、无目标的伪入口",
            ),
        ],
        "design_example": (
            "顶栏导航：模糊 → 明确入口",
            "泛词 · 去向不明",
            '<div style="display:flex;gap:16px;font-size:13px;">\n'
            '  <span style="color:var(--muted);">产品</span>\n'
            '  <span style="color:var(--muted);">资源</span>\n'
            '  <span style="color:var(--muted);">了解更多 ›</span>\n'
            '</div>',
            "明确入口 + 可跟链",
            '<div style="display:flex;flex-wrap:wrap;gap:16px;font-size:13px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">产品</a>\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">文档中心</a>\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">开发资源下载</a>\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">支持与服务</a>\n'
            '</div>',
            True,
            True,
            "「资源 / 了解更多」说不清去哪；若再做成悬停才出的伪入口，静态也跟不到文档 / 下载。",
            "<strong>要点：</strong>入口名自描述；稿面按真实可点链接出。",
        ),
        "content": [
            (
                "llms / sitemap 临时补站点入口",
                "顶栏 html 未达标前，llms.txt 或 sitemap 可临时列出「文档 / 开发者 / 下载 / 支持」等一级入口及 URL；达标后以 SSR o-nav 为准，避免双轨不一致",
            ),
            (
                "MD 不写顶栏交互态",
                "站点级入口清单写在 llms 或独立「站点地图」文档，勿把悬停展开后才出现的菜单文案当作唯一知识源",
            ),
        ],
        "frontend": [
            (
                "一级入口须 a[href]",
                "顶栏 o-nav 每一项站点入口（产品 / 解决方案 / 开发者与合作伙伴 / 文档 / 下载等）须为 OLink 或 a[href] + 可见文案；禁 div.o-nav-item-link 无 href（Ascend 首页实测：仅「支持与服务」→ /support 可跟；友商 Mintlify navbar、NVIDIA Shop / Drivers 首包可跟）",
            ),
            (
                "高频导流位禁 button 冒充",
                "「在线开发」「下载」等常问入口须带真实网址；develop-btn / div 下拉触发会导致探针「文档 / 开发者 / 下载官方链接」答不全",
            ),
            (
                "下拉子链首包 SSR",
                "o-nav-panel 内子项须在服务端一次性输出完整 a[href] 列表，禁 o-nav-head 首包为空、悬停或脚本才挂链（对标 Mintlify Learn 下拉、NVIDIA mega menu 子链在首包）",
            ),
            (
                "纯操作控件标注排除",
                "搜索框、换肤、语言、用户图标加 data-llm-exclude；与信息架构入口分区，管道勿当正文 chunk",
            ),
        ],
        "content_example": (
            "社区首页：llms 补站点入口",
            "入口只在可见顶栏",
            "【HTML】产品 / 文档 / 下载文案可见，多数无 href\n【缺失】llms 未列「从首页进官方文档 / 下载」的 URL 清单",
            "llms 平铺一级入口",
            "## 站点入口（社区首页顶栏）\n- 文档：https://www.hiascend.com/document\n- 开发者：https://www.hiascend.com/developer\n- 下载：https://www.hiascend.com/developer/download\n- 支持与服务：https://www.hiascend.com/support",
            False,
            False,
        ),
        "frontend_example": (
            "社区首页 o-nav",
            "一级 div 无 href",
            '&lt;div class="o-nav-item"&gt;&lt;div class="o-nav-item-link" title="产品"&gt;产品&lt;/div&gt;&lt;/div&gt;\n&lt;div class="o-nav-item"&gt;&lt;div class="o-nav-item-link" title="开发者与合作伙伴"&gt;…&lt;/div&gt;&lt;/div&gt;\n&lt;a class="develop-btn"&gt;在线开发&lt;/a&gt;\n&lt;div class="app-header-download-val"&gt;下载&lt;/div&gt;\n&lt;!-- 友商 Mintlify navbar / NVIDIA global-nav：一级或子级 a[href] 在首包 --&gt;',
            "SSR 全量顶栏可跟链",
            '&lt;nav class="o-nav-head"&gt;\n  &lt;a class="o-nav-item-link" href="/products" title="产品"&gt;产品&lt;/a&gt;\n  &lt;a class="o-nav-item-link" href="/document" title="文档"&gt;文档&lt;/a&gt;\n  &lt;a class="o-nav-item-link" href="/developer/download" title="下载"&gt;下载&lt;/a&gt;\n&lt;/nav&gt;\n&lt;div class="o-nav-panel"&gt;\n  &lt;a href="/developer"&gt;开发者&lt;/a&gt;…\n&lt;/div&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取社区首页后，顶栏仍含文档 / 开发者 / 下载等可跟链 href，能回答 problems-onavigation 探针问句"),
            ("html 可抓全", "顶栏 html 可抓取达到友商水准（Mintlify 文档站 navbar、NVIDIA global-nav：一级或子级 href 均在首包）"),
            ("可证伪", "对「从首页进文档 / 开发者 / 下载的官方链接」须能引用具体 href，与 problems-onavigation 失败判据互斥"),
        ],
    },
    "ofooternav": {
        "design": [
            (
                "页脚链用可读文字",
                "页脚每列链接用可读文案（法律声明 / 文档中心 / 联系我们），社交等纯图标须配文字或 aria-label；每项为真实 a[href]，可当站点地图",
            ),
        ],
        "design_example": (
            "页脚导航：图标 / 泛词 → 可读链接",
            "泛词 · 纯图标",
            '<div style="display:flex;gap:24px;font-size:12.5px;">\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">支持</p>\n'
            '    <ul class="rf-nav-links"><li><a href="#">链接</a></li><li><a href="#">更多</a></li></ul>\n'
            '  </div>\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">关注我们</p>\n'
            '    <div style="font-size:16px;">🔗 🔗 🔗</div>\n'
            '  </div>\n'
            '</div>\n'
            '<p class="rf-muted">「链接 / 更多」无意义，社交仅图标无文字；Agent 抓不到法律声明 / 文档等页脚入口。</p>',
            "可读文案 + 真实链接",
            '<div style="display:flex;gap:24px;font-size:12.5px;">\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">支持与服务</p>\n'
            '    <ul class="rf-nav-links"><li><a href="#">文档中心</a></li><li><a href="#">技术工单</a></li></ul>\n'
            '  </div>\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">关于</p>\n'
            '    <ul class="rf-nav-links"><li><a href="#">法律声明</a></li><li><a href="#">联系我们</a></li></ul>\n'
            '  </div>\n'
            '</div>\n'
            '<p class="rf-caption"><strong>要点：</strong>每列链接用可读文案 + 真实 a[href]，把页脚当站点地图；纯图标配 aria-label。</p>',
            True,
            True,
        ),
        "content": [
            (
                "llms / sitemap 收录页脚关键链",
                "页脚 html 达标后，llms.txt 仍应显式列出「文档 / 法律声明 / 联系我们 / 支持与服务」等页脚 href，与 footer SSR 互证；未达标前可临时用 llms 补位",
            ),
            (
                "列名改版写 changelog",
                "页脚分组名（关于昇腾 / 支持与服务等）或链接文案改版时，在 llms 或 changelog 写明新旧映射，避免旧 chunk 对不上当前 HTML",
            ),
        ],
        "frontend": [
            (
                "footer-main 五列 SSR",
                "app-footer footer-main 须输出五列 link-group（关于昇腾 / 新闻与活动 / 交流与资讯 / 支持与服务 / 开源社区），每项 gp-link 为 a[href] + 可见文案（对标友商：Mintlify Documentation/Legal、NVIDIA page-footer、昇腾首页实测可抓全）",
            ),
            (
                "底栏法律链须可跟",
                "法律声明 → /zh/legal/law、隐私政策、联系我们等底栏链接须进首包 HTML，禁仅图标或脚本后填",
            ),
            (
                "禁纯图标无 anchor text",
                "社交/关注我们等若保留，须配可读文字或 aria-label；友情链接 refer-link 同样须 a[href] + 文案",
            ),
            (
                "全站页脚结构一致",
                "壳页页脚 HTML 结构宜各页一致，便于 Agent 把首页 footer 当站点地图模板；勿某内页页脚空列或缺法律链",
            ),
        ],
        "content_example": (
            "社区首页：llms 补页脚入口",
            "页脚链未进 llms",
            "【HTML】footer-main 五列 + 法律声明 / 联系我们 href 已在首包\n【缺失】llms.txt 未列「关于昇腾 / 法律声明 / 联系我们」官方 URL",
            "llms 平铺页脚关键链",
            "## 站点入口（页脚）\n- 昇腾计算产业概述：https://www.hiascend.com/ecosystem/industry\n- 文档：https://www.hiascend.com/zh/document\n- 法律声明：https://www.hiascend.com/zh/legal/law\n- 联系我们：https://www.huawei.com/cn/contact-us",
            False,
            False,
        ),
        "frontend_example": (
            "社区首页 footer-main",
            "空列或脚本后填",
            '&lt;div class="footer-main"&gt;&lt;div class="link-group"&gt;&lt;h4&gt;支持与服务&lt;/h4&gt;&lt;!-- 浏览器可见列，首包为空 --&gt;&lt;/div&gt;&lt;/div&gt;\n&lt;!-- 友商 Mintlify / NVIDIA / 昇腾首页实测：多列 a[href] 在首包 --&gt;',
            "SSR 全量五列可跟链",
            '&lt;div class="footer-main"&gt;\n  &lt;div class="link-group"&gt;&lt;h4 class="gp-name"&gt;关于昇腾&lt;/h4&gt;&lt;a class="gp-link" href="/ecosystem/industry"&gt;昇腾计算产业概述&lt;/a&gt;&lt;/div&gt;\n  &lt;div class="link-group"&gt;&lt;h4 class="gp-name"&gt;支持与服务&lt;/h4&gt;&lt;a href="/zh/document"&gt;文档&lt;/a&gt;&lt;a href="/zh/feedback"&gt;技术工单&lt;/a&gt;&lt;/div&gt;\n  …\n  &lt;a href="/zh/legal/law"&gt;法律声明&lt;/a&gt;&lt;a href="https://www.huawei.com/cn/contact-us"&gt;联系我们&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取社区首页后，页脚仍含五列导航及法律声明 / 联系我们等可跟链 href，能回答 problems-ofooternav 探针问句"),
            ("html 可抓全", "页脚 html 可抓取达到友商水准（Mintlify / NVIDIA / 昇腾首页 footer-nav 首包完整）"),
            ("可证伪", "对「关于昇腾 / 法律声明 / 联系我们分别链到哪」须能引用具体 href，与 problems-ofooternav 失败判据互斥"),
        ],
    },
    "opagination": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "公开列表底部分页",
                    "要做亲和",
                    "挂在表格、卡片列表、论坛帖列表等下方，用来切第 2、3… 页；深页承载公开可引用内容。<br>页码须为真实 <code>a[href]</code>（带稳定 query，如 <code>?page=2</code>），静态抓取可跟到深页；可辅以 <code>rel=next</code> / sitemap 覆盖。<br>对应页面：<a href=\"https://www.hiascend.com/forum/\" target=\"_blank\" rel=\"noopener\">昇腾论坛</a>",
                ),
                (
                    "strip",
                    "后台 / 登录后表格分页",
                    "不做亲和 · 入库剥离",
                    "控制台、个人中心等登录后表格的翻页，指向非公开操作数据。入库管道宜标 <code>data-llm-exclude</code> 或直接剥离，别当可引用文档。",
                ),
            ],
        },
        "design_none": True,
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "content": [
            (
                "sitemap / llms 收录深页",
                "列表第 2、3… 页的稳定 URL 须进 sitemap 或 llms.txt，不单靠翻页控件才能发现深页内容",
            ),
            (
                "关键条目可平行清单",
                "论坛帖、案例卡等关键列表可在 Markdown / llms 平铺「标题 + 链接」；即使分页 HTML 未抓全，也能枚举条目",
            ),
            (
                "过渡补位",
                "页码尚无真实 URL 前，用 llms / sitemap 临时补全量条目或深页地址；分页达标后以页面为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "论坛列表：深页平行轨",
            "只有第 1 页，深页未进清单",
            "【HTML】论坛首页可见第 1 页帖列表 + 翻页控件\n"
            "【缺失】sitemap / llms 无 ?page=2、?page=3 及深页帖链接",
            "sitemap 收录深页 URL",
            "# sitemap（节选）\n"
            "https://www.hiascend.com/forum/\n"
            "https://www.hiascend.com/forum/?page=2\n"
            "https://www.hiascend.com/forum/?page=3",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "sitemap 收录深页 URL",
                "# sitemap（节选）\n"
                "https://www.hiascend.com/forum/\n"
                "https://www.hiascend.com/forum/?page=2\n"
                "https://www.hiascend.com/forum/?page=3",
            ),
            (
                "llms 临时补条目 / 深页",
                "# llms.txt（过渡）\n"
                "- [论坛第 2 页](https://www.hiascend.com/forum/?page=2)\n"
                "- [某帖标题](https://www.hiascend.com/forum/thread-…)\n"
                "- [另一帖标题](https://www.hiascend.com/forum/thread-…)",
                "分页控件输出真实 a[href] 且深页可跟后，llms 中重复深页项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "frontend_lead": "公开列表底部分页的页码须在首包 HTML 输出为带稳定 query 的真实 <code>a[href]</code>；静态抓取（不执行 JS）仍能跟到第 2、3… 页（对标常见文档/博客列表分页）。",
        "frontend": [
            (
                "页码为真实 a[href]",
                "每一页码（及上一页 / 下一页）须为带地址的 a 标签；禁纯 button / onClick 翻页导致深页无官方 URL",
            ),
            (
                "query 稳定可复用",
                "深页地址宜用稳定参数（如 ?page=2），同一页多次打开结果一致，便于 sitemap 与引用",
            ),
            (
                "可用 rel=next 辅助",
                "可在 link[rel=next] / rel=prev 标明相邻页，辅助机器发现；不能替代页码上的真实 a[href]",
            ),
        ],
        "frontend_example": (
            "论坛列表底部分页",
            "页码是 button，无深页 URL",
            '&lt;div class="o-pagination"&gt;\n'
            '  &lt;button&gt;1&lt;/button&gt;\n'
            '  &lt;button&gt;2&lt;/button&gt;\n'
            '  &lt;button&gt;3&lt;/button&gt;\n'
            '  &lt;button&gt;下一页&lt;/button&gt;\n'
            '&lt;/div&gt;\n'
            '&lt;!-- 浏览器可翻页；静态 HTML 无 ?page=2 可跟链 --&gt;',
            "页码 a[href] + 稳定 query",
            '&lt;nav class="o-pagination" aria-label="分页"&gt;\n'
            '  &lt;a href="/forum/?page=1" aria-current="page"&gt;1&lt;/a&gt;\n'
            '  &lt;a href="/forum/?page=2"&gt;2&lt;/a&gt;\n'
            '  &lt;a href="/forum/?page=3"&gt;3&lt;/a&gt;\n'
            '  &lt;a href="/forum/?page=2" rel="next"&gt;下一页&lt;/a&gt;\n'
            '&lt;/nav&gt;',
            False,
            False,
            "翻页只靠 button/脚本，静态抓取给不出第 2、3 页官方 URL，深页内容不可达。",
            "页码均为真实 a[href]；静态抓取即可回答「第 2、3 页官方 URL 是什么」。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取论坛列表页后，分页仍含 ?page=2、?page=3 等可跟链 href，能回答「第 2、3 页官方 URL」"),
            ("深页可引用", "深页 URL 稳定可复用，并可被 sitemap / llms 收录"),
            ("可证伪", "对探针问句须能引用具体 href，与实测失败判据互斥"),
        ],
    },
    "ostep": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "公开流程 / 逐步说明块",
                    "要做亲和",
                    "安装·认证·Quickstart 步骤条，或「加入开发者计划」等逐步权益格：每步标题与说明须为可见文本进首包；流程型还须标「进行中 / 已完成」。配图内字须旁注或改为文本交付。<br>对应页面：<a href=\"https://www.hiascend.com/developer\" target=\"_blank\" rel=\"noopener\">开发者入口</a>（对标 Mintlify Quickstart Steps）",
                ),
                (
                    "strip",
                    "后台 / 登录后向导",
                    "不做亲和 · 入库剥离",
                    "控制台表单向导、多步提交进度条等，指向非公开操作流程。入库管道宜标 <code>data-llm-exclude</code> 或直接剥离，别当可引用文档。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "每步标题 + 说明出可见文案",
                "稿面为每步预留标题与短说明文本位，勿把「实物礼品 / 开发资源」等字只画进配图里",
            ),
            (
                "状态勿只靠颜色",
                "「进行中 / 已完成」用文字或可辨标记标出，不只靠高亮色或数字圈",
            ),
            (
                "全步骤文案一并交付",
                "各步标题与说明都要进设计交付物，勿只标注当前步、其余步留给开发自拟",
            ),
        ],
        "design_example": (
            "流程步骤：仅数字圈 → 可见文案",
            "只有数字圈 / 高亮色",
            '<div style="display:flex;flex-direction:column;gap:10px;font-size:12.5px;">\n'
            '  <div style="display:flex;gap:10px;align-items:center;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">1</span>\n'
            '    <span style="color:var(--muted);">（无标题 / 说明）</span>\n'
            '  </div>\n'
            '  <div style="display:flex;gap:10px;align-items:center;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;opacity:0.35;">2</span>\n'
            '    <span style="color:var(--muted);">（仅颜色区分，无「进行中」文案）</span>\n'
            '  </div>\n'
            '  <div style="display:flex;gap:10px;align-items:center;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;border:1px solid var(--line);color:var(--muted);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">3</span>\n'
            '    <span style="color:var(--muted);">（无标题 / 说明）</span>\n'
            '  </div>\n'
            '</div>',
            "每步可见标题 + 短说明",
            '<div style="display:flex;flex-direction:column;gap:10px;font-size:12.5px;">\n'
            '  <div style="display:flex;gap:10px;align-items:flex-start;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">1</span>\n'
            '    <div><p style="margin:0;font-weight:600;color:var(--text);">实物礼品</p><p class="rf-muted" style="margin:2px 0 0;">完成认证可领取开发套件…</p></div>\n'
            '  </div>\n'
            '  <div style="display:flex;gap:10px;align-items:flex-start;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;border:1px solid var(--line);color:var(--muted);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">2</span>\n'
            '    <div><p style="margin:0;font-weight:600;color:var(--text);">开发资源 <span style="font-size:11px;color:var(--accent);font-weight:500;">进行中</span></p><p class="rf-muted" style="margin:2px 0 0;">开放文档、样例与工具链…</p></div>\n'
            '  </div>\n'
            '  <div style="display:flex;gap:10px;align-items:flex-start;">\n'
            '    <span style="flex:0 0 22px;height:22px;border-radius:50%;border:1px solid var(--line);color:var(--muted);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;">3</span>\n'
            '    <div><p style="margin:0;font-weight:600;color:var(--text);">身份荣誉</p><p class="rf-muted" style="margin:2px 0 0;">开发者认证与社区标识…</p></div>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "稿面只有数字圈和高亮色，没有步骤标题与说明文本位，也无法用文字标状态。",
            "<strong>要点：</strong>每步标题 + 短说明为可见文本；状态用文字标出；各步文案一并交付。",
        ),
        "content": [
            (
                "统一命名",
                "步骤标题与 MD / 正文使用同一套文案（如「实物礼品 / 开发资源」），避免 UI 与文档各写各的",
            ),
            (
                "MD 平铺步骤",
                "Markdown 版逐步写出标题 + 短说明（可附链接），作为页面步骤的平行可达入口",
            ),
            (
                "过渡补位",
                "页面步骤 HTML 未达标前，用 llms.txt 临时列出逐步标题与说明；达标后以页面为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "开发者计划：逐步说明平行轨",
            "只有导语，无逐步文本清单",
            "【HTML】加入开发者计划 h2 + 导语在首包\n"
            "【缺失】MD / llms 均无「实物礼品 / 开发资源 / …」逐步说明",
            "MD 平铺步骤",
            "## 加入开发者计划\n"
            "### 1. 实物礼品\n"
            "完成认证可领取开发套件…\n\n"
            "### 2. 开发资源\n"
            "开放文档、样例与工具链…\n\n"
            "### 3. 身份荣誉\n"
            "…\n\n"
            "### 4. 学习资源\n"
            "…",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平铺步骤",
                "## 加入开发者计划\n"
                "### 1. 实物礼品\n"
                "完成认证可领取开发套件…\n\n"
                "### 2. 开发资源\n"
                "开放文档、样例与工具链…\n\n"
                "### 3. 身份荣誉\n"
                "…\n\n"
                "### 4. 学习资源\n"
                "…",
            ),
            (
                "llms 临时补逐步说明",
                "# llms.txt（过渡）\n"
                "## 加入开发者计划\n"
                "1. 实物礼品：完成认证可领取开发套件…\n"
                "2. 开发资源：开放文档、样例与工具链…\n"
                "3. 身份荣誉：…\n"
                "4. 学习资源：…",
                "页面步骤 SSR 达标后以 HTML 为准，llms 中重复逐步项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "frontend_lead": "公开流程 / 逐步说明块的每步标题与说明须写入首包 HTML；静态抓取（不执行 JS）仍能列全步骤，并读出当前步状态（对标：Mintlify Quickstart Steps）。",
        "frontend": [
            (
                "全量步骤进首包",
                "全部步骤标题 + 说明一次性输出；勿只渲染当前步、其余步等切换才注入（开发者入口实测：可见权益名，源码常缺逐步文本）",
            ),
            (
                "标题 + 说明为可见文本",
                "每步须有可读的标题与说明节点；禁只留数字圈，也禁把说明只放在配图里",
            ),
            (
                "状态可机读",
                "「进行中 / 已完成」用可见文本或 aria-current 标注，勿只靠高亮色；须能回答「当前进行到哪一步」",
            ),
        ],
        "frontend_example": (
            "开发者计划逐步说明",
            "只有数字圈 / 配图，无 step 文本",
            '&lt;div class="o-step"&gt;\n'
            '  &lt;span class="step-index"&gt;1&lt;/span&gt;\n'
            '  &lt;span class="step-index"&gt;2&lt;/span&gt;\n'
            '  &lt;img src="…gift.png"/&gt;&lt;!-- 浏览器可见「实物礼品」，源码无标题说明 --&gt;\n'
            '&lt;/div&gt;',
            "SSR 全量步骤文本",
            '&lt;ol class="o-step"&gt;\n'
            '  &lt;li&gt;\n'
            '    &lt;p class="step-title"&gt;实物礼品&lt;/p&gt;\n'
            '    &lt;p class="step-content"&gt;完成认证可领取开发套件…&lt;/p&gt;\n'
            '  &lt;/li&gt;\n'
            '  &lt;li aria-current="step"&gt;\n'
            '    &lt;p class="step-title"&gt;开发资源&lt;/p&gt;\n'
            '    &lt;p class="step-content"&gt;开放文档、样例与工具链…&lt;/p&gt;\n'
            '    &lt;span&gt;进行中&lt;/span&gt;\n'
            '  &lt;/li&gt;\n'
            '  &lt;li&gt;…身份荣誉…&lt;/li&gt;\n'
            '&lt;/ol&gt;',
            False,
            False,
            "首包只有圈号或配图，静态抓取列不出逐步标题与说明，也答不出当前步。",
            "每步标题 + 说明均为文本；当前步有状态标注。静态抓取即可逐步复述。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取开发者入口后，仍能逐步列出标题与说明，并回答「当前进行到哪一步」"),
            ("html 可抓全", "步骤 html 达到友商水准（Mintlify Quickstart Steps：各步标题 + 说明在首包）"),
            ("可证伪", "对探针问句须能引用具体文本，与实测失败判据互斥"),
        ],
    },
    "obutton": {
        "intro_card": {
            "title": "为什么按钮是「视情况」——先分清按钮的两种角色",
            "items": [
                (
                    "keep",
                    "跳转按钮（点击跳到另一个页面）",
                    "要做亲和",
                    "如「立即查看 / 了解更多 / 前往认证」。它承诺「点了会去哪」，须做亲和：底层用可抓的 <code>a[href]</code>，样式仍可保留按钮外观，让 Agent 能给出官方落地 URL。",
                ),
                (
                    "strip",
                    "操作按钮（只在当前页做动作）",
                    "不做亲和 · 入库剥离",
                    "如「提交 / 关闭 / 确认 / 我知道了」。它不是正文知识，入库管道宜标 <code>data-llm-exclude</code> 或剥离，避免文案被 Agent 误当成可引用结论。",
                ),
            ],
        },
        "design_none": True,
        "content": [
            (
                "MD / llms 补 CTA 落地页",
                "HTML 仍用 button 伪链时，llms.txt 或活动文档页须列出「立即查看 / 了解更多」等 CTA 对应官方 URL；达标后以 SSR a[href] 为准",
            ),
            (
                "活动规则勿只放弹层",
                "认证须知、问卷规则等关键说明写在可引用正文或详情页 MD，勿只出现在点击 CTA 后的 dialog",
            ),
        ],
        "frontend": [
            (
                "跳转型 CTA 须 a[href]",
                "社区首页 banner「立即查看 / 了解更多 / 立即填写 / 前往认证 / 立即参与」等须为 OLink 或 a[href] + 可见文案；禁 button.o-btn.banner-actions-item 无 href（友商 Mintlify Get started、NVIDIA More Models 首包可跟）",
            ),
            (
                "样式可按钮、语义须链接",
                "保留 o-btn 外观时底层仍输出 href；或 button 旁并列隐藏/可见 a[href] 供爬虫跟链",
            ),
            (
                "纯操作 button 标注排除",
                "提交 / 关闭 / 我知道了等无导航语义的 button 加 data-llm-exclude，入库管道勿当正文 chunk",
            ),
        ],
        "content_example": (
            "社区首页：llms 补 CTA 落地",
            "CTA 只有 button 文案",
            "【HTML】banner 有「立即查看 / 了解更多」文案，无 href\n【缺失】llms 未列各 CTA 对应官方 URL",
            "llms 平铺 CTA 入口",
            "## 社区首页 CTA\n- 昇腾AI创新大赛2026 → https://…\n- HCCL通信库创新大赛 → https://…\n- 推理开发者认证 → https://…",
            False,
            False,
        ),
        "frontend_example": (
            "社区首页 banner CTA",
            "button 无 href",
            '&lt;p class="banner-title"&gt;HCCL通信库创新大赛&lt;/p&gt;\n&lt;button type="button" class="o-btn o-btn-primary banner-actions-item"&gt;立即查看&lt;/button&gt;\n&lt;button type="button" class="o-btn banner-actions-item"&gt;了解更多&lt;/button&gt;\n&lt;!-- 友商 Mintlify / NVIDIA build：CTA 为 a[href] 在首包 --&gt;',
            "SSR 跳转型 CTA 链接化",
            '&lt;a class="o-btn o-btn-primary banner-actions-item" href="/activity/hccl-contest"&gt;立即查看&lt;/a&gt;\n&lt;a class="o-btn banner-actions-item" href="/activity/ascend-ai-2026"&gt;了解更多&lt;/a&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取社区首页后，首屏 CTA 仍含可跟链 href，能回答 problems-obutton 探针问句"),
            ("html 可抓全", "CTA html 达到友商水准（Mintlify hero-cta、NVIDIA build list-cta：按钮文案与 href 在首包）"),
            ("可证伪", "对「立即查看 / 了解更多分别链到哪」须能引用具体 href，与昇腾 banner button 失败判据互斥"),
        ],
    },
    "olink": {
        "design": [
            (
                "锚文本自描述",
                "链接文案勿只写「软件介绍 / 快速入门 / 了解更多」等泛化词 + 外链图标；须让读者与 Agent 脱离行列标题也能知道链到哪——宜「行任务 · 目标文档」如「学习了解 · MindSpeed LLM 软件介绍」",
            ),
            (
                "站外跳转标清目标站点",
                "外链锚文本点明目标站点（如「… — GitCode ↗」），并加 title 与 <code>rel=\"noopener\"</code>；底层用绝对 URL 的真实 a[href]，让 Agent 知道去哪个站、可跟链，别用图标替代文案",
            ),
            (
                "行列语境写进交付稿",
                "设计稿标注：左列「环境安装」、顶列「进阶」与格内链文案一并交付，前端 / 文档侧 SSR 时合成可读 anchor，勿假设用户记得表头",
            ),
        ],
        "design_example": (
            "链接：泛词 + 外链图标 → 自描述 + 标清站外",
            "仅泛化词 + 外链图标",
            '<div style="font-size:12.5px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">软件介绍 ↗</a>\n'
            '</div>\n'
            '<p class="rf-muted">「软件介绍 ↗」只靠图标暗示外链，锚文本泛化、没说链到哪个站；入库后 anchor 仍是泛词，Agent 说不清去向、也不知是站外。</p>',
            "自描述 anchor + 标清站外目标",
            '<div style="font-size:12.5px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;" title="MindSpeed-LLM introduction.md（GitCode）">学习了解 · MindSpeed LLM 软件介绍<span style="color:var(--muted);"> — GitCode ↗</span></a>\n'
            '</div>\n'
            '<p class="rf-caption"><strong>要点：</strong></p>\n'
            '<ul class="rf-caption" style="margin:4px 0 0;padding-left:18px;">\n'
            '  <li>锚文本自描述：含「行任务 · 目标文档」（学习了解 · MindSpeed LLM 软件介绍），脱离表头也知道链到哪。</li>\n'
            '  <li>站外跳转标清目标站点（GitCode ↗）+ title，底层真实 a[href] 绝对 URL、<code>rel="noopener"</code>；别用图标替代文案。</li>\n'
            '</ul>',
            True,
            True,
        ),
        "content": [
            (
                "MD / llms 补 JSON 内链",
                "HTML 仍把 link 放 application/json 时，llms.txt 或平行 MD 须列出带行列语境的入口，如「[进阶 · 学习了解] 软件介绍 → URL」；勿只写「软件介绍 → URL」",
            ),
            (
                "锚文本与目的地一致",
                "链文案宜点明对象（MindSpeed LLM / CANN 安装指南），与 href 落地页标题一致；禁三列重复使用同一「软件介绍」而无区分",
            ),
            (
                "文档正文用标准 Markdown 链",
                "CANN 算子库等文档页宜 `[Math类接口](url)` 或 HTML OLink；勿只写在脚本 JSON 或 onclick",
            ),
        ],
        "frontend": [
            (
                "导流矩阵须 SSR a[href]",
                "训练开发页 hcomponent-ascend-user-journey 每一格须输出 OLink 或 a[href] + 可见文案；禁 tab-content 空挂载点 + 仅 application/json 存 link（友商 Mintlify Related topics、NVIDIA Quick Links 首包可跟）",
            ),
            (
                "锚文本合成行列语境",
                "SSR 时可将 row.text（学习了解）+ column.label（进阶）+ cell.label 合成可见 anchor 或 title；外链加 rel=\"noopener\" 与可读 title",
            ),
            (
                "禁 span/div 伪链",
                "可导航样式底层须 a[href]；禁 div.o-nav-item-link、整卡 onclick 无 href",
            ),
            (
                "占位链与路径规范",
                "禁 href=\"#\" / javascript:void 占位；站内链用 canonical 绝对或根相对路径",
            ),
        ],
        "content_example": (
            "训练开发：llms 补旅程链",
            "link 只在 JSON",
            "【HTML】用户旅程矩阵浏览器可见，tab-content 空\n【JSON】application/json 含 label+link\n【缺失】首包无 a[href]",
            "llms 平铺矩阵入口",
            "## 大语言模型训练用户旅程\n- [进阶 · 学习了解] MindSpeed LLM 软件介绍 → https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md\n- [进阶 · 环境安装] 安装指导 → …/install_guide.md\n- [高阶 · 快速体验] 快速入门 → …/quick_start.md",
            False,
            False,
        ),
        "frontend_example": (
            "训练开发旅程矩阵 vs 友商",
            "JSON 无 a[href]",
            '&lt;div class="tab-content" id="vue_…"&gt;&lt;/div&gt;\n&lt;script type="application/json"&gt;{"label":"软件介绍","link":"https://…/introduction.md"}&lt;/script&gt;\n&lt;!-- 友商 Mintlify Related topics / NVIDIA Quick Links：a[href] 在首包 --&gt;',
            "SSR 矩阵 OLink",
            '&lt;a class="o-link journey-cell-link" href="https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md" title="MindSpeed LLM 软件介绍（GitCode）" rel="noopener"&gt;学习了解 · MindSpeed LLM 软件介绍&lt;/a&gt;\n&lt;a class="o-link journey-cell-link" href="…/install_guide.md" title="安装指导"&gt;环境安装 · 安装指导&lt;/a&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取训练开发 tab1 后，用户旅程矩阵仍含可跟链 href，能回答 problems-olink 探针问句"),
            ("html 可抓全", "正文链 html 达到友商水准（Mintlify related-topics、NVIDIA topics-links：文案与 href 在首包）"),
            ("可证伪", "对「软件介绍 / 安装指导 / 快速入门 href 是什么」须能引用具体 a[href]，与昇腾 JSON 注入失败判据互斥"),
        ],
    },
    "odropdown": {
        "design_none": True,
        "content": [
            (
                "llms 补下拉子链",
                "HTML 下拉仍靠交互/JSON 挂载时，llms.txt 须平铺子项：昇腾「更多产品」各机型 URL；Mintlify Products 各特性链；NVIDIA Resources（Developer Program / GTC / On-Demand 等）；达标后以 SSR dropdown 为准",
            ),
        ],
        "content_example": (
            "集群页：llms 补「更多产品」链",
            "子链只在交互 panel",
            "【HTML】仅「更多产品」触发器\n【缺失】Atlas 900 A2 PoD / SuperCluster AI 等 href 未进首包",
            "llms 平铺同品类机型",
            "## 集群产品 · 更多产品\n- Atlas 900 A2 PoD 集群基础单元 → /hardware/cluster?tag=900\n- Atlas 900 SuperCluster AI 集群 → /hardware/cluster?tag=900ai",
            False,
            False,
        ),
        "frontend": [
            (
                "dropdown 子项须 SSR a[href]",
                "昇腾集群页「更多产品」、Mintlify Products mega menu、NVIDIA developer Resources 等须在首包输出 ODropdown/a[href] + 可见文案；禁仅 navigation-menu-trigger 或 div#header 空壳",
            ),
            (
                "禁外部 JSON 作唯一菜单",
                "NVIDIA header-secondary.json、Vue 读 application/json 等不可代替首包子链；JSON 仅作增强",
            ),
            (
                "禁 portal 延迟挂",
                "下拉 panel 不得点击后才注入 body；子项宜写在 nav/ul 静态区，视觉可 hidden 但须保留 a 节点",
            ),
            (
                "子项文案自描述",
                "每项 label 宜含对象全名（机型/特性/资源名），与 href 落地页 title 一致",
            ),
        ],
        "frontend_example": (
            "三站下拉：触发器 vs SSR 子链",
            "仅触发器 / JSON / 空壳 header",
            "昇腾：<span>更多产品</span> <!-- panel 无 a[href] -->\nMintlify：<button data-navitem=\"Products\" data-state=\"closed\">Products</button>\nNVIDIA：<div id=\"header\"></div> + fetch header-secondary.json",
            "SSR 全量子项可跟链",
            '<div class="o-dropdown-panel">\n  <a href="/hardware/cluster?tag=900">Atlas 900 A2 PoD 集群基础单元</a>\n  <a href="/hardware/cluster?tag=900ai">Atlas 900 SuperCluster AI 集群</a>\n</div>',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取集群产品页后，「更多产品」下拉子项仍含可跟链 href，能回答 problems-odropdown 探针问句"),
            ("三站互证", "与 Mintlify Products mega menu、NVIDIA Resources JSON 菜单同类问题须 SSR 解决，不可只修昇腾一处"),
            ("可证伪", "对「Atlas 900 A2 PoD / SuperCluster AI 集群分别链到哪」须能引用具体 href，与仅触发器文案失败判据互斥"),
        ],
    },
    "ocard": {
        "design": [
            (
                "三要素文案位",
                "导流卡稿面预留 o-card-title（对象名）、o-card-detail（一句话摘要）、CTA 锚文本三块可见位；禁只有封面图 + icon",
            ),
            (
                "封面图角色标注",
                "信息型封面须预留 figcaption / alt 说明位；纯装饰封面标注 aria-hidden，研发按装饰图处理",
            ),
            (
                "卡内列表版式",
                "「精品推荐 / 互动交流 / 资讯 Tab」等嵌套列表卡，稿面预留列表项标题 + 摘要 + 链接列，勿假设滑动或点击后才出现文案",
            ),
        ],
        "design_example": (
            "开发资源卡：仅 icon + 标题 → 三要素卡",
            "仅 icon + 标题",
            '<div style="border:1px solid var(--line);border-radius:8px;padding:14px;background:#fff;max-width:240px;">\n'
            '  <div style="width:36px;height:36px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;font-size:18px;">🧩</div>\n'
            '  <div style="margin-top:10px;font-weight:600;">HiDevLab-在线开发</div>\n'
            '</div>\n'
            '<p class="rf-muted" style="margin-top:8px;">整卡只有图标 + 标题，缺 o-card-detail 摘要、没有 a[href]；抓取只拿到一个标题，说不清卡片是什么、点了去哪。</p>',
            "标题 + 摘要 + 链接",
            '<a href="https://hidevlab.hiascend.com/" style="display:block;text-decoration:none;border:1px solid var(--line);border-radius:8px;padding:14px;background:#fff;max-width:260px;color:inherit;">\n'
            '  <div style="width:36px;height:36px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;font-size:18px;">🧩</div>\n'
            '  <div style="margin-top:10px;font-weight:600;">HiDevLab-在线开发</div>\n'
            '  <div style="margin-top:4px;font-size:12.5px;color:var(--muted);">提供简单、高效、易用的在线开发平台</div>\n'
            '</a>\n'
            '<p class="rf-muted" style="margin-top:8px;">整卡即一个 <code>&lt;a href&gt;</code>：点击跳转，卡面不必显示 URL，但源码里有真链接。</p>\n'
            '<p class="rf-caption" style="margin-top:8px;"><strong>要点：</strong></p>\n'
            '<ul class="rf-caption" style="margin:4px 0 0;padding-left:18px;">\n'
            '  <li>三要素齐全：标题（o-card-title）+ 一句话摘要（o-card-detail）+ 真实 a[href]。</li>\n'
            '  <li>URL 不必在卡面可见——整卡用真实 <code>&lt;a href&gt;</code> 包裹即可；但禁用 div + onclick 的整卡跳转（爬虫跟不了）。</li>\n'
            '  <li>封面图补 alt / figcaption，纯装饰图 alt=""。</li>\n'
            '</ul>',
            True,
            True,
        ),
        "content": [
            (
                "llms 补卡片入口清单",
                "首页资讯/活动 Tab 下卡片 html 未达标前，llms 可临时列出「最新发布 / 精彩活动」各卡标题 → URL；达标后以 SSR o-card 为准",
            ),
            (
                "MD 平铺资源卡",
                "按开发者页「获取开发资源」结构在 MD 写出 HiDevLab / 资源下载中心 / 昇腾镜像仓库 三卡标题、摘要与 href",
            ),
            (
                "封面图意转写",
                "课程/活动卡若用封面图，须在正文或 figcaption 复述图意，禁止「见封面」式指代",
            ),
        ],
        "content_example": (
            "首页资讯 Tab：空列表 vs llms 补位",
            "Tab 下卡片靠注入",
            "【HTML】o-scroller-container 空\n【浏览器可见】金融/SWA/CANN 资讯卡\n【缺失】llms 未列各卡标题与 URL",
            "llms 平铺默认 Tab 卡片",
            "## 社区首页 · 精彩活动\n- 昇腾AI创新大赛2026 → https://…\n- HCCL通信库创新大赛 → https://…",
            False,
            False,
        ),
        "frontend": [
            (
                "导流卡三要素 SSR",
                "每张 o-card 须输出 o-card-title + o-card-detail + a[href]（开发者页 HiDevLab 三卡已达标）；训练/推理/算子入口卡亦须补 detail 短述",
            ),
            (
                "卡内列表须进源码",
                "首页资讯 Tab 的 o-scroller-container、开发者页 o-card-content 须 SSR 列表项，禁 <!--[--><!--]--> 空壳后客户端注入",
            ),
            (
                "禁整卡 onclick",
                "发现卡用 a[href] 包裹标题与摘要，样式可保留卡片外观；纯操作区标注 data-llm-exclude",
            ),
            (
                "封面补 alt",
                "信息型封面 img 须有区分度 alt 或 figure/figcaption；装饰图 alt=\"\"",
            ),
        ],
        "frontend_example": (
            "开发者页：空 o-card-content → 全量三卡",
            "卡内列表 / 空 scroller",
            '&lt;div class="o-scroller-container"&gt;&lt;!-- 空 --&gt;&lt;/div&gt;\n&lt;div class="o-card-content"&gt;&lt;!--[--&gt;&lt;!--]--&gt;&lt;/div&gt;\n&lt;!-- 浏览器可见资讯/课程列表，源码空 --&gt;',
            "SSR title + detail + href",
            '&lt;a href="https://hidevlab.hiascend.com/"&gt;\n  &lt;div class="o-card-title"&gt;HiDevLab-在线开发&lt;/div&gt;\n  &lt;div class="o-card-detail"&gt;提供简单、高效、易用的在线开发平台&lt;/div&gt;\n&lt;/a&gt;\n&lt;div class="o-card-title"&gt;资源下载中心&lt;/div&gt;\n&lt;div class="o-card-detail"&gt;一站式资源聚合下载&lt;/div&gt;…',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取后，导流卡仍含 title + detail + href，能列表回答 problems-ocard 探针问句"),
            ("三要素齐", "开发者页 HiDevLab 三卡级：每张卡 title、detail、可跟链均在首包"),
            ("可证伪", "对「最新课程/社区活动卡片标题、摘要、URL」须能引用具体文本与 href，与 o-scroller-container 空壳失败判据互斥"),
        ],
    },
    "odatetable": {
        "design": [
            (
                "表头列须标注",
                "硬件/软件规格对照稿须明确 th 列（型号/发行版/参数项）与 td 列（CPU/内存/Kernel/GCC 等），禁把参数只放在产品渲染图或特性插画里",
            ),
            (
                "截图表标注排除",
                "设计交付标注「参数须可编辑文本表，禁截图表入库」；装饰性产品图与规格表分区",
            ),
        ],
        "design_example": (
            "集群规格：截图表 → 语义参数表",
            "参数绑在特性 PNG",
            '<div style="border:1px solid var(--line);border-radius:6px;overflow:hidden;max-width:320px;">\n'
            '  <div style="background:linear-gradient(135deg,#334155,#475569);color:#fff;padding:18px 14px;text-align:center;font-size:12.5px;line-height:1.6;">📷 规格参数（截图 / feature.png）<br>型号 · CPU · 内存 · 互联</div>\n'
            '</div>\n'
            '<p class="rf-muted" style="margin-top:8px;">参数是一张截图 / 特性配图，HTML 里没有 th/td；抓取拿不到任何单元格，无法按型号列问答。</p>',
            "表头 + 型号列参数表",
            '<table class="rf-spec">\n'
            '  <thead><tr><th>型号</th><th>CPU</th><th>内存</th><th>互联</th></tr></thead>\n'
            '  <tbody>\n'
            '    <tr><td>Atlas 900</td><td>…</td><td>…</td><td>…</td></tr>\n'
            '    <tr><td>Atlas 800</td><td>…</td><td>…</td><td>…</td></tr>\n'
            '  </tbody>\n'
            '</table>\n'
            '<p class="rf-caption" style="margin-top:8px;"><strong>要点：</strong></p>\n'
            '<ul class="rf-caption" style="margin:4px 0 0;padding-left:18px;">\n'
            '  <li>用真实 <code>&lt;table&gt;</code> + th/td，每格文本可按行列抓取问答。</li>\n'
            '  <li>文档页再镜像一份 Markdown 平行表；禁截图表、div 伪表与空 td。</li>\n'
            '</ul>',
            True,
            True,
        ),
        "content": [
            (
                "MD 平行规格表",
                "每个 HTML 规格表在文档 MD/llms 镜像一份 Markdown 表（如 CUDA Table 2 Validated OS Versions、FAQ 表1 昇腾产品系列），表头与单元格与 HTML 一致",
            ),
            (
                "表题与引用",
                "正文写清「表1 …」「Table 3 Supported Compilers」，禁止「见上表」无锚点；Agent 须能引用表题定位",
            ),
        ],
        "content_example": (
            "CUDA 指南：MD 镜像 OS 表",
            "仅 HTML 长文档",
            "【HTML】Table 2 Validated OS Versions 已在 Sphinx table\n【缺失】llms 未摘 Kernel/GCC/GLIBC 矩阵",
            "llms 平铺规格表",
            "## CUDA 13.3 · Validated OS\n| Distribution | Kernel | GCC | GLIBC |\n| RHEL 9 | 5.14… | 11.5.0 | 2.34 | …",
            False,
            False,
        ),
        "frontend": [
            (
                "语义 table SSR",
                "规格对照须 output 真实 table/thead/tbody/th/td（对标 Mintlify Custom portal Features 三列表、CUDA Table 1–4、FAQ 表1）；禁 div 网格伪表",
            ),
            (
                "禁空 td 占位",
                "集群页 spec-summary 等 table 骨架不得留空 td 等脚本填值；每格须有可读文本",
            ),
            (
                "Tab 后注入规格须 SSR",
                "型号 Tab 切换后才出现的参数矩阵，未切换页签也须在源码可读（visually-hidden 或平铺备用表）",
            ),
            (
                "caption 与 scope",
                "复杂表补 caption、th scope=\"col/row\"，合并单元格不破坏列对齐",
            ),
        ],
        "frontend_example": (
            "集群摘要表：空 td → 全量 th/td",
            "table 骨架空单元格",
            '&lt;table class="o-table-border-row"&gt;\n  &lt;tr&gt;&lt;td class="table-col-1"&gt;&lt;p&gt;&lt;/p&gt;&lt;/td&gt;&lt;td&gt;&lt;!-- 空 --&gt;&lt;/td&gt;&lt;/tr&gt;\n&lt;/table&gt;',
            "SSR 规格矩阵",
            '&lt;table&gt;\n  &lt;caption&gt;Atlas 900 vs Atlas 800 规格&lt;/caption&gt;\n  &lt;thead&gt;&lt;tr&gt;&lt;th&gt;参数&lt;/th&gt;&lt;th&gt;Atlas 900&lt;/th&gt;&lt;th&gt;Atlas 800&lt;/th&gt;&lt;/tr&gt;&lt;/thead&gt;\n  &lt;tbody&gt;&lt;tr&gt;&lt;th scope="row"&gt;CPU&lt;/th&gt;&lt;td&gt;…&lt;/td&gt;&lt;td&gt;…&lt;/td&gt;&lt;/tr&gt;…&lt;/tbody&gt;\n&lt;/table&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取后，规格表仍含 th/td 与单元格文本，能回答 problems-odatetable 探针问句"),
            ("三站互证", "与 Mintlify Features 表、CUDA Table 1–4、FAQ 表1 同级：表头 + 全行单元格在首包"),
            ("可证伪", "对「Atlas 900 vs 800 CPU/内存/互联对照」须能按列引用单元格原文，与截图表/空 td 失败判据互斥"),
        ],
    },
    "otrees": {
        "design_no_example": True,
        "design": [
            (
                "UI 基本不用改，重点在源码 + Markdown",
                "目录树的视觉与层级按常规侧栏即可，无需重新设计；真正要做的是让每个节点在 HTML 源码里是真实 <code>&lt;a href&gt;</code>、并在文档 Markdown / llms 写进对应链接。设计稿只需标注「节点 = 标题 + 可跟链」，落地交给前端 SSR 与内容清单",
            ),
        ],
        "content": [
            (
                "目录 = 嵌套列表进 llms",
                "在 llms.txt / 文档 MD 维护一份与侧栏一致的「嵌套列表 = 全量目录 + URL」，HTML 树抓不全时兜底",
            ),
            (
                "叶子标题用全称",
                "节点文本用完整文档标题（如「CANN 软件安装指南」），别用缩写 / 编号，方便 Agent 按标题定位",
            ),
        ],
        "content_example": (
            "手册目录：藏在 __NUXT_DATA__ → llms 平行目录",
            "TOC 只在 __NUXT_DATA__",
            "【Before】目录结构只序列化进 __NUXT_DATA__\nllms / 正文无等价目录清单",
            "llms 平行嵌套目录",
            "## FAQ 手册目录\n- 产品与技术常见问题\n  - [Atlas 800 常见问题](/faq/atlas800)\n  - [CANN 安装 FAQ](/faq/cann-install)\n- 开发工具 FAQ\n  - …",
            False,
            False,
        ),
        "frontend": [
            (
                "目录树 SSR 成 ul/li/a",
                "侧栏树在首包输出真实嵌套 <code>&lt;ul&gt;&lt;li&gt;&lt;a href&gt;</code>（对标 Mintlify 文档侧栏、cuQuantum 侧栏），别只留客户端 hydrate 的空容器",
            ),
            (
                "子级不靠点击挂载",
                "至少 SSR 当前分支到当前页路径；懒加载子树须有服务端渲染的降级或一次性平铺全树",
            ),
            (
                "节点用 a[href] 非 span",
                "每个叶子是真实可跟链 <code>&lt;a href&gt;</code>，展开图标另放；禁 span + onclick 假链接",
            ),
            (
                "TOC 别只进 __NUXT_DATA__",
                "目录结构须落到可爬 HTML，序列化 JSON 仅作 hydrate、不作唯一来源",
            ),
        ],
        "frontend_example": (
            "侧栏树：__NUXT_DATA__ 空壳 → SSR 嵌套 a[href]",
            "空壳容器 · 点击才挂载",
            '&lt;nav class="o-trees"&gt;&lt;/nav&gt;\n&lt;!-- 树在 __NUXT_DATA__，点击才挂载子级，无 a[href] --&gt;',
            "SSR 嵌套可跟链目录",
            '&lt;nav class="o-trees"&gt;\n  &lt;ul&gt;\n    &lt;li&gt;&lt;a href="/faq/atlas800"&gt;Atlas 800 常见问题&lt;/a&gt;&lt;/li&gt;\n    &lt;li&gt;&lt;a href="/faq/cann-install"&gt;CANN 安装 FAQ&lt;/a&gt;&lt;/li&gt;\n  &lt;/ul&gt;\n&lt;/nav&gt;',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取后，侧栏树仍含全部叶子节点的标题与 a[href]，能回答 problems-otrees 探针问句"),
            ("三站互证", "与 Mintlify 文档侧栏、cuQuantum 侧栏同级：目录树在首包可枚举叶子 URL"),
            ("可证伪", "对「某分类下所有叶子文档标题与 URL」须能给出清单，与懒加载 / __NUXT_DATA__ 失败判据互斥"),
        ],
    },
    "otoggle": {
        "intro_card": {
            "title": "为什么选择块是「视情况」——先看 Toggle 是否映射选型",
            "items": [
                (
                    "keep",
                    "映射下载 / 版本的 Toggle",
                    "要做亲和",
                    "如固件与驱动的型号 / 架构 / 安装方式：选项映射下载页或包表时，完整 option 矩阵须 SSR 或写进首包 JSON（可读 label + <code>ids=</code> 或 URL，对标 NVIDIA CUDA <code>data-react-props</code>）。",
                ),
                (
                    "strip",
                    "纯 UI 筛选 Toggle",
                    "不做亲和 · 入库剥离",
                    "不映射内容的显示切换 / 纯前端筛选，选中态不是官网知识，入库管道标 exclude；<code>?ids=</code> 编码态不能替代可读矩阵。",
                ),
            ],
        },
        "design_no_example": True,
        "design": [
            (
                "UI 基本不用改，重点在 SSR 矩阵 / 写文档",
                "Toggle 的视觉与交互按常规即可、无需重新设计；真正要做的是让映射下载 / 版本的选型矩阵 SSR 或写进首包 JSON（可读 label + <code>ids=</code> / URL），或把规格写进文档 Markdown。设计稿只需标注哪些 Toggle 映射内容、哪些是纯 UI 筛选（后者标 <code>data-llm-exclude</code>）",
            ),
        ],
    },
    "osearch": {
        "intro_card": {
            "title": "为什么搜索框是「视情况」——组件本身免改，责任在发现层",
            "items": [
                (
                    "keep",
                    "所有可搜索的 URL → sitemap / llms",
                    "硬要求",
                    "凡是搜索能命中的文档，都必须有独立可爬 URL，且收进 sitemap.xml 与 llms.txt（可配合导航 / 索引页），让 Agent 不搜索也能枚举全部文档。注意：要做亲和的是「发现层」，不是搜索框。",
                ),
                (
                    "strip",
                    "搜索框 / 搜索结果本身",
                    "永不改造 · exclude",
                    "输入框、结果列表、搜索 API 都是纯交互，别费力把它们做成可爬（结果可点击 ≠ 可被发现）；入库标 data-llm-exclude 或剥离即可。",
                ),
            ],
        },
        "design": [
            (
                "要求非搜索发现入口",
                "稿面须提供不依赖搜索的发现路径——导航、文档索引页或 sitemap 入口，别让深页只能靠搜索命中",
            ),
        ],
        "design_example": (
            "版面发现入口：只有搜索 → 导航 / 目录 + 搜索",
            "只有搜索框",
            '<div class="rf-searchbox"><span class="rf-sb-icon">🔍</span><span>搜索 CANN 文档…</span></div>\n'
            '<p class="rf-muted">版面只放了搜索框，没有导航 / 目录入口——不搜索就走不到任何文档页。</p>',
            "导航 / 目录 + 搜索",
            '<div style="display:flex;gap:12px;align-items:flex-start;">\n'
            '  <div style="min-width:118px;border:1px solid var(--line);border-radius:6px;padding:8px 10px;background:#fff;">\n'
            '    <p class="rf-sidebar-title">文档目录</p>\n'
            '    <ul class="rf-nav-links">\n'
            '      <li><a href="#">快速开始</a></li>\n'
            '      <li><a href="#">安装部署</a></li>\n'
            '      <li><a href="#">API 参考</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '  <div style="flex:1;">\n'
            '    <div class="rf-searchbox"><span class="rf-sb-icon">🔍</span><span>搜索…</span></div>\n'
            '    <p class="rf-muted" style="margin-top:8px;">版面同时预留左侧目录（非搜索入口），不靠搜索也能逐层浏览到每篇文档；搜索只是加速查找。</p>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
        ),
        "content": [
            (
                "所有可搜索 URL 进 sitemap / llms",
                "凡搜索能命中的文档，都要有独立可爬 URL 且收进 sitemap.xml 与 llms.txt；新增 / 下线同步更新，确保不搜索也能枚举全部文档",
            ),
            (
                "检索范围写进正文",
                "把「本站包含哪些文档 / 版本」写成可引用的正文或文档索引页，别只塞在搜索框 placeholder（如「搜索 CANN 文档」）里",
            ),
            (
                "导航 / 索引补发现路径",
                "关键文档除搜索外，另有导航、目录或索引页可跟链到达，避免深页只能靠搜索命中",
            ),
        ],
        "content_example": (
            "文档发现：搜索兜底 → sitemap/llms 全量",
            "深页只能靠站内搜索",
            "【现状】部分 CANN 文档仅站内搜索可达\n【缺失】sitemap / llms 未列这些文档 URL",
            "sitemap + llms 平铺清单",
            "# llms.txt\n## CANN 文档\n- 安装指南 → https://…/document/cann-install\n- 算子开发 → https://…/document/operator\n（sitemap.xml 同步全量 <loc>）",
            False,
            False,
        ),
        "frontend": [
            (
                "每篇文档独立可爬 URL",
                "文档页 SSR 出独立、稳定、可跟链的 URL（非 ?q= 搜索态、非点击后才渲染）；禁把正文只藏在搜索结果里",
            ),
            (
                "sitemap 自动输出",
                "构建时生成 sitemap.xml 覆盖全部文档 URL 并在 robots 声明，供爬虫与 Agent 枚举；无需为搜索结果页做特殊处理",
            ),
            (
                "搜索框控件可 exclude",
                "search input / 按钮 / 建议下拉是纯交互控件，入库管道可标 data-llm-exclude；发现层责任由 URL + sitemap 承担，不依赖搜索",
            ),
        ],
        "frontend_example": (
            "发现层：搜索黑盒 → 可爬 URL + sitemap",
            "内容锁在搜索里",
            '<div class="o-search">…</div>\n<!-- 深页无独立 a[href]，仅搜索 API 可达 -->',
            "SSR URL + sitemap 枚举",
            '<a href="/document/cann-install">CANN 安装指南</a>\n<!-- sitemap.xml -->\n<url><loc>https://…/document/cann-install</loc></url>',
            False,
            False,
        ),
        "acceptance": [
            ("静态可达", "禁 JS 抓取后，不用搜索也能从导航 / sitemap / llms 枚举全部文档 URL，回答 problems-osearch 探针问句"),
            ("清单齐全", "sitemap.xml 与 llms.txt 覆盖全部文档 URL，新增页同步收录"),
            ("可证伪", "对「不用搜索列出所有 CANN 安装文档 URL」须能给出清单，与仅靠搜索的失败判据互斥"),
        ],
    },
    "oselect": {
        "intro_card": {
            "title": "为什么选择器是「视情况」——先看选项是否映射内容",
            "items": [
                (
                    "keep",
                    "映射文档 / 版本的选项",
                    "要做亲和",
                    "如固件与驱动的型号 / 架构 / 安装方式：选项对应下载页或文档时，完整 option 文本与落地 URL（含 <code>?ids=</code>）须 SSR 可抓。",
                ),
                (
                    "strip",
                    "纯表单筛选选项",
                    "不做亲和 · 入库剥离",
                    "排序、纯前端筛选等不含信息架构的 select，选项态不是官网知识，入库管道可剥离。",
                ),
            ],
        },
        "design_no_example": True,
        "design": [
            (
                "规格别锁在「选完才显示」",
                "设计稿要求：选项映射的规格 / 内容要有一份不依赖选择就可读的呈现——最简单是把规格写进文档页 Markdown（有独立可爬 URL），别让参数只在选了某项后才由 JS 注入；Select 保持纯交互、选项态不入库",
            ),
        ],
        "content": [
            (
                "规格写进文档 Markdown",
                "选项映射的规格以 Markdown 平行表写进文档页（有独立可爬 URL），表头与单元格和产品页选项一致；产品页 Select 仅筛选、选项态不入库",
            ),
            (
                "选项 → 落地 URL 可查",
                "每个映射内容的选项对应可访问的文档 / 下载 URL（含 <code>?ids=</code>），在正文或 llms 可查，别只靠选中态还原",
            ),
        ],
        "content_example": (
            "选型规格：绑在选择态 → 文档 Markdown",
            "规格锁在选择后",
            "产品页规格靠选中某型号后 JS 注入；\n文档 / MD 未收录该规格 → 禁 JS 抓不到参数。",
            "文档 Markdown 平行表",
            "## Atlas 800 规格\n| 参数 | 值 |\n| NPU | 8 × 昇腾 |\n| 内存 | 1TB |\n（文档页独立 URL，可爬）",
            False,
            False,
        ),
        "frontend": [
            (
                "关键 option 进首包（SSR）",
                "映射文档 / 下载的 option 以可读 label + ids / URL 直接 SSR 进首包，别只靠选中后 JS 注入——禁 JS 时也能读到型号 / 版本与落地地址",
            ),
            (
                "llms 补 option → URL 映射",
                "无法 SSR 时，在 llms.txt / 正文维护「选项 → 落地 URL（含 <code>?ids=</code>）」映射表，供 Agent 不选也能还原",
            ),
            (
                "纯交互态可 exclude",
                "select / 建议下拉等纯交互控件标 <code>data-llm-exclude</code>，与承载知识的正文 / 映射区分，避免选项态污染入库",
            ),
        ],
        "frontend_example": (
            "选项可达：JS 注入 → SSR option + 落地 URL",
            "首包缺 option / 靠 JS",
            '<select id="model"></select>\n<!-- option 由 JS 注入；规格靠选中后渲染，首包无可读 label / URL -->',
            "SSR option + 落地 URL",
            '<select>\n  <option value="atlas800?ids=A1">Atlas 800（8×昇腾）</option>\n</select>\n<a href="/download?ids=A1">Atlas 800 固件与驱动</a>\n<!-- 或 llms.txt: Atlas 800 → /download?ids=A1 -->',
            False,
            False,
        ),
    },
    "orate": {
        "intro_card": {
            "title": "为什么评分是「视情况」——先分清「分数」与「操作文案」",
            "items": [
                (
                    "keep",
                    "评分数字（社会证明）",
                    "要做亲和",
                    "平均分 / 评分人数若在静态 HTML 可见，可作社会证明被引用，宜 SSR 成可读文本。",
                ),
                (
                    "strip",
                    "「我要评分」操作文案",
                    "不做亲和 · 入库剥离",
                    "评分按钮是操作 CTA、不是质量规格，入库应过滤；且勿与官方质量认证混淆（认证说明另走正文文档）。",
                ),
            ],
        },
        "design": [
            (
                "分数留成可见文本位",
                "设计稿为「平均分 + 评分人数」预留可见文本位（如「4.6 分 · 128 人评分」），别只画星标图标——数字要能作为社会证明被读到",
            ),
            (
                "评分按钮标纯交互",
                "「我要评分 / 提交评分」等操作按钮在稿面标「纯交互 · 入库排除」，与分数文本分区；勿与官方质量认证混淆，认证说明另走正文文档",
            ),
        ],
        "design_example": (
            "评分：只有星标 → 可读分数 + 角色标注",
            "只有星标图标",
            '<div style="display:flex;align-items:center;gap:8px;">\n'
            '  <span style="color:#f5a623;font-size:18px;">★★★★☆</span>\n'
            '  <button style="border:1px solid var(--line);border-radius:6px;padding:4px 10px;background:#fff;">我要评分</button>\n'
            '</div>\n'
            '<p class="rf-muted" style="margin-top:8px;">只有星标图标 +「我要评分」按钮；平均分 / 评分人数没有可读文本——禁 JS 抓不到分数，还容易把操作按钮误当质量规格。</p>',
            "可读分数 + 角色标注",
            '<div style="display:flex;align-items:center;gap:10px;">\n'
            '  <span style="color:#f5a623;font-size:18px;" aria-hidden="true">★★★★☆</span>\n'
            '  <span style="font-weight:600;">4.6 分</span>\n'
            '  <span class="rf-muted">· 128 人评分</span>\n'
            '</div>\n'
            '<div style="margin-top:8px;">\n'
            '  <button style="border:1px solid var(--line);border-radius:6px;padding:4px 10px;background:#fff;color:var(--muted);">我要评分</button>\n'
            '</div>\n'
            '<p class="rf-caption" style="margin-top:8px;"><strong>要点：</strong></p>\n'
            '<ul class="rf-caption" style="margin:4px 0 0;padding-left:18px;">\n'
            '  <li>「4.6 分 · 128 人评分」作为可读文本 SSR 可抓，可作社会证明被引用。</li>\n'
            '  <li>「我要评分」按钮标 <code>data-llm-exclude</code>，与官方质量认证区分、不入库。</li>\n'
            '</ul>',
            True,
            True,
        ),
    },
    "ocascader": {
        "intro_card": {
            "title": "为什么级联选择是「视情况」——先分清「内容路径」与「表单字段」",
            "items": [
                (
                    "keep",
                    "映射内容路径的级联",
                    "要做亲和",
                    "各级若代表文档分类 / 地域内容路径，则各级 option 文本须源码可读、最好带落地链；面板勿悬停/点击才挂载。",
                ),
                (
                    "strip",
                    "纯地址 / 表单字段级联",
                    "不做亲和 · 入库剥离",
                    "省市区等纯表单级联不是信息架构，选项态不承载官网知识，入库可剥离。",
                ),
            ],
        },
        "design_no_example": True,
        "design": [
            (
                "UI 基本不用改，重点在源码 + 目录",
                "级联的视觉与交互按常规即可，无需重新设计；真正要做的是让各级 option 在 HTML 源码里是真实 <code>&lt;a href&gt;</code>、并在文档 Markdown / llms 维护一份等价的分类目录。设计稿只需标注「内容路径型级联 = 各级可读 + 可跟链」，落地交给前端 SSR 与内容清单",
            ),
        ],
        "content": [
            (
                "分类目录 = 嵌套列表进 llms",
                "把级联映射的内容路径在 llms.txt / 文档 MD 写成「嵌套列表 = 全量分类 + URL」，与面板层级一致，面板抓不全时兜底",
            ),
            (
                "各级用全称",
                "各级 option 用完整分类 / 文档名（如「CANN 安装指南」），别用编号 / value，方便 Agent 按名定位",
            ),
        ],
        "content_example": (
            "内容路径：藏在面板 → llms 平行目录",
            "路径只在级联面板里",
            "【Before】分类层级只在级联面板 JS 态里\nllms / 正文无等价分类目录",
            "llms 平行分类目录",
            "## CANN 文档分类\n- CANN\n  - 安装部署\n    - [CANN 安装指南](/document/cann/install/guide)\n    - [驱动安装](/document/cann/install/driver)\n  - API 参考\n    - …",
            False,
            False,
        ),
        "frontend": [
            (
                "各级 option SSR 成 a[href]",
                "内容路径型级联的各级选项在首包输出真实 <code>&lt;a href&gt;</code>，别只在悬停 / 点击后由 JS 挂载",
            ),
            (
                "面板不靠悬停挂载",
                "至少 SSR 当前路径分支；懒加载子级须有服务端降级或一次性平铺",
            ),
            (
                "表单级联可 exclude",
                "省市区等纯表单字段级联标 <code>data-llm-exclude</code>，与承载信息架构的内容级联区分",
            ),
        ],
        "frontend_example": (
            "级联面板：悬停挂载 → SSR 各级 a[href]",
            "空壳面板 · 悬停才挂载",
            '&lt;div class="o-cascader"&gt;&lt;/div&gt;\n&lt;!-- 各级 span + onclick，悬停才挂载，无 a[href] --&gt;',
            "SSR 各级可跟链选项",
            '&lt;div class="o-cascader"&gt;\n  &lt;a href="/document/cann"&gt;CANN&lt;/a&gt;\n  &lt;a href="/document/cann/install"&gt;安装部署&lt;/a&gt;\n  &lt;a href="/document/cann/install/guide"&gt;CANN 安装指南&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
        ),
    },
    "otag": {
        "intro_card": {
            "title": "为什么标签是「视情况」——先分清「语义标签」与「装饰标签」",
            "items": [
                (
                    "keep",
                    "版本 / 状态语义标签",
                    "要做亲和",
                    "如「CANN 8.0」「已认证」「停止维护」等承载事实的标签，文本须进 HTML 可读，并在正文有对应定义 / 依据。",
                ),
                (
                    "strip",
                    "营销 / 装饰标签",
                    "不做亲和 · 入库剥离",
                    "「热门」「新品」等无规格定义的营销口号标签不是事实，入库管道宜剥离，别当官方结论。",
                ),
            ],
        },
        "design_no_example": True,
        "design": [
            (
                "UI 基本不用改，重点在正文定义 + 装饰剥离",
                "现有标签组件本身已是可读文字、无需改视觉；真正要做的是给版本 / 状态类语义标签在正文写清定义 / 时间点，并把「热门 / 新品」等营销装饰标签在入库管道剥离。设计稿只需标注哪些是语义标签、哪些是装饰标签",
            ),
        ],
        "content": [
            (
                "语义标签配正文定义",
                "版本 / 状态标签在正文或文档写清官方定义（如「停止维护 = 不再提供补丁，截止 2025-12」），别让标签成为无依据的孤立结论",
            ),
            (
                "营销标签不入正文事实",
                "「热门 / 推荐」等营销标签不写进规格正文、不当事实来源",
            ),
        ],
        "content_example": (
            "状态标签：孤立色块 → 正文有定义",
            "标签无正文依据",
            "【Before】卡片打「停止维护」标签\n正文 / 文档无对应定义或截止时间",
            "正文写清定义",
            "## 版本状态说明\n- 停止维护：不再提供补丁与安全更新，截止 2025-12\n- 在维：持续更新（当前 CANN 8.0）",
            False,
            False,
        ),
        "frontend": [
            (
                "语义标签文本 SSR 可读",
                "版本 / 状态标签的文字在首包 HTML 可读（非纯 background-color / icon font），保证状态语义能被抓取",
            ),
            (
                "装饰标签可 exclude",
                "营销 / 装饰标签标 <code>data-llm-exclude</code> 或在管道剥离，避免「热门」等口号被当作官方事实入库",
            ),
        ],
        "frontend_example": (
            "标签：全部进库 → 语义留、装饰 exclude",
            "语义 / 装饰混进库",
            '&lt;span class="tag"&gt;停止维护&lt;/span&gt;\n&lt;span class="tag"&gt;热门&lt;/span&gt;\n&lt;!-- 两类标签都被当事实入库 --&gt;',
            "装饰标 exclude",
            '&lt;span class="tag"&gt;停止维护&lt;/span&gt;\n&lt;span class="tag tag--promo" data-llm-exclude&gt;热门&lt;/span&gt;\n&lt;!-- 语义标签入库、营销标签剥离 --&gt;',
            False,
            False,
        ),
    },
    "odialog": {
        "intro_card": {
            "title": "为什么对话框是「视情况」——先分清「含关键说明」与「纯确认框」",
            "items": [
                (
                    "keep",
                    "含关键说明的对话框",
                    "要做亲和",
                    "安装步骤、活动规则等唯一说明若在弹层，须 SSR 进首包或同步到正文页；DOM 文本勿被 <code>aria-hidden</code> 删除。",
                ),
                (
                    "strip",
                    "纯确认框",
                    "不做亲和 · 入库剥离",
                    "「确定 / 取消 / 我知道了」这类无内容的 noop 确认框不承载知识，入库管道可过滤。",
                ),
            ],
        },
        "design_no_example": True,
        "design": [
            (
                "UI 不用改，重点在 SSR + 正文双写",
                "对话框的视觉与交互按常规即可；真正要做的是让含关键说明（安装步骤 / 活动规则）的弹层内容进首包 SSR，或在正文页写一份等价说明。设计稿只需标注「关键说明勿只放弹层」，落地交给前端与内容",
            ),
        ],
        "content": [
            (
                "关键说明正文 duplicate",
                "安装步骤 / 活动规则等唯一说明在正文页或文档也写一份可引用文本，别让弹层成为唯一来源",
            ),
            (
                "纯确认框不入库",
                "「确定 / 取消 / 我知道了」这类 noop 确认框不承载知识，内容清单不收录",
            ),
        ],
        "content_example": (
            "安装步骤：只在弹层 → 正文也有一份",
            "步骤只在 dialog",
            "【Before】完整安装步骤只在「安装指引」弹层\n正文 / 文档无等价说明",
            "正文 duplicate",
            "## CANN 安装步骤\n1. 下载对应版本固件与驱动\n2. 校验依赖（GCC / GLIBC）\n3. 执行安装脚本 …\n（正文可引用，弹层同源）",
            False,
            False,
        ),
        "frontend": [
            (
                "含内容的 dialog SSR 进首包",
                "承载关键说明的对话框内容在首包 HTML 就存在（可默认视觉隐藏），别等点击才由 JS 注入",
            ),
            (
                "勿用 aria-hidden 删文本",
                "弹层文本保留在 DOM，别在抓取时被移除导致为空",
            ),
            (
                "纯确认框可 exclude",
                "noop 确认框标 <code>data-llm-exclude</code>，避免「我知道了」等噪声进库",
            ),
        ],
        "frontend_example": (
            "对话框：点击才注入 → SSR 首包可读",
            "点击才注入",
            '&lt;div class="o-dialog" hidden&gt;&lt;/div&gt;\n&lt;!-- 步骤点击「安装指引」后才 JS 注入 --&gt;',
            "SSR 首包含文本",
            '&lt;div class="o-dialog" hidden&gt;\n  &lt;h3&gt;CANN 安装步骤&lt;/h3&gt;\n  &lt;ol&gt;&lt;li&gt;下载固件与驱动&lt;/li&gt;…&lt;/ol&gt;\n&lt;/div&gt;\n&lt;!-- 内容首包可读，仅视觉隐藏 --&gt;',
            False,
            False,
        ),
    },
    "opopover": {
        "intro_card": {
            "title": "为什么气泡卡片是「视情况」——先分清「字段定义」与「装饰提示」",
            "items": [
                (
                    "keep",
                    "含字段定义的气泡",
                    "要做亲和",
                    "重要字段 / 规格定义（如「CANN 版本」）若只在悬停气泡，须在正文重复一份，或 popover 内容进首包可抓。",
                ),
                (
                    "strip",
                    "装饰性 tooltip",
                    "不做亲和",
                    "纯提示、装饰性 tooltip 不含唯一知识，入库可忽略；关键在于正文是否另有一份可读定义。",
                ),
            ],
        },
        "design": [
            (
                "关键定义留成可见旁注",
                "重要字段定义（如「CANN 版本」）别只放悬停气泡，稿面为其预留一处可见旁注 / 正文说明；气泡只作补充",
            ),
            (
                "区分定义气泡与装饰 tooltip",
                "承载字段定义的气泡要在正文另写一份；纯装饰 tooltip 标「纯提示 · 入库排除」",
            ),
        ],
        "design_example": (
            "字段说明：只在悬停 → 正文旁注 + 气泡",
            "定义只在悬停气泡",
            '<div style="display:flex;align-items:center;gap:6px;">\n'
            '  <span>CANN 版本</span>\n'
            '  <span style="width:16px;height:16px;border-radius:50%;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:var(--muted);">?</span>\n'
            '</div>\n'
            '<p class="rf-muted" style="margin-top:8px;">字段定义只在悬停「?」时弹出气泡；不悬停 / 禁 JS 时正文没有这份说明，抓取读不到定义。</p>',
            "正文旁注 + 气泡补充",
            '<div style="display:flex;align-items:center;gap:6px;">\n'
            '  <span>CANN 版本</span>\n'
            '  <span style="width:16px;height:16px;border-radius:50%;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:var(--muted);">?</span>\n'
            '</div>\n'
            '<p class="rf-caption" style="margin-top:8px;">CANN 版本：昇腾异构计算架构的版本号，决定可用算子与框架适配范围（当前 8.0）。</p>\n'
            '<p class="rf-muted" style="margin-top:4px;">定义写成可见旁注（正文一份），气泡只作 hover 补充。</p>',
            True,
            True,
        ),
        "content": [
            (
                "字段定义正文 duplicate",
                "悬停气泡里的字段 / 规格定义在正文或文档也写一份可引用文本，气泡不作唯一来源",
            ),
            (
                "装饰 tooltip 可忽略",
                "纯提示 tooltip 不含唯一知识，入库可忽略；关键看正文是否另有定义",
            ),
        ],
        "content_example": (
            "字段定义：只在气泡 → 正文旁注",
            "定义只在 popover",
            "【Before】「CANN 版本」定义只在悬停气泡\n正文无等价说明",
            "正文写一份定义",
            "## 字段说明\n- CANN 版本：昇腾异构计算架构版本号，决定算子与框架适配范围（当前 8.0）",
            False,
            False,
        ),
        "frontend": [
            (
                "含定义的 popover SSR 进首包",
                "承载字段定义的气泡内容在首包 HTML 就存在（可视觉隐藏），别等 hover 才由 JS 挂载",
            ),
            (
                "勿 aria-hidden 删文本",
                "气泡文本保留在 DOM，避免抓取为空",
            ),
            (
                "装饰 tooltip 可 exclude",
                "纯装饰 tooltip 标 <code>data-llm-exclude</code>",
            ),
        ],
        "frontend_example": (
            "气泡：hover 才挂载 → SSR 首包可读",
            "hover 才挂载",
            '&lt;span class="o-popover"&gt;&lt;/span&gt;\n&lt;!-- 定义 hover 时才 JS 注入，无 SSR 文本 --&gt;',
            "SSR 首包含定义",
            '&lt;span class="o-popover" role="note"&gt;\n  CANN 版本：异构计算架构版本号（当前 8.0）\n&lt;/span&gt;\n&lt;!-- 首包可读，视觉上悬停展开 --&gt;',
            False,
            False,
        ),
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


def principles_meta_line(d: dict[str, Any], slug: str) -> str:
    if d.get("hide_sample_meta"):
        return ""
    url = d.get("sample_url")
    label = d.get("sample_label")
    if not (url and label):
        return ""
    meta = f'对应页面：<a href="{url}" target="_blank" rel="noopener">{esc(label)}</a>'
    return f'        <span class="page-desc-line">{meta}</span>'


def principles_framework_block() -> str:
    return ""


def render_intro_card(d: dict[str, Any]) -> str:
    card = d.get("intro_card")
    if not card:
        return ""
    if card.get("plain"):
        rows = "\n".join(
            f"""        <div class="scene-judge-item">
          <p class="scene-judge-head"><strong>场景{i}·{esc(label)}</strong><span class="rsc-verdict rsc-verdict--{esc(kind)}">{esc(verdict)}</span></p>
          <p class="scene-judge-body">{body}</p>
        </div>"""
            for i, (kind, label, verdict, body) in enumerate(card["items"], 1)
        )
        return f"""    <section class="section" id="scene-judge">
      <h2>{esc(card["title"])}</h2>
{rows}
    </section>
"""
    items = "\n".join(
        f"""        <div class="role-split-item role-split-item--{esc(kind)}">
          <h4><span class="rsc-name">{esc(label)}</span><span class="rsc-verdict rsc-verdict--{esc(kind)}">{esc(verdict)}</span></h4>
          <p>{body}</p>
        </div>"""
        for kind, label, verdict, body in card["items"]
    )
    return f"""    <div class="role-split-card">
      <p class="rsc-title">{esc(card["title"])}</p>
      <div class="role-split-grid">
{items}
      </div>
    </div>
"""


def render_design_section(d: dict[str, Any], design_cmp: str) -> str:
    h2 = f"设计UI调整{esc(d.get('design_heading_suffix', ''))}"
    if d.get("design_none"):
        return f"""    <section class="section" id="design-ui">
      <h2>{h2}</h2>
      <p class="principle-none">无</p>
    </section>"""
    if d.get("design_no_example"):
        return f"""    <section class="section" id="design-ui">
      <h2>{h2}</h2>
      <h3 id="design-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["design"])}
      </ul>
    </section>"""
    return f"""    <section class="section" id="design-ui">
      <h2>{h2}</h2>
      <h3 id="design-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["design"])}
      </ul>
      <h3 id="design-example">调整示例</h3>
{design_cmp}
    </section>"""


def render_content_section(d: dict[str, Any], content_cmp: str) -> str:
    h2 = f"文档内容调整{esc(d.get('content_heading_suffix', ''))}"
    if d.get("content_no_example"):
        return f"""    <section class="section" id="content-adjust">
      <h2>{h2}</h2>
      <h3 id="content-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["content"])}
      </ul>
    </section>"""
    return f"""    <section class="section" id="content-adjust">
      <h2>{h2}</h2>
      <h3 id="content-suggestions">调整建议</h3>
      <ul class="principle-suggestions">
{li_items(d["content"])}
      </ul>
      <h3 id="content-example">调整示例</h3>
{content_cmp}
    </section>"""


def render_principles_body(data: dict[str, Any], slug: str, name: str) -> str:
    d = data
    ce = d["content_example"]
    fe = d["frontend_example"]

    design_cmp = ""
    de = d.get("design_example")
    if de and not d.get("design_none") and not d.get("design_no_example"):
        design_cmp = compare_block(
            de[0], de[1], de[2], de[3], de[4],
            before_is_frame=de[5], after_is_frame=de[6],
            before_caption=(de[7] if len(de) > 7 else None),
            after_caption=(de[8] if len(de) > 8 else None),
            side_by_side=bool(d.get("design_example_side_by_side")),
        )
        extra_de = d.get("design_examples_extra")
        if extra_de:
            design_cmp += "\n" + compare_block(
                extra_de[0], extra_de[1], extra_de[2], extra_de[3], extra_de[4],
                before_is_frame=extra_de[5], after_is_frame=extra_de[6], example_num=2,
            )
    content_cmp = ""
    if not d.get("content_no_example"):
        content_cmp = compare_block(
            ce[0], ce[1], ce[2], ce[3], ce[4],
            before_is_frame=ce[5], after_is_frame=ce[6],
            before_prefix=d.get("content_example_before_prefix", "错误示范"),
            after_prefix=d.get("content_example_after_prefix", "推荐做法"),
            before_mark=bool(d.get("content_example_before_mark", True)),
            after_mark=bool(d.get("content_example_after_mark", True)),
            after_sections=d.get("content_example_after_sections"),
        )
        extra_ce = d.get("content_examples_extra")
        if extra_ce:
            content_cmp += "\n" + compare_block(
                extra_ce[0], extra_ce[1], extra_ce[2], extra_ce[3], extra_ce[4],
                before_is_frame=extra_ce[5], after_is_frame=extra_ce[6],
                before_prefix=d.get("content_example_before_prefix", "错误示范"),
                after_prefix=d.get("content_example_after_prefix", "推荐做法"),
                before_mark=bool(d.get("content_example_before_mark", True)),
                after_mark=bool(d.get("content_example_after_mark", True)),
                example_num=2,
            )
    frontend_cmp = compare_block(
        fe[0], fe[1], fe[2], fe[3], fe[4],
        before_is_frame=fe[5], after_is_frame=fe[6],
        before_caption=(fe[7] if len(fe) > 7 else None),
        after_caption=(fe[8] if len(fe) > 8 else None),
        before_prefix=d.get("frontend_example_before_prefix", "错误示范"),
        after_prefix=d.get("frontend_example_after_prefix", "推荐做法"),
        before_mark=bool(d.get("frontend_example_before_mark", True)),
        after_mark=bool(d.get("frontend_example_after_mark", True)),
    )

    fe_lead = d.get("frontend_lead")
    frontend_lead_html = (
        f'      <p class="principle-lead">{fe_lead}</p>\n      <p class="principle-subhead">具体要求：</p>\n'
        if fe_lead else ""
    )

    return f"""{render_page_header(d["title"], d["one_liner"], slug, name, d)}

{render_intro_card(d)}
{principles_framework_block()}

{render_design_section(d, design_cmp)}

{render_content_section(d, content_cmp)}

    <section class="section" id="frontend-adjust">
      <h2>前端调整{esc(d.get('frontend_heading_suffix', ''))}</h2>
      <h3 id="frontend-suggestions">调整建议</h3>
{frontend_lead_html}      <ul class="principle-suggestions">
{li_items(d["frontend"])}
      </ul>
      <h3 id="frontend-example">调整示例</h3>
{frontend_cmp}
    </section>"""


def render_no_aff_body(data: dict[str, Any], slug: str, name: str) -> str:
    comp = name.split()[0] if name else slug
    skip = no_aff_skip_example(comp)
    skip_cmp = compare_block("管道：收录 → 跳过", skip[0], skip[1], skip[2], skip[3])

    skip_items = [("无独立改动，管道可跳过", "控件态/placeholder/角标等非知识正文，设计交付无需额外亲和标注")]

    return f"""{render_page_header(data["title"], data["one_liner"], slug, name, data)}

{principles_framework_block()}

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
    </section>"""


def render_page(slug: str, name: str, data: dict[str, Any]) -> str:
    body = render_no_aff_body(data, slug, name) if data.get("no_aff") else render_principles_body(data, slug, name)
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
<div class="detail-head-bar" aria-label="组件详情导航">
  <div class="modal-title-wrap">
    <a class="back-link" href="community-ui.html" aria-label="返回组件亲和"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 6L9 12l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
    <span class="title-divider" aria-hidden="true"></span>
    <div class="modal-title">组件亲和原则</div>
  </div>
  <nav class="detail-head-tabs modal-actions" aria-label="视图切换">
    <a href="problems-{slug}.html">实测问题</a>
    <a href="{phref}" class="active">亲和原则</a>
  </nav>
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
{SHOT_MODAL_HTML}
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


def patch_remove_acceptance_section(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    patched, n = re.subn(
        r'\n    <section class="section" id="acceptance">.*?</section>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if n == 0:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


def patch_remove_section_leads(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    patched, n = re.subn(
        r'\n      <p class="section-lead">.*?</p>',
        "",
        text,
        flags=re.DOTALL,
    )
    if n == 0:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


def patch_remove_principles_framework(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    patched, n = re.subn(
        r'\n    <p class="principles-framework">.*?</p>',
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if n == 0:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


def patch_principles_delivery_framework(path: Path) -> bool:
    return False


def patch_principles_css(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "  .principles-framework {" in text:
        return False
    if "  .principle-suggestions {" in text:
        framework_css = """
  .principles-framework {
    margin: 0 0 40px;
    padding: 14px 18px;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    font-size: 14px;
    line-height: 22px;
    color: var(--muted);
  }
  .main-content > .principles-framework {
    width: 100%; max-width: var(--content-max); margin-inline: 0;
    padding-left: 0; padding-right: 0; box-sizing: border-box;
  }
  .principles-framework strong { color: var(--text); font-weight: 600; }
"""
        patched = text.replace("</style>", framework_css + "\n</style>", 1)
    else:
        patched = text.replace("</style>", PRINCIPLES_CSS_EXTRA + "\n</style>", 1)
    if patched == text:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


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
                patch_principles_css(out)
                patch_principles_delivery_framework(out)
                patch_remove_section_leads(out)
                patch_remove_acceptance_section(out)
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
    framework_removed = 0
    for _, slug, _ in all_components():
        path = principles_out_path(slug)
        if path.exists():
            if patch_sidebar_in_file(path, slug):
                sidebars_patched += 1
            if patch_principles_topbar(path, slug):
                topbars_patched += 1
            if patch_remove_principles_framework(path):
                framework_removed += 1

    aff = DOCS / "principles-affinity.html"
    if aff.exists() and patch_remove_principles_framework(aff):
        framework_removed += 1

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
    print(f"Principles framework blocks removed: {framework_removed}")
    print(f"Problems topbars patched: {problems_topbars}")
    print(f"Total principles files: {len(list(DOCS.glob('principles-*.html'))) + (1 if OCAROUSEL_CANONICAL.exists() else 0)}")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
