#!/usr/bin/env python3
"""生成友商「找的准（版本·元数据）」页，并挂到分析层面侧栏。"""
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
SCHEMA_PATH = ROOT / "data/html_schema_probe.json"
PRECISION_PATH = ROOT / "data/html_precision_probe.json"

UA = "Mozilla/5.0 (compatible; GEO-PrecisionProbe/1.0)"
CTX = ssl.create_default_context()

VERSION_RE = re.compile(
    r"(?i)(?:softwareVersion|version)\s*[\"':=]\s*[\"']?v?\d+\.\d+(?:\.\d+)?"
    r"|v(?:ersion)?\s*[:：]?\s*\d+\.\d+(?:\.\d+)?"
    r"|SemVer|\b\d+\.\d+\.\d+\b"
)
VISIBLE_VERSION_HINT = re.compile(
    r"(?i)(?:当前版本|软件版本|文档版本|Version|v\d+\.\d+|Release\s+\d)"
)
DEPRECATION_RE = re.compile(
    r"(?i)deprecated|deprecation|end[\s-]?of[\s-]?(?:life|support)|EOS|"
    r"sunset|obsolete|已弃用|停止维护|已下线|失效|不再维护"
)
LDJSON_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)

THICK_TYPES = {
    "TechArticle",
    "FAQPage",
    "QAPage",
    "SoftwareApplication",
    "Product",
    "BlogPosting",
    "Article",
    "HowTo",
    "Course",
}


def norm_url(url: str) -> str:
    p = urlsplit(url.strip())
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), path, "", ""))


def fetch(url: str, timeout: int = 18) -> tuple[int | None, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except Exception as e:
        return None, str(e).encode()


def load_schema() -> dict[str, dict]:
    if not SCHEMA_PATH.exists():
        return {}
    data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for site in (data.get("sites") or {}).values():
        for row in site.get("rows") or []:
            out[norm_url(row["url"])] = row
    return out


def schema_grade(rec: dict | None) -> tuple[str, str]:
    if not rec or not rec.get("has_schema"):
        return "无", "首包未见 Schema.org JSON-LD / microdata"
    types = rec.get("types") or []
    tset = set(types)
    methods = "/".join(rec.get("methods") or ["json-ld"])
    tip_types = "、".join(types[:8]) if types else "（未解析类型）"
    if tset & THICK_TYPES or "softwareVersion" in tip_types:
        return "厚", f"Schema（{methods}）含业务类型：{tip_types}"
    if tset <= {"ImageObject"}:
        return "薄", f"Schema（{methods}）仅 ImageObject 等装饰类型：{tip_types}"
    # WebPage/Organization/WebSite/Breadcrumb — 有但偏站点壳
    return "薄", f"Schema（{methods}）以站点壳类型为主：{tip_types}"


def detect_precision(raw: str) -> dict:
    head = raw[:120000]
    # strip scripts/styles for visible-ish scan (keep ld+json separately)
    visible = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", head)
    visible = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", visible)
    visible = re.sub(r"(?is)<[^>]+>", " ", visible)
    visible = re.sub(r"\s+", " ", visible)

    has_ld_version = bool(
        any("softwareVersion" in m.group(1) or "datePublished" in m.group(1) for m in LDJSON_RE.finditer(head))
    )
    has_visible_version = bool(VISIBLE_VERSION_HINT.search(visible[:8000])) or bool(
        VERSION_RE.search(head[:20000])
    )
    # avoid counting bare year-looking numbers as version: require keyword or vX.Y
    version_ok = has_ld_version or has_visible_version
    version_note = []
    if has_ld_version:
        version_note.append("JSON-LD 含 softwareVersion/datePublished")
    if has_visible_version:
        version_note.append("页头附近可见版本措辞")
    if not version_note:
        version_note.append("未见稳定版本号外显")

    dep = bool(DEPRECATION_RE.search(head))
    dep_note = "检出弃用/EOS 相关措辞" if dep else "未见弃用/EOS 显性标记（知识页多数为现行文档，可为空）"

    return {
        "version": version_ok,
        "version_note": "；".join(version_note),
        "deprecation_signal": dep,
        "deprecation_note": dep_note,
    }


def knowledge_rows(index_html: Path) -> list[dict]:
    t = index_html.read_text(encoding="utf-8")
    m = re.search(
        r'<h2 class="card-title">知识</h2>(.*?)(?=<h2 class="card-title">|\Z)',
        t,
        re.S,
    )
    if not m:
        return []
    chunk = m.group(1)
    rows = []
    # split by path cells
    for pm in re.finditer(
        r'<td class="path"><a href="([^"]+)"[^>]*>(.*?)</a>(.*?)</td>',
        chunk,
        re.S,
    ):
        url = pm.group(1)
        label = re.sub(r"<[^>]+>", "", pm.group(2)).strip()
        extra = pm.group(3)
        sub = re.search(r'class="mn-sub">([^<]+)', extra)
        if sub:
            label = sub.group(1).strip()
        if not label or label.startswith("/"):
            label = urlsplit(url).path or url
        rows.append({"url": url, "label": label})
    return rows


def probe_urls(urls: list[str], *, workers: int = 12) -> dict[str, dict]:
    out: dict[str, dict] = {}

    def one(u: str) -> tuple[str, dict]:
        st, body = fetch(u)
        if st != 200 or not isinstance(body, bytes):
            return norm_url(u), {
                "url": u,
                "ok": False,
                "status": st,
                "version": False,
                "version_note": f"抓取失败 status={st}",
                "deprecation_signal": False,
                "deprecation_note": "未测",
            }
        raw = body.decode("utf-8", "ignore")
        det = detect_precision(raw)
        return norm_url(u), {"url": u, "ok": True, "status": st, **det}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, u) for u in urls]
        for fut in as_completed(futs):
            k, v = fut.result()
            out[k] = v
    return out


