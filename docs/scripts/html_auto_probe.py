#!/usr/bin/env python3
"""批量抓取 HTML 并生成组件聚合用的自动楼层（供索引表同步）。"""
from __future__ import annotations

import html as htmlmod
import json
import re
import ssl
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = ROOT / "data/html_readability_auto.json"

UA = "Mozilla/5.0 (compatible; GEO-HtmlProbe/1.0)"
CTX = ssl.create_default_context()

CHROME_RE = re.compile(
    r"(华为计算微信公众号|昇腾AI开发者公众号|华为计算微博|华为计算今日头条|"
    r"关于昇腾|昇腾计算产业概述|新闻与活动|新闻资讯|昇腾活动|交流与资讯|昇腾论坛|技术干货|"
    r"支持与服务|开源社区|昇思社区|昇腾开放资源|关注我们|友情链接|华为官网|华为计算|鲲鹏社区|华为云|启智社区|华为开发者|"
    r"版权所有|保留一切权利|法律声明|隐私政策|Cookie协议|用户协议|联系我们|"
    r"我们使用cookie|继续浏览本站|查看详情|"
    r"Links Huawei Corporate Kunpeng|NVIDIA Home|Privacy Policy|Terms of Service)",
    re.I,
)

NOTE_RE = re.compile(r"^text=(\d+),h=(\d+),main=(True|False)$")


