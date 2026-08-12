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

SKIP_BODY: set[str] = set()  # all principles pages generated from overrides

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

  .comp-sidebar { overflow-anchor: none; }
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
<script>
(function () {
  var sidebar = document.querySelector('.comp-sidebar');
  if (!sidebar) return;
  var key = 'geo-comp-sidebar-scroll';
  var y = null;
  try {
    var q = new URLSearchParams(location.search).get('sb');
    if (q !== null && q !== '') y = parseInt(q, 10);
  } catch (e) {}
  if (y === null || isNaN(y)) {
    try {
      var saved = sessionStorage.getItem(key);
      if (saved !== null) y = parseInt(saved, 10);
    } catch (e) {}
  }
  if (y === null || isNaN(y)) y = null;

  function restore() {
    if (y === null) return;
    sidebar.scrollTop = y;
  }
  restore();
  requestAnimationFrame(function () {
    restore();
    requestAnimationFrame(restore);
  });
  window.addEventListener('pageshow', restore);
  window.addEventListener('load', restore);
  var t0 = Date.now();
  var iv = setInterval(function () {
    restore();
    if (Date.now() - t0 > 600) clearInterval(iv);
  }, 40);

  try {
    if (new URLSearchParams(location.search).has('sb')) {
      var u = new URL(location.href);
      u.searchParams.delete('sb');
      history.replaceState(null, '', u.pathname + u.search + u.hash);
    }
  } catch (e) {}

  function persist() {
    y = sidebar.scrollTop;
    try { sessionStorage.setItem(key, String(y)); } catch (e) {}
  }
  sidebar.addEventListener('scroll', persist, { passive: true });

  function stampHref(a) {
    persist();
    try {
      var raw = a.getAttribute('href') || '';
      var hash = '';
      var hi = raw.indexOf('#');
      if (hi >= 0) { hash = raw.slice(hi); raw = raw.slice(0, hi); }
      var qi = raw.indexOf('?');
      if (qi >= 0) raw = raw.slice(0, qi);
      if (raw && raw.indexOf('http') !== 0) {
        a.setAttribute('href', raw + '?sb=' + String(sidebar.scrollTop) + hash);
      }
    } catch (e) {}
  }
  sidebar.querySelectorAll('.comp-nav a[href]').forEach(function (a) {
    a.addEventListener('pointerdown', function () { stampHref(a); }, true);
    a.addEventListener('click', function () { stampHref(a); }, true);
  });
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
    return f"principles-{slug}.html"


def principles_out_path(slug: str) -> Path:
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
    content_sidebar = getattr(_probe_mod, "CONTENT_SIDEBAR", None)
    groups = list(GROUPS) + ([content_sidebar] if content_sidebar else [])
    for group, items in groups:
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
        "otrees": "同页切换内容树须可读",
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
        "onavigation": "顶栏<strong>站点入口</strong>（文档 / 开发者 / 下载等）及悬停面板子链须为可跟 <code>a[href]</code> 并进首包；搜索 / 换肤 / 语言等纯操作控件见下方场景判断。",
        "ofooternav": "社区首页页脚须把<strong>五列导航与法律声明 / 联系我们等写成可跟链接</strong>（a[href]），列名稳定；并同步进 llms/sitemap，作为顶栏之外的第二发现层。",
        "obutton": "社区首页首屏 CTA（立即查看 / 了解更多等）须用<strong>可抓 a[href]</strong>；纯提交/关闭类 button 管道宜剥离（对标 Mintlify hero、NVIDIA en-sg 首屏 CTA）。",
        "olink": "正文与导航链接须带<strong>真实 a[href]</strong>；锚文本宜自描述（禁仅「软件介绍↗」）；禁 JSON/onclick/span 伪链（昇腾训练旅程矩阵须 SSR 链化）。",
        "odropdown": "下拉菜单子项须在<strong>首包 HTML 可读</strong>（a[href]+可见文案）；禁仅触发器、portal 延迟挂或外部 JSON 菜单（昇腾「更多产品」/ Mintlify Products / NVIDIA Resources 均须 SSR 链化）。",
        "otrees": "同页切换的文档树：节点<strong>不必都有 URL</strong>；各内容块须<strong>首包 SSR</strong>（可用隐藏，勿点击后才注入）。跳转型手册目录见 <a href=\"principles-omenu.html\">OMenu</a>。",
        "osearch": "搜索框本身<strong>不做亲和改造</strong>（纯交互，入库剥离）；真正的硬要求是<strong>所有可搜索的 URL 都要进 sitemap / llms</strong>，让 Agent 不靠搜索也能发现全部文档。",
        "oselect": "若选项映射文档/版本，<strong>选项文本与落地页须可证伪</strong>；纯表单 select 管道可跳过。",
        "otoggle": "下载/版本页 Toggle 若映射 OS、架构、安装方式等选型，<strong>完整 option 矩阵须 SSR 或写进首包 JSON</strong>（对标 NVIDIA CUDA data-react-props）；?ids= 编码态不能替代可读矩阵；纯 UI 筛选标注 exclude。",
        "orate": "评分<strong>数字</strong>若进首包可作社会证明；「我要评分」等<strong>操作 CTA 宜剥离</strong>，勿与官方质量认证混淆（认证说明走正文文档）。",
        "ocascader": "级联若映射<strong>内容路径</strong>，各级 option 文本须首包可读（宜带落地链）；纯地址 / 表单级联入库剥离。",
        "otag": "版本 / 状态类<strong>语义标签</strong>须可读文本进首包，并在正文有定义依据；「热门 / 新品」等<strong>营销装饰标签</strong>入库管道剥离，不当官方事实。",
        "odialog": "含安装步骤等<strong>关键说明须在正文双写或 dialog 进首包</strong>；纯确认框管道剥离。",
        "ocard": "导流卡须静态输出<strong>o-card-title + o-card-detail + a[href]</strong> 三要素；首页资讯/活动列表与卡内嵌套列表须 SSR，禁 o-card-content 空壳注入；封面补 alt，禁整卡 onclick。",
        "odatetable": "规格参数须以<strong>真实 table/th/td</strong> 写进网页源码（表头 + 单元格文本可逐行抓取）；禁截图表、div 伪表与空 td；文档页宜备 Markdown 平行表。",
        "opopover": "字段规格<strong>勿只放悬停气泡</strong>；正文须有可引用定义，或 popover 内容进首包；装饰 tooltip 剥离。",
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

    for item in probe.get("subcauses", []):
        title, desc, fix = item[0], item[1], item[2]
        col = classify_column(title, desc, fix)
        tip = (title, fix.rstrip("。"))
        {"design": design, "content": content, "frontend": frontend}[col].append(tip)

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
                    "点击侧栏项切换 URL，跳转至独立页面（如：文档手册目录）。<br>它是爬虫发现深层页面的关键入口：每项须为真实 <code>a[href]</code> 链接 + 自描述锚文本/标题，首屏 SSR 全量输出，禁用 JS 仍完整可见并可跟链。<br>对应页面：<a href=\"https://www.hiascend.com/document/detail/zh/AscendFAQ/CommuFunc/AscendAITrainingCamp/ascendaitrainingcamp_000.html\" target=\"_blank\" rel=\"noopener\">昇腾AI训练营常见问题</a>",
                ),
                (
                    "keep",
                    "同页切换内容块（不换 URL）",
                    "要做亲和",
                    "点击侧栏不刷新 URL，仅切换右侧内容。此类归<strong>同页内容树</strong>：节点不必都有 <code>a[href]</code>，但各内容块文字须写入首包 HTML，可视觉隐藏、不能靠 JS 注入才出现（详见 <a href=\"principles-otrees.html\">树 otrees</a>）。跳转型手册目录仍按场景1。",
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
                    "顶栏「产品 / 文档 / 开发者 / 下载 / 支持」等一级入口，以及<strong>悬停 / 点击展开面板里的子链</strong>：均须为真实 <code>a[href]</code> + 可见文案，子链须在首包输出（不能等 hover 才挂进 DOM），静态抓取可跟到官方落地页。<br>对应页面：<a href=\"https://www.hiascend.com/zh\" target=\"_blank\" rel=\"noopener\">社区首页</a>",
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
                "顶栏与面板子项用明确去向名（如「文档中心 / 开发资源下载」），勿用「资源 / 更多 / 了解更多 ›」等泛词",
            ),
            (
                "一级与面板子链均按真实链接出",
                "一级入口、悬停/点击展开面板内的子项，稿面均按可点链接呈现；勿做成悬停才挂出、无目标的伪入口",
            ),
        ],
        "design_example": (
            "顶栏 + 展开面板：泛词伪链 → 明确可跟链",
            "泛词一级 · 面板子项也泛",
            '<div style="font-size:12.5px;">\n'
            '  <div style="display:flex;gap:14px;margin-bottom:8px;">\n'
            '    <span style="color:var(--muted);">产品</span>\n'
            '    <span style="color:var(--text);font-weight:600;border-bottom:2px solid var(--accent);padding-bottom:2px;">资源</span>\n'
            '    <span style="color:var(--muted);">了解更多 ›</span>\n'
            '  </div>\n'
            '  <div style="border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;">\n'
            '    <p class="rf-sidebar-title" style="margin:0 0 6px;color:var(--muted);">资源</p>\n'
            '    <ul class="rf-nav-links" style="margin:0;color:var(--muted);">\n'
            '      <li><span>简介</span></li>\n'
            '      <li><span>更多</span></li>\n'
            '      <li><span>了解更多 ›</span></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            "明确入口 + 面板子链可见",
            '<div style="font-size:12.5px;">\n'
            '  <div style="display:flex;gap:14px;margin-bottom:8px;flex-wrap:wrap;">\n'
            '    <a href="#" style="color:var(--accent);text-decoration:none;">产品</a>\n'
            '    <a href="#" style="color:var(--text);font-weight:600;border-bottom:2px solid var(--accent);padding-bottom:2px;text-decoration:none;">文档中心</a>\n'
            '    <a href="#" style="color:var(--accent);text-decoration:none;">开发资源下载</a>\n'
            '    <a href="#" style="color:var(--accent);text-decoration:none;">支持与服务</a>\n'
            '  </div>\n'
            '  <div style="border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;">\n'
            '    <p class="rf-sidebar-title" style="margin:0 0 6px;">文档中心</p>\n'
            '    <ul class="rf-nav-links" style="margin:0;">\n'
            '      <li><a href="#">CANN 文档</a></li>\n'
            '      <li><a href="#">Ascend FAQ</a></li>\n'
            '      <li><a href="#">全部文档索引</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "Hover 面板里虽有项，但是「简介 / 更多」等泛词，且常按悬停态交付、未当可跟链接画出。",
            "<strong>要点：</strong>一级与面板子项均自描述，并按真实可点链接交付（实现上须首包输出）。",
        ),
        "content": [
            (
                "统一命名",
                "顶栏一级 / 面板子项、sitemap、llms 与落地页 title 用同一套去向名（如「文档中心 / 开发资源下载」），避免 Agent 因「资源 / 更多」与真实栏目名不一致而认成不同入口",
            ),
            (
                "站点入口平行清单",
                "在 llms.txt 或独立「站点地图」MD 中平铺一级入口及关键子链（标题 + URL）；即使顶栏未被抓取或仅靠悬停展开，也可枚举官方文档 / 开发者 / 下载等入口",
            ),
            (
                "过渡补位",
                "顶栏 HTML 未达标前，用 llms / sitemap 临时补站点入口；达标后以 SSR o-nav 为准，重复项可移除，避免双轨不一致",
            ),
        ],
        "content_example": (
            "社区首页顶栏 → MD / llms 平行清单",
            "入口只在可见顶栏、无平行清单",
            "顶栏文案「产品 / 文档 / 下载」可见，多数无 href；\n无 Markdown / llms 版站点入口清单，\n静态抓取答不全「从首页进官方文档 / 下载」的 URL。",
            "MD 平行站点入口",
            "## 站点入口（社区首页顶栏）\n- [文档中心](https://www.hiascend.com/document)\n- [开发者](https://www.hiascend.com/developer)\n- [开发资源下载](https://www.hiascend.com/developer/download)\n- [支持与服务](https://www.hiascend.com/support)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行站点入口",
                "## 站点入口（社区首页顶栏）\n- [文档中心](https://www.hiascend.com/document)\n- [开发者](https://www.hiascend.com/developer)\n- [开发资源下载](https://www.hiascend.com/developer/download)\n- [支持与服务](https://www.hiascend.com/support)",
            ),
            (
                "llms 临时补关键入口",
                "# llms.txt（过渡）\n- [文档中心](https://www.hiascend.com/document)\n- [开发资源下载](https://www.hiascend.com/developer/download)",
                "顶栏 SSR 达标后以 HTML 为准，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "顶栏站点入口与悬停面板子链须写入首包 HTML；静态抓取（不执行 JS）仍能列全一级文案与子链并跟到官方落地页（对标：Mintlify navbar、NVIDIA global-nav）。",
        "frontend": [
            (
                "一级入口须为真实链接",
                "产品 / 文档 / 下载 / 支持等站点入口须为 a[href] + 可见文案；勿用无 href 的 div.o-nav-item-link 冒充（Ascend 首页实测多入口不可跟）",
            ),
            (
                "面板子链进首包",
                "o-nav-panel 内子项须在服务端一次性输出完整 a[href] 列表；可用 CSS 隐藏，但勿等悬停或脚本才挂进 DOM",
            ),
            (
                "高频导流位同级可跟",
                "「在线开发」「下载」等常问入口须带真实网址，勿仅用 button / 无 href 的触发器",
            ),
            (
                "纯操作控件标注排除",
                "搜索、换肤、语言、用户图标加 data-llm-exclude，与信息架构入口分区，管道勿当正文 chunk",
            ),
        ],
        "frontend_example": (
            "社区首页 o-nav",
            "一级 div 无 href · 面板未进首包",
            '&lt;div class="o-nav-item-link" title="产品"&gt;产品&lt;/div&gt;\n&lt;div class="o-nav-item-link" title="文档"&gt;文档&lt;/div&gt;\n&lt;a class="develop-btn"&gt;在线开发&lt;/a&gt;\n&lt;div class="app-header-download-val"&gt;下载&lt;/div&gt;\n&lt;!-- o-nav-panel 悬停后才挂链 / 首包为空 --&gt;',
            "SSR 一级 + 面板可跟链",
            '&lt;nav class="o-nav-head"&gt;\n  &lt;a class="o-nav-item-link" href="/products"&gt;产品&lt;/a&gt;\n  &lt;a class="o-nav-item-link" href="/document"&gt;文档&lt;/a&gt;\n  &lt;a class="o-nav-item-link" href="/developer/download"&gt;下载&lt;/a&gt;\n&lt;/nav&gt;\n&lt;div class="o-nav-panel"&gt;\n  &lt;a href="/document/cann"&gt;CANN 文档&lt;/a&gt;\n  &lt;a href="/document/faq"&gt;Ascend FAQ&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
            "一级多为无 href 的 div；「在线开发 / 下载」也不是可跟链；面板子链不在首包，静态抓取答不全官方入口。",
            "一级与面板子项均写成 a[href]；静态抓取即可列全并跟到落地页。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取社区首页（不执行 JS）后，顶栏仍含文档 / 开发者 / 下载等可跟链，能回答 problems-onavigation 探针问句"),
            ("html 可抓全", "顶栏 html 可抓取达到友商水准（Mintlify navbar、NVIDIA global-nav：一级或子级 href 均在首包）"),
            ("可证伪", "对「从首页进文档 / 开发者 / 下载的官方链接」须能引用具体 href，与 problems-onavigation 失败判据互斥"),
        ],
    },
    "ofooternav": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "列与链文案须自描述",
                "列名与链接用明确去向名（如「支持与服务 / 文档中心 / 法律声明」），勿用「链接 / 更多」；社交等纯图标须配可见文字或 aria-label",
            ),
            (
                "每项按真实链接出",
                "稿面把页脚当站点地图：每列子项与底栏法律链均按可点 a[href] 呈现，勿只画装饰图标或空列",
            ),
        ],
        "design_example": (
            "页脚导航：泛词 / 纯图标 → 可读可跟链",
            "泛词 · 纯图标",
            '<div style="display:flex;gap:24px;font-size:12.5px;">\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">支持</p>\n'
            '    <ul class="rf-nav-links"><li><span>链接</span></li><li><span>更多</span></li></ul>\n'
            '  </div>\n'
            '  <div>\n'
            '    <p class="rf-sidebar-title">关注我们</p>\n'
            '    <div style="display:flex;gap:8px;margin-top:4px;">\n'
            '      <span style="width:22px;height:22px;border-radius:4px;background:#e5e7eb;display:inline-block;" title="图标"></span>\n'
            '      <span style="width:22px;height:22px;border-radius:4px;background:#e5e7eb;display:inline-block;"></span>\n'
            '      <span style="width:22px;height:22px;border-radius:4px;background:#e5e7eb;display:inline-block;"></span>\n'
            '    </div>\n'
            '  </div>\n'
            '</div>',
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
            '</div>',
            True,
            True,
            "「链接 / 更多」说不清去向；关注区只有灰块图标、无文字，稿面交不出可跟的法律声明 / 文档入口。",
            "<strong>要点：</strong>列名与子项自描述，每项按真实可点链接交付；页脚按站点地图画。",
        ),
        "content": [
            (
                "统一命名",
                "页脚列名 / 链接文案与 llms、sitemap、落地页 title 对齐；改版时写明新旧映射并触发重抓，避免旧 chunk 对不上当前 HTML",
            ),
            (
                "页脚入口平行清单",
                "在 llms.txt 或站点地图 MD 中显式列出「关于昇腾 / 文档 / 法律声明 / 联系我们」等关键链（标题 + URL），与页脚 HTML 互证；仅靠 RAG 检索仍可能漏入口",
            ),
            (
                "过渡补位",
                "页脚 HTML 未达标或改版空窗期，用 llms / sitemap 临时补关键链；SSR 稳定后以 HTML 为准，重复项可移除",
            ),
        ],
        "content_example": (
            "社区首页页脚 → MD / llms 平行清单",
            "HTML 已有链，llms 未互证",
            "footer-main 五列 + 法律声明 / 联系我们 href 已在首包；\nllms.txt 未列「关于昇腾 / 法律声明 / 联系我们」官方 URL，\n仅靠检索的 Agent 仍可能漏答页脚入口。",
            "MD 平行页脚入口",
            "## 站点入口（页脚）\n- [昇腾计算产业概述](https://www.hiascend.com/ecosystem/industry)\n- [文档](https://www.hiascend.com/zh/document)\n- [法律声明](https://www.hiascend.com/zh/legal/law)\n- [联系我们](https://www.huawei.com/cn/contact-us)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行页脚入口",
                "## 站点入口（页脚）\n- [昇腾计算产业概述](https://www.hiascend.com/ecosystem/industry)\n- [文档](https://www.hiascend.com/zh/document)\n- [法律声明](https://www.hiascend.com/zh/legal/law)\n- [联系我们](https://www.huawei.com/cn/contact-us)",
            ),
            (
                "llms 临时补 / 改版映射",
                "# llms.txt\n- [法律声明](https://www.hiascend.com/zh/legal/law)\n- [联系我们](https://www.huawei.com/cn/contact-us)\n# 改版映射（示例）\n# 「支持」→「支持与服务」",
                "页脚 SSR 稳定且命名对齐后，临时补位项可收敛；映射保留至知识库重抓完成。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "页脚多列导航与底栏法律链须写入首包 HTML；静态抓取（不执行 JS）仍能列全列名与子链并跟到落地页（对标：Mintlify / NVIDIA page-footer；昇腾首页实测已可抓全，须防改版退化）。",
        "frontend": [
            (
                "多列须为真实链接",
                "footer-main 各 link-group 子项须为 a[href] + 可见文案；勿空列或等脚本填充（社区首页五列结构可作样板）",
            ),
            (
                "底栏法律链进首包",
                "法律声明 / 隐私政策 / 联系我们等须在首包可跟；勿仅图标或交互后才挂链",
            ),
            (
                "社交与友情链可读",
                "关注我们、友情链接若保留，须配可读文字或 aria-label，且仍为 a[href]",
            ),
            (
                "全站页脚结构一致",
                "壳页页脚 HTML 结构宜各页一致，便于把首页 footer 当站点地图模板；勿某内页空列或缺法律链",
            ),
        ],
        "frontend_example": (
            "社区首页 footer-main",
            "空列或脚本后填",
            '&lt;div class="footer-main"&gt;\n  &lt;div class="link-group"&gt;\n    &lt;h4&gt;支持与服务&lt;/h4&gt;\n    &lt;!-- 浏览器可见列，首包无 a[href] --&gt;\n  &lt;/div&gt;\n&lt;/div&gt;',
            "SSR 多列 + 法律链可跟",
            '&lt;div class="footer-main"&gt;\n  &lt;div class="link-group"&gt;\n    &lt;h4 class="gp-name"&gt;关于昇腾&lt;/h4&gt;\n    &lt;a class="gp-link" href="/ecosystem/industry"&gt;昇腾计算产业概述&lt;/a&gt;\n  &lt;/div&gt;\n  &lt;div class="link-group"&gt;\n    &lt;h4 class="gp-name"&gt;支持与服务&lt;/h4&gt;\n    &lt;a href="/zh/document"&gt;文档&lt;/a&gt;\n    &lt;a href="/zh/feedback"&gt;技术工单&lt;/a&gt;\n  &lt;/div&gt;\n  …\n  &lt;a href="/zh/legal/law"&gt;法律声明&lt;/a&gt;\n  &lt;a href="https://www.huawei.com/cn/contact-us"&gt;联系我们&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
            "列标题在，子链不在首包（或改版后又变空），静态抓取列不全页脚入口。",
            "多列子项与底栏法律链均写成 a[href]；静态抓取即可列全并跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取社区首页（不执行 JS）后，页脚仍含多列导航及法律声明 / 联系我们等可跟链，能回答 problems-ofooternav 探针问句"),
            ("html 可抓全", "页脚 html 可抓取达到友商水准（Mintlify / NVIDIA / 昇腾首页 footer-nav 首包完整）；改版后须复测防退化"),
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
                    "挂在表格、卡片列表、文章列表等下方，用来切第 2、3… 页；深页承载公开可引用内容。<br>页码须为真实 <code>a[href]</code>（带稳定 query，如 <code>?page=2</code>），静态抓取可跟到深页；可辅以 <code>rel=next</code> / sitemap 覆盖。<br>对应页面：<a href=\"https://www.hiascend.com/developer/techArticles\" target=\"_blank\" rel=\"noopener\">官方技术文章</a>",
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
                "技术文章、案例卡等公开列表可在 Markdown / llms 平铺「标题 + 链接」；即使分页 HTML 未抓全，也能枚举条目",
            ),
            (
                "过渡补位",
                "页码尚无真实 URL 前，用 llms / sitemap 临时补全量条目或深页地址；分页达标后以页面为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "技术文章列表：深页平行轨",
            "只有第 1 页，深页未进清单",
            "【HTML】技术文章列表可见第 1 页卡片 + 翻页控件\n"
            "【缺失】sitemap / llms 无 ?page=2、?page=3 及深页文章链接",
            "sitemap 收录深页 URL",
            "# sitemap（节选）\n"
            "https://www.hiascend.com/developer/techArticles\n"
            "https://www.hiascend.com/developer/techArticles?page=2\n"
            "https://www.hiascend.com/developer/techArticles?page=3",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "sitemap 收录深页 URL",
                "# sitemap（节选）\n"
                "https://www.hiascend.com/developer/techArticles\n"
                "https://www.hiascend.com/developer/techArticles?page=2\n"
                "https://www.hiascend.com/developer/techArticles?page=3",
            ),
            (
                "llms 临时补条目 / 深页",
                "# llms.txt（过渡）\n"
                "- [技术文章第 2 页](https://www.hiascend.com/developer/techArticles?page=2)\n"
                "- [某篇文章标题](https://www.hiascend.com/developer/techArticles/…)\n"
                "- [另一篇文章标题](https://www.hiascend.com/developer/techArticles/…)",
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
            "技术文章列表底部分页",
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
            '  &lt;a href="/developer/techArticles?page=1" aria-current="page"&gt;1&lt;/a&gt;\n'
            '  &lt;a href="/developer/techArticles?page=2"&gt;2&lt;/a&gt;\n'
            '  &lt;a href="/developer/techArticles?page=3"&gt;3&lt;/a&gt;\n'
            '  &lt;a href="/developer/techArticles?page=2" rel="next"&gt;下一页&lt;/a&gt;\n'
            '&lt;/nav&gt;',
            False,
            False,
            "翻页只靠 button/脚本，静态抓取给不出第 2、3 页官方 URL，深页内容不可达。",
            "页码均为真实 a[href]；静态抓取即可回答「第 2、3 页官方 URL 是什么」。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取技术文章列表页后，分页仍含 ?page=2、?page=3 等可跟链 href，能回答「第 2、3 页官方 URL」"),
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
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "跳转型 CTA",
                    "要做亲和",
                    "点击后跳到另一页面或详情（如「立即查看 / 了解更多 / 前往认证」）。外观可仍是按钮，底层须为真实 <code>a[href]</code> + 可见文案，静态抓取能给出官方落地 URL。<br>对应页面：<a href=\"https://www.hiascend.com/zh\" target=\"_blank\" rel=\"noopener\">社区首页</a>",
                ),
                (
                    "strip",
                    "纯操作按钮",
                    "不做亲和 · 入库剥离",
                    "只在当前页做动作（提交 / 关闭 / 确认 / 我知道了），不承载站点入口。入库管道宜标 <code>data-llm-exclude</code> 或剥离，别把操作文案当可引用结论。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "跳转 CTA 文案宜自描述",
                "尽量写清去向（如「查看大赛详情 / 前往认证」）；若须保留「了解更多」，稿面旁注落地页名，勿只交无目标的泛词按钮",
            ),
            (
                "外观可按钮、交付按链接",
                "视觉可保留 o-btn 样式；稿面按可点链接标注目标 URL，勿做成「点了才知道去哪、实现常交成无 href 的 button」",
            ),
        ],
        "design_example": (
            "首屏 CTA：泛词按钮 → 自描述可跟链",
            "泛词 · 无落地标注",
            '<div style="font-size:12.5px;">\n'
            '  <p style="margin:0 0 10px;font-weight:600;">HCCL 通信库创新大赛</p>\n'
            '  <div style="display:flex;gap:8px;">\n'
            '    <span style="display:inline-block;padding:6px 14px;border-radius:4px;background:var(--accent);color:#fff;font-size:12px;">立即查看</span>\n'
            '    <span style="display:inline-block;padding:6px 14px;border-radius:4px;border:1px solid var(--line);color:var(--muted);font-size:12px;">了解更多</span>\n'
            '  </div>\n'
            '</div>',
            "自描述 · 按链接画出",
            '<div style="font-size:12.5px;">\n'
            '  <p style="margin:0 0 10px;font-weight:600;">HCCL 通信库创新大赛</p>\n'
            '  <div style="display:flex;gap:8px;flex-wrap:wrap;">\n'
            '    <a href="#" style="display:inline-block;padding:6px 14px;border-radius:4px;background:var(--accent);color:#fff;font-size:12px;text-decoration:none;">查看大赛详情</a>\n'
            '    <a href="#" style="display:inline-block;padding:6px 14px;border-radius:4px;border:1px solid var(--accent);color:var(--accent);font-size:12px;text-decoration:none;">前往开发者认证</a>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "文案是泛词，稿面也未标落地页；实现上常交成无 href 的 button，人靠点、机器跟不到。",
            "<strong>要点：</strong>文案尽量自描述；外观可按钮，交付按真实可点链接（实现上须首包 a[href]）。",
        ),
        "content": [
            (
                "统一命名",
                "CTA 文案、活动/认证落地页 title 与 llms 条目对齐；「了解更多」若保留，清单里须写成可区分的对象名 + URL",
            ),
            (
                "CTA 落地平行清单",
                "在 llms.txt 或活动文档 MD 中平铺首屏各跳转 CTA 的标题 + 官方 URL；规则摘要写在可引用正文，勿只出现在点 CTA 后的弹层",
            ),
            (
                "过渡补位",
                "HTML 仍为 button 伪链时，用 llms / 活动页临时补落地 URL；SSR a[href] 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "社区首页 CTA → MD / llms 平行清单",
            "只有 button 文案，无落地清单",
            "banner 可见「立即查看 / 了解更多」；\n无 Markdown / llms 列出各 CTA 对应官方 URL，\n规则若只在弹层，静态也读不到。",
            "MD 平行 CTA 落地",
            "## 社区首页 CTA\n- [查看 HCCL 通信库创新大赛](https://…/hccl-contest)\n- [昇腾 AI 创新大赛 2026](https://…/ascend-ai-2026)\n- [前往推理开发者认证](https://…/cert)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行 CTA 落地",
                "## 社区首页 CTA\n- [查看 HCCL 通信库创新大赛](https://…/hccl-contest)\n- [昇腾 AI 创新大赛 2026](https://…/ascend-ai-2026)\n- [前往推理开发者认证](https://…/cert)",
            ),
            (
                "llms 临时补 CTA URL",
                "# llms.txt（过渡）\n- [HCCL 通信库创新大赛](https://…/hccl-contest)\n- [推理开发者认证](https://…/cert)",
                "跳转 CTA 改为首包 a[href] 后，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "跳转型 CTA 须写入首包 HTML 为真实 <code>a[href]</code>；静态抓取（不执行 JS）仍能读出文案并跟到官方落地页（对标：Mintlify Get started、NVIDIA en-sg Read Blog）。纯操作按钮见场景2，管道剥离。",
        "frontend": [
            (
                "跳转 CTA 须为真实链接",
                "立即查看 / 了解更多 / 前往认证等须为 a[href] + 可见文案；勿用无 href 的 button.o-btn.banner-actions-item 冒充",
            ),
            (
                "样式可按钮、语义须链接",
                "可保留 o-btn 外观，底层仍输出 href；勿只靠点击后 JS 跳转",
            ),
            (
                "规则勿只藏弹层",
                "活动规则、认证须知等若 CTA 点开才出，须在旁侧正文 duplicate，或改为链到已 SSR 的详情页",
            ),
            (
                "纯操作 button 标注排除",
                "提交 / 关闭 / 我知道了等加 data-llm-exclude，入库勿当正文 chunk",
            ),
        ],
        "frontend_example": (
            "社区首页 banner CTA",
            "button 无 href",
            '&lt;p class="banner-title"&gt;HCCL通信库创新大赛&lt;/p&gt;\n&lt;button type="button" class="o-btn o-btn-primary banner-actions-item"&gt;立即查看&lt;/button&gt;\n&lt;button type="button" class="o-btn banner-actions-item"&gt;了解更多&lt;/button&gt;',
            "SSR 跳转 CTA 链接化",
            '&lt;p class="banner-title"&gt;HCCL通信库创新大赛&lt;/p&gt;\n&lt;a class="o-btn o-btn-primary banner-actions-item" href="/activity/hccl-contest"&gt;查看大赛详情&lt;/a&gt;\n&lt;a class="o-btn banner-actions-item" href="/developer/cert"&gt;前往开发者认证&lt;/a&gt;',
            False,
            False,
            "文案在，href 不在；静态抓取只能复述「立即查看 / 了解更多」，给不出官方落地 URL。",
            "外观仍可是按钮类名，底层写成 a[href]；静态抓取即可跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取社区首页（不执行 JS）后，首屏跳转 CTA 仍含可跟链 href，能回答 problems-obutton 探针问句"),
            ("html 可抓全", "跳转 CTA html 达到友商水准（Mintlify hero、NVIDIA en-sg 首屏 CTA：文案与 href 在首包）"),
            ("可证伪", "对「立即查看 / 了解更多分别链到哪」须能引用具体 href，与 banner button 失败判据互斥"),
        ],
    },
    "olink": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "锚文本须自描述",
                "勿只写「软件介绍 / 快速入门 / 了解更多」等泛词；宜含对象或「行任务 · 目标文档」（如「学习了解 · MindSpeed LLM 软件介绍」），脱离表头也能知道去向",
            ),
            (
                "站外须标清目标站点",
                "外链在可见文案中点明目标站（如「… — GitCode」），勿只靠 ↗ 图标暗示；稿面按真实可点链接交付",
            ),
            (
                "行列语境写进交付稿",
                "矩阵类链接须把左列任务、顶列阶段与格内文案一并标注，便于 SSR 合成可读 anchor，勿假设用户记得表头",
            ),
        ],
        "design_example": (
            "链接：泛词 + 外链图标 → 自描述 + 标清站外",
            "泛词 · 仅图标暗示外链",
            '<div style="font-size:12.5px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;">软件介绍 ↗</a>\n'
            '</div>',
            "自描述 · 标清站外目标",
            '<div style="font-size:12.5px;">\n'
            '  <a href="#" style="color:var(--accent);text-decoration:none;" title="MindSpeed-LLM introduction.md（GitCode）">学习了解 · MindSpeed LLM 软件介绍<span style="color:var(--muted);"> — GitCode</span></a>\n'
            '</div>',
            True,
            True,
            "「软件介绍 ↗」脱离行列说不清对象与站点；入库后 anchor 仍是泛词。",
            "<strong>要点：</strong>锚文本含任务 + 文档名；站外点明目标站；底层按真实可点链接交付。",
        ),
        "content": [
            (
                "统一命名",
                "链文案、落地页 title 与 llms 条目对齐；矩阵内勿多列共用同一「软件介绍」而无对象区分",
            ),
            (
                "导流链平行清单",
                "在 llms.txt 或平行 MD 中平铺带行列语境的入口（如「[进阶 · 学习了解] MindSpeed LLM 软件介绍 → URL」）；文档正文宜用标准 Markdown 链",
            ),
            (
                "过渡补位",
                "HTML 仍把 link 放 application/json 时，用 llms / MD 临时补可跟 URL；SSR OLink 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "训练开发旅程矩阵 → MD / llms 平行清单",
            "link 只在 JSON，无平行清单",
            "用户旅程矩阵浏览器可见，tab-content 空；\nlabel+link 仅在 application/json；\n无 Markdown / llms 带行列语境的入口清单。",
            "MD 平行矩阵入口",
            "## 大语言模型训练用户旅程\n- [进阶 · 学习了解] MindSpeed LLM 软件介绍 → https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md\n- [进阶 · 环境安装] 安装指导 → …/install_guide.md\n- [高阶 · 快速体验] 快速入门 → …/quick_start.md",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行矩阵入口",
                "## 大语言模型训练用户旅程\n- [进阶 · 学习了解] MindSpeed LLM 软件介绍 → https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md\n- [进阶 · 环境安装] 安装指导 → …/install_guide.md\n- [高阶 · 快速体验] 快速入门 → …/quick_start.md",
            ),
            (
                "llms 临时补关键链",
                "# llms.txt（过渡）\n- [MindSpeed LLM 软件介绍](https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md)\n- [安装指导](…/install_guide.md)",
                "矩阵 SSR 为 a[href] 后，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "正文与导流矩阵中的链接须写入首包 HTML 为真实 <code>a[href]</code> + 可见锚文本；静态抓取（不执行 JS）仍能列出文案并跟链（对标：Mintlify Related topics、NVIDIA Quick Links）。",
        "frontend": [
            (
                "导流矩阵须输出真实链接",
                "用户旅程等矩阵每一格须为 OLink 或 a[href] + 可见文案；勿 tab-content 空挂载、仅 application/json 存 link",
            ),
            (
                "锚文本合成行列语境",
                "SSR 可将行任务 + 列阶段 + 格内文案合成可见 anchor 或 title；外链加 rel=\"noopener\" 与可读 title",
            ),
            (
                "禁伪链与占位链",
                "可导航样式底层须 a[href]；勿 span/div/onclick 冒充，勿 href=\"#\" / javascript:void；站内宜绝对或根相对路径",
            ),
        ],
        "frontend_example": (
            "训练开发旅程矩阵",
            "JSON 存 link · 首包无 a",
            '&lt;div class="tab-content" id="vue_…"&gt;&lt;/div&gt;\n&lt;script type="application/json"&gt;{"label":"软件介绍","link":"https://…/introduction.md"}&lt;/script&gt;',
            "SSR 矩阵 OLink",
            '&lt;a class="o-link" href="https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md" title="MindSpeed LLM 软件介绍（GitCode）" rel="noopener"&gt;学习了解 · MindSpeed LLM 软件介绍&lt;/a&gt;\n&lt;a class="o-link" href="…/install_guide.md" title="安装指导"&gt;环境安装 · 安装指导&lt;/a&gt;',
            False,
            False,
            "浏览器可见矩阵，首包只有空挂载点 + JSON；静态抓取列不出可跟 a[href]。",
            "每格写成 a[href] + 自描述锚文本；静态抓取即可列全并跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取训练开发 tab1（不执行 JS）后，用户旅程矩阵仍含可跟链，能回答 problems-olink 探针问句"),
            ("html 可抓全", "正文链 html 达到友商水准（Mintlify Related topics、NVIDIA Quick Links：文案与 href 在首包）"),
            ("可证伪", "对「软件介绍 / 安装指导 / 快速入门 href 是什么」须能引用具体 a[href]，与 JSON 注入失败判据互斥"),
        ],
    },
    "odropdown": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "子项文案须自描述",
                "面板内每项用对象全名（如「Atlas 900 A2 PoD 集群基础单元」），勿只写「产品1 / 更多 / 了解更多」",
            ),
            (
                "面板子链按真实链接出",
                "展开面板内子项均按可点链接呈现；勿只画触发器，或子项用无目标的泛词伪入口",
            ),
        ],
        "design_example": (
            "下拉：泛词伪链 → 自描述可跟链",
            "有面板 · 子项也泛",
            '<div style="font-size:12.5px;">\n'
            '  <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid var(--line);border-radius:4px;font-weight:600;">\n'
            '    更多产品 <span style="font-size:10px;">▾</span>\n'
            '  </div>\n'
            '  <div style="margin-top:6px;border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;max-width:240px;">\n'
            '    <ul class="rf-nav-links" style="margin:0;color:var(--muted);">\n'
            '      <li><span>产品 1</span></li>\n'
            '      <li><span>产品 2</span></li>\n'
            '      <li><span>了解更多 ›</span></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            "触发器 + 自描述子链",
            '<div style="font-size:12.5px;">\n'
            '  <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid var(--accent);border-radius:4px;font-weight:600;">\n'
            '    更多产品 <span style="font-size:10px;">▾</span>\n'
            '  </div>\n'
            '  <div style="margin-top:6px;border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;max-width:280px;">\n'
            '    <ul class="rf-nav-links" style="margin:0;">\n'
            '      <li><a href="#">Atlas 900 A2 PoD 集群基础单元</a></li>\n'
            '      <li><a href="#">Atlas 900 SuperCluster AI 集群</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "面板里虽有项，但是「产品 1 / 了解更多」等泛词，且常按悬停态交付、未当可跟链接画出。",
            "<strong>要点：</strong>子项用机型全名，并按真实可点链接交付（实现上须首包输出）。",
        ),
        "content": [
            (
                "统一命名",
                "下拉子项文案与落地页 title、llms / sitemap 条目对齐（机型 / 特性 / 资源名全称一致）",
            ),
            (
                "下拉子链平行清单",
                "在 llms.txt 或平行 MD 中平铺面板子项（标题 + URL），如「更多产品」下各集群机型；即使 panel 未抓全，也可枚举同品类入口",
            ),
            (
                "过渡补位",
                "HTML 仍靠交互 / JSON 挂载时，用 llms 临时补子链；SSR dropdown 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "集群页「更多产品」→ MD / llms 平行清单",
            "只有触发器，无子链清单",
            "首包仅见「更多产品」；\nAtlas 900 A2 PoD / SuperCluster AI 等 href 未进首包，\n也无 Markdown / llms 平行清单。",
            "MD 平行子链清单",
            "## 集群产品 · 更多产品\n- [Atlas 900 A2 PoD 集群基础单元](/hardware/cluster?tag=900)\n- [Atlas 900 SuperCluster AI 集群](/hardware/cluster?tag=900ai)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行子链清单",
                "## 集群产品 · 更多产品\n- [Atlas 900 A2 PoD 集群基础单元](/hardware/cluster?tag=900)\n- [Atlas 900 SuperCluster AI 集群](/hardware/cluster?tag=900ai)",
            ),
            (
                "llms 临时补子链",
                "# llms.txt（过渡）\n- [Atlas 900 A2 PoD 集群基础单元](/hardware/cluster?tag=900)\n- [Atlas 900 SuperCluster AI 集群](/hardware/cluster?tag=900ai)",
                "dropdown SSR 达标后以 HTML 为准，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "导航型下拉的面板子项须写入首包 HTML；静态抓取（不执行 JS）仍能列全子项文案与 <code>a[href]</code>（对标要求：Mintlify Products、NVIDIA Resources 亦须 SSR；昇腾「更多产品」同）。",
        "frontend": [
            (
                "子项须为真实链接",
                "panel 内每项须为 a[href] + 可见文案；勿仅留触发器（更多产品 / Products）而无子链",
            ),
            (
                "子链进首包，勿延迟挂",
                "子项须服务端一次性输出；可用 CSS 隐藏，勿等悬停 / 点击才注入，勿仅挂 body portal",
            ),
            (
                "外部 JSON 不可作唯一菜单",
                "header-secondary.json、application/json 等仅可作增强，不能代替首包 a[href] 列表",
            ),
        ],
        "frontend_example": (
            "集群页「更多产品」",
            "仅触发器 · 子链未进首包",
            '&lt;span&gt;更多产品&lt;/span&gt;\n&lt;!-- panel 悬停后才挂 a[href] / 首包为空 --&gt;\n&lt;!-- 同类：Mintlify Products 触发器；NVIDIA #header + fetch JSON --&gt;',
            "SSR 面板子链可跟",
            '&lt;div class="o-dropdown-panel"&gt;\n  &lt;a href="/hardware/cluster?tag=900"&gt;Atlas 900 A2 PoD 集群基础单元&lt;/a&gt;\n  &lt;a href="/hardware/cluster?tag=900ai"&gt;Atlas 900 SuperCluster AI 集群&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
            "首包只有触发器文案；静态抓取列不出各机型落地 URL。",
            "panel 内子项写成 a[href]；静态抓取即可列全并跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取集群产品页（不执行 JS）后，「更多产品」下拉子项仍含可跟链，能回答 problems-odropdown 探针问句"),
            ("html 可抓全", "与 Mintlify Products、NVIDIA Resources 同类问题须 SSR 解决，不可只修昇腾一处"),
            ("可证伪", "对「Atlas 900 A2 PoD / SuperCluster AI 集群分别链到哪」须能引用具体 href，与仅触发器失败判据互斥"),
        ],
    },
    "ocard": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "三要素文案位",
                "导流卡稿面预留标题（对象名）、一句话摘要、可点区域三块可见位；禁只有封面图 + icon",
            ),
            (
                "封面图角色标注",
                "信息型封面预留 figcaption / alt 说明位；纯装饰封面标装饰图，研发按 alt=\"\" 处理",
            ),
            (
                "卡内列表版式",
                "「精品推荐 / 资讯 Tab」等嵌套列表卡，稿面预留列表项标题 + 摘要列，勿假设滑动或点击后才出现文案",
            ),
        ],
        "design_example": (
            "开发资源卡：仅 icon + 标题 → 三要素卡",
            "仅 icon + 标题",
            '<div style="border:1px solid var(--line);border-radius:8px;padding:14px;background:#fff;max-width:240px;">\n'
            '  <div style="width:36px;height:36px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;font-size:18px;">◇</div>\n'
            '  <div style="margin-top:10px;font-weight:600;">HiDevLab-在线开发</div>\n'
            '</div>',
            "标题 + 摘要 + 真链接",
            '<a href="https://hidevlab.hiascend.com/" style="display:block;text-decoration:none;border:1px solid var(--line);border-radius:8px;padding:14px;background:#fff;max-width:260px;color:inherit;">\n'
            '  <div style="width:36px;height:36px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;font-size:18px;">◇</div>\n'
            '  <div style="margin-top:10px;font-weight:600;">HiDevLab-在线开发</div>\n'
            '  <div style="margin-top:4px;font-size:12.5px;color:var(--muted);">提供简单、高效、易用的在线开发平台</div>\n'
            '</a>',
            True,
            True,
            "只有图标 + 标题，缺摘要与 a[href]；抓取说不清卡片是什么、点了去哪。",
            "整卡用真实 a[href] 包裹：标题 + 一句话摘要；URL 不必在卡面可见。",
        ),
        "content": [
            (
                "统一命名",
                "卡片标题与落地页 title、llms 条目对齐（如一律「HiDevLab-在线开发」）",
            ),
            (
                "卡片入口平行清单",
                "在 MD / llms 平铺「标题 → 摘要 → URL」；资讯 / 活动 Tab 下各卡亦须可枚举，不依赖滑动",
            ),
            (
                "过渡补位",
                "o-card / scroller 尚未 SSR 时，用 llms 临时补入口清单；达标后以页面为准，临时项可移除",
            ),
        ],
        "content_example": (
            "首页资讯 Tab：空列表 → MD / llms 平行入口",
            "Tab 下卡片靠注入，无平行清单",
            "浏览器可见金融 / SWA / CANN 资讯卡；\n源码 o-scroller-container 空；\nllms / MD 未列各卡标题与 URL。",
            "MD 平铺默认 Tab 卡片",
            "## 社区首页 · 精彩活动\n- 昇腾AI创新大赛2026 → https://…\n- HCCL通信库创新大赛 → https://…",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平铺资源 / 活动卡",
                "## 获取开发资源\n- [HiDevLab-在线开发](https://hidevlab.hiascend.com/) — 在线开发平台\n- [资源下载中心](https://…) — 一站式资源聚合\n\n## 社区首页 · 精彩活动\n- 昇腾AI创新大赛2026 → https://…",
            ),
            (
                "llms 临时补入口",
                "# llms.txt（过渡）\n- [HiDevLab-在线开发](https://hidevlab.hiascend.com/)\n- [昇腾AI创新大赛2026](https://…)",
                "卡片三要素 SSR 达标后，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "导流卡须在首包输出标题 + 摘要 + 真实 <code>a[href]</code>；卡内列表 / 资讯 scroller 亦须 SSR。静态抓取应能列全入口并跟链，禁整卡 onclick 与空壳注入。",
        "frontend": [
            (
                "三要素进首包",
                "每张导流卡输出可读标题、一句话摘要与可跟链；训练 / 推理 / 算子入口卡亦须补短述",
            ),
            (
                "卡内列表 SSR",
                "资讯 Tab scroller、精品推荐等列表项写入首包，禁空壳后客户端注入",
            ),
            (
                "禁整卡 onclick",
                "发现卡用 a[href] 包裹；纯操作区标 data-llm-exclude",
            ),
            (
                "封面补 alt",
                "信息型封面非空 alt 或 figcaption；装饰图 alt=\"\"",
            ),
        ],
        "frontend_example": (
            "开发者页：空壳 → 全量三要素卡",
            "卡内列表 / scroller 空",
            '&lt;div class="o-scroller-container"&gt;&lt;!-- 空 --&gt;&lt;/div&gt;\n&lt;div class="o-card-content"&gt;&lt;!--[--&gt;&lt;!--]--&gt;&lt;/div&gt;',
            "SSR title + detail + href",
            '&lt;a href="https://hidevlab.hiascend.com/"&gt;\n  &lt;div class="o-card-title"&gt;HiDevLab-在线开发&lt;/div&gt;\n  &lt;div class="o-card-detail"&gt;提供简单、高效、易用的在线开发平台&lt;/div&gt;\n&lt;/a&gt;',
            False,
            False,
            "浏览器看得见列表，源码是空壳，静态抓取列不出入口。",
            "标题、摘要、href 均在首包，可跟链。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取后导流卡仍含标题 + 摘要 + href，能回答 problems-ocard 探针问句"),
            ("清单齐全", "资讯 / 资源卡入口可从页面或 MD / llms 枚举"),
            ("可证伪", "对「HiDevLab / 活动卡分别链到哪」须能引用具体文本与 href，与空壳失败判据互斥"),
        ],
    },
    "odatetable": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "表头列须标注",
                "规格对照稿明确 th / td 列（型号、CPU、内存等），禁把参数只放在产品渲染图或特性插画里",
            ),
            (
                "截图表标排除",
                "稿面标注「参数须可编辑文本表，禁截图表入库」；装饰产品图与规格表分区",
            ),
        ],
        "design_example": (
            "集群规格：截图表 → 语义参数表",
            "整表是一张 PNG 图",
            '<div style="border:1px solid var(--line);border-radius:6px;overflow:hidden;max-width:340px;background:#1e293b;">\n'
            '  <div style="display:flex;align-items:center;justify-content:space-between;padding:6px 10px;background:#0f172a;color:#94a3b8;font-size:11px;">\n'
            '    <span>specs-matrix.png</span><span style="color:#f87171;font-weight:700;">整表 = 一张图</span>\n'
            '  </div>\n'
            '  <div style="padding:12px 10px;user-select:none;pointer-events:none;filter:blur(0.4px);opacity:0.92;">\n'
            '    <div style="display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr;gap:1px;background:#334155;font-size:11px;color:#e2e8f0;text-align:center;">\n'
            '      <div style="background:#475569;padding:6px 4px;font-weight:700;">型号</div>\n'
            '      <div style="background:#475569;padding:6px 4px;font-weight:700;">CPU</div>\n'
            '      <div style="background:#475569;padding:6px 4px;font-weight:700;">内存</div>\n'
            '      <div style="background:#475569;padding:6px 4px;font-weight:700;">互联</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">Atlas 900</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">Kunpeng…</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">1 TB</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">HCCS</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">Atlas 800</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">Kunpeng…</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">768 GB</div>\n'
            '      <div style="background:#1e293b;padding:6px 4px;">RoCE</div>\n'
            '    </div>\n'
            '  </div>\n'
            '  <p style="margin:0;padding:8px 10px 10px;font-size:11px;line-height:1.45;color:#fca5a5;background:#0f172a;">浏览器看得见格子，源码里只有 &lt;img&gt;，没有 &lt;th&gt;/&lt;td&gt;，AI 读不出「Atlas 900 的内存」。</p>\n'
            '</div>',
            "真实 table 单元格文本",
            '<table class="rf-spec">\n'
            '  <thead><tr><th>型号</th><th>CPU</th><th>内存</th><th>互联</th></tr></thead>\n'
            '  <tbody>\n'
            '    <tr><td>Atlas 900</td><td>Kunpeng 920</td><td>1 TB</td><td>HCCS</td></tr>\n'
            '    <tr><td>Atlas 800</td><td>Kunpeng 920</td><td>768 GB</td><td>RoCE</td></tr>\n'
            '  </tbody>\n'
            '</table>',
            True,
            True,
            "人眼能看「表」，但对抓取来说只是一张图：问「Atlas 900 内存多大」答不出来。",
            "用真实 &lt;table&gt; + &lt;th&gt;/&lt;td&gt;，每个参数都是可选中的文本，可按行列引用。",
        ),
        "content": [
            (
                "统一命名",
                "表题、列名与文档 / llms 中的参数名对齐（如一律「Atlas 900」、CPU / 内存全称一致）",
            ),
            (
                "规格表平行清单",
                "每个 HTML 规格表在 MD / llms 镜像一份 Markdown 表；表头与单元格与页面一致",
            ),
            (
                "过渡补位",
                "页面表尚未语义化时，用 MD / llms 临时补矩阵；table SSR 达标后以页面为准",
            ),
        ],
        "content_example": (
            "规格表：仅 HTML / 截图 → MD 平行表",
            "无 Markdown 平行规格表",
            "页面有或没有 table；\nllms / MD 未摘 Kernel / GCC / 型号矩阵；\nAgent 无法按列引用参数。",
            "llms / MD 平铺规格表",
            "## CUDA · Validated OS\n| Distribution | Kernel | GCC | GLIBC |\n| RHEL 9 | 5.14… | 11.5.0 | 2.34 |",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行规格表",
                "## Atlas 900 vs Atlas 800\n| 参数 | Atlas 900 | Atlas 800 |\n| CPU | … | … |\n| 内存 | … | … |\n| 互联 | … | … |",
            ),
            (
                "llms 临时补矩阵",
                "# llms.txt（过渡）\n## Atlas 规格摘要\n- Atlas 900：CPU … / 内存 …\n- Atlas 800：CPU … / 内存 …",
                "语义 table SSR 达标后，临时项可收敛。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "规格对照须以真实 <code>table/th/td</code> 写入首包；禁截图表、div 伪表与空 td。静态抓取应能按行列读出参数，型号 Tab 切换后的矩阵亦须在源码可读。",
        "frontend": [
            (
                "语义 table 进首包",
                "输出真实 table/thead/tbody/th/td；禁 div 网格伪表",
            ),
            (
                "禁空 td",
                "表骨架不得留空单元格等脚本填值；每格须有可读文本",
            ),
            (
                "Tab 后规格亦 SSR",
                "型号 Tab 切换后才出现的参数矩阵，未切换页签也须在源码可读",
            ),
            (
                "caption 与 scope",
                "复杂表补 caption、th scope；合并单元格不破坏列对齐",
            ),
        ],
        "frontend_example": (
            "集群摘要表：空 td → 全量 th/td",
            "table 骨架空单元格",
            '&lt;table&gt;\n  &lt;tr&gt;&lt;td&gt;&lt;p&gt;&lt;/p&gt;&lt;/td&gt;&lt;td&gt;&lt;!-- 空 --&gt;&lt;/td&gt;&lt;/tr&gt;\n&lt;/table&gt;',
            "SSR 规格矩阵",
            '&lt;table&gt;\n  &lt;caption&gt;Atlas 900 vs Atlas 800 规格&lt;/caption&gt;\n  &lt;thead&gt;&lt;tr&gt;&lt;th&gt;参数&lt;/th&gt;&lt;th&gt;Atlas 900&lt;/th&gt;&lt;th&gt;Atlas 800&lt;/th&gt;&lt;/tr&gt;&lt;/thead&gt;\n  &lt;tbody&gt;&lt;tr&gt;&lt;th scope="row"&gt;CPU&lt;/th&gt;&lt;td&gt;…&lt;/td&gt;&lt;td&gt;…&lt;/td&gt;&lt;/tr&gt;…&lt;/tbody&gt;\n&lt;/table&gt;',
            False,
            False,
            "空 td 占位，静态抓取读不到任何参数。",
            "表头与单元格全文在首包，可按列问答。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取后规格表仍含 th/td 与单元格文本，能回答 problems-odatetable 探针问句"),
            ("平行可证", "MD / llms 有与页面一致的规格表，或页面表已语义化可独立引用"),
            ("可证伪", "对「Atlas 900 vs 800 CPU/内存」须能按列引用单元格原文，与截图 / 空 td 失败判据互斥"),
        ],
    },
    "ocarousel": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "白名单产品 / 文档入口帧",
                    "要做亲和",
                    "帧指向产品能力、文档或认证等可引用入口时：须输出「标题 + 可引用摘要 + <code>a[href]</code>」，并完成图意转写；跳转型 CTA 禁 button 伪链。<br>对应页面：<a href=\"https://www.hiascend.com/zh\" target=\"_blank\" rel=\"noopener\">社区首页</a>",
                ),
                (
                    "strip",
                    "运营 / 活动 / 招募口号帧",
                    "不做亲和 · 入库剥离",
                    "赛事、招募、实习生、纯营销口号与产品规格混层时：默认 <code>data-llm-exclude</code> 出 llms 与知识库；人读发现归轮播，规格事实归文档页。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "信息帧三块文案位",
                "白名单入口帧稿面预留标题、一句话事实摘要、CTA 锚文本。允许文案视觉叠在 Banner 上，但须是独立 DOM 层（可抓）；禁整段烧进图、禁仅图标按钮",
            ),
            (
                "图意转写位 + 角色标注",
                "信息型 Banner 预留 figcaption / 短说明；纯装饰背景图标装饰。运营帧与入口帧在稿面分区标注（后者交付三要素，前者标 exclude）",
            ),
        ],
        "design_example": (
            "口号 Banner → 可引用入口帧",
            "文案烧进图",
            '<div style="height:118px;border-radius:8px;background:linear-gradient(135deg,#1d4ed8 0%,#3b82f6 55%,#93c5fd 100%);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-weight:600;font-size:13px;letter-spacing:.02em;user-select:none;" role="img" aria-label="算子开发者认证整图"><span style="opacity:.95;">算子开发者认证 · 立即前往 ›</span><span style="font-size:10px;font-weight:500;opacity:.7;">（像素图 · 源码无独立文案层）</span></div>',
            "叠字也可抓",
            '<div style="position:relative;border:1px solid var(--line);border-radius:8px;overflow:hidden;max-width:320px;height:118px;background:linear-gradient(135deg,#1d4ed8 0%,#3b82f6 55%,#93c5fd 100%);">\n'
            '  <div style="position:absolute;inset:0;opacity:.18;background:repeating-linear-gradient(135deg,transparent,transparent 8px,rgba(255,255,255,.35) 8px,rgba(255,255,255,.35) 9px);" aria-hidden="true"></div>\n'
            '  <div style="position:relative;z-index:1;height:100%;padding:12px 14px;display:flex;flex-direction:column;justify-content:center;color:#fff;">\n'
            '    <div style="font-weight:650;font-size:14px;">算子开发者认证（入门级）</div>\n'
            '    <div style="margin-top:4px;font-size:12px;opacity:.9;">官方认证入口，非 CANN API 规格。</div>\n'
            '    <a href="https://example.com/cert" style="margin-top:8px;font-size:12.5px;font-weight:600;color:#fff;text-decoration:underline;text-underline-offset:2px;">前往算子开发者认证报名 →</a>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "看起来有字，但字是图的一部分；源码抠不到标题 / 摘要 / 真链接。",
            "字仍叠在 Banner 上，但是独立 DOM（标题 + 摘要 + a[href]）；图意另用 alt / figcaption。",
        ),
        "content": [
            (
                "统一命名",
                "帧标题 / CTA 与落地文档 title、认证页名称对齐（如一律「算子开发者认证」）",
            ),
            (
                "入口与规格平行清单",
                "规格事实写在可引用文档页；白名单帧在 MD / llms 平铺「标题 → 摘要 → URL」。运营帧不进清单",
            ),
            (
                "过渡补位",
                "帧尚未 SSR 达标时，用 llms 临时补白名单入口；达标后以页面为准。运营 / 活动帧默认不入库",
            ),
        ],
        "content_example": (
            "帧文案：口号 → 事实摘要 + 文档深链",
            "只有营销口号，无平行入口",
            "标题：算子开发者认证（入门级）\n摘要：（无）\nCTA：前往认证\n落地：活动报名页；llms 未列文档深链。",
            "可引用摘要 + 文档",
            "标题：算子开发者认证（入门级）\n摘要：官方认证入口，覆盖 Ascend C 入门；安装与 API 见 CANN 文档。\nCTA：前往算子开发者认证报名\n文档：/doc/…/cann-install",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平铺白名单入口",
                "## 社区首页 · 推广入口（白名单）\n- [算子开发者认证](https://…/cert) — 官方认证入口，非 API 规格\n- [CANN 安装文档](https://…/doc/cann-install)",
            ),
            (
                "llms 临时补入口",
                "# llms.txt（过渡）\n- [算子开发者认证报名](https://…/cert)\n- [CANN 安装文档](https://…/doc/cann-install)",
                "白名单帧 SSR 达标后临时项可移除；勿把运营口号帧写入清单。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "白名单入口帧：标题、摘要、<code>a[href]</code> 须写入首包，全量帧均可抓（可用位移隐藏，勿删 DOM）。运营轮播根节点默认 <code>data-llm-exclude</code>；静态抓取不应把口号当产品规格。",
        "frontend": [
            (
                "全量帧进首包",
                "每帧独立节点输出标题、摘要、真实 a[href]；禁止只渲染当前帧",
            ),
            (
                "图意与装饰分流",
                "信息图 figure + 非空 alt；装饰图 alt=\"\" / aria-hidden",
            ),
            (
                "运营根节点 exclude",
                "运营轮播加 data-llm-exclude；仅白名单帧可加 data-llm-cite",
            ),
        ],
        "frontend_example": (
            "轮播：仅当前帧 → 全量帧 + exclude",
            "仅当前帧 / button 伪链",
            '&lt;div class="o-carousel"&gt;\n  &lt;div class="banner-title"&gt;算子开发者认证&lt;/div&gt;\n  &lt;button&gt;前往认证&lt;/button&gt;\n  &lt;!-- 其余帧 JS 注入 --&gt;\n&lt;/div&gt;',
            "全量帧 + 排除标记",
            '&lt;div class="o-carousel" data-llm-exclude="true"&gt;\n  &lt;article class="o-carousel-item" data-llm-cite="true"&gt;\n    &lt;h2&gt;算子开发者认证（入门级）&lt;/h2&gt;\n    &lt;p&gt;官方认证入口，非 CANN API 规格。&lt;/p&gt;\n    &lt;a href="https://…/cert"&gt;前往算子开发者认证报名&lt;/a&gt;\n  &lt;/article&gt;\n  &lt;!-- 其余帧同样完整输出 --&gt;\n&lt;/div&gt;',
            False,
            False,
            "其余帧不在首包，CTA 是 button，静态抓取跟不了链。",
            "全量帧可读；运营根 exclude，白名单帧可 cite。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取后白名单帧仍含标题 + 摘要 + href；运营口号未当规格入库"),
            ("规格归文档", "产品能力说明可从文档页引用，不依赖 Banner 口号"),
            ("可证伪", "对「算子认证入口链到哪 / 是不是 API 规格」须能引用摘要与 href，与纯口号失败判据互斥"),
        ],
    },
    "otrees": {
        "hide_sample_meta": True,
        "design_example_side_by_side": True,
        "design": [
            (
                "视觉层级可维持",
                "树外观与展开交互按常规即可，无需为亲和重做视觉",
            ),
            (
                "节点文案自描述",
                "树节点用可读标题标明对应内容块（如「安装步骤 / 依赖说明」）；勿只写「节点1 / 更多」。节点不必都画成链接",
            ),
        ],
        "design_example": (
            "同页树：只交当前块 → 各节点内容均交付",
            "仅当前选中块有内容",
            '<div style="display:flex;gap:12px;font-size:12.5px;">\n'
            '  <ul class="rf-nav-links" style="margin:0;min-width:100px;color:var(--muted);">\n'
            '    <li><span>节点 1</span></li>\n'
            '    <li><span style="font-weight:600;color:var(--text);border-bottom:2px solid var(--accent);">节点 2</span></li>\n'
            '    <li><span>更多 ›</span></li>\n'
            '  </ul>\n'
            '  <div style="flex:1;border:1px solid var(--line);border-radius:6px;padding:10px;background:#fff;">\n'
            '    <p style="margin:0 0 4px;font-weight:600;color:var(--muted);">简介</p>\n'
            '    <p style="margin:0;color:var(--muted);font-size:12px;">一段可见说明…</p>\n'
            '  </div>\n'
            '</div>',
            "节点自描述 · 各块均交付",
            '<div style="display:flex;gap:12px;font-size:12.5px;">\n'
            '  <ul class="rf-nav-links" style="margin:0;min-width:120px;">\n'
            '    <li><span>安装步骤</span></li>\n'
            '    <li><span style="font-weight:600;border-bottom:2px solid var(--accent);">依赖说明</span></li>\n'
            '    <li><span>常见问题</span></li>\n'
            '  </ul>\n'
            '  <div style="flex:1;">\n'
            '    <div style="border:1px solid var(--line);border-radius:6px;padding:10px;background:#fff;">\n'
            '      <p style="margin:0 0 4px;font-weight:600;">依赖说明</p>\n'
            '      <p style="margin:0;color:var(--muted);font-size:12px;">需 GCC 7.3+、GLIBC 2.27+ …</p>\n'
            '    </div>\n'
            '    <p style="margin:8px 0 0;font-size:11px;color:var(--muted);">稿面另交：安装步骤、常见问题全文案位</p>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "默认选中块看起来有内容，但节点是泛词，其它节点正文未交付；实现上常等切换才注入。",
            "<strong>要点：</strong>节点自描述；每个节点对应内容块都要交付（实现上须首包输出，不必每节点都有 URL）。",
        ),
        "content": [
            (
                "统一命名",
                "树节点标题与内容块标题、MD 章节名对齐，避免「节点2」与正文对不上",
            ),
            (
                "内容块平行清单",
                "各节点对应要点写入 Markdown / 独立文档；勿只存在于点击树节点后才出现的面板里",
            ),
            (
                "过渡补位",
                "页面内容块未进首包前，用 MD / llms 临时补各节点说明；SSR 达标后以页面为准",
            ),
        ],
        "content_example": (
            "同页内容树 → MD 平行结构",
            "要点只在选中节点后",
            "默认只看到「依赖说明」一块；\n切到「安装步骤 / 常见问题」才出正文；\n无按树结构写的 Markdown 可对照。",
            "MD 按树节点平铺",
            "## 安装与依赖\n### 安装步骤\n1. …\n### 依赖说明\n需 GCC 7.3+、GLIBC 2.27+ …\n### 常见问题\n- …",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 按树节点平铺",
                "## 安装与依赖\n### 安装步骤\n1. …\n### 依赖说明\n需 GCC 7.3+、GLIBC 2.27+ …\n### 常见问题\n- …",
            ),
            (
                "llms 临时补内容块",
                "# llms.txt（过渡）\n## 依赖说明\n需 GCC 7.3+ …\n## 安装步骤\n1. …",
                "各内容块 SSR 进首包后，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "同页切换内容树：节点不必都有 <code>a[href]</code>；各内容块须写入首包 HTML。静态抓取（不执行 JS）仍能读到全部节点标题与对应正文。跳转型手册目录见 <a href=\"principles-omenu.html\">OMenu</a>（面板型页签见 <a href=\"principles-otab.html\">OTab</a>）。",
        "frontend": [
            (
                "节点标题进首包",
                "树节点名称写进源码；勿只留空容器后靠 JS 注入节点文案",
            ),
            (
                "未选中内容块也进首包",
                "各节点对应正文全量 SSR；可用 hidden / display:none，禁止点击节点后才注入",
            ),
            (
                "勿把 TOC 只放 __NUXT_DATA__",
                "节点名与内容块文本须落到可爬 HTML；JSON 仅作 hydrate",
            ),
        ],
        "frontend_example": (
            "同页内容树",
            "空壳 · 点击才挂内容",
            '&lt;nav class="o-trees"&gt;&lt;/nav&gt;\n&lt;div class="tree-panel"&gt;&lt;!-- 点击节点后才注入 --&gt;&lt;/div&gt;',
            "SSR 全量内容块",
            '&lt;nav class="o-trees"&gt;\n  &lt;button type="button" aria-selected="false"&gt;安装步骤&lt;/button&gt;\n  &lt;button type="button" aria-selected="true"&gt;依赖说明&lt;/button&gt;\n  &lt;button type="button"&gt;常见问题&lt;/button&gt;\n&lt;/nav&gt;\n&lt;div hidden&gt;安装步骤正文…&lt;/div&gt;\n&lt;div&gt;依赖说明：需 GCC 7.3+…&lt;/div&gt;\n&lt;div hidden&gt;常见问题…&lt;/div&gt;',
            False,
            False,
            "节点与正文都不在首包，静态抓取读不到各内容块。",
            "节点标题与全部内容块进首包；未选中可用 hidden，文本仍可抓。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取（不执行 JS）后，仍能读到全部树节点标题与对应内容块正文"),
            ("可证伪", "对「依赖说明 / 安装步骤分别写了什么」须能引用首包文本，与点击后才注入失败判据互斥"),
            ("与 OMenu 分工", "换 URL 的手册目录归 OMenu；本组件不要求每个节点都有 href"),
        ],
    },
    "otoggle": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "映射下载 / 版本的选型 Toggle",
                    "要做亲和",
                    "型号 / 架构 / 安装方式等选项映射下载页或包表时，完整 option 矩阵须进首包（可读 label + <code>ids=</code> 或 URL），或平行写进 MD / llms；<code>?ids=</code> 编码态不能替代可读矩阵。<br>对应页面：<a href=\"https://www.hiascend.com/hardware/firmware-drivers\" target=\"_blank\" rel=\"noopener\">固件与驱动</a>",
                ),
                (
                    "strip",
                    "纯 UI 筛选 Toggle",
                    "不做亲和 · 入库剥离",
                    "不映射内容的显示切换 / 纯前端筛选，选中态不是官网知识。入库管道宜标 <code>data-llm-exclude</code> 或剥离。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_no_example": True,
        "design": [
            (
                "视觉交互可维持",
                "Toggle 外观与点选交互按常规即可，无需为亲和重做视觉",
            ),
            (
                "稿面标注角色",
                "标注哪些 Toggle 映射下载 / 版本（须交全量 option 文案），哪些是纯 UI 筛选（标 exclude）；勿假定「未选中项不用交付」",
            ),
        ],
        "content": [
            (
                "统一命名",
                "option 文案与包表 / 下载页 title、llms 条目对齐（型号 / 架构 / 安装方式全称一致）",
            ),
            (
                "选型矩阵平行清单",
                "在 llms.txt 或文档 MD 中平铺「选项 → 落地 URL（含 ids=）」或交叉表；即使页面只渲染当前选中态，也能枚举全部组合入口",
            ),
            (
                "过渡补位",
                "首包尚无完整矩阵时，用 llms / MD 临时补；SSR 或首包 JSON 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "固件与驱动 → MD / llms 平行矩阵",
            "只有当前 ids，无全量选项清单",
            "浏览器可见型号 / 架构 / 安装方式筛选；\n首包无完整 option 文本，靠 ?ids= 与 __NUXT_DATA__ 恢复；\n无 Markdown / llms 的选项 → URL 清单。",
            "MD 平行选型清单",
            "## 固件与驱动 · 选型\n- 架构：x86_64 → …?ids=…,x86_64,…\n- 架构：AArch64 → …?ids=…,AArch64,…\n- 安装方式：online_apt_get → …",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行选型清单",
                "## 固件与驱动 · 选型\n- 架构：x86_64 → …?ids=…,x86_64,…\n- 架构：AArch64 → …?ids=…,AArch64,…\n- 安装方式：online_apt_get → …",
            ),
            (
                "llms 临时补 option → URL",
                "# llms.txt（过渡）\n- [AArch64 · online](https://www.hiascend.com/hardware/firmware-drivers?ids=…)\n- [x86_64 · online](https://www.hiascend.com/hardware/firmware-drivers?ids=…)",
                "页面 SSR / 首包 JSON 矩阵达标后，llms 中重复项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "映射下载 / 版本的 Toggle 须把完整 option 矩阵写入首包 HTML 或首包 JSON；静态抓取（不执行 JS）仍能枚举型号 / 架构 / 安装方式及对应 URL（对标：NVIDIA CUDA <code>data-react-props</code>）。",
        "frontend": [
            (
                "全量 option 进首包",
                "全部选项以可读 label + ids / URL 输出；未选中项可用隐藏样式保留，勿只留当前选中态",
            ),
            (
                "ids 不能替代可读矩阵",
                "?ids= 仅表达当前组合；须另有人类可读 option 列表，或把完整矩阵 JSON 写进首包 data-* 并文档化解析方式",
            ),
            (
                "交叉表可静态读",
                "包列表随 Toggle 切换时，关键交叉表须 SSR 或旁路 JSON / llms；勿仅客户端按选中态注入",
            ),
            (
                "纯 UI Toggle 标注排除",
                "不映射内容的筛选加 data-llm-exclude，管道勿当正文 chunk",
            ),
        ],
        "frontend_example": (
            "固件与驱动 Toggle",
            "仅当前 ids · 无 option 矩阵",
            '&lt;!-- URL: ?ids=d802,…,AArch64,online_apt_get --&gt;\n&lt;!-- 浏览器可见筛选；首包无「x86_64 / AArch64 / …」全量 option 文本 --&gt;\n&lt;script id="__NUXT_DATA__"&gt;…选中态…&lt;/script&gt;',
            "SSR option 或首包 JSON 矩阵",
            '&lt;div class="o-toggle" data-dim="arch"&gt;\n  &lt;button type="button" data-ids="…,x86_64,…"&gt;x86_64&lt;/button&gt;\n  &lt;button type="button" data-ids="…,AArch64,…"&gt;AArch64&lt;/button&gt;\n&lt;/div&gt;\n&lt;!-- 或 data-react-props 含完整 structure，禁 JS 也可解析 --&gt;',
            False,
            False,
            "静态抓取只能看到当前 ?ids=，列不全架构 / 安装方式及对应包表入口。",
            "全量 option 可读 label 进首包（或首包 JSON 矩阵）；静态抓取即可枚举选型。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取固件与驱动页（不执行 JS）后，仍能枚举型号 / 架构 / 安装方式等选项及对应 URL，能回答 problems-otoggle 探针问句"),
            ("html 可抓全", "选型矩阵可读性达到友商水准（NVIDIA CUDA：OS/Architecture 树在首包 data-react-props）"),
            ("可证伪", "对「各 Toggle 选项对应哪个下载 URL / ids」须能引用具体文本或 JSON 字段，与仅 ?ids= 失败判据互斥"),
        ],
    },
    "osearch": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "可搜索文档的发现层",
                    "要做亲和",
                    "凡搜索能命中的文档，须有独立可爬 URL，并收进 sitemap / llms（可配合导航 / 索引页），让 Agent 不搜索也能枚举全部文档。要做亲和的是<strong>发现层</strong>，不是搜索框。<br>对应页面：<a href=\"https://www.hiascend.com/zh\" target=\"_blank\" rel=\"noopener\">社区首页</a>",
                ),
                (
                    "strip",
                    "搜索框 / 搜索结果本身",
                    "不做亲和 · 入库剥离",
                    "输入框、结果列表、搜索 API 都是纯交互黑盒（结果靠 JS 返回）。别费力把它们做成可爬；入库标 <code>data-llm-exclude</code> 或剥离即可。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "预留非搜索发现路径",
                "稿面须有导航、文档目录或索引入口；别让深页只能靠搜索命中",
            ),
            (
                "搜索只作加速，不作唯一入口",
                "搜索框可保留，但同屏须能看出不搜索也能逐层到达文档的路径",
            ),
        ],
        "design_example": (
            "版面发现入口：只有搜索 → 目录 + 搜索",
            "只有搜索框",
            '<div style="border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;color:var(--muted);font-size:12.5px;">\n'
            '  搜索 CANN 文档…\n'
            '</div>',
            "目录 + 搜索",
            '<div style="display:flex;gap:12px;align-items:flex-start;font-size:12.5px;">\n'
            '  <div style="min-width:118px;border:1px solid var(--line);border-radius:6px;padding:8px 10px;background:#fff;">\n'
            '    <p class="rf-sidebar-title">文档目录</p>\n'
            '    <ul class="rf-nav-links">\n'
            '      <li><a href="#">快速开始</a></li>\n'
            '      <li><a href="#">安装部署</a></li>\n'
            '      <li><a href="#">API 参考</a></li>\n'
            '    </ul>\n'
            '  </div>\n'
            '  <div style="flex:1;border:1px solid var(--line);border-radius:6px;padding:10px 12px;background:#fff;color:var(--muted);">\n'
            '    搜索…\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "版面只有搜索框，没有导航 / 目录；不搜索就走不到文档页。",
            "<strong>要点：</strong>同屏预留目录或索引链；搜索只是加速，不是唯一发现层。",
        ),
        "content": [
            (
                "全量 URL 进 sitemap / llms",
                "凡搜索能命中的文档都要有独立可爬 URL，并收进 sitemap.xml 与 llms.txt；新增 / 下线同步更新",
            ),
            (
                "检索范围写进正文",
                "「本站含哪些文档 / 版本」写成可引用正文或文档索引页，勿只塞在 placeholder（如「搜索 CANN 文档」）",
            ),
            (
                "过渡补位",
                "导航尚未覆盖的深页，先用 llms / sitemap 临时补全；发现层达标后以清单 + 页面链为准，去掉重复维护",
            ),
        ],
        "content_example": (
            "文档发现 → sitemap / llms 全量清单",
            "深页只能靠站内搜索",
            "部分 CANN 文档仅站内搜索可达；\nsitemap / llms 未列这些文档 URL，\n禁 JS 时枚举不全。",
            "llms 平铺文档清单",
            "# llms.txt\n## CANN 文档\n- [安装指南](https://…/document/cann-install)\n- [算子开发](https://…/document/operator)",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "llms 平铺文档清单",
                "# llms.txt\n## CANN 文档\n- [安装指南](https://…/document/cann-install)\n- [算子开发](https://…/document/operator)",
            ),
            (
                "sitemap 同步全量",
                "# sitemap.xml（节选）\nhttps://…/document/cann-install\nhttps://…/document/operator",
                "新增 / 下线文档须与 llms 同步更新。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "搜索框本身不改造；发现层须保证每篇文档有独立可爬 URL，并由 sitemap / llms 枚举。静态抓取（不执行 JS）不靠搜索也能列出文档入口。",
        "frontend": [
            (
                "文档独立可爬 URL",
                "每篇文档 SSR 出稳定可跟链地址；勿把正文只藏在 ?q= 搜索态或点击后才渲染的结果里",
            ),
            (
                "sitemap 自动覆盖",
                "构建生成 sitemap.xml 覆盖全部文档 URL，并在 robots 声明；不必为搜索结果页做特殊爬取",
            ),
            (
                "搜索控件标注排除",
                "search input / 按钮 / 建议下拉加 data-llm-exclude；发现层责任由 URL + sitemap 承担",
            ),
        ],
        "frontend_example": (
            "发现层：搜索黑盒 → 可爬 URL + sitemap",
            "内容锁在搜索里",
            '&lt;div class="o-search"&gt;…&lt;/div&gt;\n&lt;!-- 深页无独立 a[href]，仅搜索 API 可达 --&gt;',
            "SSR URL + sitemap 枚举",
            '&lt;a href="/document/cann-install"&gt;CANN 安装指南&lt;/a&gt;\n&lt;!-- sitemap.xml --&gt;\n&lt;url&gt;&lt;loc&gt;https://…/document/cann-install&lt;/loc&gt;&lt;/url&gt;',
            False,
            False,
            "搜索结果靠 JS 返回，静态抓取拿不到文档列表，深页也无独立入口。",
            "文档有独立 a[href]，sitemap / llms 可枚举；不搜索也能发现。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取后，不用搜索也能从导航 / sitemap / llms 枚举文档 URL，能回答 problems-osearch 探针问句"),
            ("清单齐全", "sitemap.xml 与 llms.txt 覆盖全部可搜索文档 URL，新增页同步收录"),
            ("可证伪", "对「不用搜索列出 CANN 安装文档 URL」须能给出清单，与仅靠搜索的失败判据互斥"),
        ],
    },
    "oselect": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "映射文档 / 下载的选项",
                    "要做亲和",
                    "型号 / 架构 / 安装方式等选项对应下载页或文档时，完整 option 文本与落地 URL（含 <code>?ids=</code>）须进首包可读；规格宜有不依赖选中态的平行文档。<br>对应页面：<a href=\"https://www.hiascend.com/hardware/firmware-drivers\" target=\"_blank\" rel=\"noopener\">固件与驱动</a>",
                ),
                (
                    "strip",
                    "纯表单筛选选项",
                    "不做亲和 · 入库剥离",
                    "排序、纯前端筛选等不含信息架构的 select，选项态不是官网知识。入库管道宜标 <code>data-llm-exclude</code> 或剥离。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_no_example": True,
        "design": [
            (
                "视觉交互可维持",
                "Select 外观与下拉交互按常规即可，无需为亲和重做视觉",
            ),
            (
                "规格勿只锁在选中态",
                "稿面要求选项映射的规格有一份不依赖选择就可读的呈现（文档页平行表即可）；标注哪些 Select 映射内容、哪些纯筛选（后者 exclude）",
            ),
        ],
        "content": [
            (
                "统一命名",
                "option 文案与落地页 title、规格表、llms 条目对齐（型号 / 架构 / 安装方式全称一致）",
            ),
            (
                "规格与选项平行清单",
                "规格以 Markdown 平行表写进独立可爬文档页；同时在 llms / 正文维护「选项 → 落地 URL（含 ids=）」；产品页 Select 仅筛选，选项态不入库",
            ),
            (
                "过渡补位",
                "首包尚无完整 option 时，用 llms / MD 临时补映射；SSR 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "选型规格 → 文档 MD / llms 平行轨",
            "规格锁在选中后，无平行表",
            "产品页规格靠选中某型号后 JS 注入；\n文档 / MD 未收录该规格，也无选项 → URL 清单；\n禁 JS 时读不到参数与落地地址。",
            "文档 Markdown 平行表",
            "## Atlas 800 规格\n| 参数 | 值 |\n| NPU | 8 × 昇腾 |\n| 内存 | 1TB |\n（文档页独立 URL，可爬）",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "文档 Markdown 平行表",
                "## Atlas 800 规格\n| 参数 | 值 |\n| NPU | 8 × 昇腾 |\n| 内存 | 1TB |",
            ),
            (
                "llms 临时补 option → URL",
                "# llms.txt（过渡）\n- [Atlas 800 固件与驱动](https://www.hiascend.com/hardware/firmware-drivers?ids=A1)\n- [Atlas 800 规格说明](https://…/document/atlas800-spec)",
                "option SSR 达标且规格页可爬后，临时映射可收敛。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "映射文档 / 下载的 Select 须把完整 option（可读 label + ids / URL）写入首包；静态抓取（不执行 JS）仍能枚举选项并跟到落地页。纯表单筛选见场景2，管道剥离。",
        "frontend": [
            (
                "关键 option 进首包",
                "映射内容的 option 以可读 label + ids / URL SSR；勿空 <select> 后靠 JS 注入，也勿只留当前选中项",
            ),
            (
                "label 须人类可读",
                "可见文案用型号 / 架构 / 安装方式全称；勿仅 value/ids 编码而无可读 text",
            ),
            (
                "纯交互态标注排除",
                "纯筛选 select 加 data-llm-exclude，与正文 / 映射清单区分，避免选项态污染入库",
            ),
        ],
        "frontend_example": (
            "固件与驱动 Select",
            "首包空 select · 靠 JS 注入",
            '&lt;select id="model"&gt;&lt;/select&gt;\n&lt;!-- option 由 JS 注入；规格靠选中后渲染 --&gt;',
            "SSR option + 落地链",
            '&lt;select id="model"&gt;\n  &lt;option value="atlas800?ids=A1"&gt;Atlas 800（8×昇腾）&lt;/option&gt;\n  &lt;option value="atlas800?ids=A2"&gt;Atlas 800I A2&lt;/option&gt;\n&lt;/select&gt;\n&lt;a href="/hardware/firmware-drivers?ids=A1"&gt;Atlas 800 固件与驱动&lt;/a&gt;',
            False,
            False,
            "静态抓取读不到 option 文本，也无法证伪各型号对应下载 URL。",
            "option 可读 label 进首包，并可跟到落地页；静态抓取即可枚举选型。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取固件与驱动页（不执行 JS）后，仍能枚举 Select 选项及对应 URL，能回答 problems-oselect 探针问句"),
            ("可证伪", "对「各选项对应哪个下载 URL / ids」须能引用具体 option 文本或平行清单，与空 select / 仅 ids 失败判据互斥"),
            ("管道", "映射内容的 option 可入库或由 MD/llms 互证；纯表单 select 标 exclude"),
        ],
    },
    "orate": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "评分数字（社会证明）",
                    "要做亲和",
                    "平均分 / 评分人数若需被引用，须在首包以可读文本呈现（如「4.6 分 · 128 人评分」），勿只靠星标图标或客户端拉取。",
                ),
                (
                    "strip",
                    "「我要评分」等操作 CTA",
                    "不做亲和 · 入库剥离",
                    "评分按钮是操作入口，不是质量规格。入库宜标 <code>data-llm-exclude</code>；官方认证说明另写正文文档，勿与用户评分混为一谈。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "分数留成可见文本",
                "稿面为平均分 + 人数预留可读文案位（如「4.6 分 · 128 人评分」），勿只画星标",
            ),
            (
                "操作按钮标纯交互",
                "「我要评分」与分数文本分区，稿面标 exclude；勿画成官方认证印章",
            ),
        ],
        "design_example": (
            "评分：只有星标 → 可读分数 + 角色分区",
            "只有星标 · 操作混排",
            '<div style="display:flex;align-items:center;gap:8px;font-size:12.5px;">\n'
            '  <span style="color:#f5a623;letter-spacing:1px;" aria-hidden="true">★★★★☆</span>\n'
            '  <span style="display:inline-block;padding:4px 10px;border:1px solid var(--line);border-radius:4px;color:var(--muted);">我要评分</span>\n'
            '</div>',
            "可读分数 · CTA 分区",
            '<div style="font-size:12.5px;">\n'
            '  <div style="display:flex;align-items:center;gap:8px;">\n'
            '    <span style="color:#f5a623;letter-spacing:1px;" aria-hidden="true">★★★★☆</span>\n'
            '    <span style="font-weight:600;">4.6 分</span>\n'
            '    <span style="color:var(--muted);">· 128 人评分</span>\n'
            '  </div>\n'
            '  <div style="margin-top:8px;">\n'
            '    <span style="display:inline-block;padding:4px 10px;border:1px solid var(--line);border-radius:4px;color:var(--muted);font-size:12px;">我要评分</span>\n'
            '  </div>\n'
            '</div>',
            True,
            True,
            "只有星标 + 操作按钮；平均分 / 人数无可读文本，还容易把 CTA 误当质量规格。",
            "<strong>要点：</strong>分数与人数作可见文本交付；「我要评分」标纯交互、与认证说明分开。",
        ),
        "content": [
            (
                "统一表述",
                "若引用社会证明，正文 / llms 与页面分数文案一致（分值、人数口径相同）",
            ),
            (
                "认证说明走独立文档",
                "官方质量 / 合规认证写进可引用文档页，勿用「我要评分」或星标暗示已认证",
            ),
            (
                "过渡补位",
                "分数尚未 SSR 时，可在文档旁注临时写明「用户评分约 x 分」；页面达标后以首包文本为准",
            ),
        ],
        "content_example": (
            "评分社会证明 → 正文可引用",
            "只有 UI 星标，无正文口径",
            "页面仅有星标与「我要评分」；\n正文 / MD 未写平均分与人数，\n也未把官方认证与用户评分分开。",
            "正文旁注社会证明",
            "## 文档反馈\n- 用户评分：4.6 分（128 人）\n- 官方认证：见《质量认证说明》…\n（「我要评分」为操作入口，不作规格）",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "正文旁注社会证明",
                "## 文档反馈\n- 用户评分：4.6 分（128 人）\n- 官方认证：见《质量认证说明》…",
            ),
            (
                "llms 临时补口径（可选）",
                "# llms.txt（过渡）\n- 某文档用户评分：4.6 / 128 人",
                "页面分数 SSR 可读后，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "若需引用评分作社会证明，平均分 / 人数须写入首包可读文本；「我要评分」等操作 CTA 标 exclude。静态抓取应能读到分数，且不会把 CTA 当成认证结论。",
        "frontend": [
            (
                "分数文本进首包",
                "输出可读的分值与人数节点；勿只渲染星标图标，也勿仅靠 JS 拉取后才出现数字",
            ),
            (
                "操作 CTA 标注排除",
                "「我要评分 / 提交评分」加 data-llm-exclude，入库勿当正文 chunk",
            ),
            (
                "与认证 DOM 分区",
                "官方认证徽章 / 说明若存在，用独立区块或链到文档；勿与 ORate 操作区混在同一可抓文案里",
            ),
        ],
        "frontend_example": (
            "ORate 评分区",
            "仅星标 + button，无分数字",
            '&lt;div class="o-rate"&gt;\n  &lt;span class="stars"&gt;★★★★☆&lt;/span&gt;\n  &lt;button type="button"&gt;我要评分&lt;/button&gt;\n&lt;/div&gt;',
            "分数 SSR · CTA exclude",
            '&lt;div class="o-rate"&gt;\n  &lt;span aria-hidden="true"&gt;★★★★☆&lt;/span&gt;\n  &lt;span class="o-rate-score"&gt;4.6 分&lt;/span&gt;\n  &lt;span class="o-rate-count"&gt;128 人评分&lt;/span&gt;\n  &lt;button type="button" data-llm-exclude&gt;我要评分&lt;/button&gt;\n&lt;/div&gt;',
            False,
            False,
            "静态抓取读不到平均分，还可能把「我要评分」当质量结论。",
            "分值与人数进首包可引用；操作按钮 exclude，不与认证混淆。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "若需社会证明：静态抓取后仍能读到平均分 / 人数文本"),
            ("管道分流", "操作 CTA 不入库；分数文本可引用，且不与官方认证说明混读"),
            ("可证伪", "对「平均分是多少 / 是否等于官方认证」须能区分引用分数与认证文档，与仅星标+CTA 失败判据互斥"),
        ],
    },
    "ocascader": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "映射内容路径的级联",
                    "要做亲和",
                    "各级代表文档分类 / 内容路径时，option 须用可读全称进首包；映射到落地页的宜带 <code>a[href]</code>。面板勿等悬停 / 点击才挂载选项。",
                ),
                (
                    "strip",
                    "纯地址 / 表单字段级联",
                    "不做亲和 · 入库剥离",
                    "省市区等纯表单级联不承载官网知识。入库宜标 <code>data-llm-exclude</code> 或剥离。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_no_example": True,
        "design": [
            (
                "视觉交互可维持",
                "级联外观与逐级展开按常规即可，无需为亲和重做视觉",
            ),
            (
                "稿面标注角色与文案",
                "标注内容路径型 vs 表单型；内容路径各级用分类 / 文档全称，映射落地的按可跟链交付",
            ),
        ],
        "content": [
            (
                "统一命名",
                "各级 option 文案与落地页 title、llms 分类名对齐；勿只用编号 / value",
            ),
            (
                "分类路径平行清单",
                "在 llms.txt / 文档 MD 写成与级联层级一致的嵌套列表（分类 + URL）；面板抓不全时仍可枚举路径",
            ),
            (
                "过渡补位",
                "级联 HTML 未达标前，用 llms / MD 临时补分类路径；SSR 达标后以页面为准，重复项可移除",
            ),
        ],
        "content_example": (
            "内容路径级联 → MD / llms 平行目录",
            "路径只在级联面板里",
            "分类层级只在级联 JS 面板中；\n首包读不全各级 option；\n无 Markdown / llms 嵌套分类 + URL。",
            "MD 平行分类目录",
            "## CANN 文档分类\n- CANN\n  - 安装部署\n    - [CANN 安装指南](/document/cann/install/guide)\n    - [驱动安装](/document/cann/install/driver)\n  - API 参考\n    - …",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平行分类目录",
                "## CANN 文档分类\n- CANN\n  - 安装部署\n    - [CANN 安装指南](/document/cann/install/guide)\n    - [驱动安装](/document/cann/install/driver)\n  - API 参考\n    - …",
            ),
            (
                "llms 临时补路径",
                "# llms.txt（过渡）\n- [CANN 安装指南](/document/cann/install/guide)\n- [驱动安装](/document/cann/install/driver)",
                "级联 SSR 达标后以 HTML 为准，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "内容路径型级联：各级 option 可读文本须写入首包；映射落地页的宜为 <code>a[href]</code>。静态抓取仍能枚举路径（表单级联见场景2，管道剥离）。",
        "frontend": [
            (
                "各级 option 进首包",
                "用人类可读全称输出；勿空面板后靠悬停 / 点击才挂，也勿仅 value/id 无可见文案",
            ),
            (
                "落地项宜为真实链接",
                "映射文档 / 分类页的选项宜 a[href]；至少当前路径分支须在首包可读",
            ),
            (
                "表单级联标注排除",
                "省市区等纯表单字段加 data-llm-exclude，与内容路径级联区分",
            ),
        ],
        "frontend_example": (
            "内容路径级联",
            "空壳 · 悬停才挂选项",
            '&lt;div class="o-cascader"&gt;&lt;/div&gt;\n&lt;!-- 各级悬停 / 点击后才挂，无可读 option / a[href] --&gt;',
            "SSR 可读路径 + 落地链",
            '&lt;div class="o-cascader"&gt;\n  &lt;span&gt;CANN&lt;/span&gt;\n  &lt;span&gt;安装部署&lt;/span&gt;\n  &lt;a href="/document/cann/install/guide"&gt;CANN 安装指南&lt;/a&gt;\n&lt;/div&gt;',
            False,
            False,
            "静态抓取读不到各级分类名，也无法跟到安装指南等落地页。",
            "各级可读文案进首包；叶子落地写成 a[href]，静态抓取即可枚举路径。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可达", "静态抓取后，内容路径级联仍能读到各级 option 文案，映射落地的可跟链"),
            ("管道分流", "表单级联 exclude；内容路径可入库或由 MD/llms 互证"),
            ("可证伪", "对「级联路径对应哪些官方内容 URL」须能引用可读文本或 href，与空面板 / 仅 id 失败判据互斥"),
        ],
    },
    "otag": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "版本 / 状态语义标签",
                    "要做亲和",
                    "「CANN 8.0」「已认证」「停止维护」等承载事实的标签：文案须进首包可读，并在正文 / 文档有对应定义与时间点。<br>对应页面：<a href=\"https://www.hiascend.com/developer\" target=\"_blank\" rel=\"noopener\">开发者中心</a>",
                ),
                (
                    "strip",
                    "营销 / 装饰标签",
                    "不做亲和 · 入库剥离",
                    "「热门」「新品」「推荐」等无规格定义的营销口号不是事实。入库管道宜标 <code>data-llm-exclude</code> 或剥离，别当官方结论。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "视觉可维持",
                "标签外观（色块 / 圆角 / 字号）按常规即可，无需为亲和重做视觉",
            ),
            (
                "稿面标注角色",
                "标注哪些是语义标签（须交正文定义）、哪些是装饰标签（标 exclude）；勿把「热门」与「停止维护」画成同级事实",
            ),
        ],
        "design_example": (
            "卡片标签：混排无标注 → 语义 / 装饰分流",
            "两类标签同级混排",
            '<div style="border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:#fff;">\n'
            '  <p style="margin:0 0 8px;font-weight:600;color:var(--text);">CANN 软件包</p>\n'
            '  <p style="margin:0;display:flex;gap:6px;flex-wrap:wrap;">\n'
            '    <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#fef3f2;color:#b42318;">停止维护</span>\n'
            '    <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#fffaeb;color:#b54708;">热门</span>\n'
            '    <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#eff8ff;color:#175cd3;">新品</span>\n'
            '  </p>\n'
            '</div>',
            "语义保留 · 装饰标角色",
            '<div style="border:1px solid var(--line);border-radius:8px;padding:12px 14px;background:#fff;">\n'
            '  <p style="margin:0 0 8px;font-weight:600;color:var(--text);">CANN 软件包</p>\n'
            '  <p style="margin:0;display:flex;gap:6px;flex-wrap:wrap;align-items:center;">\n'
            '    <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#fef3f2;color:#b42318;">停止维护</span>\n'
            '    <span style="font-size:11px;color:var(--muted);">← 语义 · 正文须有定义</span>\n'
            '  </p>\n'
            '  <p style="margin:8px 0 0;display:flex;gap:6px;flex-wrap:wrap;align-items:center;">\n'
            '    <span style="font-size:12px;padding:2px 8px;border-radius:4px;background:#fffaeb;color:#b54708;opacity:.7;">热门</span>\n'
            '    <span style="font-size:11px;color:var(--muted);">← 装饰 · 入库剥离</span>\n'
            '  </p>\n'
            '</div>',
            True,
            True,
            "「停止维护 / 热门 / 新品」同级展示，稿面未区分事实与口号，落地易整批入库。",
            "语义标签单独成组并要求正文定义；装饰标签标 exclude，不当规格事实。",
        ),
        "content": [
            (
                "统一命名",
                "标签文案与正文 / 规格表 / 版本说明中的状态名对齐（如一律「停止维护」，勿混用「停维 / EOL / 下线」）",
            ),
            (
                "语义定义平行清单",
                "在文档 MD 或规格页维护「标签 → 官方定义 / 截止时间」；卡片上的短标签只作索引，不作唯一依据",
            ),
            (
                "过渡补位",
                "正文尚未写清定义时，用 llms / MD 临时补状态口径；页面达标后以正文为准，临时项可移除。营销标签不进清单",
            ),
        ],
        "content_example": (
            "状态标签：孤立口号 → 正文有定义",
            "卡片有标签，正文无定义",
            "开发者中心卡片打「停止维护」「热门」；\n正文 / 文档无对应定义或截止时间；\nAgent 只能复述色块文案，无法引用官方依据。",
            "正文写清定义",
            "## 版本状态说明\n- 停止维护：不再提供补丁与安全更新，截止 2025-12\n- 在维：持续更新（当前 CANN 8.0）",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 状态定义表",
                "## 版本状态说明\n| 标签 | 定义 | 截止 |\n| 停止维护 | 不再提供补丁与安全更新 | 2025-12 |\n| 在维 | 持续更新 | — |",
            ),
            (
                "llms 临时补口径",
                "# llms.txt（过渡）\n- 停止维护：不再提供补丁与安全更新，截止 2025-12\n- 在维（CANN 8.0）：持续更新",
                "正文状态说明达标后，临时项可移除；勿把「热门」写入清单。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "语义标签的可见文字须写入首包 HTML；营销装饰标签标 <code>data-llm-exclude</code> 或管道剥离。静态抓取应能读到状态文案，且不会把「热门」当官方事实。",
        "frontend": [
            (
                "语义文案进首包",
                "版本 / 状态标签用真实文本节点输出（非纯 background / icon font）；静态抓取可读到「停止维护」等字面",
            ),
            (
                "装饰标 exclude",
                "「热门 / 新品 / 推荐」等营销标签加 <code>data-llm-exclude</code>，或在入库管道按 class / 角色剥离",
            ),
        ],
        "frontend_example": (
            "标签：混进库 → 语义留、装饰 exclude",
            "语义 / 装饰一并入库",
            '&lt;span class="tag"&gt;停止维护&lt;/span&gt;\n&lt;span class="tag"&gt;热门&lt;/span&gt;\n&lt;!-- 两类都被当事实抓取 --&gt;',
            "装饰标 exclude",
            '&lt;span class="tag"&gt;停止维护&lt;/span&gt;\n&lt;span class="tag tag--promo" data-llm-exclude&gt;热门&lt;/span&gt;\n&lt;!-- 语义入库 · 营销剥离 --&gt;',
            False,
            False,
            "「热门」与「停止维护」同级进库，易被当成同等官方结论。",
            "语义标签可抓；装饰标签 exclude，静态抓取不会把口号当事实。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可读", "静态抓取后能读到语义标签字面，且营销装饰标签未作为事实入库"),
            ("有依据", "对「停止维护」等状态问句能引用正文 / MD 定义与时间点，与仅复述色块失败判据互斥"),
            ("管道分流", "装饰标签 exclude 或剥离；语义标签与状态定义表可互证"),
        ],
    },
    "odialog": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "含关键说明的对话框",
                    "要做亲和",
                    "安装步骤、活动规则等唯一说明若在弹层：须写入首包 HTML，或在正文页写一份等价可引用文本；DOM 文本勿被 <code>aria-hidden</code> 删空。",
                ),
                (
                    "strip",
                    "纯确认框",
                    "不做亲和 · 入库剥离",
                    "「确定 / 取消 / 我知道了」等无知识的 noop 确认框不承载规格。入库管道宜标 <code>data-llm-exclude</code> 或过滤。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_no_example": True,
        "design": [
            (
                "视觉交互可维持",
                "对话框外观与开关交互按常规即可，无需为亲和重做视觉",
            ),
            (
                "稿面标注角色",
                "标注哪些弹层含关键说明（须正文双写或交首包文案），哪些是纯确认框（标 exclude）；勿假定「点开才看见的步骤不用交付」",
            ),
        ],
        "content": [
            (
                "统一命名",
                "弹层标题与正文 / MD 中的步骤名、规则名对齐（如一律「CANN 安装步骤」）",
            ),
            (
                "关键说明平行清单",
                "安装步骤 / 活动规则在文档 MD 或正文页平铺一份可引用文本；弹层不作唯一来源",
            ),
            (
                "过渡补位",
                "弹层尚未进首包时，用 llms / MD 临时补步骤；SSR 或正文达标后以页面为准。纯确认框不进清单",
            ),
        ],
        "content_example": (
            "安装步骤：只在弹层 → 正文也有一份",
            "步骤只在 dialog",
            "完整安装步骤只在「安装指引」弹层；\n正文 / 文档无等价说明；\n不点开 / 禁 JS 时读不到步骤。",
            "正文 duplicate",
            "## CANN 安装步骤\n1. 下载对应版本固件与驱动\n2. 校验依赖（GCC / GLIBC）\n3. 执行安装脚本 …",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 平铺步骤",
                "## CANN 安装步骤\n1. 下载对应版本固件与驱动\n2. 校验依赖（GCC / GLIBC）\n3. 执行安装脚本 …",
            ),
            (
                "llms 临时补步骤",
                "# llms.txt（过渡）\n## CANN 安装步骤\n1. 下载固件与驱动\n2. 校验依赖\n3. 执行安装脚本",
                "弹层 SSR 或正文双写达标后，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "含关键说明的 dialog 内容须写入首包 HTML（可默认视觉隐藏）；纯确认框标 exclude。静态抓取应能读到步骤 / 规则，且不会把「我知道了」当知识入库。",
        "frontend": [
            (
                "说明进首包",
                "承载关键说明的弹层正文在首包就存在，别等点击才由 JS 注入",
            ),
            (
                "勿 aria-hidden 删文本",
                "弹层文本保留在 DOM，抓取时勿被移除为空",
            ),
            (
                "纯确认框 exclude",
                "noop 确认框标 <code>data-llm-exclude</code>，避免操作文案进库",
            ),
        ],
        "frontend_example": (
            "对话框：点击才注入 → 首包可读",
            "点击才注入",
            '&lt;div class="o-dialog" hidden&gt;&lt;/div&gt;\n&lt;!-- 步骤点击后才 JS 注入 --&gt;',
            "首包含文本",
            '&lt;div class="o-dialog" hidden&gt;\n  &lt;h3&gt;CANN 安装步骤&lt;/h3&gt;\n  &lt;ol&gt;&lt;li&gt;下载固件与驱动&lt;/li&gt;…&lt;/ol&gt;\n&lt;/div&gt;\n&lt;!-- 首包可读，仅视觉隐藏 --&gt;',
            False,
            False,
            "步骤不在首包，静态抓取读不到安装说明。",
            "说明在首包；纯确认框另标 exclude。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可读", "静态抓取后，含说明的 dialog 文案仍可读，或正文 / MD 有等价步骤"),
            ("可证伪", "对「CANN 安装步骤写了什么」须能引用正文或首包文本，与点击才注入失败判据互斥"),
            ("管道分流", "纯确认框 exclude；关键说明可入库或由 MD 互证"),
        ],
    },
    "opopover": {
        "hide_sample_meta": True,
        "intro_card": {
            "plain": True,
            "title": "场景判断",
            "items": [
                (
                    "keep",
                    "含字段定义的气泡",
                    "要做亲和",
                    "重要字段 / 规格定义（如「CANN 版本」）若只在悬停气泡：须在正文写一份可引用定义，或 popover 内容写入首包可抓。",
                ),
                (
                    "strip",
                    "装饰性 tooltip",
                    "不做亲和 · 入库剥离",
                    "纯提示、装饰性 tooltip 不含唯一知识。入库可忽略或标 <code>data-llm-exclude</code>；关键看正文是否另有定义。",
                ),
            ],
        },
        "design_heading_suffix": " · 场景1",
        "content_heading_suffix": " · 场景1",
        "frontend_heading_suffix": " · 场景1",
        "design_example_side_by_side": True,
        "design": [
            (
                "关键定义留成可见旁注",
                "重要字段定义别只放悬停气泡，稿面预留可见旁注 / 正文说明位；气泡只作补充",
            ),
            (
                "稿面标注角色",
                "标注哪些气泡承载字段定义（须正文双写），哪些是纯装饰 tooltip（标 exclude）",
            ),
        ],
        "design_example": (
            "字段说明：只在悬停 → 正文旁注 + 气泡",
            "定义只在悬停气泡",
            '<div style="display:flex;align-items:center;gap:6px;">\n'
            '  <span>CANN 版本</span>\n'
            '  <span style="width:16px;height:16px;border-radius:50%;border:1px solid var(--line);display:inline-flex;align-items:center;justify-content:center;font-size:11px;color:var(--muted);">?</span>\n'
            '</div>',
            "正文旁注可见",
            '<div style="display:flex;align-items:center;gap:6px;">\n'
            '  <span>CANN 版本</span>\n'
            '</div>\n'
            '<p class="rf-caption" style="margin-top:8px;">CANN 版本：昇腾异构计算架构的版本号，决定可用算子与框架适配范围（当前 8.0）。</p>',
            True,
            True,
            "字段定义只在悬停「?」时出现；不悬停 / 禁 JS 时正文没有这份说明。",
            "定义写成可见旁注（正文一份）；气泡若保留，只作 hover 补充，不能当唯一来源。",
        ),
        "content": [
            (
                "统一命名",
                "字段名与正文 / 规格表 / 气泡文案对齐（如一律「CANN 版本」）",
            ),
            (
                "字段定义平行清单",
                "在文档 MD 或规格页维护「字段 → 官方定义」；气泡不作唯一来源",
            ),
            (
                "过渡补位",
                "正文尚未写清时，用 llms / MD 临时补字段口径；页面达标后以正文为准。装饰 tooltip 不进清单",
            ),
        ],
        "content_example": (
            "字段定义：只在气泡 → 正文旁注",
            "定义只在 popover",
            "「CANN 版本」定义只在悬停气泡；\n正文无等价说明；\nAgent 无法引用官方依据。",
            "正文写一份定义",
            "## 字段说明\n- CANN 版本：昇腾异构计算架构版本号，决定算子与框架适配范围（当前 8.0）",
            False,
            False,
        ),
        "content_example_after_sections": [
            (
                "MD 字段定义表",
                "## 字段说明\n| 字段 | 定义 |\n| CANN 版本 | 昇腾异构计算架构版本号，决定算子与框架适配范围（当前 8.0） |",
            ),
            (
                "llms 临时补口径",
                "# llms.txt（过渡）\n- CANN 版本：昇腾异构计算架构版本号（当前 8.0）",
                "正文旁注达标后，临时项可移除。",
            ),
        ],
        "content_example_before_prefix": "当前问题",
        "content_example_before_mark": True,
        "frontend_lead": "含字段定义的 popover 内容须写入首包 HTML（可视觉隐藏），或依赖正文旁注；装饰 tooltip 标 exclude。静态抓取应能读到定义，且不会把纯提示当规格。",
        "frontend": [
            (
                "定义进首包或旁注",
                "承载字段定义的气泡文本在首包就存在，别等 hover 才 JS 挂载；更优是正文旁注已可读",
            ),
            (
                "勿 aria-hidden 删文本",
                "气泡文本保留在 DOM，避免抓取为空",
            ),
            (
                "装饰 tooltip exclude",
                "纯装饰 tooltip 标 <code>data-llm-exclude</code>",
            ),
        ],
        "frontend_example": (
            "气泡：hover 才挂载 → 首包可读",
            "hover 才挂载",
            '&lt;span class="o-popover"&gt;&lt;/span&gt;\n&lt;!-- 定义 hover 时才 JS 注入 --&gt;',
            "首包含定义",
            '&lt;span class="o-popover" role="note"&gt;\n  CANN 版本：异构计算架构版本号（当前 8.0）\n&lt;/span&gt;\n&lt;!-- 首包可读，视觉上悬停展开 --&gt;',
            False,
            False,
            "定义不在首包，静态抓取读不到字段说明。",
            "定义在首包；装饰 tooltip 另标 exclude。",
        ),
        "frontend_example_before_prefix": "当前问题",
        "acceptance": [
            ("静态可读", "静态抓取后能读到字段定义（正文旁注或首包 popover），装饰 tooltip 未当事实入库"),
            ("可证伪", "对「CANN 版本是什么」须能引用正文 / MD 定义，与仅悬停才出现失败判据互斥"),
            ("管道分流", "装饰 tooltip exclude；字段定义可入库或由 MD 互证"),
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
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
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
      <a href="{phref}" class="active">亲和原则</a>
    <a href="problems-{slug}.html">实测问题</a>
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
        f'    <a href="{phref}" class="active">亲和原则</a>\n'
        f'    <a href="problems-{slug}.html">实测问题</a>'
    )
    patched, n = re.subn(
        r'\s*<a href="[^"]+"(?: class="active")?>亲和原则</a>\s*\n'
        r'\s*<a href="problems-[^"]+\.html"(?: class="active")?>实测问题</a>',
        '\n' + new_tabs,
        text,
        count=1,
    )
    if n == 0:
        patched, n = re.subn(
            r'\s*<a href="problems-[^"]+\.html"(?: class="active")?>实测问题</a>\s*\n'
            r'\s*<a href="[^"]+"(?: class="active")?>亲和原则</a>',
            '\n' + new_tabs,
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
        f'    <a href="{phref}">亲和原则</a>\n'
        f'    <a href="problems-{slug}.html" class="active">实测问题</a>'
    )
    patched, n = re.subn(
        r'\s*<a href="[^"]+"(?: class="active")?>亲和原则</a>\s*\n'
        r'\s*<a href="problems-[^"]+\.html"(?: class="active")?>实测问题</a>',
        '\n' + new_tabs,
        text,
        count=1,
    )
    if n == 0:
        patched, n = re.subn(
            r'\s*<a href="problems-[^"]+\.html"(?: class="active")?>实测问题</a>\s*\n'
            r'\s*<a href="[^"]+"(?: class="active")?>亲和原则</a>',
            '\n' + new_tabs,
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
            if slug in PRINCIPLES_OVERRIDES:
                probe = {
                    "title_short": {
                        "ocarousel": "轮播帧语义隔离",
                    }.get(slug, name),
                    "term": name.split()[-1] if name else slug,
                    "definition": "",
                    "sample_url": "https://www.hiascend.com/zh",
                    "sample_label": "社区首页",
                }
            else:
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

    problems_topbars = 0
    for _, slug, _ in all_components():
        ppath = DOCS / f"problems-{slug}.html"
        if ppath.exists() and patch_problems_topbar(ppath, slug):
            problems_topbars += 1

    copy_to_report_serve()

    print(f"Generated: {len(generated)}")
    for f in sorted(generated):
        print(f"  {f}")
    if skipped_body:
        print(f"Skipped body (preserved): {', '.join(skipped_body)}")
    print(f"Sidebars patched: {sidebars_patched}")
    print(f"Principles topbars patched: {topbars_patched}")
    print(f"Principles framework blocks removed: {framework_removed}")
    print(f"Problems topbars patched: {problems_topbars}")
    print(f"Total principles files: {len(list(DOCS.glob('principles-*.html')))}")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