def tag_yes(text: str, tip: str) -> str:
    tip_e = escape(tip, quote=True).replace("\n", "&#10;")
    return (
        f'<span class="tag tag-yes why-tip" data-tip="{tip_e}" title="{tip_e}">{text}</span>'
    )


def tag_no(text: str, tip: str) -> str:
    tip_e = escape(tip, quote=True).replace("\n", "&#10;")
    return (
        f'<span class="tag tag-no why-tip" data-tip="{tip_e}" title="{tip_e}">{text}</span>'
    )


def tag_warn(text: str, tip: str) -> str:
    tip_e = escape(tip, quote=True).replace("\n", "&#10;")
    return (
        f'<span class="tag tag-warn why-tip" data-tip="{tip_e}" title="{tip_e}">{text}</span>'
    )


def version_cell(rec: dict | None) -> str:
    if not rec or not rec.get("ok"):
        return tag_no("未测", (rec or {}).get("version_note", "抓取失败"))
    if rec.get("version"):
        return tag_yes("有", rec.get("version_note", "可见版本"))
    return tag_no("无", rec.get("version_note", "未见版本外显"))


def dep_cell(rec: dict | None) -> str:
    if not rec or not rec.get("ok"):
        return tag_no("未测", "抓取失败")
    if rec.get("deprecation_signal"):
        return tag_warn("有信号", rec.get("deprecation_note", "检出弃用措辞"))
    return tag_no("无", rec.get("deprecation_note", "未见弃用标记"))


def schema_cell(grade: str, tip: str) -> str:
    if grade == "厚":
        return tag_yes("厚", tip)
    if grade == "薄":
        return tag_warn("薄", tip)
    return tag_no("无", tip)


def peer_nav(site: str, active: str) -> str:
    if site == "mintlify":
        links = {
            "overview": "mintlify.html",
            "index": "mintlify-index.html",
            "precision": "mintlify-precision.html",
            "html": "citability-html-mintlify.html",
            "md": "citability-mintlify.html",
        }
    else:
        links = {
            "overview": "nvidia.html",
            "index": "nvidia-index.html",
            "precision": "nvidia-precision.html",
            "html": "citability-html-nvidia.html",
            "md": "citability-nvidia.html",
        }

    def item(key: str, label: str) -> str:
        cls = ' class="active"' if active == key else ""
        return f'        <li><a href="{links[key]}"{cls}>{label}</a></li>'

    return (
        '      <div class="peer-group-label">分析层面</div>\n'
        "      <ul>\n"
        + "\n".join(
            [
                item("overview", "分析概览"),
                item("index", "找的到（收录索引）"),
                item("precision", "找的准（版本·元数据）"),
                item("html", "读的懂（html 可读）"),
                item("md", "读的顺（双轨交付）"),
            ]
        )
        + "\n      </ul>"
    )


