#!/usr/bin/env python3
"""Measure remaining HiAscend domains (知识/内容运营/生态/社区运营/公司事务)."""
import json, re, urllib.request, urllib.error, ssl, html as htmlmod
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit
from collections import Counter

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (compatible; GEO-AffinityAudit/1.0)"
ROOT = Path("/Users/melody/Desktop/GEO")
HOST = "www.hiascend.com"

DOMAINS = ["知识", "内容运营", "生态", "社区运营", "公司事务"]

CHROME_RE = re.compile(
    r"(华为计算微信公众号|昇腾AI开发者公众号|华为计算微博|华为计算今日头条|"
    r"关于昇腾|昇腾计算产业概述|新闻与活动|新闻资讯|昇腾活动|交流与资讯|昇腾论坛|技术干货|"
    r"支持与服务|开源社区|昇思社区|昇腾开放资源|关注我们|友情链接|华为官网|华为计算|鲲鹏社区|华为云|启智社区|华为开发者|"
    r"版权所有|保留一切权利|法律声明|隐私政策|Cookie协议|用户协议|联系我们|"
    r"我们使用cookie|继续浏览本站|查看详情|"
    r"Links Huawei Corporate Kunpeng)",
    re.I,
)


def fetch(url, headers=None, timeout=30):
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.geturl(), r.headers.get_content_type(), r.read()
    except urllib.error.HTTPError as e:
        body = e.read() if e.fp else b""
        return e.code, getattr(e, "geturl", lambda: url)(), (e.headers.get_content_type() if e.headers else ""), body
    except Exception as e:
        return None, url, "", str(e).encode()


def load_urls():
    data = json.loads((ROOT / "data/hiascend_nav_grouped.json").read_text())
    # Dedup order matching status.html (keep first occurrence per domain)
    out = {}
    for dom in DOMAINS:
        seen = set()
        items = []
        for u, name, src in data["buckets"][dom]:
            if u in seen:
                continue
            seen.add(u)
            items.append((u, name, src))
        out[dom] = items
    return out


def load_sitemaps(include_docs=True):
    robots = fetch("https://www.hiascend.com/robots.txt")[3].decode("utf-8", "ignore")
    smaps = re.findall(r"(?i)^Sitemap:\s*(\S+)", robots, re.M)
    for s in [
        "https://www.hiascend.com/sitemap.xml",
        "https://www.hiascend.com/cn/sitemap-zh-CN.xml",
        "https://www.hiascend.com/sitemap/sitemapdata1.xml",
        "https://www.hiascend.com/sitemap/sitemapdata2.xml",
    ]:
        if s not in smaps:
            smaps.append(s)
    focus = smaps if include_docs else [s for s in smaps if "sitemapdoc" not in s]
    print(f"sitemaps focus: {len(focus)}")
    sitemap_urls = set()
    for sm in focus:
        st, _, _, body = fetch(sm, timeout=90)
        if st != 200 or not body:
            print("fail sitemap", sm, st)
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body.decode("utf-8", "ignore"))
        print(sm, "locs", len(locs))
        for loc in locs:
            sitemap_urls.add(loc)
            sitemap_urls.add(loc.rstrip("/"))
    print("total sitemap locs", len(sitemap_urls))
    return sitemap_urls


def check_llms():
    st, _, _, body = fetch("https://www.hiascend.com/llms.txt")
    if st == 200 and body and b"<html" not in body[:200].lower():
        text = body.decode("utf-8", "ignore")
        return True, text
    return False, ""


def in_sitemap(url, sitemap_urls):
    sp = urlsplit(url)
    if sp.netloc and sp.netloc != HOST and not sp.netloc.endswith(".hiascend.com"):
        return "站外"
    base = f"{sp.scheme}://{sp.netloc}{sp.path}".rstrip("/")
    candidates = {url, url.rstrip("/"), base, base + "/"}
    if sp.query:
        candidates.add(f"{base}?{sp.query}")
    for v in candidates:
        if v in sitemap_urls or v.rstrip("/") in sitemap_urls:
            return "有"
    # path-only match on same host
    target = (sp.netloc, sp.path.rstrip("/"))
    for s in sitemap_urls:
        ssp = urlsplit(s)
        if (ssp.netloc, ssp.path.rstrip("/")) == target:
            return "有"
    return "无"


