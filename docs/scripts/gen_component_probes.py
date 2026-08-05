#!/usr/bin/env python3
"""Generate problems-component-probe HTML pages for community UI catalog."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REPORT = ROOT / "report-serve"

HOME = "https://www.hiascend.com/zh"
DOWNLOAD = "https://www.hiascend.com/developer/download"
CLUSTER = "https://www.hiascend.com/hardware/cluster"
DEVELOPER = "https://www.hiascend.com/developer"
FAQ = "https://www.hiascend.com/document/detail/zh/AscendFAQ/ProduTech/productform/hardwaredesc_0001.html"
CANN_AOLAPI_INTRO = "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta3/API/aolapi/operatorlist_00001.html"
FORUM = "https://www.hiascend.com/forum/"
TRAINING_DEV = "https://www.hiascend.com/cn/developer/training?tab=tab1"
FIRMWARE_DRIVERS = "https://www.hiascend.com/hardware/firmware-drivers"
CUDA_DOWNLOADS = "https://developer.nvidia.com/cuda-downloads/?target_os=Linux"

GROUPS = [
    ("导航类", [
        ("omenu", "OMenu 菜单"),
        ("otab", "OTab 标签页"),
        ("obreadcrumb", "OBreadcrumb 面包屑"),
        ("oanchor", "OAnchor 锚点"),
        ("opagination", "OPagination 分页"),
        ("ostep", "OStep 步骤条"),
        ("onavigation", "ONavigation 导航"),
        ("ofooternav", "底部导航"),
    ]),
    ("操作类", [
        ("obutton", "OButton 按钮"),
        ("olink", "OLink 链接"),
        ("odropdown", "ODropdown 下拉菜单"),
        ("otoggle", "OToggle 选择块"),
    ]),
    ("输入类", [
        ("osearch", "OSearch 搜索框"),
        ("oselect", "OSelect 选择器"),
        ("otrees", "Trees 树"),
        ("orate", "ORate 评分"),
        ("ocascader", "OCascader 级联选择"),
    ]),
    ("展示类", [
        ("otag", "OTag 标签"),
    ]),
    ("容器类", [
        ("ocarousel", "OCarousel 幻灯片"),
        ("odialog", "ODialog 对话框"),
        ("ocard", "OCard 卡片"),
        ("odatetable", "Odate-table 数据表格"),
    ]),
    ("反馈类", [
        ("opopover", "气泡卡片"),
    ]),
]

# Probe content keyed by slug
PROBES: dict[str, dict] = {
    "omenu": {
        "title_short": "侧栏菜单不可达",
        "badge_class": "badge-should",
        "badge_text": "样本缺失 · 侧栏难抓",
        "term": "侧栏菜单不可达",
        "definition": "设计侧栏/层级菜单（OMenu）上的文档目录与链接；若首包无完整树或无真实 href，RAG 无法按手册结构发现页面",
        "sample_url": FAQ,
        "sample_label": "Ascend FAQ 概览",
        "desc_extra": "FAQ 作预期侧栏场景；静态未见 o-menu，目录多依赖前端注入",
        "prompt": f'我在看 <a href="{FAQ}" target="_blank" rel="noopener">Ascend FAQ 概览</a>，手册左侧目录完整有哪些章节？「安装部署」下第一篇官方文档链接是什么？',
        "prompt_plain": f"我在看 Ascend FAQ 概览（{FAQ}），手册左侧目录完整有哪些章节？「安装部署」下第一篇官方文档链接是什么？",
        "answer": "根据当前静态 HTML，我看不到完整的 o-menu / 侧栏目录树，只能依据页面正文或零散链接猜测。无法可靠列出「安装部署」下的第一篇官方深链——目录很可能由前端注入，禁 JS 抓取时侧栏知识结构丢失。",
        "insights": [
            ("友商侧栏可抓全", "Mintlify 73 条、NVIDIA 700+ 条侧栏 href 均在静态 HTML"),
            ("昇腾 TOC 在 NUXT", "FAQ 侧栏节点在 __NUXT_DATA__，禁 JS 无完整目录树"),
            ("样本未见 OMenu", "社区首页与 FAQ 静态 DOM 均无 o-menu；顶栏 o-nav 不能冒充 OMenu"),
            ("发现层缺口", "无 SSR 目录时 Agent 只能靠 sitemap/llms，失去手册内结构线索"),
        ],
        "root_cause": "左侧手册目录没有写进网页源码，章节列表要等脚本运行才出现，爬虫和 AI 默认读不到",
        "subcauses": [
            (
                "左侧章节目录未写进网页源码",
                "Ascend FAQ 页「查看网页源代码」时，看不到完整的左侧章节目录；目录数据在 __NUXT_DATA__ 里，须执行 JavaScript 才会渲染，因此列不出「安装部署」有哪些小节，也拿不出其下第一篇文档的链接",
                "在服务端直接输出完整目录树，每一项都是带地址的链接；不要把目录只放在前端脚本加载的数据里",
            ),
            (
                "目录项没有可点击的链接",
                "侧栏条目若只是文字或点击事件、没有 href，爬虫和 Agent 无法从当前页跳到上级章节或兄弟页面",
                "每一级目录都输出真实链接地址；展开/收起按钮不能代替链接",
            ),
            (
                "没有备用的章节清单",
                "侧栏读不到时，若 llms.txt 或 sitemap 也未按手册列出各章链接，AI 只知道当前页正文，不知道这本手册还有哪些页",
                "在 llms.txt 或 Markdown 版手册里列出章节标题与链接，与侧栏目录互为补充",
            ),
        ],
        "preview_url": FAQ,
    },
    "otab": {
        "title_short": "Tab 隐藏语义",
        "badge_class": "badge-bad",
        "badge_text": "抓取差",
        "term": "Tab 隐藏语义",
        "definition": "非激活 Tab 面板被隐藏或未进首包时，默认抓取只得到当前面板，选型/安装等多轴内容丢失",
        "sample_url": DOWNLOAD,
        "sample_label": "CANN 软件下载",
        "desc_extra": "社区首页有 o-tab 样例；CANN 下载为自定义 tab-*，亲和问题更重",
        "prompt": f'我在看 <a href="{DOWNLOAD}" target="_blank" rel="noopener">CANN 软件下载</a>，想给 Atlas 训练卡做离线安装，下载命令和安装说明在哪个 Tab？把完整命令原文给我。',
        "prompt_plain": f"我在看 CANN 软件下载（{DOWNLOAD}），想给 Atlas 训练卡做离线安装，下载命令和安装说明在哪个 Tab？把完整命令原文给我。",
        "answer": "静态 HTML 中安装命令与多轴 Tab 面板正文几乎不在首包，我只能看到页壳与当前默认组合。无法给出 Atlas 800 离线安装的完整命令原文——非激活面板很可能未 SSR 或被 display:none 隐藏。",
        "insights": [
            ("NVIDIA tabpanel 全进首包", "partners 页 4 个 role=tabpanel 未切换也可抓各面板标题与说明"),
            ("昇腾 Tab 静态空壳", "download 页改版 Tab 与配套横幅在 HTML 快照无正文"),
            ("Mintlify 折叠面板同类", "pricing FAQ 关闭态 region 无答文，展开后才挂入 DOM"),
            ("多轴叠加丢失", "选型 × 折叠时 RAG 易只答默认面板"),
        ],
        "root_cause": "Tab 标签名与各页签里的正文没有写进网页源码，不点切换只能看到默认那一页",
        "subcauses": [
            (
                "Tab 标签名未写进网页源码",
                "昇腾下载页浏览器里能看到「下载资源 / 昇腾资源·三方资源」等页签名，但查看源码时 Tab 导航区域为空或不完整，AI 不知道这一页有哪些页签维度",
                "页签标题直接写在网页源码里，使不执行脚本也能读到全部 Tab 名称",
            ),
            (
                "未选中页签的内容缺失",
                "安装命令、版本说明等多在未默认选中的页签里，或要点页签后才加载；CANN 下载页源码里几乎只有外壳，答不出「Atlas 800 离线安装命令原文」",
                "每一个页签对应的正文都预先写进网页源码，不必点击切换才能抓到",
            ),
            (
                "用隐藏让内容从源码里消失",
                "未激活页签常用 display:none 或干脆不输出 HTML，抓取时当作「没有这些内容」，而不是「还有别的页签可看」",
                "若需视觉隐藏，仍保留文本节点；或为每个页签提供独立页面/锚点链接",
            ),
            (
                "没有不点 Tab 也能读到的说明",
                "安装步骤、下载链接等没有单独的文档页，也没有在 llms.txt 里按页签列出来，AI 只能依赖这一页的交互",
                "安装/下载类内容提供独立文档页，或在 llms.txt 中按页签列出要点与链接",
            ),
        ],
        "preview_url": DOWNLOAD,
    },
    "obreadcrumb": {
        "title_short": "路径链断裂",
        "badge_class": "badge-should",
        "badge_text": "需可爬链",
        "term": "路径链断裂",
        "definition": "面包屑应把当前页在站点中的祖先路径做成可爬链接；若只有纯文本或 JS 渲染，Agent 无法沿路径回溯上下文",
        "sample_url": FAQ,
        "sample_label": "昇腾产品形态说明",
        "desc_extra": "文档页顶栏 o-breadcrumb 可见三级路径链；设计期望 ancestors 为 a[href]，当前页为纯文本",
        "prompt": f'我在看 <a href="{FAQ}" target="_blank" rel="noopener">昇腾产品形态说明</a>，当前页在站点层级中的完整路径是什么？每一级祖先页的可点击链接分别是什么？',
        "prompt_plain": f"我在看昇腾产品形态说明（{FAQ}），当前页在站点层级中的完整路径是什么？每一级祖先页的可点击链接分别是什么？",
        "answer": "Ascend FAQ 顶栏有 o-breadcrumb，浏览器可见「昇腾常见问题 › 产品与技术常见问题 › 昇腾产品形态说明」，但静态 HTML 首包仅 SSR 部分祖先为 a[href]，中间层级需客户端补全，沿链回溯仍不完整。",
        "insights": [
            ("顶栏有 o-breadcrumb", "浏览器可见三级路径链"),
            ("祖先须可链", "纯文本路径无法被爬虫沿链扩展"),
            ("当前页宜非链", "避免循环；但祖先 href 必须稳定"),
        ],
        "root_cause": "面包屑在页面上看得见，但祖先级没有完整写进网页源码里的可点链接，爬虫和 AI 没法沿路径一层层往上找",
        "subcauses": [
            (
                "祖先级缺少真实链接",
                "昇腾产品形态说明页顶栏虽显示「昇腾常见问题 › 产品与技术常见问题 › 昇腾产品形态说明」，但「查看网页源代码」里 o-breadcrumb 的 server-breadcrumb 只有 2 个 a[href]，中间层级不在首包；若祖先只渲染成 span 或纯文字、没有 href，Agent 无法从当前页跳到上级章节",
                "每一级祖先都输出带真实地址的 a[href]；当前页用纯文本即可，但上级必须可爬、可跟链",
            ),
            (
                "完整路径依赖客户端补全",
                "浏览器里路径看起来完整，静态 HTML 却缺中间几级——路径数据常在 __NUXT_DATA__ 或前端脚本里，要等 JavaScript 运行后才补进 o-breadcrumb；禁 JS 抓取时只能看到残缺路径，回答不了「每一级祖先的可点击链接是什么」",
                "在服务端（SSR）首包直接输出与可见 UI 一致的完整 breadcrumb 列表，不要把路径链只放在客户端计算",
            ),
            (
                "路径文案与站图对不上",
                "首包 SSR 的文案（如「文档中心」）与浏览器可见路径（如「昇腾常见问题」）不一致，或 href 与 sitemap / 侧栏目录里的 URL 对不上，Agent 沿链回溯时会和站图结构错位",
                "面包屑每一级的显示文案与 href 须与 sitemap、手册目录保持一致，避免同一层级多套说法",
            ),
        ],
        "preview_url": FAQ,
    },
    "oanchor": {
        "title_short": "锚点目录不可达",
        "badge_class": "badge-should",
        "badge_text": "需 id 对齐",
        "term": "锚点目录不可达",
        "definition": "长文页右侧/顶栏章节目录锚点须用真实 #id 与 href 对齐正文标题；否则 RAG 无法按章节切片回答",
        "sample_url": CANN_AOLAPI_INTRO,
        "sample_label": "CANN 算子库简介",
        "desc_extra": "长文页右侧 document-anc 章节目录须与正文 h4.sectiontitle、section id 对齐",
        "prompt": f'我在看 <a href="{CANN_AOLAPI_INTRO}" target="_blank" rel="noopener">CANN 算子库简介</a>，右侧章节目录里「概述」对应正文哪一节？给出该节标题与 #id。',
        "prompt_plain": f"我在看 CANN 算子库简介（{CANN_AOLAPI_INTRO}），右侧章节目录里「概述」对应正文哪一节？给出该节标题与 #id。",
        "answer": "CANN 算子库简介页浏览器右侧可见章节目录（概述 / 使用说明 / 使用向导），但静态 HTML 无 document-anc 可跟链 nav 列表。正文 h4.sectiontitle 与 section id 已在首包；若锚点 href 与 id 不对齐，我无法可靠映射「目录项 → 正文块」。",
        "insights": [
            ("href 须对齐 id", "锚点与标题 section id 不一致则 chunk 切不准"),
            ("右侧锚点目录", "document-anc 浏览器可见，首包常缺 nav 列表"),
            ("纯视觉选中态不足", "颜色变化对抓取无增量"),
        ],
        "root_cause": "长文页右侧章节目录在浏览器里看得见，但目录项没有完整写进网页源码里的 #hash 链接，或与正文标题 id 对不齐，Agent 无法按章节证伪回答",
        "subcauses": [
            (
                "右侧章节目录未 SSR 进首包",
                "CANN 算子库简介页浏览器右侧可见 document-anc（概述 / 使用说明 / 使用向导），但「查看网页源代码」里没有可跟链 nav 列表；友商 Mintlify 的 On this page、NVIDIA 的 page-toc 却在静态 HTML 里带 #open-the-editor、#installing-cuquantum 等 hash，禁 JS 抓取时昇腾侧目录项无法列出",
                "在服务端（SSR）首包直接输出右侧 anchor nav，每一项为 a[href=\"#section-id\"] + 可见章节名，对齐 Mintlify/NVIDIA 文档页做法",
            ),
            (
                "锚点 href 须与正文 id 对齐",
                "目录项若只用 click 滚动、没有 href，或 #hash 与正文 h2/h4.sectiontitle 的 section id 不一致，Agent 无法可靠回答「概述对应哪一节、#id 是什么」——chunk 切片也会对错块",
                "每个可导航标题输出稳定 id；章节目录每一项一律 a[href=\"#…\"] 指向正文同名 heading/section",
            ),
            (
                "正文有 id 但目录半成品",
                "昇腾 CANN 页正文 h4.sectiontitle 与 section id（如 …section10818103975019）已在首包，但右侧 document-anc 列表缺失，形成「正文可切片、目录不可引」的半成品态",
                "目录与正文 id 同批 SSR；勿只写正文 id 而把章节目录留给客户端补全",
            ),
        ],
        "preview_url": CANN_AOLAPI_INTRO,
    },
    "opagination": {
        "title_short": "分页 URL 不可达",
        "badge_class": "badge-should",
        "badge_text": "需可爬页码",
        "term": "分页 URL 不可达",
        "definition": "列表/搜索结果分页须为可抓 URL；纯前端翻页会导致下一页内容对爬虫不可达",
        "sample_url": FORUM,
        "sample_label": "昇腾论坛",
        "desc_extra": "论坛帖列表含翻页；页码须为可抓 URL，勿纯 button 切换",
        "prompt": f'我在看 <a href="{FORUM}" target="_blank" rel="noopener">昇腾论坛</a> 列表页，第 2、3 页帖子列表的官方 URL 分别是什么？请给出完整 href。',
        "prompt_plain": f"我在看昇腾论坛（{FORUM}）列表页，第 2、3 页帖子列表的官方 URL 分别是什么？请给出完整 href。",
        "answer": "论坛列表在浏览器可见翻页，但若分页仅 button/onClick 切换、静态 HTML 无 page=2 的链接，我只能描述「还有下一页」但给不出可爬地址，后续页内容对 RAG 不可达。",
        "insights": [
            ("页码应是链接", "a[href] 带 page 参数"),
            ("纯 JS 翻页断链", "sitemap 难覆盖深页"),
            ("rel=next 可辅助", "机器发现下一页"),
        ],
        "root_cause": "分页交互未暴露稳定 URL，列表深页对默认管道不可达",
        "subcauses": [
            ("页码是 button", "无 href", "每页用带 query 的真实 URL"),
            ("仅 infinite scroll", "无页界", "提供分页或完整 sitemap"),
            ("SEO 与 RAG 未对齐", "深页未收录", "llms/sitemap 补列表全量"),
        ],
        "preview_url": FORUM,
    },
    "ostep": {
        "title_short": "步骤说明不可抓",
        "badge_class": "badge-should",
        "badge_text": "需文本进源码",
        "term": "步骤说明不可抓",
        "definition": "步骤条上的标题与说明须写入 HTML 文本；进行中/完成态勿只靠颜色，否则安装/认证流程对 RAG 不完整",
        "sample_url": DEVELOPER,
        "sample_label": "开发者入口",
        "desc_extra": "开发者计划等流程区块含多步语义；步骤标题与说明须写入源码",
        "prompt": f'我在看 <a href="{DEVELOPER}" target="_blank" rel="noopener">开发者入口</a>，「加入开发者计划」流程每一步的标题和说明原文是什么？当前进行到哪一步？',
        "prompt_plain": f"我在看开发者入口（{DEVELOPER}），「加入开发者计划」流程每一步的标题和说明原文是什么？当前进行到哪一步？",
        "answer": "Mintlify Quickstart 的 Web editor Steps 我能逐步列出 Open the web editor → Edit a page → Publish → View live 的标题与说明。昇腾开发者入口「加入开发者计划」浏览器可见四格权益，但实物礼品/开发资源等文案在配图内，源码无逐步可引用的步骤正文。",
        "insights": [
            ("友商 Steps 可抓全", "Mintlify quickstart Web editor 四步 step-title + step-content 在首包"),
            ("说明勿绑配图", "昇腾计划权益格文字在图内、源码缺文本"),
            ("状态须文本化", "进行中/完成勿只靠颜色或圈号"),
        ],
        "root_cause": "流程步骤在页面上看得见，但标题与说明若不进源码文本——只在配图、tooltip 或切换后才出现的 DOM 里——Agent 无法逐步复述；友商 Mintlify Steps 已可抓全，昇腾侧权益说明仍绑在视觉块上",
        "subcauses": [
            (
                "步骤说明绑在配图或视觉块",
                "昇腾开发者入口「加入开发者计划」四格权益（实物礼品 / 开发资源 / 身份荣誉 / 学习资源）浏览器可见，但文字在配图内、源码无独立文本；友商 Mintlify Quickstart Web editor Tab 内 Steps 四步 step-title + step-content 均在首包",
                "每步标题与说明 SSR 为文本节点（h/p 或 step-title + step-content）；配图内字须补 alt 或逐步旁注正文",
            ),
            (
                "仅当前步保留说明",
                "步骤条若只渲染当前步文案、其余步等切换或脚本注入才挂入 DOM，禁 JS 抓取时列不出完整流程清单",
                "全部步骤标题 + 说明一次性进首包 HTML（对标 Mintlify role=listitem Steps）；勿动态剥离非当前步文本",
            ),
            (
                "状态只靠颜色或圈号",
                "进行中 / 完成若只靠高亮色、数字圈无 aria 或文本标注，Agent 答不出「当前进行到哪一步」",
                "用 aria-current / 可见文本标注步骤状态；说明写在步骤旁，勿只放 tooltip",
            ),
        ],
        "preview_url": DEVELOPER,
    },
    "onavigation": {
        "title_short": "主导航链接可发现性",
        "badge_class": "badge-should",
        "badge_text": "部分可抓",
        "term": "主导航链接可发现性",
        "definition": "顶栏/主导航中的信息架构入口是否以真实链接写入 HTML；语言、主题等纯交互可弱化入库",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "社区首页顶栏为 o-nav-* 体系",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，昇腾社区主导航里，从首页能进「文档/开发者/下载」的官方链接文案和地址分别是什么？',
        "prompt_plain": f"我在看社区首页（{HOME}），昇腾社区主导航里，从首页能进「文档/开发者/下载」的官方链接文案和地址分别是什么？",
        "answer": "社区首页顶栏我能读到「产品 / 解决方案 / 开发者与合作伙伴 / 支持与服务」等文案，但多数一级项是 div 无 href，只有「支持与服务」→ /support 等少数可跟链；「文档 / 在线开发 / 下载」要么在折叠 panel 里、要么是 button/div，无法完整列出官方入口地址。",
        "insights": [
            ("友商顶栏可抓全", "Mintlify 文档站 navbar、NVIDIA global-nav 一级或子级 href 均在首包"),
            ("一级多缺 href", "o-nav-item-link 常见 div，文案可见却跟不到"),
            ("导流项靠按钮", "在线开发 / 下载无稳定 a[href]"),
        ],
        "root_cause": "顶栏主导航在浏览器里一目了然，但许多一级入口没有写进网页源码里的可点链接，AI 看得见「产品 / 文档 / 下载」等文案，却跟不到官方地址",
        "subcauses": [
            (
                "一级入口缺少 href",
                "社区首页顶栏 o-nav 里「产品」「解决方案」「开发者与合作伙伴」等多为 div.o-nav-item-link，没有 href；友商 Mintlify 文档站 Documentation / Get started、NVIDIA Shop / Drivers 等一级入口在「查看网页源代码」里即可跟链",
                "每一级站点入口一律用 OLink / a[href] 输出，文案与目标地址同时写进首包 HTML",
            ),
            (
                "关键导流项缺少可跟链接",
                "顶栏右侧的「在线开发」「下载」是人最常找的入口：前者在源码里没有网页地址，后者只是下拉框，不展开就不知道链到哪。问「从首页怎么进官方文档 / 开发者 / 下载中心」时，往往只能答出一两条，清单对不齐——友商同类入口在「查看网页源代码」里就能直接跟链。",
                "把文档、开发者、下载等高频入口改成带真实网址的顶栏链接；下拉面板里每一项也在首屏 HTML 里写好完整 a[href]，不要等点击才出现。",
            ),
            (
                "下拉子链与工具控件混排",
                "CANN 推广位、搜索、登录图标和「产品 / 文档」等导航挤在同一顶栏；部分子菜单要鼠标悬停或跑脚本后才挂出来，首包 HTML 里 o-nav-head 甚至可能为空。友商 Mintlify navbar、NVIDIA mega menu 的下拉子链，大多一开始就写在源码里，禁 JS 也能抓全。",
                "下拉菜单在服务端一次性输出完整链接树；搜索、换肤、语言切换等纯操作控件标注 data-llm-exclude，入库管道勿当正文知识。",
            ),
        ],
        "preview_url": HOME,
    },
    "ofooternav": {
        "title_short": "页脚链接可发现性",
        "badge_class": "badge-should",
        "badge_text": "宜全量可抓",
        "term": "页脚链接可发现性",
        "definition": "页脚多列导航链接须进源码；列名与链接文案保持稳定，便于 sitemap 与 Agent 对照站点结构",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页页脚通常含产品/支持/法律等列",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，页脚「关于昇腾 / 法律声明 / 联系我们」分别链到哪些官方 URL？',
        "prompt_plain": f"我在看社区首页（{HOME}），页脚「关于昇腾 / 法律声明 / 联系我们」分别链到哪些官方 URL？",
        "answer": "社区首页页脚我能完整列出五列及法律声明 → /zh/legal/law、联系我们等 href——友商表 html 可抓全。但若 llms 未收录这些链、或日后改版改回脚本注入，Agent 仍可能对不齐站图。",
        "insights": [
            ("首页 html 已达标", "友商表三站 footer 多列 href 均在首包，昇腾可抓全"),
            ("页脚补顶栏", "顶栏缺链的文档 / 法律 / 支持入口常在这里才完整"),
            ("守 llms 与列名", "html 可抓 ≠ 入库后永不过期"),
        ],
        "root_cause": "虽社区首页页脚 html 已可抓全（友商表三站均达标），页脚仍是顶栏之外的第二发现层——须防改回脚本注入、守列名稳定、并与 llms 互证，否则 Agent 仍会漏答",
        "subcauses": [
            (
                "守住 SSR 多列链接",
                "首页 footer-main 实测五列 + 法律链已在首包，友商表判「可抓全」；风险不在当前快照，而在后续改版若某列改等 JavaScript 填充、或只剩社交图标无文字链，html 抓取会退化",
                "维持每一列 gp-name + gp-link 在服务端输出 a[href]；改版后复测 problems-ofooternav 探针，确保仍禁 JS 可答「法律声明 / 联系我们链到哪」",
            ),
            (
                "列名改版导致知识库错位",
                "html 可抓全不代表入库后永不过期：页脚分组名或链接文案随营销改版，已入库旧 chunk 仍用旧说法，Agent 检索时对不上当前 HTML",
                "列名保持稳定；必须改版时在 llms 或 changelog 写明新旧映射，并触发知识库重抓",
            ),
            (
                "页脚须与 llms 互证",
                "探针问「关于昇腾 / 法律声明 / 联系我们链到哪」——答案已在页脚 HTML；但若 llms.txt / sitemap 未收录这些 URL，仅靠 RAG 检索的 Agent 仍可能漏入口（这不反映在「html 可抓取」列）",
                "llms 显式列出页脚关键链（文档 / 法律声明 / 联系我们等），与 footer SSR 双轨互证",
            ),
        ],
        "preview_url": HOME,
    },
    "obutton": {
        "title_short": "按钮与链接角色混淆",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "按钮与链接角色混淆",
        "definition": "跳转型控件应是可抓链接；纯提交/弹层按钮文案入库时宜剥离，避免被当成正文结论",
        "aff_note": "同一组件要分角色——跳转型 CTA（立即查看 / 了解更多 / 前往认证等）须写成可抓 a[href]，本页根因分析主要针对这类；纯提交 / 关闭 / 弹层确认等操作按钮不必当正文知识，入库管道宜剥离",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页大量 CTA 按钮",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，首页上「立即下载 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。',
        "prompt_plain": f"我在看社区首页（{HOME}），首页上「立即下载 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。",
        "answer": "若 CTA 是 button + JS 跳转而非 a[href]，静态抓取看不到目标地址，我只能复述按钮文案，给不出可靠落地 URL。",
        "insights": [
            ("友商 CTA 可抓全", "Mintlify Get started、NVIDIA More Models 首包有真实 href"),
            ("首页 banner 无 href", "立即查看/了解更多等为 button.o-btn，静态看不到落地 URL"),
            ("探针只能复述文案", "问 href 时给不出官方地址清单"),
        ],
        "root_cause": "首屏 CTA 在浏览器里像可点入口，但源码里是 button + JS 跳转、没有 href——AI 只能复述「立即查看 / 了解更多」等文案，给不出官方落地 URL；友商 Mintlify 首屏 Get started、NVIDIA build 列表底部 More Models 等在首包即有 a[href]",
        "subcauses": [
            (
                "首屏轮播 CTA 用 button 伪链",
                "昇腾侧：社区首页 banner 各帧 CTA（立即查看 / 了解更多 / 立即填写 / 前往认证 / 立即参与）源码为 `button.o-btn.banner-actions-item`，无 href，跳转靠 JS；探针问「这类按钮 href 是什么」时只能复述文案。\n\n友商侧：Mintlify 首屏「Get started」「Sign up with Google」、NVIDIA build「More Models」「View Skills」均为真实 `a[href]`，首包可跟链。",
                "跳转型 CTA 一律用 OLink 或 `a[href]` + 可见文案；样式可保留按钮外观，底层须输出可爬 href。",
            ),
            (
                "button 文案误入知识 chunk",
                "「立即下载 / 提交 / 关闭 / 我知道了」等纯操作词若与正文混排入库，Agent 会把操作提示当成可引用结论，或把无 URL 的 CTA 文本误当「官方入口说明」",
                "入库管道对 type=submit、纯关闭、无 href 的 button 标注 data-llm-exclude 或剥离；仅保留带 href 的跳转链作为可证伪入口",
            ),
            (
                "弹层 / 对话框里的唯一说明",
                "部分 CTA 点开才弹出表单或活动详情，关键落地信息不在首屏 HTML；静态抓取时只有按钮文案，没有目标页 URL 或规则正文",
                "弹层前的关键说明（活动规则摘要、认证入口 URL）同步写在按钮旁可见正文，或改为 a[href] 指向 SSR 详情页",
            ),
        ],
        "preview_url": HOME,
    },
    "olink": {
        "title_short": "链接 href 缺失",
        "badge_class": "badge-bad",
        "badge_text": "需真实 href",
        "term": "链接 href 缺失",
        "definition": "正文与导航中的链接必须带真实 href；伪链、javascript: 或空 href 会导致 Agent 无法跟进深页",
        "sample_url": TRAINING_DEV,
        "sample_label": "训练开发",
        "desc_extra": "大语言模型训练用户旅程矩阵含多级导流链接",
        "prompt": f'我在看 <a href="{TRAINING_DEV}" target="_blank" rel="noopener">训练开发</a>（tab=tab1），「大语言模型训练用户旅程」表格里「软件介绍 / 安装指导 / 快速入门」这些链接的 href 原文是什么？有没有 javascript:void 或空链？',
        "prompt_plain": f"我在看训练开发（{TRAINING_DEV}），「大语言模型训练用户旅程」表格里「软件介绍 / 安装指导 / 快速入门」这些链接的 href 原文是什么？有没有 javascript:void 或空链？",
        "answer": "浏览器可见用户旅程矩阵里的可点链，但静态 HTML 里 tab-content 挂载点为空；label+link 在 hcomponent-ascend-user-journey 的 application/json 脚本里，首包无 a[href] 节点，我只能从 JSON 片段复述，无法像正文 OLink 那样直接列出可跟链。",
        "insights": [
            ("友商正文链可抓全", "Mintlify Related topics、NVIDIA Quick Links 首包有 a[href]"),
            ("旅程矩阵无 a 节点", "训练开发页 label+link 只在 application/json"),
            ("文档正文可对照", "CANN 使用向导表内 OLink 首包可跟链"),
        ],
        "root_cause": "导流链在浏览器里可点，但 URL 若不进首包 a[href]——只放 JSON 脚本、onclick 或 span 冒充——Agent 只能复述文案或从 JSON 片段猜地址，跟不到官方落地页；友商 Mintlify Related topics、NVIDIA Quick Links 等在静态 HTML 即有可跟链",
        "subcauses": [
            (
                "用户旅程矩阵链未 SSR 为 a[href]",
                "昇腾侧：训练开发页「大语言模型训练用户旅程」矩阵（软件介绍 / 安装指导 / 快速入门 / 模型使用指导等）浏览器可见，但 hcomponent-ascend-user-journey 的 tab-content 挂载点首包为空，label+link 仅在 application/json；探针问「这些链接 href 是什么」时给不出可跟 a 节点。\n\n友商侧：Mintlify 文档编辑器 Related topics（Editor overview / Automations overview 等）、NVIDIA 首页 Quick Links（Overview / Machine Learning 等）文案与 href 均在首包 a 标签。",
                "矩阵内每一格导流链 SSR 为 OLink 或 `a[href]` + 可见文案；勿只把 link 字段留给 Vue 读 JSON 后再渲染。",
            ),
            (
                "span / div 冒充可导航链",
                "顶栏 o-nav-item-link、整卡 onclick 等可点击样式若无 a 标签，静态管道看不见 href；Agent 只能读到可见文案，无法证伪「点这里会到哪」。",
                "可导航一律 OLink 或 `a[href]`；样式可保留，底层须输出 href，禁 span/div 伪链。",
            ),
            (
                "占位链与相对路径不规范",
                "href=\"#\" / javascript:void 占位链未就绪仍渲染；CANN 文档 operatorlist_00010.html 等相对路径在镜像抓取或跨域入库时可能解析失败，Agent 跟链不稳定。",
                "未就绪勿渲染假链；站内链宜 canonical 绝对 URL 或稳定的根相对路径，外链补 rel/title。",
            ),
        ],
        "preview_url": TRAINING_DEV,
    },
    "odropdown": {
        "title_short": "下拉子链首包缺失",
        "badge_class": "badge-should",
        "badge_text": "子项须进源码",
        "term": "下拉子链首包缺失",
        "definition": "下拉菜单内导航项须在首包 HTML 可读；勿悬停/点击/JSON 注入才挂载子链，否则发现层断裂",
        "sample_url": CLUSTER,
        "sample_label": "集群产品页",
        "desc_extra": "集群页标题旁「更多产品」下拉切换同品类机型",
        "prompt": f'我在看 <a href="{CLUSTER}" target="_blank" rel="noopener">集群产品页</a>，标题旁「更多产品」下拉里各款集群/超节点（如 Atlas 900 A2 PoD 集群基础单元、Atlas 900 SuperCluster AI 集群等）对应的落地页 URL 分别是什么？',
        "prompt_plain": f"我在看集群产品页（{CLUSTER}），标题旁「更多产品」下拉里各款集群/超节点（如 Atlas 900 A2 PoD 集群基础单元、Atlas 900 SuperCluster AI 集群等）对应的落地页 URL 分别是什么？",
        "answer": "静态 HTML 首包仅见「更多产品」触发器文案，dropdown-panel 内各机型 a[href] 须点击/悬停才挂载；禁 JS 时无法列出 Atlas 900 A2 PoD、SuperCluster AI 集群等同品类落地 URL。",
        "insights": [
            ("三站下拉均抓不全", "Mintlify Products mega menu、NVIDIA developer Resources JSON 菜单、昇腾「更多产品」panel 均未 SSR 子链"),
            ("触发器可见、子项丢失", "首包常见 navigation-menu-trigger /「更多产品」文案，panel 内 a[href] 缺失"),
            ("与 OMenu 勿混", "页内 ODropdown 子链亦须首包可读，不能指望顶栏大菜单代替"),
        ],
        "root_cause": "下拉面板子项依赖点击/悬停或外部 JSON 才挂载，静态抓取只能看到触发器（「更多产品 / Products / Resources」），看不到各子项 a[href]",
        "subcauses": [
            (
                "dropdown-panel 空壳",
                "昇腾侧：集群页浏览器可见「更多产品」及 Atlas 900 A2 PoD / SuperCluster AI 集群等项，静态 HTML 无 panel 内 a[href] 列表。\n\n友商侧：Mintlify pricing 顶栏 Products/Solutions/Resources 触发器在首包，mega menu 子项（Platform / Editor / Authentication / Automations / Agent 等）须悬停/点击才挂载 panel。",
                "SSR 输出完整 dropdown 子项：每项可读 label + href；视觉可折叠但 DOM 须保留 a 节点",
            ),
            (
                "菜单 JSON 外部注入",
                "NVIDIA developer.nvidia.com：Resources 下拉含 Developer Program / Community Hub / Discord / GTC / On-Demand 等，静态 HTML 仅 div#header 空壳，子链在 header-secondary.json 须 fetch + NVDeveloperHeader 客户端挂载。",
                "关键子链 SSR 进首包 HTML；外部 JSON 菜单仅作增强，不可作唯一发现层",
            ),
            (
                "portal / 延迟挂载",
                "下拉项在点击后才注入 DOM 或挂到 body portal，首包无 li/a；与 Mintlify navigation-menu data-state=closed 同类。",
                "子项写在页面静态 nav/ul 区，勿仅 portal 延迟挂",
            ),
            (
                "触发器当唯一信息",
                "入库 chunk 只有「更多产品 / Products / Resources」等触发器文案，Agent 无法证伪各子项 URL。",
                "子项文案与落地页 title 一致，并带 canonical href",
            ),
        ],
        "preview_url": CLUSTER,
    },
    "oradio": {
        "title_short": "单选控件（非内容载体）",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "单选控件（非内容载体）",
        "definition": "表单选项态本身不是官网知识正文；说明应写在旁侧段落，勿把选项文案当规格唯一来源",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "无强制样例；属交互控件",
        "prompt": "我在看昇腾社区相关页面（组件：ORadio 单选框，暂无确认 DOM 样例 URL），这个单选项里写的参数，是不是官方推荐的默认配置？请当正文规格解释。",
        "prompt_plain": "我在看昇腾社区相关页面（组件：ORadio 单选框，暂无确认 DOM 样例 URL），这个单选项里写的参数，是不是官方推荐的默认配置？请当正文规格解释。",
        "answer": "单选框选项通常只是表单 UI。若没有旁侧说明文档，我不应当把选项标签解释成产品规格；该组件默认不需要内容亲和改造。",
        "insights": [
            ("非知识载体", "选项态无增量知识价值"),
            ("说明走正文", "勿只靠 label"),
            ("结论：不需要", "与社区 UI 清单一致"),
        ],
        "root_cause": "误把表单控件文案当成可引用规格",
        "subcauses": [
            ("唯一说明在 label", "无旁注", "规格写进正文/文档页"),
            ("入库未过滤", "选项进 chunk", "管道可跳过纯表单控件区"),
            ("无障碍文本当正文", "混淆", "区分 UI 文案与知识正文"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "ocheckbox": {
        "title_short": "多选控件（非内容载体）",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "多选控件（非内容载体）",
        "definition": "多选框表示用户选择，不是能力说明书；说明应写在旁侧正文，勿把勾选项当产品模块清单",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "无强制样例；属交互控件",
        "prompt": "我在看昇腾社区相关页面（组件：OCheckbox 多选框，暂无确认 DOM 样例 URL），用户勾选的这些选项是否代表官方推荐启用的全部功能？请按规格解释。",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OCheckbox 多选框，暂无确认 DOM 样例 URL），用户勾选的这些选项是否代表官方推荐启用的全部功能？请按规格解释。",
        "answer": "多选框表示用户选择，不是能力说明书。没有旁侧文档时，不应把勾选项解释成产品模块清单。组件本身不需要亲和改造。",
        "insights": [
            ("非知识载体", "勾选态对 RAG 无规格价值"),
            ("说明走正文", "旁注段落承载知识"),
            ("结论：不需要", "与清单「不需要」一致"),
        ],
        "root_cause": "误把表单勾选文案当成可引用规格",
        "subcauses": [
            ("选项即唯一说明", "无旁注", "规格写进正文/文档页"),
            ("入库未过滤", "选项进 chunk", "管道跳过纯表单区"),
            ("默认态当推荐", "误读 UI", "区分交互态与官方说明"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "oswitch": {
        "title_short": "开关态",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "开关态",
        "definition": "开关表示 UI 交互态，对静态抓取无信息增量；功能说明应写在旁侧正文",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "开关态对抓取无信息增量",
        "prompt": "我在看昇腾社区相关页面（组件：OSwitch 开关，暂无确认 DOM 样例 URL），这个开关现在是开还是关，是否代表产品的默认发布配置？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OSwitch 开关，暂无确认 DOM 样例 URL），这个开关现在是开还是关，是否代表产品的默认发布配置？",
        "answer": "开关的 on/off 只是当前 UI 态，不是产品规格。除非旁侧有文档说明该开关含义，否则不应做亲和改造或当知识入库。",
        "insights": [
            ("态非规格", "开/关无默认知识语义"),
            ("说明在旁注", "非 switch 本身"),
            ("结论：不需要", "清单标记不需要"),
        ],
        "root_cause": "把瞬时 UI 态误读为可引用配置事实",
        "subcauses": [
            ("态写进 chunk", "噪声", "过滤纯 switch DOM"),
            ("缺旁注", "用户误解", "功能说明放正文"),
            ("默认值靠颜色", "不可抓", "默认配置写文档"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "oscrollbar": {
        "title_short": "滚动条样式",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "滚动条样式",
        "definition": "OScrollbar 为纯视觉样式组件，与内容可抓性无关；滚动区域内的正文才是关键",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "样式组件；关注容器内正文是否可抓即可",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，自定义滚动条是否意味着首屏外还有被隐藏的正文？请列出滚动区内全部章节标题。',
        "prompt_plain": f"我在看社区首页（{HOME}），自定义滚动条是否意味着首屏外还有被隐藏的正文？请列出滚动区内全部章节标题。",
        "answer": "滚动条样式与内容是否可抓无直接关系。首屏外内容是否在 HTML 中，取决于是否 SSR 全文，而非 scrollbar 组件。该组件不需要亲和改造。",
        "insights": [
            ("纯样式", "与 RAG 无关"),
            ("看容器正文", "非 scrollbar 本身"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "混淆视觉滚动组件与内容交付边界",
        "subcauses": [
            ("误以为隐藏", "scrollbar ≠ lazy", "正文仍须 SSR"),
            ("过度优化样式", "分散注意力", "优先保证容器内文本"),
            ("无知识语义", "勿入库", "管道忽略纯样式节点"),
        ],
        "preview_url": HOME,
        "no_aff": True,
    },
    "otoggle": {
        "title_short": "Toggle 版本矩阵首包缺失",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "Toggle 版本矩阵首包缺失",
        "definition": "下载/版本页 Toggle 若映射 OS、架构、安装方式等选型，完整 option 矩阵须在首包可读；纯 UI 筛选则宜 exclude",
        "sample_url": FIRMWARE_DRIVERS,
        "sample_label": "固件与驱动",
        "desc_extra": "固件与驱动页含产品型号/架构/安装方式 Toggle 筛选矩阵",
        "prompt": f'我在看 <a href="{FIRMWARE_DRIVERS}" target="_blank" rel="noopener">固件与驱动</a>，产品型号 / 架构 / 安装方式等 Toggle 各选项对应的官方下载页或带 <code>ids=</code> 的 URL 分别是什么？',
        "prompt_plain": f"我在看固件与驱动（{FIRMWARE_DRIVERS}），产品型号 / 架构 / 安装方式等 Toggle 各选项对应的官方下载页或带 ids= 的 URL 分别是什么？",
        "answer": "固件与驱动页浏览器可见型号/架构/安装方式筛选与包列表，但静态 HTML 无完整 Toggle option 矩阵；当前组合靠 URL ?ids= 与 __NUXT_DATA__ 恢复，禁 JS 时无法列出全部选项与对应包表。",
        "insights": [
            ("NVIDIA 矩阵在 props", "CUDA 下载页 OS/Architecture 全树嵌在 data-react-props，禁 JS 可解析"),
            ("昇腾 ids 不可读", "固件与驱动 ?ids= 编码选中态，首包无 option 文本列表"),
            ("导航 vs 筛选", "映射包表/落地页须 SSR；纯表单筛选勿当 IA"),
        ],
        "root_cause": "下载选型 Toggle 的完整 option 矩阵未进首包：昇腾固件与驱动页仅 ?ids= 与 __NUXT_DATA__ 恢复选中态，静态 HTML 无型号/架构/安装方式全量列表；对标 NVIDIA CUDA 下载页虽由 React 渲染按钮，但 OS/Architecture 嵌套树已写在 data-react-props JSON",
        "subcauses": [
            (
                "Toggle option 文本未 SSR",
                "昇腾侧：固件与驱动页浏览器可见产品型号/架构/安装方式 Toggle 与包列表，静态 HTML 无完整 option 文本；选中组合靠 ?ids= 与 __NUXT_DATA__ 恢复，禁 JS 无法枚举矩阵。\n\n友商侧：NVIDIA cuda-downloads 页 Operating System（Linux/Windows）、Architecture（x86_64/arm64-sbsa）及 Distribution→Version→Installer 嵌套树写在 data-react-props 的 pageData.structure，target_os / target_arch 映射 URL 选中态。",
                "SSR 全量 Toggle option（可读 label + ids 或 href）；或像 NVIDIA 一样把完整矩阵 JSON 写进首包 data-* 属性并文档化解析方式",
            ),
            (
                "ids 编码承载 IA",
                "?ids=d802,…,AArch64,online_apt_get 仅表达当前选中组合，Agent 无法从首包反推「还有哪些架构/安装方式可选」及各选项对应包表。",
                "每项 option 附带人类可读 label 与 canonical URL（或 ids→包表映射写进 llms.txt）",
            ),
            (
                "未选中项 DOM 缺失",
                "仅当前选中 Toggle 在静态 HTML 可见，其余架构/安装方式选项不在首包 DOM；与 Mintlify pricing 矩阵类对照表不同，此处是动态版本选型而非静态正文。",
                "全部选项 SSR 进 DOM（未选中项可用 visually-hidden 保留）；纯 UI 筛选标注 data-llm-exclude",
            ),
            (
                "选中态依赖客户端",
                "固件与驱动页包列表随 Toggle 切换由 Nuxt 客户端渲染；首包只见当前 ids 对应片段，无法一次性抓取全版本×架构×安装方式交叉表。",
                "关键交叉表 SSR 或旁路 llms/JSON 清单；Toggle 只作 UI，矩阵数据须有静态可读源",
            ),
        ],
        "preview_url": FIRMWARE_DRIVERS,
    },
    "oinput": {
        "title_short": "输入框",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "输入框",
        "definition": "输入控件本身不承载官网知识；关键说明勿只写在 placeholder，应出现在正文段落",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页搜索/登录等含 input；placeholder 非知识源",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，搜索框 placeholder 里的说明是不是官方检索范围定义？请当规格引用。',
        "prompt_plain": f"我在看社区首页（{HOME}），搜索框 placeholder 里的说明是不是官方检索范围定义？请当规格引用。",
        "answer": "placeholder 只是 UI 提示，不是可引用规格。检索范围、字段含义应在文档正文说明。OInput 不需要亲和改造。",
        "insights": [
            ("placeholder 非正文", "易丢失且非规格"),
            ("说明走文档", "非 input 属性"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把占位符提示误当作唯一规格说明",
        "subcauses": [
            ("规格在 placeholder", "抓取不稳定", "写进旁注/文档"),
            ("input 进 chunk", "噪声", "过滤纯表单区"),
            ("label 过短", "缺上下文", "正文补全含义"),
        ],
        "preview_url": HOME,
        "no_aff": True,
    },
    "otextarea": {
        "title_short": "多行输入框",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "多行输入框",
        "definition": "多行文本输入为用户编辑区，不承载官网知识；长说明应放正文段落而非 textarea 占位",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；长说明应放正文",
        "prompt": "我在看昇腾社区相关页面（组件：OTextarea 多行文本输入框，暂无确认 DOM 样例 URL），textarea 占位符里的长说明是不是官方配置规范全文？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OTextarea 多行文本输入框，暂无确认 DOM 样例 URL），textarea 占位符里的长说明是不是官方配置规范全文？",
        "answer": "textarea 是用户输入区，placeholder 不是官方规范正文。长说明应出现在可引用文档页。该组件不需要亲和改造。",
        "insights": [
            ("编辑区非知识", "用户生成内容"),
            ("占位非规格", "勿入库"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把输入占位当成规格交付面",
        "subcauses": [
            ("长说明放 placeholder", "不可靠", "改正文段落"),
            ("textarea 进库", "噪声", "过滤表单区"),
            ("缺文档链", "用户误读", "链到正式说明页"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "osearch": {
        "title_short": "搜索框与可达 URL",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "搜索框与可达 URL",
        "definition": "搜索框可有，但站内文档仍需独立可达 URL 与 sitemap；不能只靠搜索作为唯一发现层",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页含站内搜索；文档发现不能仅靠搜索",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，不用搜索框，能否从静态 HTML 列出所有 CANN 安装文档的官方 URL？',
        "prompt_plain": f"我在看社区首页（{HOME}），不用搜索框，能否从静态 HTML 列出所有 CANN 安装文档的官方 URL？",
        "answer": "搜索框本身不提供可抓文档列表——结果由 JS 返回，对禁 JS 的抓取管道是黑盒（Mintlify、NVIDIA、昇腾三站搜索框实测皆抓不全）。要不靠搜索也能发现全部文档，须每篇文档有独立可爬 URL 并进 sitemap / llms 清单；搜索只是补充，不能当唯一发现层。",
        "insights": [
            ("搜索是黑盒", "结果 JS 返回，爬虫拿不到列表"),
            ("须 sitemap / llms", "全站文档 URL 的显式清单"),
            ("检索范围写正文", "别只放 placeholder / 交互文案"),
            ("搜索框可 exclude", "控件本身不入库，发现层靠 URL"),
        ],
        "root_cause": "搜索框是给人用的补充入口、对爬虫是黑盒；文档发现层若只靠搜索而缺少可爬 URL 与 sitemap / llms 清单，Agent 禁 JS 时就枚举不到全部文档",
        "subcauses": [
            (
                "搜索被当唯一发现层",
                "深页文档只在站内搜索后可达，静态 HTML 无导航或清单可枚举入口；搜索结果又由 JS 返回，禁 JS 抓取时既拿不到结果列表、也发现不到这些文档。",
                "每篇文档提供独立、稳定、可跟链的 URL，并进 sitemap.xml 与 llms.txt 全量清单；搜索仅作人用补充入口",
            ),
            (
                "缺 sitemap / llms 清单",
                "没有 sitemap.xml 或 llms.txt 时，爬虫只能顺导航一层层点，深页极易漏收；缺少「全站文档在哪」的显式清单，Agent 无法一次性枚举文档 URL。",
                "构建时自动生成 sitemap.xml 覆盖全部文档 URL 并在 robots 声明，同时维护 llms.txt / llms-full.txt；新增 / 下线文档同步更新",
            ),
            (
                "检索范围只在 placeholder",
                "「本站包含哪些文档 / 版本」等范围说明只写在搜索框 placeholder（如「搜索 CANN 文档」「mindie」）或交互提示里，静态正文无对应可引用说明。",
                "把文档索引与检索范围写进可引用正文或文档索引页，别只塞在 placeholder / 交互文案",
            ),
            (
                "搜索控件文案误入知识",
                "搜索框、建议下拉、「搜索 / Ask」按钮等纯交互文案若随正文入库，会产生噪声 chunk，并掩盖真正的发现层缺失。",
                "搜索控件标 data-llm-exclude 或入库剥离；发现层责任交给 URL + sitemap，不依赖搜索",
            ),
        ],
        "preview_url": HOME,
    },
    "oselect": {
        "title_short": "选择器选项可抓性",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "选择器选项可抓性",
        "definition": "若选项映射文档/版本，选项文本与对应页应可抓；纯表单选择则不必入库",
        "sample_url": FIRMWARE_DRIVERS,
        "sample_label": "固件与驱动",
        "desc_extra": "固件与驱动页含产品型号/架构/安装方式 Select 筛选",
        "prompt": f'我在看 <a href="{FIRMWARE_DRIVERS}" target="_blank" rel="noopener">固件与驱动</a>，产品型号 / 架构 / 安装方式等 Select 下拉里每个选项对应的官方下载页或带 <code>ids=</code> 的 URL 是什么？',
        "prompt_plain": f"我在看固件与驱动（{FIRMWARE_DRIVERS}），产品型号 / 架构 / 安装方式等 Select 下拉里每个选项对应的官方下载页或带 ids= 的 URL 是什么？",
        "answer": "固件与驱动页浏览器可见型号/架构/安装方式筛选与包列表，但静态 HTML 无完整 Select option 列表；当前组合靠 URL ?ids= 与 __NUXT_DATA__ 恢复，禁 JS 时无法列出全部选项。",
        "insights": [
            ("版本选型须可证伪", "option 须 SSR 或可映射 URL"),
            ("纯表单则剥离", "无 IA 的 select 宜 exclude"),
            ("option 文本要完整", "非 value/id 隐藏"),
        ],
        "root_cause": "固件与驱动页 Select 选项代表版本/架构筛选，但完整 option 列表未 SSR",
        "subcauses": [
            (
                "Select option 未进首包",
                "固件与驱动页浏览器可见产品型号/架构/安装方式等 Select，静态 HTML 无完整 option 文本；选中组合靠 ?ids= 与 __NUXT_DATA__ 恢复。",
                "关键 option SSR 进首包（可读 label + ids/URL）；或 llms 补 option→包表映射",
            ),
            (
                "选项无映射",
                "若 option 映射不同固件/驱动包，Agent 无法从首包证伪各选项对应包表。",
                "版本改链接或旁注表",
            ),
            (
                "value 不可读",
                "仅 ids 编码而无人类可读版本/架构 label 在首包。",
                "text 用人类可读型号/架构/安装方式",
            ),
        ],
        "preview_url": FIRMWARE_DRIVERS,
    },
    "odatepicker": {
        "title_short": "日期控件",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "日期控件",
        "definition": "DatePicker 为日期交互控件，非叙述内容；日程/版本日期说明应写在正文",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "日期控件，非内容知识",
        "prompt": "我在看昇腾社区相关页面（组件：DatePicker 日期选择器，暂无确认 DOM 样例 URL），datepicker 上默认显示的日期是不是产品发布日期规格？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：DatePicker 日期选择器，暂无确认 DOM 样例 URL），datepicker 上默认显示的日期是不是产品发布日期规格？",
        "answer": "日期选择器默认值只是 UI 态，不是产品发布规格。发布日期、支持周期应在文档正文。不需要亲和改造。",
        "insights": [
            ("控件非知识", "日期态无规格语义"),
            ("说明在正文", "非控件"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把日期 UI 默认值误读为规格事实",
        "subcauses": [
            ("发布日在控件", "不可抓", "写 release note 正文"),
            ("picker 进 chunk", "噪声", "过滤表单控件"),
            ("locale 格式", "混淆", "规格用 ISO 日期写在文档"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "otimepicker": {
        "title_short": "时间控件",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "时间控件",
        "definition": "TimePicker 为时间交互控件，非内容知识；时间规则应写在正文",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "时间控件，非内容知识",
        "prompt": "我在看昇腾社区相关页面（组件：TimePicker 时间选择器，暂无确认 DOM 样例 URL），所选时间是否代表官方维护窗口规格？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：TimePicker 时间选择器，暂无确认 DOM 样例 URL），所选时间是否代表官方维护窗口规格？",
        "answer": "时间选择器只是表单 UI，不代表维护窗口等规格。此类说明应在公告/文档正文。不需要亲和改造。",
        "insights": [
            ("控件非知识", "时间态无规格"),
            ("窗口说明在公告", "非 picker"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把时间表单态误读为运维规格",
        "subcauses": [
            ("维护窗在 picker", "不可靠", "写公告正文"),
            ("picker 进库", "噪声", "过滤控件 DOM"),
            ("时区未说明", "误解", "文档标明时区"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "otrees": {
        "title_short": "树形导航不可抓",
        "badge_class": "badge-bad",
        "badge_text": "目录须 SSR",
        "term": "树形导航不可抓",
        "definition": "树节点为文档导航时须链接+标题进 HTML；展开子级源码可读或可爬，否则手册结构丢失",
        "sample_url": FAQ,
        "sample_label": "Ascend FAQ 概览",
        "desc_extra": "文档侧栏树与 OMenu 同类；静态 HTML 几乎无 o-trees 可跟链",
        "prompt": f'我在看 <a href="{FAQ}" target="_blank" rel="noopener">Ascend FAQ 概览</a>，手册树里「产品与技术常见问题」下所有叶子文档的标题和 URL 是什么？',
        "prompt_plain": f"我在看 Ascend FAQ 概览（{FAQ}），手册树里「产品与技术常见问题」下所有叶子文档的标题和 URL 是什么？",
        "answer": "Mintlify 文档站左侧目录树在静态 HTML 直接 SSR 出成排 `<a href>`，NVIDIA cuQuantum 入门页侧栏同样可爬，我能顺着树枚举叶子文档。但昇腾 FAQ 概览的手册树几乎没有侧栏 `<a href>`，节点标题与 TOC 序列化在 `__NUXT_DATA__` 里、子级要点击才懒加载；探针问「产品与技术常见问题」下所有叶子文档的标题与 URL 时，我无法从首包枚举，与 OMenu / 侧栏 SSR 问题同类。",
        "insights": [
            ("友商目录树 SSR", "Mintlify 侧栏 / cuQuantum 侧栏可爬"),
            ("昇腾树在 __NUXT_DATA__", "侧栏首包无 a[href]"),
            ("懒加载断 RAG", "子级点击后才挂载"),
            ("md 平行目录兜底", "llms / 嵌套列表补 HTML 缺口"),
        ],
        "root_cause": "文档树是站点的发现层，节点须以「标题 + a[href]」进静态 HTML；昇腾侧手册树依赖客户端展开与 __NUXT_DATA__，静态管道看不到子节点链接，Agent 无法沿树枚举全部叶子文档",
        "subcauses": [
            (
                "懒加载子树只在点击后挂载",
                "手册树默认只渲染顶层节点，子级要点击父节点才由 JS 请求并挂载；禁 JS 或首包抓取时，「产品与技术常见问题」下的叶子文档根本不在 HTML 里，深页 URL 无法枚举。",
                "SSR 当前分支（至少展开到当前页所在路径）或一次性输出全树节点；子级不靠点击也在首包可读",
            ),
            (
                "节点是 span/click 而非 a[href]",
                "树节点用 span + onclick 跳转，没有真实 a[href]；爬虫只能看到一串无链接的标题文本，无法把标题映射到具体文档 URL。",
                "每个叶子节点输出真实 a[href]（展开图标可保留），标题与目标 URL 同在源码",
            ),
            (
                "整棵目录树序列化进 __NUXT_DATA__",
                "TOC 结构进 __NUXT_DATA__ / 客户端 store，静态 HTML 侧栏近乎空壳；抓取管道读不到层级，手册结构关系丢失。",
                "目录树 SSR 成真实 ul/li/a 嵌套列表，别只留客户端 hydrate 的空容器",
            ),
            (
                "缺 llms / MD 平行目录",
                "HTML 树无法完整 SSR 时又没有等价目录清单，Agent 只能在零散页面间迷路，无法确认某分类下有哪些文档。",
                "在 llms.txt / 文档 MD 维护一份「嵌套列表 = 全量目录 + URL」平行轨，与侧栏树一致",
            ),
        ],
        "preview_url": FAQ,
    },
    "oupload": {
        "title_short": "上传控件",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "上传控件",
        "definition": "上传为交互控件；文件格式/大小限制说明应写在旁注正文，控件本身无需亲和改造",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "上传交互；限制说明可进旁注正文",
        "prompt": "我在看昇腾社区相关页面（组件：OUpload 上传，暂无确认 DOM 样例 URL），上传区提示的文件大小限制是不是官方支持规格的唯一来源？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OUpload 上传，暂无确认 DOM 样例 URL），上传区提示的文件大小限制是不是官方支持规格的唯一来源？",
        "answer": "上传区提示只是 UI 文案。格式、大小、权限等限制应在可引用文档说明。OUpload 不需要亲和改造。",
        "insights": [
            ("控件非知识", "上传态无规格"),
            ("限制写文档", "非 dragger 文案"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把上传区提示当成唯一规格说明",
        "subcauses": [
            ("限制只在 UI", "易变", "写进文档/FAQ"),
            ("upload 进 chunk", "噪声", "过滤交互区"),
            ("错误仅 toast", "不可抓", "错误码写文档"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "orate": {
        "title_short": "评分与社会证明",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "评分与社会证明",
        "definition": "评分数字若作社会证明可抓；「我要评分」等操作文案入库可剥离",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；数字可抓，操作词宜剥离",
        "prompt": "我在看昇腾社区相关页面（组件：ORate 评分，暂无确认 DOM 样例 URL），当前文档的平均评分是多少？「我要评分」按钮文案是否代表官方质量认证？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：ORate 评分，暂无确认 DOM 样例 URL），当前文档的平均评分是多少？「我要评分」按钮文案是否代表官方质量认证？",
        "answer": "若评分数字在静态 HTML 中可见，我可以引用作社会证明。但「我要评分」是操作 CTA，不是质量规格；不应与官方认证混淆。",
        "insights": [
            ("分数可抓", "若 SSR 数字"),
            ("CTA 宜剥离", "非知识"),
            ("认证走正文", "非 rate 组件"),
        ],
        "root_cause": "混淆用户评分 UI 与官方质量规格",
        "subcauses": [
            ("分数 JS 拉", "首包无", "关键分数 SSR 或剥离"),
            ("CTA 进库", "噪声", "过滤操作文案"),
            ("与认证混用", "误导", "认证说明独立文档"),
        ],
        "preview_url": None,
    },
    "ocascader": {
        "title_short": "级联选项与路径",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "级联选项与路径",
        "definition": "级联若选文档路径/地域内容，各级选项文本应可抓；纯地址表单则不必入库",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；视是否映射内容路径",
        "prompt": "我在看昇腾社区相关页面（组件：OCascader 级联选择，暂无确认 DOM 样例 URL），级联每一级的选项是否对应可访问的官方内容 URL？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OCascader 级联选择，暂无确认 DOM 样例 URL），级联每一级的选项是否对应可访问的官方内容 URL？",
        "answer": "若无样例无法实测。若级联只是地址/表单字段，不必当知识；若代表文档分类路径，各级选项文本须在源码可读且最好有落地链。",
        "insights": [
            ("路径选型须可读", "各级 option 文本"),
            ("表单则剥离", "非 IA"),
            ("面板勿悬停才见", "级联菜单 SSR"),
        ],
        "root_cause": "级联组件未区分「内容路径导航」与「纯表单字段」",
        "subcauses": [
            ("选项 JS 级联", "首包空", "SSR 首两级或全量"),
            ("无 URL 映射", "却承载 IA", "分类改链接"),
            ("仅 value id", "不可读", "text 人类可读"),
        ],
        "preview_url": None,
    },
    "oslider": {
        "title_short": "滑动条",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "滑动条",
        "definition": "数值滑条为交互控件，非叙述内容；阈值/范围说明应写在正文",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "数值滑条，非叙述内容",
        "prompt": "我在看昇腾社区相关页面（组件：OSlider 滑动条，暂无确认 DOM 样例 URL），滑块当前值是不是官方推荐的性能参数默认值？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OSlider 滑动条，暂无确认 DOM 样例 URL），滑块当前值是不是官方推荐的性能参数默认值？",
        "answer": "滑块当前值只是 UI 态，不是官方推荐默认值。性能参数规格应在文档表格/正文说明。不需要亲和改造。",
        "insights": [
            ("值非规格", "动态 UI 态"),
            ("范围写文档", "非 slider"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把滑块当前值误读为官方默认规格",
        "subcauses": [
            ("默认在 slider", "不可抓", "写参数表"),
            ("slider 进库", "噪声", "过滤控件"),
            ("min/max 无文本", "不可读", "范围写旁注"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "odivider": {
        "title_short": "分割线",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "分割线",
        "definition": "ODivider 为视觉分隔，对 RAG 无语义；md 用 --- 即可，无需 HTML 亲和改造",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "视觉分隔；md 用 --- 即可",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，页面上的分割线是章节边界吗？分割线上下各是什么主题的官方规格段落？',
        "prompt_plain": f"我在看社区首页（{HOME}），页面上的分割线是章节边界吗？分割线上下各是什么主题的官方规格段落？",
        "answer": "分割线只是视觉分隔，不携带章节语义。章节边界应靠 heading 标题表达。ODivider 不需要亲和改造。",
        "insights": [
            ("纯视觉", "无知识语义"),
            ("章节靠标题", "非 divider"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "误把装饰性分隔当成结构语义",
        "subcauses": [
            ("用线代替标题", "结构不清", "补 h2/h3"),
            ("divider 进 chunk", "噪声", "可忽略"),
            ("md 用 ---", "足够", "不必特殊 HTML"),
        ],
        "preview_url": HOME,
        "no_aff": True,
    },
    "otag": {
        "title_short": "标签语义",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "标签语义",
        "definition": "标签若有版本/状态等语义，建议进 HTML 文本；装饰性标签可忽略",
        "sample_url": DEVELOPER,
        "sample_label": "开发者中心",
        "desc_extra": "开发者中心等列表卡片常含版本/状态标签",
        "prompt": f'我在看 <a href="{DEVELOPER}" target="_blank" rel="noopener">开发者中心</a>，卡片上「新版本 / 热门」等标签分别对应什么官方定义？请引用正文依据。',
        "prompt_plain": f"我在看开发者中心（{DEVELOPER}），卡片上「新版本 / 热门」等标签分别对应什么官方定义？请引用正文依据。",
        "answer": "若标签文本在 HTML 中可见，我可以复述。但「热门」等营销标签未必有规格定义；版本类标签应有文档依据，否则不宜当事实入库。",
        "insights": [
            ("语义标签可抓", "版本/状态"),
            ("装饰标签剥离", "热门/新品口号"),
            ("定义在正文", "非 tag  alone"),
        ],
        "root_cause": "装饰性标签与规格型标签未区分，易当事实入库",
        "subcauses": [
            ("口号 tag 进库", "噪声", "策展剥离营销 tag"),
            ("版本 tag 无定义", "误读", "版本说明写正文"),
            ("仅颜色区分", "文本缺失", "tag 内可读文字"),
        ],
        "preview_url": DEVELOPER,
    },
    "obadge": {
        "title_short": "徽标角标",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "徽标角标",
        "definition": "未读角标/数字徽标对知识抓取无价值；通知类信息不应是规格唯一来源",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "未读角标对知识抓取无价值",
        "prompt": "我在看昇腾社区相关页面（组件：OBadge 徽标，暂无确认 DOM 样例 URL），导航上的红色数字 3 代表什么官方公告或规格更新？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OBadge 徽标，暂无确认 DOM 样例 URL），导航上的红色数字 3 代表什么官方公告或规格更新？",
        "answer": "角标数字通常是未读计数等瞬时 UI 态，不是产品规格。重要公告应在可引用页面说明。OBadge 不需要亲和改造。",
        "insights": [
            ("瞬时态", "非知识"),
            ("公告走正文", "非 badge"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把通知角标误读为规格变更信号",
        "subcauses": [
            ("计数进 chunk", "噪声", "过滤 badge 数字"),
            ("公告仅 badge", "不可抓", "公告页 SSR"),
            ("动态变化", "chunk 过期", "勿当稳定事实"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "odialog": {
        "title_short": "对话框隐藏说明",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "对话框隐藏说明",
        "definition": "对话框若含安装步骤等关键说明，须在源码可读或同步到正文页；纯确认框不必入库",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；关键说明勿只放弹层",
        "prompt": "我在看昇腾社区相关页面（组件：ODialog 对话框，暂无确认 DOM 样例 URL），不点击「安装指引」按钮，能否从静态 HTML 读到弹层里的完整安装步骤？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：ODialog 对话框，暂无确认 DOM 样例 URL），不点击「安装指引」按钮，能否从静态 HTML 读到弹层里的完整安装步骤？",
        "answer": "若安装步骤只在 dialog 且默认 hidden/未 SSR，禁 JS 抓取读不到。关键说明必须在正文页 duplicated 或 dialog 内容进首包。",
        "insights": [
            ("关键说明勿仅弹层", "与折叠同类"),
            ("确认框可忽略", "非知识"),
            ("打开态非必须", "DOM 须存在"),
        ],
        "root_cause": "把唯一规格说明放在默认不可见的对话框中",
        "subcauses": [
            ("dialog 未 SSR", "首包无", "步骤同步正文或 SSR dialog"),
            ("aria-hidden 删文本", "抓取空", "保留 DOM 文本"),
            ("纯确认框进库", "噪声", "过滤 noop dialog"),
        ],
        "preview_url": None,
    },
    "ocard": {
        "title_short": "卡片摘要不可抓",
        "badge_class": "badge-should",
        "badge_text": "宜全量文本",
        "term": "卡片摘要不可抓",
        "definition": "卡片标题、摘要、链接须写入 HTML；图需 alt/图注，否则列表发现层不完整",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页课程/活动等多为卡片列表",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，「最新课程 / 社区活动」卡片各自的标题、摘要和落地页 URL 是什么？',
        "prompt_plain": f"我在看社区首页（{HOME}），「最新课程 / 社区活动」卡片各自的标题、摘要和落地页 URL 是什么？",
        "answer": "开发者页「获取开发资源」底部三卡（HiDevLab / 资源下载中心 / 昇腾镜像仓库）在静态 HTML 中各有 o-card-title 与 o-card-detail，我能列表回答。但社区首页「最新发布 / 精彩活动」等 Tab 下的课程/资讯卡，以及开发者页「精品推荐」「参与互动交流」卡内嵌列表，浏览器可见、源码里 o-scroller-container / o-card-content 为空——须等脚本注入，禁 JS 时列不出标题、摘要与 URL。",
        "insights": [
            ("资源三卡可抓", "开发者页 HiDevLab 等 title+detail+href 在首包"),
            ("首页列表靠注入", "资讯 Tab 下内容卡 o-scroller-container 空"),
            ("卡内列表空壳", "精品推荐/互动交流 o-card-content 无列表项"),
            ("三要素须齐", "标题+摘要+href 缺一即残缺"),
        ],
        "root_cause": "OCard 导流卡在同一站点实现不一：部分楼层已 SSR 标题 + 摘要 + 链接，但首页资讯/活动列表与卡内嵌套列表仍靠脚本注入或绑在封面图上，未平铺为可引用文本链",
        "subcauses": [
            (
                "卡内列表未写进网页源码",
                "社区首页「最新发布 / 产业资讯 / 精彩活动 / 官方技术文章」Tab 下浏览器可见金融/SWA/CANN 等内容卡，但 pane 内 o-scroller-container 为空；开发者页「精品推荐」「参与互动交流」各卡内课程/帖子列表亦靠注入，o-card-content 为 <!--[--><!--]-->。探针问「最新课程 / 社区活动卡片标题、摘要、URL」时首包列不出。",
                "默认 Tab 与卡内列表项 SSR 进 HTML（o-card-title + o-card-detail + a[href]），不必点击或滑动才加载",
            ),
            (
                "封面图替代 card 文本",
                "部分课程/活动/权益卡只有封面图或 icon，源码无 o-card-title / o-card-detail，图意无法转写为可检索 chunk。",
                "卡片三要素平铺为文本：标题 + 一句话摘要 + 链接；封面补 alt 或 figcaption",
            ),
            (
                "整卡绑点击无 href",
                "发现卡若用 div 或整卡 onclick 跳转，静态 HTML 无 a[href]，Agent 能复述标题但给不出落地页 URL。",
                "跳转型卡片用 a[href] 包裹标题与摘要，样式可保留卡片外观",
            ),
            (
                "入口卡缺摘要",
                "开发者页训练/推理/算子三卡仅有 resource-card-title + href、无独立短述；虽可跟链，但 RAG 缺可引用摘要句，与 HiDevLab 三卡（title + detail + href 齐全）写法不一致。",
                "每张导流卡补齐 o-card-detail 短述；外链卡输出完整 href",
            ),
        ],
        "preview_url": HOME,
    },
    "odatetable": {
        "title_short": "表格语义缺失",
        "badge_class": "badge-bad",
        "badge_text": "忌截图表",
        "term": "表格语义缺失",
        "definition": "规格表须用真实 table/单元格文本，勿截图；表头语义清晰，md 用 Markdown 表",
        "sample_url": CLUSTER,
        "sample_label": "集群产品页",
        "desc_extra": "集群页等含硬件参数表",
        "prompt": f'我在看 <a href="{CLUSTER}" target="_blank" rel="noopener">集群产品页</a>，Atlas 900 与 Atlas 800 的 CPU/内存/互联参数对照表原文是什么？请按表头列给出。',
        "prompt_plain": f"我在看集群产品页（{CLUSTER}），Atlas 900 与 Atlas 800 的 CPU/内存/互联参数对照表原文是什么？请按表头列给出。",
        "answer": "Ascend FAQ「表1 昇腾产品系列」与 NVIDIA CUDA Linux 安装指南 Table 1–4、Mintlify Custom portal Features 表均在静态 HTML 中有 th/td，我能按行列回答。但集群产品页探针问「Atlas 900 与 Atlas 800 CPU/内存/互联对照」时，部分规格绑在特性配图内、摘要表存在空 td，或型号 Tab 切换后才注入，无法可靠还原完整参数矩阵。",
        "insights": [
            ("友商文档表可抓", "Mintlify Features / CUDA Table 1–4 / FAQ 表1"),
            ("集群摘要表空壳", "spec-summary 部分 td 空"),
            ("特性绑配图", "cluster 特性卡文字在 PNG 内"),
            ("md 平行表", "HTML 表不全时 MD 补"),
        ],
        "root_cause": "规格参数须以语义化 table/th/td 交付；文档页与 FAQ 已达标，但产品页仍存在截图规格、空单元格或 Tab 后注入，Agent 无法按表头逐格问答",
        "subcauses": [
            (
                "参数图代替 table",
                "集群产品页「产品特性」等区块浏览器可见六格能力说明，但文案在 feature PNG 图内，静态 HTML 无 th/td 参数矩阵；探针问「Atlas 900 与 Atlas 800 CPU/内存/互联对照表原文」时，图表格无法当可检索 chunk。",
                "硬件规格改 HTML table 或 Markdown 表（th 列型号、td 列 CPU/内存/互联）；配图仅装饰时 alt=\"\" 并正文复述参数",
            ),
            (
                "规格表单元格空壳",
                "集群页「技术规格摘要」虽有 table 骨架，但部分 td/p 为空或靠客户端填充；探针问「Atlas 900 vs 800 CPU/内存/互联对照」时首包读不出完整规格值矩阵。",
                "每个规格行 SSR 可读 label + 值；禁留空 td 占位等待脚本注入",
            ),
            (
                "div/grid 伪表",
                "产品对比若用 div+flex 网格排版而无 th/td，抓取管道无法识别表头与单元格边界，RAG 列错位或丢列。",
                "对照表一律用语义 table + thead/tbody；合并单元格须保持列对齐并写 scope",
            ),
            (
                "缺 MD 平行表",
                "HTML 表不完整时（如仅 meta/og 描述含表1 片段），Agent 只能靠零散文本猜测；应在文档 MD/llms 同步输出完整 Markdown 表。",
                "每个规格表在 MD 镜像一份「表头 + 全行单元格」；与 HTML table 文案一致",
            ),
        ],
        "preview_url": CLUSTER,
    },
    "oprogress": {
        "title_short": "进度条",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "进度条",
        "definition": "进度条展示任务进度，非知识正文；完成条件应在文档说明",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "进度展示，非知识正文",
        "prompt": "我在看昇腾社区相关页面（组件：OProgress 进度条，暂无确认 DOM 样例 URL），进度 60% 是否表示官方定义的安装完成标准？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OProgress 进度条，暂无确认 DOM 样例 URL），进度 60% 是否表示官方定义的安装完成标准？",
        "answer": "进度百分比只是 UI 反馈，不是安装完成规格。完成标准应在安装文档步骤说明。不需要亲和改造。",
        "insights": [
            ("进度非规格", "瞬时态"),
            ("标准在文档", "非 progress"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把 UI 进度态误读为完成规格",
        "subcauses": [
            ("完成标准在 bar", "不可抓", "写进步骤文档"),
            ("progress 进库", "噪声", "过滤"),
            ("无文字说明", "仅百分比", "步骤正文补全"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "omessage": {
        "title_short": "消息提示",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "消息提示",
        "definition": "OMessage 为瞬时反馈；重要错误/告警说明应落到正文或文档页",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "瞬时反馈；重要说明应落到文档页",
        "prompt": "我在看昇腾社区相关页面（组件：OMessage 消息提示，暂无确认 DOM 样例 URL），页面顶部红条错误码 ERR-001 的完整官方解释在哪里？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OMessage 消息提示，暂无确认 DOM 样例 URL），页面顶部红条错误码 ERR-001 的完整官方解释在哪里？",
        "answer": "若错误说明只在瞬时 message 条且非常驻 HTML，抓取管道可能错过。错误码完整说明应在 FAQ/文档页。OMessage 本身不需要亲和改造。",
        "insights": [
            ("瞬时非唯一源", "重要说明须常驻"),
            ("错误码写 FAQ", "非 message"),
            ("结论：不需要", "组件无需改造"),
        ],
        "root_cause": "把瞬时 message 当成错误规格唯一交付面",
        "subcauses": [
            ("错误仅 toast/message", "不可抓", "FAQ 常驻说明"),
            ("message 进 chunk", "过期噪声", "过滤瞬时节点"),
            ("码无文档链", "Agent 瞎猜", "链到错误码表"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "otoast": {
        "title_short": "轻提示",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "轻提示",
        "definition": "OToast 为轻量瞬时提示，勿承载唯一说明；成功/失败语义应在正文可追溯",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "轻提示瞬时，勿承载唯一说明",
        "prompt": "我在看昇腾社区相关页面（组件：OToast 轻提示，暂无确认 DOM 样例 URL），刚才弹出的「复制成功」是否意味着许可证已按官方规范激活？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OToast 轻提示，暂无确认 DOM 样例 URL），刚才弹出的「复制成功」是否意味着许可证已按官方规范激活？",
        "answer": "Toast 只是操作反馈，不包含许可证等业务规格。激活规则应在文档说明。OToast 不需要亲和改造。",
        "insights": [
            ("反馈非规格", "瞬时文案"),
            ("规则在文档", "非 toast"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "把操作反馈 toast 误读为业务规格确认",
        "subcauses": [
            ("唯一说明在 toast", "不可抓", "写进文档"),
            ("toast 进库", "噪声", "过滤"),
            ("成功态误导", "非规格", "正文定义成功条件"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
    "opopover": {
        "title_short": "气泡隐藏说明",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "气泡隐藏说明",
        "definition": "重要说明勿只放悬停/点击气泡；须在页面正文也有一份，否则禁 JS 抓取不到",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页等或有 tooltip/popover 补充说明",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，不悬停问号图标，能否从静态 HTML 读到「CANN 版本」字段的完整官方定义？',
        "prompt_plain": f"我在看社区首页（{HOME}），不悬停问号图标，能否从静态 HTML 读到「CANN 版本」字段的完整官方定义？",
        "answer": "若定义只在 popover/tooltip 且默认不在 DOM 或未 SSR，我无法读取。重要字段定义必须在正文重复或 popover 内容进首包。",
        "insights": [
            ("悬停层不可抓", "与 dropdown 同类"),
            ("正文须 duplicate", "规格双写"),
            ("装饰 tooltip 可忽略", "非关键"),
        ],
        "root_cause": "把字段规格唯一放在悬停气泡中",
        "subcauses": [
            ("popover 未 SSR", "首包无", "正文同步定义"),
            ("aria-hidden 删", "文本丢失", "保留 DOM"),
            ("关键项靠 icon", "无文本", "旁注段落说明"),
        ],
        "preview_url": HOME,
    },
    "oloading": {
        "title_short": "加载态",
        "badge_class": "badge-ok",
        "badge_text": "不需要亲和",
        "term": "加载态",
        "definition": "OLoading 表示内容加载中，与正文亲和无关；正文应在加载完成后 SSR 或可抓",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "加载态，与内容亲和无关",
        "prompt": "我在看昇腾社区相关页面（组件：OLoading 加载，暂无确认 DOM 样例 URL），loading 动画消失后才会显示的正文，在静态 HTML 里是否存在？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OLoading 加载，暂无确认 DOM 样例 URL），loading 动画消失后才会显示的正文，在静态 HTML 里是否存在？",
        "answer": "loading 组件本身无知识语义。关键问题是正文是否 SSR：若正文等 JS 才注入，与 loading 无关，是交付策略问题。OLoading 不需要亲和改造。",
        "insights": [
            ("loading 非内容", "纯状态"),
            ("看 SSR", "非 spinner"),
            ("结论：不需要", "清单一致"),
        ],
        "root_cause": "混淆加载态组件与正文 SSR 交付问题",
        "subcauses": [
            ("正文 client-only", "误怪 loading", "改 SSR 正文"),
            ("loading 进 chunk", "噪声", "过滤"),
            ("骨架屏无限", "正文永不 SSR", "首包出文本"),
        ],
        "preview_url": None,
        "no_aff": True,
    },
}

NO_AFF_SLUGS = frozenset(slug for slug, probe in PROBES.items() if probe.get("no_aff"))

SKIP_CONTENT = {"ocarousel"}  # preserve hand-written page

PEER_SITES = [
    ("Mintlify", "citability-html-mintlify.html", "citability-html-mintlify-case.html", DOCS / "assets/cases-html/cases-data.json"),
    ("NVIDIA", "citability-html-nvidia.html", "citability-html-nvidia-case.html", DOCS / "assets/cases-html-nvidia/cases-data.json"),
    ("昇腾社区", "citability-html-ascend.html", "citability-html-ascend-case.html", DOCS / "assets/cases-html-ascend/cases-data.json"),
]

# 友商测试：每组件三站对照 (peer_label, case_key, floor_id)
PEER_COMPONENT_MAP: dict[str, list[tuple[str, str, str]]] = {
    "ocarousel": [
        ("Mintlify", "home", "carousel-slides"),
        ("NVIDIA", "home", "carousel-slides"),
        ("昇腾社区", "home", "banner-slides"),
    ],
    "omenu": [
        ("Mintlify", "docs-editor", "sidebar-nav"),
        ("NVIDIA", "cuquantum-getting-started", "sidebar-nav"),
        ("昇腾社区", "faq", "sidebar-nav"),
    ],
    "otab": [
        ("Mintlify", "docs-tabs", "tabs-demo"),
        ("NVIDIA", "partners", "types"),
        ("昇腾社区", "download", "edition-note"),
    ],
    "obreadcrumb": [
        ("NVIDIA", "cuquantum-release-notes", "breadcrumb-nav"),
        ("昇腾社区", "faq", "doc-breadcrumb"),
    ],
    "oanchor": [
        ("Mintlify", "docs-editor", "page-anchor-nav"),
        ("NVIDIA", "cuquantum-getting-started", "page-anchor-nav"),
        ("昇腾社区", "cann-aolapi-intro", "doc-anchor-nav"),
    ],
    "opagination": [
        ("Mintlify", "blog", "list"),
        ("NVIDIA", "news", "list"),
        ("昇腾社区", "edu", "success-cases"),
    ],
    "ostep": [
        ("Mintlify", "quickstart", "web-editor-steps"),
        ("昇腾社区", "developer", "devplan"),
    ],
    "onavigation": [
        ("Mintlify", "docs", "top-nav"),
        ("昇腾社区", "home", "top-nav"),
    ],
    "ofooternav": [
        ("Mintlify", "home", "footer-nav"),
        ("NVIDIA", "home", "footer-nav"),
        ("昇腾社区", "home", "footer-nav"),
    ],
    "obutton": [
        ("Mintlify", "home", "hero-cta"),
        ("NVIDIA", "build", "list-cta"),
        ("昇腾社区", "home", "banner-cta"),
    ],
    "olink": [
        ("Mintlify", "docs-editor", "related-topics"),
        ("NVIDIA", "home", "topics-links"),
        ("昇腾社区", "training-dev", "journey-matrix-links"),
    ],
    "odropdown": [
        ("Mintlify", "pricing", "products-nav-dropdown"),
        ("NVIDIA", "devzone", "resources-nav-dropdown"),
        ("昇腾社区", "cluster", "more-products-dropdown"),
    ],
    "oradio": [
        ("Mintlify", "pricing", "plans"),
        ("NVIDIA", "partners", "types"),
        ("昇腾社区", "cluster", "product-intro"),
    ],
    "ocheckbox": [
        ("Mintlify", "pricing", "matrix"),
        ("NVIDIA", "partners", "specializations"),
        ("昇腾社区", "firmware-drivers", "version-matrix"),
    ],
    "oswitch": [
        ("Mintlify", "home", "platform"),
        ("NVIDIA", "home", "recommend"),
        ("昇腾社区", "home", "marketplace"),
    ],
    "oscrollbar": [
        ("Mintlify", "home", "carousel-slides"),
        ("NVIDIA", "automotive", "partners"),
        ("昇腾社区", "home", "news-tabs"),
    ],
    "otoggle": [
        ("NVIDIA", "cuda-downloads", "os-arch-toggle"),
        ("昇腾社区", "firmware-drivers", "version-matrix"),
    ],
    "oinput": [
        ("Mintlify", "home", "hero-copy"),
        ("NVIDIA", "automotive", "getstarted"),
        ("昇腾社区", "download", "hero"),
    ],
    "otextarea": [
        ("Mintlify", "docs-editor", "body"),
        ("NVIDIA", "build", "hero"),
        ("昇腾社区", "faq", "doc-body"),
    ],
    # osearch 的友商对照走 PEER_ROW_OVERRIDES 内联行（三站搜索框未作为 citability 楼层捕获）。
    "oselect": [
        ("Mintlify", "pricing", "plans"),
        ("NVIDIA", "partners", "types"),
        ("昇腾社区", "firmware-drivers", "version-matrix"),
    ],
    "odatepicker": [
        ("Mintlify", "blog", "list"),
        ("NVIDIA", "events", "calendar"),
        ("昇腾社区", "edu", "success-cases"),
    ],
    "otimepicker": [
        ("Mintlify", "blog", "list"),
        ("NVIDIA", "events", "calendar"),
        ("昇腾社区", "developer", "devplan"),
    ],
    "otrees": [
        ("Mintlify", "docs-editor", "sidebar-nav"),
        ("NVIDIA", "cuquantum-getting-started", "sidebar-nav"),
        ("昇腾社区", "faq", "sidebar-nav"),
    ],
    "oupload": [
        ("Mintlify", "docs-editor", "layout-img"),
        ("NVIDIA", "build", "promos"),
        ("昇腾社区", "download", "software-cards"),
    ],
    "orate": [
        ("Mintlify", "home", "testimonials"),
        ("NVIDIA", "automotive", "quotes"),
        ("昇腾社区", "edu", "success-cases"),
    ],
    "ocascader": [
        ("Mintlify", "docs-editor", "sidebar-nav"),
        ("NVIDIA", "industries", "grid"),
        ("昇腾社区", "cluster", "scenarios"),
    ],
    "oslider": [
        ("Mintlify", "home", "stats"),
        ("NVIDIA", "home", "carousel-slides"),
        ("昇腾社区", "edu", "banner-slides"),
    ],
    "odivider": [
        ("Mintlify", "pricing", "matrix"),
        ("NVIDIA", "dgx-cloud", "overview"),
        ("昇腾社区", "ccae", "banner-title"),
    ],
    "otag": [
        ("Mintlify", "home", "updates"),
        ("NVIDIA", "partners", "types"),
        ("昇腾社区", "cluster", "scenarios"),
    ],
    "obadge": [
        ("Mintlify", "home", "hero-traffic-num"),
        ("NVIDIA", "home", "gtc"),
        ("昇腾社区", "ccae", "banner-title"),
    ],
    "odialog": [
        ("Mintlify", "pricing", "faq"),
        ("NVIDIA", "partners", "competencies"),
        ("昇腾社区", "faq", "doc-body"),
    ],
    "ocard": [
        ("Mintlify", "home", "companies"),
        ("NVIDIA", "dgx-cloud", "usecases"),
        ("昇腾社区", "developer", "dev-resource-cards"),
    ],
    "odatetable": [
        ("Mintlify", "custom-portal", "features-table"),
        ("NVIDIA", "cuda-installation-guide-linux", "os-compiler-tables"),
        ("昇腾社区", "faq", "product-table"),
    ],
    "oprogress": [
        ("Mintlify", "home", "stats"),
        ("NVIDIA", "home", "carousel-slides"),
        ("昇腾社区", "developer", "devplan"),
    ],
    "omessage": [
        ("Mintlify", "docs-editor", "tip"),
        ("NVIDIA", "automotive", "getstarted"),
        ("昇腾社区", "developer", "support-help"),
    ],
    "otoast": [
        ("Mintlify", "docs-editor", "tip"),
        ("NVIDIA", "dgx-cloud", "apps"),
        ("昇腾社区", "developer", "support-help"),
    ],
    "opopover": [
        ("Mintlify", "docs-editor", "tip"),
        ("NVIDIA", "dgx-cloud", "overview"),
        ("昇腾社区", "developer", "support-help"),
    ],
    "oloading": [
        ("Mintlify", "pricing", "faq"),
        ("NVIDIA", "home", "recommend"),
        ("昇腾社区", "home", "news-tabs"),
    ],
}

# 内联友商对照行：用于三站均未把该组件作为可捕获 citability 楼层的情况（如搜索框）。
# 每行 (peer_label, case_key) 借用已有案例取 URL/案例名；object/badge/grab/tag_cls/reason 直接给定。
PEER_ROW_OVERRIDES: dict[str, list[dict]] = {
    "osearch": [
        {
            "peer_label": "Mintlify", "case_key": "docs",
            "object": "站内搜索（Cmd+K / Ask Assistant）", "badge": "搜索 / 问答",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "搜索框为「Search or ask a question」+ Ask Assistant，纯前端交互、无静态可爬入口，结果由 JS 返回；只看搜索发现不到文档，须由 sitemap.xml、llms.txt / llms-full.txt 兜底。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "build",
            "object": "搜索框 + Shortcuts", "badge": "搜索 / 快捷入口",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "搜索框（Search for models, blueprints…）与 Shortcuts（Models / Blueprints / Skills）均由客户端渲染、结果靠 JS 返回，静态 HTML 无搜索产出；只看搜索本身发现不到内容。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "developer",
            "object": "顶栏搜索框（mindie）", "badge": "搜索",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "顶栏搜索框（mindie 占位）为纯前端交互、结果靠 JS 返回，静态 HTML 无搜索产出；只看搜索发现不到文档。",
        },
    ],
}

PEER_KEYWORDS: dict[str, list[str]] = {
    "omenu": ["侧栏", "目录", "Related topics", "导航", "页脚链接", "页脚导航"],
    "otab": ["Tab", "标签", "页签", "折叠", "收起", "多 Tab"],
    "obreadcrumb": ["面包屑", "路径"],
    "oanchor": ["Related", "锚点", "锚"],
    "opagination": ["分页", "页码", "列表无正文"],
    "ostep": ["步骤", "日程"],
    "onavigation": ["导航", "入口", "Explore", "Quick Links", "导流", "链接可跟", "帮助入口", "帮助"],
    "ofooternav": ["页脚", "footer", "订阅", "Get Started 联系", "页脚转化", "页脚按钮"],
    "obutton": ["按钮", "CTA", "Get started", "Sign up", "页脚按钮", "列表底部按钮"],
    "olink": ["链接", "相关链接", "列表链接", "入口链接", "卡片链接", "href"],
    "odropdown": ["下拉", "dropdown", "navigation-menu", "mega", "折叠答文", "折叠面板", "折叠标题", "折叠"],
    "oradio": ["单选"],
    "ocheckbox": ["多选"],
    "oswitch": ["开关"],
    "oscrollbar": ["滚动"],
    "otoggle": ["选择块", "筛选", "动态筛选"],
    "oinput": ["输入"],
    "otextarea": ["多行"],
    "osearch": ["搜索"],
    "oselect": ["选择器", "筛选"],
    "odatepicker": ["日期"],
    "otimepicker": ["时间"],
    "otrees": ["侧栏", "目录", "树", "TOC"],
    "oupload": ["上传"],
    "orate": ["证言", "评分"],
    "ocascader": ["级联"],
    "oslider": ["滑动"],
    "odivider": ["分割线"],
    "otag": ["标签", "场景标签", "场景导流"],
    "obadge": ["徽标", "角标"],
    "ocarousel": ["轮播", "多帧", "Banner", "头条", "幻灯"],
    "odialog": ["FAQ", "对话框", "折叠答文"],
    "ocard": ["卡", "网格", "Logo", "公司", "客户", "案例", "博客", "精选", "套餐", "方案", "场景", "产品", "模型", "应用", "列表", "推广", "证言", "入口", "下载", "资源"],
    "odatetable": ["表", "矩阵", "Leaderboard", "榜单", "规格", "对照", "参数"],
    "oprogress": ["进度"],
    "omessage": ["消息"],
    "otoast": ["轻提示", "提示"],
    "opopover": ["提示说明", "提示正文", "提示", "气泡"],
    "oloading": ["加载", "客户端渲染", "注入", "缺少静态", "动态"],
}

_PEER_CASES: list[tuple[str, str, str, str, str, str, dict]] | None = None
_PEER_CASE_INDEX: dict[tuple[str, str], dict] | None = None


def _load_peer_case_index() -> dict[tuple[str, str], dict]:
    global _PEER_CASE_INDEX
    if _PEER_CASE_INDEX is not None:
        return _PEER_CASE_INDEX
    index: dict[tuple[str, str], dict] = {}
    for peer_label, _index, _case_page, json_path in PEER_SITES:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for case_key, case in data.items():
            index[(peer_label, case_key)] = case
    _PEER_CASE_INDEX = index
    return index


def _find_peer_floor(peer_label: str, case_key: str, floor_id: str) -> dict | None:
    case = _load_peer_case_index().get((peer_label, case_key))
    if not case:
        return None
    for floor in case.get("floors", []):
        if floor.get("id") == floor_id:
            return floor
    return None


def _load_peer_cases() -> list[tuple[str, str, str, str, str, str, dict]]:
    global _PEER_CASES
    if _PEER_CASES is not None:
        return _PEER_CASES
    out: list[tuple[str, str, str, str, str, str, dict]] = []
    for peer_label, _index, case_page, json_path in PEER_SITES:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for case_key, case in data.items():
            title = (case.get("title") or case_key).split("·")[0].split("/")[0].strip()
            case_url = case.get("leftUrl") or case.get("rightUrl") or ""
            case_name = case.get("pageName") or case.get("leftLabel") or title
            for floor in case.get("floors", []):
                out.append((peer_label, case_page, case_key, title, case_url, case_name, floor))
    _PEER_CASES = out
    return out


def _floor_reason(floor: dict) -> str:
    if floor.get("peerReason"):
        return html.escape(floor["peerReason"].replace("\n", " ").strip())
    desc = (floor.get("desc") or "").replace("\n", " ")
    m = re.search(r"问题点：(.+?)(?:判断：|$)", desc)
    if m:
        return html.escape(m.group(1).strip())
    if floor.get("kind") == "in" and desc:
        return html.escape(desc.split("。")[0].strip() + "。")
    name = floor.get("name") or "—"
    return html.escape(f"{name}（详见 citability 案例页）")


def _floor_html_grab(floor: dict) -> tuple[str, str]:
    """html 可抓取：仅判静态 HTML 能否抓全侧栏导航，不含「可不解决」修复语义。"""
    if floor.get("kind") == "in":
        return "可抓全", "peer-tag-ok"
    if floor.get("kind") == "warn":
        return "抓不全", "peer-tag-partial"
    return "—", "peer-tag-warn-ok"


def _floor_verdict(floor: dict) -> tuple[str, str]:
    if floor.get("kind") == "in":
        return "完整", "peer-tag-ok"
    if floor.get("kind") == "warn":
        if floor.get("fixNeeded", True):
            return "部分", "peer-tag-partial"
        return "可不解决", "peer-tag-warn-ok"
    return "—", "peer-tag-warn-ok"


def _floor_matches(slug: str, floor: dict) -> bool:
    kws = PEER_KEYWORDS.get(slug, [])
    if not kws:
        return False
    blob = f"{floor.get('name', '')} {floor.get('badge', '')}"
    return any(kw in blob for kw in kws)


def _floor_match_score(slug: str, floor: dict) -> int:
    kws = PEER_KEYWORDS.get(slug, [])
    blob = f"{floor.get('name', '')} {floor.get('badge', '')}"
    score = sum(2 for kw in kws if kw in blob)
    if floor.get("kind") in ("in", "warn"):
        score += 1
    if floor.get("peerReason"):
        score += 1
    return score


def _peer_entries_for_slug(slug: str) -> list[tuple[str, str, str]]:
    if slug in PEER_COMPONENT_MAP:
        return PEER_COMPONENT_MAP[slug]
    by_peer: dict[str, tuple[str, str, str, int]] = {}
    for peer_label, case_key, _title, _url, _name, floor in _load_peer_cases():
        if not _floor_matches(slug, floor):
            continue
        score = _floor_match_score(slug, floor)
        prev = by_peer.get(peer_label)
        if prev is None or score > prev[3]:
            by_peer[peer_label] = (case_key, floor["id"], peer_label, score)
    order = [label for label, *_ in PEER_SITES]
    return [(label, by_peer[label][0], by_peer[label][1]) for label in order if label in by_peer]


def _floor_object_label(floor: dict) -> str:
    name = html.escape(floor.get("name") or "被测对象")
    badge = floor.get("badge") or ""
    if badge:
        return (
            f'<span class="peer-object-name">{name}</span>'
            f'<span class="peer-floor-badge">{html.escape(badge)}</span>'
        )
    return f'<span class="peer-object-name">{name}</span>'


def _case_label(case_key: str, title: str) -> str:
    labels = {
        "home": "首页", "faq": "FAQ", "download": "下载中心", "developer": "开发者",
        "cann-aolapi-intro": "CANN 算子库简介",
        "training-dev": "训练开发",
        "firmware-drivers": "固件与驱动",
        "cluster": "集群", "ccae": "CCAE", "edu": "教育", "pricing": "定价",
        "docs": "文档站", "quickstart": "Quickstart", "docs-editor": "文档编辑器", "docs-tabs": "Tabs 组件", "blog": "博客", "score": "Score",
        "dgx-cloud": "DGX Cloud", "industries": "行业", "automotive": "汽车",
        "cuquantum-release-notes": "Release Notes",
        "build": "Build", "partners": "伙伴", "news": "新闻", "events": "活动",
        "cuda-downloads": "CUDA 下载",
        "devzone": "开发者站",
    }
    return labels.get(case_key, title or case_key)


def _render_peer_override_rows(slug: str) -> list[str]:
    rows: list[str] = []
    index = _load_peer_case_index()
    for row in PEER_ROW_OVERRIDES[slug]:
        case = index.get((row["peer_label"], row["case_key"]), {})
        case_url = case.get("leftUrl") or case.get("rightUrl") or ""
        title = (case.get("title") or row["case_key"]).split("·")[0].split("/")[0].strip()
        case_name = case.get("pageName") or case.get("leftLabel") or _case_label(row["case_key"], title)
        object_title = html.escape(row["object"])
        badge = row.get("badge") or ""
        floor_label = f'<span class="peer-object-name">{object_title}</span>'
        if badge:
            floor_label += f'<span class="peer-floor-badge">{html.escape(badge)}</span>'
        if case_url:
            case_cell = f'<td><a href="{case_url}" target="_blank" rel="noopener">{case_name}</a></td>'
            floor_cell = (
                f'<td><a class="peer-object-link" href="{case_url}" target="_blank" rel="noopener" '
                f'title="该页{object_title}所在的友商线上页面">{floor_label}</a></td>'
            )
        else:
            case_cell = f"<td>{case_name}</td>"
            floor_cell = f'<td><span class="peer-object-link">{floor_label}</span></td>'
        rows.append(
            f'            <tr><td>{row["peer_label"]}</td>'
            f"{case_cell}{floor_cell}"
            f'<td><span class="peer-tag {row["tag_cls"]}">{html.escape(row["grab"])}</span></td>'
            f'<td class="peer-reason">{html.escape(row["reason"])}</td></tr>'
        )
    return rows


def render_peer_section(slug: str) -> str:
    rows: list[str] = []
    if slug in PEER_ROW_OVERRIDES:
        rows = _render_peer_override_rows(slug)
        return _wrap_peer_section(slug, rows)
    peer_sites = {label: (index, case_page, json_path) for label, index, case_page, json_path in PEER_SITES}
    for peer_label, case_key, floor_id in _peer_entries_for_slug(slug):
        floor = _find_peer_floor(peer_label, case_key, floor_id)
        if not floor:
            continue
        case = _load_peer_case_index()[(peer_label, case_key)]
        case_url = case.get("leftUrl") or case.get("rightUrl") or ""
        title = (case.get("title") or case_key).split("·")[0].split("/")[0].strip()
        case_name = case.get("pageName") or case.get("leftLabel") or _case_label(case_key, title)
        floor_label = _floor_object_label(floor)
        grab, tag_cls = _floor_html_grab(floor)
        reason = _floor_reason(floor)
        object_title = html.escape(floor.get("name") or "被测对象")
        if case_url:
            case_cell = f'<td><a href="{case_url}" target="_blank" rel="noopener">{case_name}</a></td>'
            floor_cell = (
                f'<td><a class="peer-object-link" href="{case_url}" target="_blank" rel="noopener" '
                f'title="该页{object_title}所在的友商线上页面">{floor_label}</a></td>'
            )
        else:
            case_cell = f"<td>{case_name}</td>"
            floor_cell = f'<td><span class="peer-object-link">{floor_label}</span></td>'
        rows.append(
            f'            <tr><td>{peer_label}</td>'
            f"{case_cell}"
            f"{floor_cell}"
            f'<td><span class="peer-tag {tag_cls}">{grab}</span></td>'
            f'<td class="peer-reason">{reason}</td></tr>'
        )
    return _wrap_peer_section(slug, rows)


def _wrap_peer_section(slug: str, rows: list[str]) -> str:
    if rows:
        body = (
            '        <table class="peer-test-table">\n'
            + "          <thead>\n"
            + '            <tr><th>友商</th><th>案例</th>'
            + '<th>被测对象</th><th>html 可抓取</th><th>原因</th></tr>\n'
            + "          </thead>\n          <tbody>\n"
            + "\n".join(rows)
            + "\n          </tbody>\n        </table>"
        )
    else:
        body = (
            f'        <p class="peer-test-empty">暂无 {html.escape(slug)} 组件友商对照数据；'
            "请先在 citability-html 案例 JSON 中补全对应楼层。</p>"
        )
    return f"""    <section class="section" id="peer">
      <h2>友商测试</h2>
      <div class="content-unit">
{body}
      </div>
    </section>