def extract_shell(index_path: Path) -> tuple[str, str]:
    """Return (head_through_style_and_topbar_open_wrapper, closing_footer_part)."""
    t = index_path.read_text(encoding="utf-8")
    # take from start through peer-main wrap header area — we'll rebuild body
    # Use CSS from index: everything before <div class="peer-main">
    i = t.find('<div class="peer-main">')
    if i < 0:
        raise SystemExit(f"no peer-main in {index_path}")
    head = t[:i]
    # ensure why-tip / tag styles exist (already in index)
    return head, "</div><!-- /.peer-main -->\n</div><!-- /.page-wrapper -->\n</body>\n</html>\n"


PRECISION_CARD_CSS = """
  .precision-cards {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin: 0 0 8px;
    width: 100%;
  }
  .precision-card {
    display: flex;
    flex-direction: row;
    align-items: stretch;
    gap: 0;
    width: 100%;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
  }
  .precision-card .pc-head {
    flex: 0 0 168px;
    padding: 20px 18px;
    border-right: 1px solid var(--line);
    background: var(--panel2);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
  }
  .precision-card .pc-num {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .08em;
    color: var(--accent);
  }
  .precision-card h3 {
    margin: 0;
    font-size: 18px;
    line-height: 28px;
    font-weight: 650;
    letter-spacing: -0.01em;
  }
  .precision-card .pc-body {
    flex: 1 1 auto;
    min-width: 0;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0;
  }
  .precision-card .pc-block {
    margin: 0;
    padding: 18px 18px;
    border-right: 1px solid var(--line);
  }
  .precision-card .pc-block:last-child { border-right: none; }
  .precision-card .pc-label {
    display: block;
    font-size: 12px;
    font-weight: 650;
    color: var(--muted);
    margin: 0 0 6px;
    letter-spacing: .02em;
  }
  .precision-card p {
    margin: 0;
    font-size: var(--body-size);
    line-height: var(--body-lh);
    color: var(--text);
  }
  @media (max-width: 900px) {
    .precision-card {
      flex-direction: column;
    }
    .precision-card .pc-head {
      flex-basis: auto;
      border-right: none;
      border-bottom: 1px solid var(--line);
    }
    .precision-card .pc-body {
      grid-template-columns: 1fr;
    }
    .precision-card .pc-block {
      border-right: none;
      border-bottom: 1px solid var(--line);
    }
    .precision-card .pc-block:last-child { border-bottom: none; }
  }
"""

PRECISION_CARDS = {
    "mintlify": [
        {
            "num": "01",
            "title": "版本外显",
            "when": "多版本并存时：API / SDK / 组件文档、changelog、升级指南。模型要回答「现在该跟哪一版」，页头或近标题处必须有人可读的版本信号（SemVer、世代名、文档版次），不能只埋在路径或 changelog 长文里。",
            "peer": "Mintlify 知识页多靠 URL 与 changelog 叙事；页头缺少统一版本徽章。changelog / Learn 偶见版本措辞，日常 docs 叶子页偏弱。",
            "do": "知识叶页：页头或面包屑给出现行版本；多版本并存时标明「现行 / 归档」；版本变更写进可抓文本节点。",
        },
        {
            "num": "02",
            "title": "失效显化",
            "when": "旧页仍可能被召回时：接口废弃、功能迁移、教程过期。若页还在 Sitemap / 搜索结果里，却没有废弃顶条或替代链接，模型容易把过期步骤当现行事实。",
            "peer": "现行 Mintlify docs 少见 deprecated 页顶条；对本样本不是主战场，但社区有历史文档时仍要按此闸门验收。",
            "do": "废弃页：首包可见废弃标记 + 指向替代页；勿只删导航或只改颜色。仍被索引的旧 URL，失效信号优先于「默默下线」。",
        },
        {
            "num": "03",
            "title": "Schema",
            "when": "需要机器可读元数据消歧时：文档类型、softwareVersion、dateModified、作者/组织。它帮检索排序与过滤，不能单独证明「找的准」。",
            "peer": "Mintlify 文档页普遍有 WebPage / Breadcrumb 等壳层 Schema（薄）；TechArticle、softwareVersion 等业务厚度仍少。有 Schema ≠ 找的准。",
            "do": "壳层（WebSite / WebPage）只算起步；知识叶优先补业务类型与版本字段。厚度看字段，不看「有没有 JSON-LD」打勾。",
        },
    ],
    "nvidia": [
        {
            "num": "01",
            "title": "版本外显",
            "when": "产品世代与文档版次并行时：CUDA / 驱动 / 硬件世代、docs 多版本、SDK 发布说明。召回后要能一眼判断「是不是这代、是不是这版」。",
            "peer": "NVIDIA 产品线页偶见世代/版本措辞；文档级 SemVer 外显不统一，常靠路径或正文散落出现，缺页头统一徽章。",
            "do": "规格与文档叶：页头给出可读版本/世代；多版本文档标明现行；与「找的到」互补——找得到还要找得准版本。",
        },
        {
            "num": "02",
            "title": "失效显化",
            "when": "生命周期结束或接口弃用时：EOS / EOL、deprecated API、迁移公告。旧规格仍可被索引命中时，必须阻止当现行引用。",
            "peer": "部分规格/开发者页能检出弃用相关措辞，但并非处处有页顶废弃条；信号需结合具体规格页，不能假设全站统一。",
            "do": "弃用与 EOS 页：首包顶条 + 替代/迁移入口；归档知识保留 URL 时，失效标记比静默删除更利于消歧。",
        },
        {
            "num": "03",
            "title": "Schema",
            "when": "大站分面多、同名实体多时：用结构化类型（Product、TechArticle、FAQ）和版本/日期字段帮机器过滤，而不是只堆 ImageObject / Organization 壳。",
            "peer": "覆盖面相对大，但多数偏薄（站点壳、ImageObject）；含 Product / FAQ 等业务类型才算厚。找的准看厚度与版本字段，不看有无打勾。",
            "do": "优先给知识/产品叶补业务 Schema 与版本相关属性；营销壳页有薄 Schema 不必当深度亲和证据。",
        },
    ],
}