def score_html(body: bytes):
    text = body.decode("utf-8", "ignore")
    main = None
    for pat in [
        r"(?is)<main\b[^>]*>(.*?)</main>",
        r"(?is)<article\b[^>]*>(.*?)</article>",
        r'(?is)<div[^>]*(?:class|id)=["\'][^"\']*(?:main|content|page)[^"\']*["\'][^>]*>(.*?)</div>',
    ]:
        m = re.search(pat, text)
        if m and len(m.group(1)) > 500:
            main = m.group(1)
            break
    chunk = main if main else text
    cleaned = re.sub(r"(?is)<(script|style|noscript|header|footer|nav)[^>]*>.*?</\1>", " ", chunk)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = htmlmod.unescape(cleaned)
    cleaned = CHROME_RE.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    hcount = len(re.findall(r"(?i)<h[1-6]\b", chunk if main else text))
    n = len(cleaned)
    has_state = "window.__INITIAL_STATE__" in text or "__NUXT__" in text
    if n >= 1800 and hcount >= 2:
        label = "完整"
    elif n >= 600:
        label = "部分"
    else:
        label = "缺失"
    if has_state and n < 900 and not main:
        label = "缺失" if n < 500 else "部分"
    return label, f"text={n},h={hcount},main={bool(main)}", cleaned[:120]


def check_md(url):
    sp = urlsplit(url)
    if sp.netloc and sp.netloc != HOST:
        return "无", None
    path = sp.path
    if path.endswith("/"):
        mdpath = path.rstrip("/") + ".md"
    elif path.endswith(".html"):
        mdpath = path[:-5] + ".md"
    else:
        mdpath = path + ".md"
    mdurl = f"{sp.scheme}://{sp.netloc}{mdpath}"
    st, _, ctype, body = fetch(mdurl, headers={"Accept": "text/markdown, text/plain, */*"})
    if st == 200 and body:
        low = body[:200].lower()
        if b"<html" not in low and b"<!doctype" not in low:
            if b"#" in body[:500] or "markdown" in (ctype or "") or body[:1] in (b"#", b"-", b"*") or len(body) > 200:
                return "有", mdurl
    st2, _, _, body2 = fetch(url, headers={"Accept": "text/markdown"})
    if st2 == 200 and body2 and b"<html" not in body2[:200].lower() and (body2.startswith(b"#") or b"\n# " in body2[:1000]):
        return "有", url
    return "无", None


def check_one(item, sitemap_urls, llms_ok, llms_text):
    url, name, src = item
    sp = urlsplit(url)
    external = bool(sp.netloc and sp.netloc != HOST and not sp.netloc.endswith(".hiascend.com"))
    st, final, ctype, body = fetch(url)
    if st is None:
        return {
            "url": url, "name": name, "src": src, "status": None, "external": external,
            "html": "缺失", "html_note": body.decode("utf-8", "ignore")[:80],
            "md": "无", "md_url": None, "sitemap": "站外" if external else "无", "llms": "无", "sample": "",
        }
    if isinstance(body, bytes) and st == 200:
        html_l, note, sample = score_html(body)
    else:
        html_l, note, sample = "缺失", f"status={st}", ""
    md, mdurl = ("无", None) if external else check_md(url)
    sm = in_sitemap(url, sitemap_urls)
    # llms: only mark 有 if URL/path appears in llms.txt when it exists
    if not llms_ok or external:
        llms = "无"
    else:
        path = sp.path or "/"
        llms = "有" if (url in llms_text or path in llms_text) else "无"
    return {
        "url": url, "name": name, "src": src, "status": st, "final_url": final, "external": external,
        "html": html_l, "html_note": note, "md": md, "md_url": mdurl, "sitemap": sm, "llms": llms, "sample": sample,
    }


def main():
    buckets = load_urls()
    all_items = []
    for dom in DOMAINS:
        for it in buckets[dom]:
            all_items.append((dom, it))
    print("urls to measure", len(all_items))

    sitemap_urls = load_sitemaps(include_docs=True)
    llms_ok, llms_text = check_llms()
    print("llms.txt", llms_ok, "len", len(llms_text))

    results_by_dom = {d: [] for d in DOMAINS}

    def run(pair):
        dom, it = pair
        r = check_one(it, sitemap_urls, llms_ok, llms_text)
        r["domain"] = dom
        return r

    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(run, p) for p in all_items]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            results_by_dom[r["domain"]].append(r)
            print(i, r["domain"], r["html"], r["md"], r["sitemap"], r["name"][:18], r["url"][:70])

    # restore order
    out = {}
    for dom in DOMAINS:
        order = {u: i for i, (u, _, _) in enumerate(buckets[dom])}
        rows = results_by_dom[dom]
        rows.sort(key=lambda r: order[r["url"]])
        out[dom] = rows
        print(dom, Counter(r["html"] for r in rows), "sm", Counter(r["sitemap"] for r in rows), "md", Counter(r["md"] for r in rows))

    path = ROOT / "data/hiascend_remaining_measure.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