"""

CSS_BLOCK = Path(DOCS / "problems-omenu.html").read_text(encoding="utf-8")
CSS = CSS_BLOCK.split("<style>")[1].split("</style>")[0]

SIDEBAR_AFF_CSS = """
  .comp-nav a, .comp-nav .comp-pending {
    display: flex; align-items: center; justify-content: space-between; gap: 8px;
  }
  .comp-nav-label { flex: 1; min-width: 0; }
  .comp-nav .aff {
    display: inline-block; flex-shrink: 0;
    font-size: 11px; font-weight: 600; line-height: 18px;
    padding: 0 6px; border-radius: 999px; white-space: nowrap;
  }
  .comp-nav .aff-need { color: #b42318; background: #fef3f2; }
  .comp-nav .aff-maybe { color: #b54708; background: #fffaeb; }
  .comp-nav .aff-no { color: #595959; background: #F5F5F5; }
  .comp-nav .comp-dot {
    flex-shrink: 0;
    width: 8px; height: 8px; border-radius: 50%;
    background: #2563eb;
  }
"""
if ".comp-nav .aff-need" not in CSS:
    CSS += SIDEBAR_AFF_CSS
# CSS 基线是从已生成的 problems-omenu.html 读回来的，若其中已含 aff 标签样式，
# 上面的 guard 会跳过，导致新增的 comp-dot 规则进不去，这里单独补一条 guard。
if ".comp-nav .comp-dot" not in CSS:
    CSS += (
        "\n  .comp-nav .comp-dot {\n"
        "    flex-shrink: 0;\n"
        "    width: 8px; height: 8px; border-radius: 50%;\n"
        "    background: #2563eb;\n"
        "  }\n"
    )

SCRIPT_BLOCK = """
<script>
(function () {
  function bindModal(openBtn, modal) {
    if (!openBtn || !modal) return;
    var closeBtns = modal.querySelectorAll('[data-close]');
    function open(e) { if (e) e.preventDefault(); modal.hidden = false; document.body.classList.add('modal-open'); }
    function close() { modal.hidden = true; document.body.classList.remove('modal-open'); }
    openBtn.addEventListener('click', open);
    closeBtns.forEach(function (b) { b.addEventListener('click', close); });
    modal.addEventListener('click', function (e) { if (e.target === modal) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !modal.hidden) close(); });
  }
  bindModal(document.getElementById('btn-answer'), document.getElementById('answer-modal'));
  var prev = document.getElementById('btn-preview');
  if (prev && !prev.disabled) bindModal(prev, document.getElementById('preview-modal'));

  var main = document.querySelector('.main-content');
  var tocList = document.getElementById('page-toc-list');
  var used = {};
  function slugify(text) {
    var base = (text || '').trim().toLowerCase().replace(/[^\\w\\u4e00-\\u9fff]+/g, '-').replace(/^-+|-+$/g, '');
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
    tocLinks.forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + id); });
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      var visible = entries.filter(function (e) { return e.isIntersecting; })
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


def all_components() -> list[tuple[str, str, str]]:
    out = []
    for group, items in GROUPS:
        for slug, name in items:
            out.append((group, slug, name))
    return out


def slug_to_name() -> dict[str, str]:
    return {slug: name for _, slug, name in all_components()}


def aff_status(slug: str) -> tuple[str, str]:
    probe = PROBES.get(slug, {})
    if probe.get("no_aff"):
        return "不需要", "aff-no"
    if probe.get("badge_text") == "视情况":
        return "视情况", "aff-maybe"
    return "需要", "aff-need"


def render_aff_tag(slug: str) -> str:
    label, cls = aff_status(slug)
    return f'<span class="aff {cls}">{label}</span>'


# 有 UI 小样（设计示例为可视化 render-frame）的组件：侧边栏名称后加一个蓝色圆点标记
DESIGN_CHANGED_SLUGS = {
    "omenu", "obreadcrumb", "oanchor", "onavigation", "ofooternav",
    "olink", "ocard", "odatetable", "osearch", "orate", "opopover", "ocarousel",
}


def render_design_dot(slug: str) -> str:
    if slug in DESIGN_CHANGED_SLUGS:
        return '<span class="comp-dot" title="设计侧有改动" aria-hidden="true"></span>'
    return ""


def sidebar_label(name: str) -> str:
    """Sidebar shows Chinese label only (drop leading English component id)."""
    if " " in name:
        return name.split(" ", 1)[1]
    return name


def render_nav_item(name: str, href: str, slug: str, *, active: bool) -> str:
    cls = ' class="active"' if active else ""
    return (
        f'        <li><a href="{href}"{cls}>'
        f'<span class="comp-nav-label">{html.escape(sidebar_label(name))}</span>{render_aff_tag(slug)}{render_design_dot(slug)}</a></li>'
    )


def render_sidebar(active: str | None, *, principles: bool = False) -> str:
    lines = ['  <aside class="comp-sidebar" aria-label="组件列表">', '    <div class="comp-sidebar-title">组件列表</div>', '    <nav class="comp-nav">']
    for group, items in GROUPS:
        lines.append(f'      <div class="comp-group-label">{group}</div>')
        lines.append("      <ul>")
        for slug, name in items:
            if principles and slug == "ocarousel":
                href = "principles-affinity.html"
                is_active = active == "ocarousel"
            else:
                href = f"problems-{slug}.html"
                is_active = active == slug
            lines.append(render_nav_item(name, href, slug, active=is_active))
        lines.append("      </ul>")
    lines.extend(["    </nav>", "  </aside>"])
    return "\n".join(lines)


def preview_button(probe: dict) -> str:
    url = probe.get("preview_url")
    if url:
        return f'<a class="btn-preview" href="{url}" target="_blank" rel="noopener">查看测试页面</a>'
    return '<button type="button" class="btn-preview" id="btn-preview" disabled title="暂无样例 URL">查看测试页面</button>'


def desc_line2(probe: dict) -> str:
    if probe.get("sample_url") and probe.get("sample_label"):
        return (
            f'      <span class="page-desc-line">以 <a href="{probe["sample_url"]}" target="_blank" rel="noopener">'
            f'{probe["sample_label"]}</a> 为例：{probe["desc_extra"]}。</span>'
        )
    return f'      <span class="page-desc-line">{probe["desc_extra"]}。</span>'


def desc_aff_note(probe: dict) -> str:
    note = probe.get("aff_note", "").strip()
    if not note:
        return ""
    if note[-1] not in "。！？；":
        note += "。"
    return f'      <span class="page-desc-line"><strong>视情况</strong>：{html.escape(note)}</span>\n'


def guide_aff_note(probe: dict) -> str:
    note = probe.get("aff_note", "").strip()
    if not note:
        return ""
    if note[-1] not in "。！？；":
        note += "。"
    return f"""
      <div class="content-unit">
        <p><strong>视情况</strong>：{html.escape(note)}</p>
      </div>"""


def _sentence(text: str) -> str:
    s = text.strip()
    if s and s[-1] not in "。！？；":
        s += "。"
    return s


def _inline_code(text: str) -> str:
    """Wrap `backtick` spans as <code> after HTML escape."""
    parts = re.split(r"`([^`]+)`", text)
    out: list[str] = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 1:
            out.append(f"<code>{html.escape(part)}</code>")
        else:
            out.append(html.escape(part))
    return "".join(out)


def render_issue_body(desc: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\n+", desc.strip()) if p.strip()]
    if not paragraphs:
        return "<p><strong>问题：</strong></p>"
    first = _sentence(paragraphs[0]).rstrip("。")
    lines = [f'<p><strong>问题：</strong>{_inline_code(first)}。</p>']
    for p in paragraphs[1:]:
        s = _sentence(p).rstrip("。")
        lines.append(f"<p>{_inline_code(s)}。</p>")
    return "\n        ".join(lines)


def render_fix_body(fix: str) -> str:
    s = _sentence(fix).rstrip("。")
    return f"<p>{_inline_code(s)}。</p>"


def render_page(slug: str, name: str, probe: dict) -> str:
    comp_label = name.split()[0] if name else slug
    sub_html = ""
    for i, (title, desc, fix) in enumerate(probe["subcauses"], 1):
        sub_html += f"""
      <div class="content-unit">
        <h3>{i}. {title}</h3>
        <div class="issue-body">
        {render_issue_body(desc)}
        </div>
        <div class="fix-suggestion">
          <h4>修改建议</h4>
          {render_fix_body(fix)}
        </div>
      </div>"""

    sidebar = render_sidebar(slug)
    principles_href = "principles-affinity.html" if slug == "ocarousel" else f"principles-{slug}.html"
    peer_section = render_peer_section(slug)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{probe["title_short"]} · 亲和分析 · 昇腾社区 AI 亲和原则</title>
<style>
{CSS}
</style>
</head>
<body data-module="problems" data-page="{slug}">
<div class="detail-head-bar" aria-label="组件详情导航">
  <div class="modal-title-wrap">
    <a class="back-link" href="community-ui.html" aria-label="返回组件亲和"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 6L9 12l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a>
    <span class="title-divider" aria-hidden="true"></span>
    <div class="modal-title">组件亲和原则</div>
  </div>
  <nav class="detail-head-tabs modal-actions" aria-label="视图切换">
    <a href="problems-{slug}.html" class="active">实测问题</a>
    <a href="{principles_href}">亲和原则</a>
  </nav>
</div>

<div class="page-wrapper">
{sidebar}

  <main class="main-content">
    <div class="page-header">
      <div class="page-header-top">
        <h1>{probe["title_short"]} <span class="badge {probe["badge_class"]}">{probe["badge_text"]}</span></h1>
        {preview_button(probe)}
      </div>
    </div>

    <p class="page-desc page-desc--split">
      <span class="page-desc-line"><strong>{probe["term"]}</strong>指{probe["definition"]}。</span>
{desc_aff_note(probe)}{desc_line2(probe)}
    </p>

    <section class="section" id="problem">
      <h2>问题实测</h2>
      <div class="content-unit">
        <h3>1. 向模型提问</h3>
        <div class="test-prompt-card">
          <p>{probe["prompt"]}</p>
        </div>
      </div>
      <div class="content-unit">
        <h3>2. 大模型回答</h3>
        <p><a href="#" id="btn-answer">查看大模型回答内容</a></p>
      </div>
    </section>

{peer_section}

    <section class="section" id="guide">
      <h2 id="solution">根因分析</h2>{guide_aff_note(probe)}
      <div class="content-unit">
        <p><strong>{probe["term"]}</strong>的核心原因：<strong style="color:var(--text)">{probe["root_cause"]}</strong>。</p>
      </div>{sub_html}
    </section>
  </main>

  <aside class="page-toc" id="page-toc" aria-label="本篇目录">
    <div class="page-toc-title">本篇目录</div>
    <nav class="page-toc-nav"><ul id="page-toc-list"></ul></nav>
  </aside>
</div>

<div class="modal" id="answer-modal" role="dialog" aria-modal="true" aria-labelledby="answer-title" hidden>
  <div class="modal-panel">
    <div class="modal-head">
      <h2 class="modal-title" id="answer-title">大模型回答</h2>
      <button type="button" class="modal-close" data-close>关闭</button>
    </div>
    <div class="modal-body">
      <div class="dialog-card">
        <span class="dialog-role">用户</span>
        <p>{probe["prompt_plain"]}</p>
      </div>
      <div class="dialog-card">
        <span class="dialog-role">大模型</span>
        <p>{probe["answer"]}</p>
      </div>
    </div>
  </div>
</div>
{SCRIPT_BLOCK}
</body>
</html>
"""


def patch_sidebar_in_file(path: Path, active: str | None, *, principles: bool = False) -> bool:
    text = path.read_text(encoding="utf-8")
    new_sidebar = render_sidebar(active, principles=principles)
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


def delete_no_aff_pages() -> list[str]:
    deleted: list[str] = []
    for slug in sorted(NO_AFF_SLUGS):
        for prefix in ("problems", "principles"):
            for root in (DOCS, REPORT):
                path = root / f"{prefix}-{slug}.html"
                if path.exists():
                    path.unlink()
                    deleted.append(str(path.relative_to(ROOT)))
    return deleted


def prune_community_ui() -> tuple[int, int]:
    """Remove 不需要 rows from community-ui.html; renumber and refresh section counts."""
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    removed = 0
    while True:
        new_text, n = re.subn(
            r'\n\s*<tr data-aff="不需要">.*?</tr>',
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )
        if n == 0:
            break
        text = new_text
        removed += 1

    seq = 0

    def renum_row(match: re.Match[str]) -> str:
        nonlocal seq
        seq += 1
        return f'{match.group(1)}{seq}{match.group(2)}'

    text = re.sub(
        r'(<tr data-aff="[^"]+"><td class="col-num">)\d+(</td>)',
        renum_row,
        text,
    )

    catalog_count = len(list(all_components()))
    text = re.sub(r"共 \d+ 个组件", f"共 {catalog_count} 个组件", text, count=1)
    text = re.sub(
        r'(<label><input type="checkbox" name="aff" value="不需要"[^/]*/>不需要</label>\s*)',
        "",
        text,
        count=1,
    )

    for group, items in GROUPS:
        section_ids = {
            "导航类": "cat-nav",
            "操作类": "cat-action",
            "输入类": "cat-input",
            "展示类": "cat-display",
            "容器类": "cat-container",
            "反馈类": "cat-feedback",
        }
        sid = section_ids.get(group)
        if not sid:
            continue
        count = len(items)
        text = re.sub(
            rf'(<h2 id="{sid}">[^<]+<span class="count">)\d+(</span></h2>)',
            rf"\g<1>{count}\g<2>",
            text,
            count=1,
        )

    path.write_text(text, encoding="utf-8")
    if REPORT.joinpath("community-ui.html").exists() or path.exists():
        shutil.copy2(path, REPORT / "community-ui.html")
    return removed, catalog_count


def update_community_ui_samples() -> int:
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    count = 0
    for _, slug, name in all_components():
        probe = PROBES.get(slug, {})
        url = probe.get("sample_url")
        label = probe.get("sample_label")
        if not url or not label:
            continue
        sample_cell = f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
        pattern = (
            rf'(<tr[^>]*>.*?{re.escape(name)}.*?<td class="col-sample">)'
            rf'(?:<span class="sample-empty">—</span>|<a href="[^"]+"[^>]*>[^<]+</a>)'
            rf'(</td><td class="col-detail">)'
        )
        new_text, n = re.subn(pattern, rf"\1{sample_cell}\2", text, count=1, flags=re.DOTALL)
        if n:
            text = new_text
            count += 1
    path.write_text(text, encoding="utf-8")
    shutil.copy2(path, REPORT / "community-ui.html")
    return count


def update_community_ui() -> int:
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    name_to_slug = {name: slug for _, slug, name in all_components()}
    count = 0
    for name, slug in name_to_slug.items():
        old = f'<button type="button" class="comp-link" data-name="{name}"'
        if old not in text:
            continue
        # replace detail cell on same row - match row containing this button
        pattern = (
            rf'(<tr[^>]*>.*?{re.escape(name)}.*?</td><td class="col-detail">)'
            rf'(?:<span class="detail-empty">查看详情</span>|<a href="problems-{slug}\.html">查看详情</a>)'
            rf'(</td></tr>)'
        )
        new_detail = rf'\1<a href="problems-{slug}.html">查看详情</a>\2'
        new_text, n = re.subn(pattern, new_detail, text, count=1, flags=re.DOTALL)
        if n:
            text = new_text
            count += 1
    path.write_text(text, encoding="utf-8")
    return count


def copy_to_report_serve() -> None:
    REPORT.mkdir(parents=True, exist_ok=True)
    for path in DOCS.glob("problems-*.html"):
        shutil.copy2(path, REPORT / path.name)
    for extra in ("community-ui.html", "principles-affinity.html"):
        src = DOCS / extra
        if src.exists():
            shutil.copy2(src, REPORT / extra)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate problems-component-probe HTML pages.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing problems-*.html (except hand-written skip list).",
    )
    args = parser.parse_args()

    deleted = delete_no_aff_pages()
    removed_rows, catalog_count = prune_community_ui()

    generated: list[str] = []
    skipped: list[str] = []

    for _, slug, name in all_components():
        out = DOCS / f"problems-{slug}.html"
        if slug in SKIP_CONTENT:
            skipped.append(out.name)
            continue
        if out.exists() and not args.force:
            skipped.append(out.name)
            continue
        probe = PROBES.get(slug)
        if not probe:
            raise SystemExit(f"Missing probe data for {slug}")
        out.write_text(render_page(slug, name, probe), encoding="utf-8")
        generated.append(out.name)

    # refresh sidebars everywhere
    sidebars_patched = 0
    for _, slug, _ in all_components():
        path = DOCS / f"problems-{slug}.html"
        if path.exists() and patch_sidebar_in_file(path, slug):
            sidebars_patched += 1

    if patch_sidebar_in_file(DOCS / "principles-affinity.html", "ocarousel", principles=True):
        sidebars_patched += 1

    links_updated = update_community_ui()
    samples_updated = update_community_ui_samples()
    copy_to_report_serve()

    print(f"Generated/refreshed: {len(generated)}")
    for f in sorted(generated):
        print(f"  {f}")
    if deleted:
        print(f"Deleted no-aff pages: {len(deleted)}")
        for f in deleted:
            print(f"  {f}")
    print(f"community-ui pruned: {removed_rows} rows removed, {catalog_count} components in catalog")
    print(f"Skipped existing/hand-written: {len(skipped)}")
    print(f"Sidebars patched: {sidebars_patched}")
    print(f"community-ui detail links updated: {links_updated} rows")
    print(f"community-ui sample URLs updated: {samples_updated} rows")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