def precision_cards_html(site: str) -> str:
    parts = [
        '  <h2 class="block-title" id="precision">三个方面</h2>',
        '  <div class="precision-cards">',
    ]
    for c in PRECISION_CARDS[site]:
        parts.append(
            f"""    <article class="precision-card">
      <div class="pc-head">
        <div class="pc-num">{c['num']}</div>
        <h3>{c['title']}</h3>
      </div>
      <div class="pc-body">
        <div class="pc-block">
          <span class="pc-label">何时需要</span>
          <p>{c['when']}</p>
        </div>
        <div class="pc-block">
          <span class="pc-label">友商观察</span>
          <p>{c['peer']}</p>
        </div>
        <div class="pc-block">
          <span class="pc-label">怎么做</span>
          <p>{c['do']}</p>
        </div>
      </div>
    </article>"""
        )
    parts.append("  </div>")
    return chr(10).join(parts)


def build_page(
    *,
    site: str,
    brand: str,
    index_path: Path,
    out_path: Path,
) -> None:
    head, _ = extract_shell(index_path)
    head = re.sub(
        r"<title>.*?</title>",
        f"<title>{brand} · 找的准 · 昇腾社区 AI 亲和原则</title>",
        head,
        count=1,
        flags=re.S,
    )
    if ".precision-cards" not in head:
        head = head.replace("</style>", PRECISION_CARD_CSS + "\n</style>", 1)
    head = re.sub(
        r'<div class="peer-group-label">分析层面</div>\s*<ul>.*?</ul>',
        peer_nav(site, "precision"),
        head,
        count=1,
        flags=re.S,
    )
    # 对标友商同层互跳，避免切友商掉回「找的到」
    mintlify_cls = ' class="active"' if site == "mintlify" else ""
    nvidia_cls = ' class="active"' if site == "nvidia" else ""
    head = re.sub(
        r'<div class="peer-group-label">对标友商</div>\s*<ul>.*?</ul>',
        (
            '      <div class="peer-group-label">对标友商</div>\n'
            "      <ul>\n"
            f'        <li><a href="mintlify-precision.html"{mintlify_cls}>Mintlify</a></li>\n'
            f'        <li><a href="nvidia-precision.html"{nvidia_cls}>NVIDIA</a></li>\n'
            "      </ul>"
        ),
        head,
        count=1,
        flags=re.S,
    )
    if site == "mintlify":
        head = re.sub(
            r'(<nav class="site-nav"[^>]*>[\s\S]*?<a href="mintlify\.html")([^>]*>友商对照</a>)',
            r'\1 class="active"\2',
            head,
            count=1,
        )
        head = head.replace(
            'href="mintlify-index.html" class="active">找的到',
            'href="mintlify-index.html">找的到',
        )
    else:
        head = re.sub(
            r'(<nav class="site-nav"[^>]*>[\s\S]*?<a href="(?:mintlify|nvidia)\.html")([^>]*>友商对照</a>)',
            r'\1 class="active"\2',
            head,
            count=1,
        )
        head = head.replace(
            'href="nvidia-index.html" class="active">找的到',
            'href="nvidia-index.html">找的到',
        )

    body = f"""<div class="peer-main">
<div class="wrap">
  <header>
    <h1>{brand} · 找的准（版本·元数据）</h1>
    <p class="sub" style="color:var(--muted);font-size: var(--body-size);margin:0 0 24px;line-height: var(--body-lh);">
      召回时能否选对版本与时效。拆成三件事看：版本外显、失效显化、Schema——各自有适用场景；Schema 是手段之一，不是「找的准」的全部。
    </p>
  </header>

{precision_cards_html(site)}

  <footer>昇腾社区 AI 亲和原则研究 · 找的准</footer>
</div>

</div><!-- /.peer-main -->
</div><!-- /.page-wrapper -->
</body>
</html>
"""
    out_path.write_text(head + body, encoding="utf-8")
    report = ROOT / "report-serve" / out_path.name
    if report.parent.exists():
        shutil.copy2(out_path, report)


