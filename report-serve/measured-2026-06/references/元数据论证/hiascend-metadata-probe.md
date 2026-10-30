---
title: 昇腾文档页元数据探测
probe_date: 2026-06-07
html_module: problems-structure-metadata.html
status: 已复现
---

# 昇腾文档页元数据探测

> **关联页面**：[元数据字段规范](../../problems-structure-metadata.html)  
> **探测日期**：2026-06-07  
> **方法**：静态 HTTP GET + 正则解析 `<title>` / `<meta>` / JSON-LD（不执行 JS）

## 结论摘要

| 观测 | 结果 |
|------|------|
| 同主题页跨版本 | `atlas_ascendc_map_10_0002` 在 900 / 850 / 910beta 下 `<title>` 版本串不同，正文主题相同 |
| 结构化 schema | 页面 **0** 条 `application/ld+json` |
| breadcrumb | 仅压缩进 `<title>` / `og:title` 字符串，**无**独立机器字段 |
| `doc_id` | 出现在 URL 路径，未以 Front Matter 输出到机器层 |

---

## 1. 同 doc_id · 跨版本 title 对照

```bash
python3 << 'PY'
import urllib.request, re
pairs = [
 ("900社区", "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/programug/Ascendcopdevg/atlas_ascendc_map_10_0002.html"),
 ("850商用", "https://www.hiascend.com/document/detail/zh/canncommercial/850/opdevg/Ascendcopdevg/atlas_ascendc_map_10_0002.html"),
 ("910beta", "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/programug/Ascendcopdevg/docs/guide/什么是Ascend-C.md"),
]
for label, url in pairs:
    html = urllib.request.urlopen(url, timeout=20).read().decode()
    t = re.search(r"<title>([^<]+)</title>", html)
    print(label, "→", t.group(1) if t else "N/A")
PY
```

**实测输出（2026-06-07）**

```
900社区 → 什么是Ascend C-入门教程-Ascend C算子开发-编程指南-CANN社区版9.0.0开发文档-昇腾社区
850商用 → 什么是Ascend C-入门教程-Ascend C算子开发-算子开发-CANN商用版8.5.0开发文档-昇腾社区
910beta → 什么是Ascend C-入门教程-Ascend C算子开发-编程指南-CANN社区版9.1.0-beta.1开发文档-昇腾社区
```

推论：向量库若只存正文、不写 `version` 字段，三版 chunk 语义高度相似，**无法按版本过滤**。

---

## 2. 单页字段存在形态（900 · 什么是 Ascend C）

```bash
curl -s "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/programug/Ascendcopdevg/atlas_ascendc_map_10_0002.html" \
  | python3 -c "
import sys, re
html = sys.stdin.read()
print('title:', re.search(r'<title>([^<]+)</title>', html).group(1))
print('h1:', re.findall(r'<h1[^>]*>([^<]+)</h1>', html))
print('json-ld:', len(re.findall(r'application/ld\+json', html)))
print('devices:', list(dict.fromkeys(re.findall(r'Atlas [^<]{4,30}产品', html)))[:4])
"
```

**实测摘录**

- `<title>`：`什么是Ascend C-入门教程-Ascend C算子开发-编程指南-CANN社区版9.0.0开发文档-昇腾社区`（面包屑 + 版本挤在一条字符串里）
- `h1`：`什么是 Ascend C`
- `json-ld`：**0**
- 设备型号（正文列表）：`Atlas A2/A3 训练/推理系列产品` 等——页面可见，但无 `applicable_devices` 字段

---

## 3. 下游印证 · 检索脚注版本混杂

同 prompt「基于官方资料，介绍一下 Ascend C 算子开发」：

| 模型 | 与「什么是 Ascend C」相关的官方 URL | 路径版本 |
|------|-----------------------------------|----------|
| 千问 `[^10]` | `…/canncommercial/850/…/atlas_ascendc_map_10_0002.html` | **850 商用** |
| Claude #5 | `…/850alpha001/…/atlas_ascendc_10_0001.html` | 8.5 alpha |
| Claude #6 | `…/910beta1/…/index.html` | 9.1 beta |

完整列表：[千问-检索网页.md](../官方信源感知弱/千问-检索网页.md)、[claude-检索网页.md](../官方信源感知弱/claude-检索网页.md)

---

## 4. 与 RAG 管线的关系

入库后 chunk 若无 `version` / `breadcrumb` / `doc_id` 字段：

- 检索侧无法 `filter(version="CANN社区版 9.0.0")`
- 同名章节（如多处「环境准备」）无法靠 `breadcrumb` 消歧
- 引用溯源只能回退到裸 URL，难以稳定映射到 `doc_id`

方案侧字段模板：[元数据字段规范 · 解决方案](../../problems-structure-metadata.html#solution)
