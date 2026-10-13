---
name: robots-txt-audit
description: >-
  按 AI 亲和「配置 robots.txt 许可声明」原则诊断站点 robots.txt：核验入口可达、Allow/Disallow、
  Sitemap 绝对 URL 声明、可选 LLMs.txt 声明，输出与示例报告同构的 HTML（Part1 当前配置分析 +
  Part2 优化建议，含顶栏导出 PDF）。适用于 robots.txt、Robots Exclusion、爬虫许可、
  Sitemap 声明、Agent 抓取准入等场景。
---

# robots.txt 配置诊断

## 核心命题

`robots.txt` 是 Agent / 爬虫读取的**许可声明**。诊断只回答：规则是否可获取、开放/禁止范围是否写清、发现入口（Sitemap / 可选 llms）是否在文件内声明。

## 范围（必守）

**要查（robots.txt 本体 + 轻量关联探测）**

| 检查项 | 通过标准 |
|--------|----------|
| 入口可达 | `https://{域名}/robots.txt` GET → 200，正文可解析 |
| Allow | 有显式 `Allow:`（建议至少 `Allow: /`），或记录「仅默认放行」为问题 |
| Disallow | 列出全部路径；标记疑似误屏蔽的公开/知识向路径 |
| Sitemap 声明 | 文件内有 `Sitemap:` / `sitemap:` **绝对 URL**（有即不算 P0；小写可记 P2） |
| LLMs.txt 声明 | 若站点目标含 AI Agent：有 `LLMs.txt:`（或等价）绝对 URL；未部署则标待确认，勿强行写入不可达地址 |

**不要查**

- Sitemap **文件本体**质量（lastmod、http/https、条数、是否过期）——只确认「有没有在 robots 里声明绝对 URL」
- 全站内容审计、WAF 策略深挖、训练合规法务结论（可进「待确认」一句带过）

## 诊断工作流

```
Step 0  输入
        · 站点根域名（或完整 robots URL）
        · 可选：是否需要 AI Agent / llms 场景

Step 1  拉取 robots.txt
        · GET https://{域名}/robots.txt（需网络权限）
        · 解析：User-agent 组、Allow[]、Disallow[]、Sitemap[]、LLMs.txt[]、Content-Signal
        · 记录状态码与字节数

Step 2  轻量关联探测（同日 GET，表格用）
        · Allow / Sitemap 声明条数（来自解析，不是猜）
        · HEAD/GET /llms.txt（若相关）→ 是否可声明
        · GET 候选 Sitemap 路径仅用于「能否作为声明候选」（200/非 200），不评价清单质量
        · 对疑似知识向 Disallow 路径抽 1～2 条探测，供待确认

Step 3  对照原则出问题列表
        · 读下方「问题判定」；文案风格：标题一句 + 证据一句
        · 严重度：P0 发现入口缺失 → P1 放行/屏蔽/索引声明 → P2 写法/可维护性

Step 4  生成建议稿 robots.txt
        · 保留明确噪声 Disallow
        · 知识向路径改为注释 + 待确认
        · 补 Allow、Sitemap；LLMs.txt 仅在可访问或业务确认后取消注释
        · Content-Signal 可选

Step 5  输出 HTML 报告
        · 复制 [report-template.html](report-template.html)，填占位符
        · 若在 GEO 仓库：写入 docs/ 与 report-serve/ 双份
        · 必须遵守下方「壳层与布局」；参考成品 docs/robots-audit-huaweicloud.html

Step 6  导出 PDF（可选）
        · 顶栏右侧「导出 PDF」→ 浏览器打印 →「存储为 PDF」
        · 模板已含 @media print（隐藏顶栏/按钮；A4；保留代码块底色）
        · 勿删 #btn-export-pdf 与 print 样式
```

## 壳层与布局（必须同构）

| 规则 | 要求 |
|------|------|
| 侧栏 | **不要** `#module-sidebar` |
| 顶栏 | 仅品牌 + 导出按钮；**不要**站点导航（首页 / 友商对照 / 社区诊断等） |
| 品牌 | 文案「AI 亲和原则」；链接 `https://liminshuo.github.io/ascend-ai/principles-overview.html`（`target="_blank"`） |
| 导出按钮 | `#btn-export-pdf` 放在 `.topbar-inner` **右侧**（`justify-content: space-between`） |
| 顶栏对齐 | `.topbar-inner` 与正文同宽：`min(1000px, 100% - 2*gutter)` + `margin: 0 auto`；品牌左对齐标题，按钮右对齐内容栏 |
| 正文间距 | `.page-wrapper` `padding-top: var(--header-height, 56px)`；`.main-content` `padding-top: 16px`；主区白底 |
| 内容宽度 | `.page-header` / `.page-meta` / `.section` 最大 1000px 居中 |