def fetch(url: str, timeout: int = 35) -> tuple[int | None, str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.geturl(), r.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, getattr(e, "geturl", lambda: url)(), body
    except Exception as e:
        return None, url, str(e).encode()


def score_html(body: bytes) -> tuple[str, str, str, dict]:
    raw = body.decode("utf-8", "ignore")
    main = None
    for pat in (
        r"(?is)<main\b[^>]*>(.*?)</main>",
        r"(?is)<article\b[^>]*>(.*?)</article>",
        r'(?is)<div[^>]*(?:class|id)=["\'][^"\']*(?:main|content|page)[^"\']*["\'][^>]*>(.*?)</div>',
    ):
        m = re.search(pat, raw)
        if m and len(m.group(1)) > 500:
            main = m.group(1)
            break
    chunk = main if main else raw
    cleaned = re.sub(r"(?is)<(script|style|noscript|header|footer|nav)[^>]*>.*?</\1>", " ", chunk)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = htmlmod.unescape(cleaned)
    cleaned = CHROME_RE.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    hcount = len(re.findall(r"(?i)<h[1-6]\b", chunk if main else raw))
    n = len(cleaned)
    has_state = "window.__INITIAL_STATE__" in raw or "__NUXT__" in raw or "__NUXT_DATA__" in raw
    empty_app = bool(re.search(r"<div[^>]+id=['\"]app['\"][^>]*>\s*</div>", raw))
    empty_tabs = 'class="o-tab-nav-list"></div>' in raw or "o-tab-nav-list\"></div>" in raw
    empty_vue = "<!--[--><!--]-->" in raw
    if n >= 1800 and hcount >= 2:
        label = "完整"
    elif n >= 600:
        label = "部分"
    else:
        label = "缺失"
    if has_state and n < 900 and not main:
        label = "缺失" if n < 500 else "部分"
    note = f"text={n},h={hcount},main={bool(main)}"
    signals = {
        "n": n,
        "h": hcount,
        "main": bool(main),
        "has_state": has_state,
        "empty_app": empty_app,
        "empty_tabs": empty_tabs,
        "empty_vue": empty_vue,
    }
    return label, note, cleaned[:120], signals


def floors_from_probe(label: str, note: str, signals: dict) -> list[dict]:
    n, h = signals["n"], signals["h"]
    floors: list[dict] = []
    idx = 1

    if label == "完整":
        floors.append(
            {
                "id": "static-body",
                "idx": idx,
                "kind": "in",
                "name": "整页静态正文",
                "badge": "自动探测",
                "desc": (
                    f"批量探测：可见正文 {n} 字、标题 {h} 个"
                    f"{'、有 main 容器' if signals['main'] else ''}。"
                    "达完整阈值（≥1800 字且 ≥2 标题）。"
                ),
            }
        )
        idx += 1
    elif label == "部分":
        floors.append(
            {
                "id": "static-body",
                "idx": idx,
                "kind": "in",
                "name": "基础静态正文",
                "badge": "自动探测",
                "desc": (
                    f"批量探测：可见正文 {n} 字、标题 {h} 个"
                    f"{'、有 main 容器' if signals['main'] else ''}。"
                    "有基础文案但未达完整阈值。"
                ),
            }
        )
        idx += 1
        floors.append(
            {
                "id": "threshold-gap",
                "idx": idx,
                "kind": "warn",
                "name": "正文未达完整",
                "badge": "阈值",
                "fixNeeded": True,
                "desc": "完整需 ≥1800 字且 ≥2 标题；或关键区块仍靠脚本注入（待组件细测补证）。",
            }
        )
        idx += 1
    else:
        if n > 0:
            floors.append(
                {
                    "id": "thin-body",
                    "idx": idx,
                    "kind": "in",
                    "name": "少量静态文案",
                    "badge": "自动探测",
                    "desc": f"批量探测：可见正文仅 {n} 字、标题 {h} 个。",
                }
            )
            idx += 1
        floors.append(
            {
                "id": "body-miss",
                "idx": idx,
                "kind": "warn",
                "name": "静态正文不足",
                "badge": "缺失",
                "fixNeeded": True,
                "desc": (
                    "批量探测：首包可见正文 <600 字或近乎空壳，"
                    "规格/列表/详情可能依赖脚本渲染。"
                ),
            }
        )
        idx += 1

    extras = []
    if signals["empty_app"]:
        extras.append("首包仅 #app 空壳")
    if signals["has_state"] and n < 900:
        extras.append("框架状态块(__NUXT__/INITIAL_STATE)")
    if signals["empty_tabs"]:
        extras.append("Tab 导航/面板为空")
    if signals["empty_vue"]:
        extras.append("Vue 空占位 <!--[--><!--]-->")

    for i, reason in enumerate(extras, start=0):
        floors.append(
            {
                "id": f"signal-{i}",
                "idx": idx,
                "kind": "warn",
                "name": reason,
                "badge": "CSR",
                "fixNeeded": True,
                "desc": f"批量探测信号：{reason}。",
            }
        )
        idx += 1

    return floors


def floors_from_measure(rec: dict) -> list[dict]:
    label = rec.get("html", "缺失")
    note = rec.get("html_note", "")
    m = NOTE_RE.match(note)
    if m:
        n, h, main = int(m.group(1)), int(m.group(2)), m.group(3) == "True"
    else:
        n, h, main = 0, 0, False
    signals = {
        "n": n,
        "h": h,
        "main": main,
        "has_state": False,
        "empty_app": n == 0,
        "empty_tabs": False,
        "empty_vue": False,
    }
    return floors_from_probe(label, note, signals)


def load_measure_index() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for fp in ROOT.glob("data/hiascend*.json"):
        data = json.loads(fp.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else [x for v in data.values() for x in v]
        for r in rows:
            if isinstance(r, dict) and r.get("url"):
                out[r["url"]] = r
    nv = json.loads((ROOT / "data/nv_affinity_measure.json").read_text(encoding="utf-8"))
    for r in nv:
        out[r["url"]] = r
    return out


def probe_one(url: str, name: str, measure: dict[str, dict]) -> dict:
    if url in measure and measure[url].get("html_note", "").startswith("text="):
        floors = floors_from_measure(measure[url])
        source = "measure-cache"
        note = measure[url]["html_note"]
        status = measure[url].get("html", "")
    else:
        st, final, body = fetch(url)
        if st is None or not isinstance(body, bytes) or st != 200:
            err = body.decode("utf-8", "ignore")[:80] if isinstance(body, bytes) else "fetch-fail"
            floors = [
                {
                    "id": "fetch-fail",
                    "idx": 1,
                    "kind": "warn",
                    "name": "抓取失败",
                    "badge": "错误",
                    "fixNeeded": True,
                    "desc": f"批量探测：HTTP {st} · {err}",
                }
            ]
            return {
                "pageName": name,
                "leftUrl": url,
                "floors": floors,
                "source": "fetch-error",
                "html_note": f"status={st}",
            }
        label, note, _sample, signals = score_html(body)
        floors = floors_from_probe(label, note, signals)
        source = "live-fetch"
        status = label

    return {
        "pageName": name,
        "leftUrl": url,
        "floors": floors,
        "source": source,
        "html_note": note,
        "html": status,
    }


def urls_from_index(html_path: Path) -> list[tuple[str, str]]:
    t = html_path.read_text(encoding="utf-8")
    out: list[tuple[str, str]] = []
    for m in re.finditer(r'<td class="path"><a href="([^"]+)"', t):
        url = m.group(1)
        chunk = t[m.end() : m.end() + 240]
        mn = re.search(r'<span class="mn-sub">([^<]+)</span>', chunk)
        nav = re.search(r'<div class="nav-src">([^<]+)</div>', chunk)
        name = (mn.group(1) if mn else nav.group(1) if nav else "").strip()
        if not name:
            name = urlsplit(url).path or url
        out.append((url, name))
    return out


SITE_TARGETS = {
    "ascend": ROOT / "docs/reachability.html",
    "nvidia": ROOT / "docs/nvidia-index.html",
    "mintlify": ROOT / "docs/mintlify-index.html",
}


def build_auto_index(*, live_fetch: bool = True, workers: int = 10) -> dict:
    measure = load_measure_index()
    result: dict[str, dict] = {}

    for site, html_path in SITE_TARGETS.items():
        entries: dict[str, dict] = {}
        rows = urls_from_index(html_path)
        print(f"[{site}] probing {len(rows)} urls…")

        def work(item: tuple[str, str]) -> tuple[str, dict]:
            url, name = item
            if live_fetch:
                st, _final, body = fetch(url)
                if st == 200 and isinstance(body, bytes):
                    label, note, _s, signals = score_html(body)
                    floors = floors_from_probe(label, note, signals)
                    return url, {
                        "pageName": name,
                        "leftUrl": url,
                        "floors": floors,
                        "source": "live-fetch",
                        "html_note": note,
                        "html": label,
                    }
            return url, probe_one(url, name, measure)

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(work, row) for row in rows]
            for i, fut in enumerate(as_completed(futs), 1):
                url, rec = fut.result()
                entries[url] = rec
                if i % 20 == 0 or i == len(rows):
                    print(f"  [{site}] {i}/{len(rows)}")
        result[site] = entries

    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT_PATH)
    return result


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-only", action="store_true", help="只用既有 measure 缓存，不重新抓取")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()
    build_auto_index(live_fetch=not args.cache_only, workers=args.workers)
