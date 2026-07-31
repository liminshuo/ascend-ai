# 高优组件实测 · OMenu / OTab / OCarousel

探测视角：静态 HTML（禁 JS）。日期：2026-07-31。样例页按 **DOM class 实测** 复核。

## 样本页

| 组件 | 样例判定 | URL |
|------|----------|-----|
| OMenu | 现有镜像 **未见** `o-menu` DOM；FAQ 作预期侧栏场景对照 | https://www.hiascend.com/document/detail/zh/AscendFAQ/overview/index.html |
| OTab | **社区首页** 有 `o-tab`；CANN 下载为自定义 `tab-*`（亲和问题更重） | https://www.hiascend.com/zh ；https://www.hiascend.com/developer/download |
| OCarousel | **社区首页** 有 `o-carousel` | https://www.hiascend.com/zh |

## OMenu 菜单

**当前问题**
- 设计定义为侧栏/层级菜单；社区首页与 FAQ 静态 HTML 均无 `o-menu` 节点。
- 首页顶栏是 `o-nav-*`（ONavigation），不可标成 OMenu 样例。
- FAQ 手册目录/侧栏树几乎不在首包，依赖前端注入。

**亲和建议**
- 文档侧栏 SSR 输出完整目录或当前手册 sibling 链为真实链接。
- 组件清单样例列：未确认 DOM 前标 —，勿用首页顶栏冒充。
- 用目录 MD / llms 清单补侧栏不可抓缺口。

## OTab 标签页

**当前问题**
- 社区首页存在真实 `o-tab` DOM（可作为组件样例）。
- CANN 下载页用自定义 `tab-list`/`tab-item`；静态可见正文偏壳，安装命令/非激活面板不在首包。
- 多轴选型与折叠叠加时，RAG 易答不全。

**亲和建议**
- 各面板 SSR 全量；禁止关键步骤仅靠隐藏面板交付。
- 机器层按 Tab 标题 H3 展开；维度写入标题/元数据。
- 出预展开 MD 或独立安装页，RAG 优先 MD 轨。

## OCarousel 幻灯片

问题实测页：`problems-ocarousel.html`（本站独立页）。

**当前问题**
- 首页多帧 `o-carousel` / `banner-title` 已进源码。
- 内容偏活动/营销噪声，不宜当知识事实。
- 教育站亦有轮播，静态文案相对弱。

**亲和建议**
- 能力/入口帧：标题+摘要+CTA 每帧静态 DOM。
- 轮播默认不进 llms；要点落到文档页。
- 图片 alt 有区分度。