def patch_all_navs() -> int:
    """Insert 找的准 link after 找的到 in peer sidebars."""
    files = list((ROOT / "docs").glob("*.html")) + list((ROOT / "report-serve").glob("*.html"))
    n = 0
    for path in files:
        t = path.read_text(encoding="utf-8")
        if "分析层面" not in t or "找的到（收录索引）" not in t:
            continue
        if "找的准（版本·元数据）" in t:
            continue
        # mintlify family
        t2, c1 = re.subn(
            r'(<li><a href="mintlify-index\.html"[^>]*>找的到（收录索引）</a></li>)',
            r'\1\n        <li><a href="mintlify-precision.html">找的准（版本·元数据）</a></li>',
            t,
            count=1,
        )
        # nvidia family
        t2, c2 = re.subn(
            r'(<li><a href="nvidia-index\.html"[^>]*>找的到（收录索引）</a></li>)',
            r'\1\n        <li><a href="nvidia-precision.html">找的准（版本·元数据）</a></li>',
            t2,
            count=1,
        )
        if c1 + c2:
            path.write_text(t2, encoding="utf-8")
            n += 1
    return n


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-probe", action="store_true", help="仅重建页面，不重跑探测")
    ap.add_argument("--workers", type=int, default=14)
    args = ap.parse_args()

    schema_by = load_schema()
    targets = [
        ("mintlify", "Mintlify", ROOT / "docs/mintlify-index.html", ROOT / "docs/mintlify-precision.html"),
        ("nvidia", "NVIDIA", ROOT / "docs/nvidia-index.html", ROOT / "docs/nvidia-precision.html"),
    ]

    # 探测仍可更新 data/html_precision_probe.json；页面正文已改为三卡说明，不再嵌表
    if not args.skip_probe:
        all_precision: dict = {"sites": {}}
        if PRECISION_PATH.exists():
            all_precision = json.loads(PRECISION_PATH.read_text(encoding="utf-8"))
        for site, brand, index_path, _out in targets:
            rows = knowledge_rows(index_path)
            urls = [r["url"] for r in rows]
            print(f"{site}: probing knowledge urls {len(urls)}", flush=True)
            prec_map = probe_urls(urls, workers=args.workers)
            all_precision.setdefault("sites", {})[site] = {
                "count": len(prec_map),
                "rows": list(prec_map.values()),
            }
            # attach schema grade snapshot
            for row in all_precision["sites"][site]["rows"]:
                g, tip = schema_grade(schema_by.get(norm_url(row["url"])))
                row["schema_grade"] = g
                row["schema_tip"] = tip
        PRECISION_PATH.write_text(
            json.dumps(all_precision, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    for site, brand, index_path, out_path in targets:
        build_page(site=site, brand=brand, index_path=index_path, out_path=out_path)
        print(f"wrote {out_path.name}", flush=True)

    n = patch_all_navs()
    print(f"nav patched files: {n}", flush=True)


if __name__ == "__main__":
    main()
