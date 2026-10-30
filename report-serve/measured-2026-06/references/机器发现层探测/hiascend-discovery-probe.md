---
title: 昇腾社区机器发现层探测
probe_date: 2026-06-07
html_module: problems-structure-llms.html
status: 已复现
---

# 昇腾社区机器发现层探测

> **关联页面**：[llms.txt 与机器入口](../../problems-structure-llms.html)  
> **探测日期**：2026-06-07  
> **方法**：静态 HTTP GET（`curl` / Python `urllib`），不执行 JS、不登录

## 结论摘要

| 探测项 | 结果 |
|--------|------|
| `/llms.txt` | HTTP **404** |
| `/robots.txt` | HTTP 200；含 `Disallow: /doc_center/` |
| `/sitemap/sitemapdoc1.xml` | 10,000 条 URL；`doc_center` **0** 条；`document/detail` **10,000** 条 |

---

## 1. llms.txt

```bash
curl -sI "https://www.hiascend.com/llms.txt" | head -5
```

**实测响应头（2026-06-07）**

```
HTTP/1.1 404 Page not found: /llms.txt
Date: Sun, 07 Jun 2026 12:37:03 GMT
Content-Type: application/json
Connection: keep-alive
Server: openresty
```

---

## 2. robots.txt

```bash
curl -s "https://www.hiascend.com/robots.txt"
```

**实测正文摘录**

```
User-agent: *
Allow: /
Disallow: /profile/
Disallow: /doc_center/

Sitemap: https://www.hiascend.com/sitemap.xml
Sitemap: https://www.hiascend.com/cn/sitemap-zh-CN.xml
Sitemap: https://www.hiascend.com/eng/sitemap-en-GB.xml
Sitemap: https://www.hiascend.com/sitemap/sitemapdata1.xml
Sitemap: https://www.hiascend.com/sitemap/sitemapdata2.xml
Sitemap: https://www.hiascend.com/sitemap/sitemapdoc1.xml
…（共 15 个 sitemapdoc 分片，至 sitemapdoc15.xml）
```

要点：`/doc_center/` 被全站禁止，合规爬虫不应索引源 HTML / PDF 目录。

---

## 3. sitemap 路径分布

仅统计 `sitemapdoc1.xml` 一个分片（共 15 个 doc 分片，每片上限 10,000 条）。

### curl + grep（快速抽样前 5 条）

```bash
curl -s "https://www.hiascend.com/sitemap/sitemapdoc1.xml" \
  | grep -o '<loc>[^<]*</loc>' | head -5
```

### Python（统计 doc_center vs document/detail）

```bash
python3 << 'PY'
import urllib.request, re
xml = urllib.request.urlopen(
    "https://www.hiascend.com/sitemap/sitemapdoc1.xml", timeout=30
).read().decode("utf-8", "replace")
locs = re.findall(r"<loc>([^<]+)</loc>", xml)
print("total", len(locs))
print("doc_center", sum(1 for u in locs if "doc_center" in u))
print("document/detail", sum(1 for u in locs if "document/detail" in u))
print("sample:")
for u in locs[:5]:
    print(" ", u)
PY
```

**实测输出（2026-06-07）**

```
total 10000
doc_center 0
document/detail 10000
sample:
  https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/devaids/aoe/aoeref_16_0009.html
  https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/maintenref/basicdataapi/atlasopapi_07_00542.html
  https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/maintenref/basicdataapi/atlasopapi_07_00198.html
  https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/maintenref/basicdataapi/atlasopapi_07_00196.html
  https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/maintenref/basicdataapi/atlasopapi_07_00604.html
```

首条即为 **910beta1**，与后续 **900** 社区版条目并列，sitemap 未标注 canonical 优先级。

---

## 4. 可选：遍历全部分片

```bash
python3 << 'PY'
import urllib.request, re
dc = dd = total = 0
for i in range(1, 16):
    url = f"https://www.hiascend.com/sitemap/sitemapdoc{i}.xml"
    try:
        xml = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        print(i, "SKIP", e)
        continue
    locs = re.findall(r"<loc>([^<]+)</loc>", xml)
    total += len(locs)
    dc += sum(1 for u in locs if "doc_center" in u)
    dd += sum(1 for u in locs if "document/detail" in u)
    print(f"sitemapdoc{i}.xml", len(locs))
print("ALL total", total, "doc_center", dc, "document/detail", dd)
PY
```

> 全量遍历耗时较长；论证页仅引用 `sitemapdoc1.xml` 分片即可说明「发现层只索引渲染页」。

---

## 关联数据

- 检索阶段 URL 列表：[claude-检索网页.md](../官方信源感知弱/claude-检索网页.md)、[deepseek-检索网页.md](../官方信源感知弱/deepseek-检索网页.md)、[千问-检索网页.md](../官方信源感知弱/千问-检索网页.md)
- 载体体积对比：[02-读取AscendC文档内容.md](../claude-conversations/02-读取AscendC文档内容.md)