顶栏 HTML 固定形态：

```html
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="https://liminshuo.github.io/ascend-ai/principles-overview.html" target="_blank" rel="noopener"><span>AI 亲和原则</span></a>
    <button type="button" class="btn-export-pdf" id="btn-export-pdf">导出 PDF</button>
  </div>
</div>
```

## 问题判定（速查）

| 严重度 | 何时记入问题列表 |
|--------|------------------|
| **P0** | 无任何 `Sitemap:` / `sitemap:` 绝对 URL |
| **P1** | 无任何 `Allow:`；或无 `LLMs.txt:` 且场景需要 AI 发现；或 Disallow 含疑似公开知识路径 |
| **P2** | `Disallow:/path` 冒号后无空格；或 `sitemap:` 小写等写法不统一（多数解析器仍可用） |

问题文案模板：

```html
<li>
  <span class="sev sev-p0">P0</span>
  <strong>{一句话问题}。</strong>
  {一句证据/影响}。
</li>
```

## 报告结构（必须同构）

```
顶栏  品牌（左） · 导出 PDF（右）

H1  robots.txt 配置诊断 · {站点简称}
page-meta  示例站点 · 实测日期 · 依据（原则页链接，若有）

Part1. 当前配置分析                    ← H2
  当前 robots.txt（带标注）            ← H3.aj-caption
    figure.file-sample--robots-full
    标注块为兄弟 llms-sec，勿嵌套：
      文件头 | Sitemap | LLMs.txt | Allow | Disallow
  关联探测（同日 GET）                 ← H3
    表：探测项 / 结果 / 解读
  问题列表                             ← H3
    ol + P0/P1/P2

Part2. robots.txt 的优化建议           ← H2
  建议模板                             ← H3.aj-caption
    浅色 file-sample；.add / .keep / .ask 高亮
  修改说明                             ← H3
    每条：动作 + 要点（短）
  待确认事项                           ← H3
    标签文案固定为「待确认」；每条一句决策问句
```

### 标注块规则

- Sitemap、LLMs.txt、Allow、Disallow **各自一个** `span.llms-sec`，互为兄弟，禁止嵌套
- 缺失字段用注释行展示，例如 `# （无 Sitemap: 行）`，右侧 pin 写清状态
- 与原则页 NVIDIA 示例同构：见 `principles-robots.html` `#vendor-analysis`

### 建议稿着色

| class | 含义 |
|-------|------|
| `.add` | 建议新增 |
| `.keep` | 建议保留 |
| `.ask` | 待确认（可先注释） |

### 待确认文案

- 徽章：`<span class="sev sev-ask">待确认</span>`
- 只写决策问句，不复述长篇诊断过程

## 建议稿骨架

```
# {Brand} · robots.txt
# RFC 9309 · Last reviewed: {YYYY-MM-DD}

User-agent: *
# Content-Signal: search=yes, ai-input=yes, ai-train=no   ← 可选

Allow: /

Disallow: {噪声路径…}

# 待确认公开内容路径（确认前保持注释）
# Disallow: {疑似知识路径…}

Sitemap: https://{域名}/sitemap.xml

# LLMs.txt: https://{域名}/llms.txt   ← 可访问后再启用
```

## 输出落盘（GEO）

| 文件 | 说明 |
|------|------|
| `docs/robots-audit-{slug}.html` | 主报告 |
| `report-serve/robots-audit-{slug}.html` | 同步副本 |
| 原则页入口（可选） | `principles-robots.html` `#references` 下加链接 |

复用站点 `assets/css/style.css` + 模板内联样式（见 [report-template.html](report-template.html)）。

## 可调整说明

本 Skill 可随时改：编辑 `SKILL.md` / `report-template.html`，并同步：

- 仓库：`.cursor/skills/robots-txt-audit/`
- 个人：`~/.cursor/skills/robots-txt-audit/`
- 桌面副本（若有）：`~/Desktop/robots-txt-audit/`

## 附加资源

- 可填壳模板：[report-template.html](report-template.html)
- 原则依据：GEO `docs/principles-robots.html`
- 示例报告：`docs/robots-audit-huaweicloud.html`、`docs/robots-audit-developer-huawei.html`
