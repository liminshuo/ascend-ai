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
FAQ_CAMP = "https://www.hiascend.com/document/detail/zh/AscendFAQ/CommuFunc/AscendAITrainingCamp/ascendaitrainingcamp_000.html"
CANN_AOLAPI_INTRO = "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta3/API/aolapi/operatorlist_00001.html"
TECH_ARTICLES = "https://www.hiascend.com/developer/techArticles"
SIMT_MEMORY = (
    "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/latest/programug/Ascendcopdevg/docs/guide/%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97/%E7%BC%96%E7%A8%8B%E6%A8%A1%E5%9E%8B/AI-Core-SIMT%E7%BC%96%E7%A8%8B/%E5%86%85%E5%AD%98%E5%B1%82%E7%BA%A7.md"
)
FORUM = "https://www.hiascend.com/forum/"
TRAINING_DEV = "https://www.hiascend.com/cn/developer/training?tab=tab1"
FIRMWARE_DRIVERS = "https://www.hiascend.com/hardware/firmware-drivers"
CUDA_DOWNLOADS = "https://developer.nvidia.com/cuda-downloads/?target_os=Linux"
EDU_TEACHING = (
    "https://edu.hicomputing.huawei.com/teaching"
    "?activeTab=%E9%B2%B2%E9%B9%8F%E4%B8%93%E5%8C%BA,%E6%98%87%E8%85%BE%E4%B8%93%E5%8C%BA,"
    "%E5%8D%8E%E4%B8%BA%E4%BA%91%E4%B8%93%E5%8C%BA,%E8%81%94%E6%8E%A5%E4%B8%93%E5%8C%BA,"
    "%E9%80%9A%E7%94%A8%E8%BD%AF%E4%BB%B6%E4%B8%93%E5%8C%BA"
    "&resourceType=%E5%88%9B%E6%96%B0%E5%AE%9E%E8%B7%B5%E8%AF%BE"
    "&subTab=openEuler%E6%99%BA%E8%83%BD%E8%B0%83%E4%BC%98%EF%BC%88A-Tune%EF%BC%89"
)
FIND_TRAINING = "https://www.nvidia.com/en-us/training/find-training/"
EDU_GROWTH = "https://www.hiascend.com/edu/growth"
MINDX = "https://www.hiascend.com/developer/software/mindx"
BUILD_SPARK = "https://build.nvidia.com/spark"
BUILD_SKILLS = (
    "https://build.nvidia.com/skills?filters=audience%3Aaudience_developer"
)
MINTLIFY_API_TRIGGER = "https://www.mintlify.com/docs/api/update/trigger"

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
        "sample_url": FAQ_CAMP,
        "sample_label": "昇腾AI训练营常见问题",
        "desc_extra": "FAQ 文档侧栏场景；静态未见 o-menu / 侧栏 a[href] 树，目录节点与 URL 在 __NUXT_DATA__",
        "prompt": f'我在看 <a href="{FAQ_CAMP}" target="_blank" rel="noopener">昇腾AI训练营常见问题</a>，手册左侧目录完整有哪些章节？「昇腾AI训练营常见问题」的上一篇、下一篇官方文档链接分别是什么？',
        "prompt_plain": f"我在看昇腾AI训练营常见问题（{FAQ_CAMP}），手册左侧目录完整有哪些章节？「昇腾AI训练营常见问题」的上一篇、下一篇官方文档链接分别是什么？",
        "answer": "根据当前静态 HTML，我看不到完整的左侧手册目录树（无 o-menu / 侧栏 a[href] 列表），只能看到当前页标题等零散文案。无法可靠列出「社区功能与服务」下各章，也答不出上一篇「账号与认证」、下一篇「伙伴计划」的官方深链——这些节点与各自独立 URL 写在 __NUXT_DATA__ 里，须执行脚本才渲染成可点目录。",
        "insights": [
            ("友商侧栏可抓全", "Mintlify 73 条、NVIDIA 700+ 条侧栏 href 均在静态 HTML"),
            ("昇腾 TOC 在 NUXT", "训练营 FAQ 页静态几乎无侧栏链；节点名与路径在 __NUXT_DATA__（如 ascendaitrainingcamp_000 / developerpartner_011 / accfaq_000 各不相同）"),
            ("样本未见 OMenu", "该页静态 DOM 无 o-menu；顶栏 o-nav 不能冒充手册侧栏"),
            ("发现层缺口", "无 SSR 目录时 Agent 只能靠 sitemap/llms，失去手册内结构线索"),
        ],
        "root_cause": "人在浏览器里能看到左侧目录，但「查看网页源代码」里几乎没有这些目录链接——章节名和地址藏在页面脚本数据里，要等 JavaScript 跑完才画出来，所以爬虫和 AI 默认读不到",
        "root_evidence": {
            "title": "实测证据 · 浏览器侧栏 vs 静态源码",
            "shot": "assets/cases-html-ascend/faq-sidebar.jpg",
            "shot_alt": "昇腾 FAQ 文档页浏览器可见左侧目录",
            "shot_label": "浏览器里能看见的左侧目录",
            "code_label": "「查看网页源代码」里几乎没有侧栏链接",
            "code": "<!-- 查看网页源代码 / 禁 JS：几乎无手册侧栏 a[href] 树 -->\n"
            "<!-- 仅见零散文档链，例如： -->\n"
            '<a href="…/AscendFAQ/overview/index.html">常见问题</a>\n'
            '<a href="…/ascendaitrainingcamp_000.html">昇腾AI训练营常见问题</a>\n'
            "<!-- 无「账号与认证 / 伙伴计划 / 活动与大赛…」侧栏目录列表 -->",
            "caption": "左图是人眼看到的目录；右边是源码里实际能抠出来的链接——侧栏整棵树基本不在。",
        },
        "subcauses": [
            (
                "源码里没有完整的左侧目录",
                "打开昇腾AI训练营常见问题页，用「查看网页源代码」核对：左侧那一整棵章节目录几乎找不到，只有很少几条零散链接。各篇其实都有自己的文档地址，但没有写成侧栏上的可点链接，要等脚本跑完才画出来——爬虫打开源码时跟不到目录链",
                "页面一出来就把完整目录写进 HTML：每一项都是「章节名 + 真实地址」的链接，展开收起按钮不能代替链接",
                {
                    "title": "证据 · 侧栏链接本来应该长这样",
                    "code_label": "期望写进网页的侧栏链接（示意，当前页没有）",
                    "code": "<nav class=\"doc-sidebar\">\n"
                    '  <a href="…/accfaq_000.html">账号与认证</a>\n'
                    '  <a href="…/ascendaitrainingcamp_000.html">昇腾AI训练营常见问题</a>\n'
                    '  <a href="…/developerpartner_011.html">伙伴计划</a>\n'
                    "</nav>",
                    "caption": "每篇不同地址是对的；缺的是把它们直接写在侧栏 HTML 里。",
                },
            ),
            (
                "脚本数据里也只有邻篇，没有整棵目录",
                "即便从页面脚本数据（__NUXT_DATA__）里抠「上一篇 / 下一篇」，也只能拿到「账号与认证」「伙伴计划」两个邻居，看不到「社区功能与服务」下其余章节。所以既列不全手册结构，也不能靠这段数据补出完整发现层",
                "若脚本数据要作备用，须带完整子节点列表（标题 + URL），不能只有当前页和上一篇 / 下一篇",
                {
                    "title": "证据 · 脚本里只有邻接节点",
                    "code_label": "页面脚本数据摘录（训练营 FAQ 实测）",
                    "code": '{\n'
                    '  "finalNodeName": "昇腾AI训练营常见问题",\n'
                    '  "finalNodeUrl": "zh/AscendFAQ/CommuFunc/AscendAITrainingCamp/ascendaitrainingcamp_000.html",\n'
                    '  "upNodeName": "账号与认证",\n'
                    '  "upNodeUrl": "zh/AscendFAQ/CommuFunc/Account&AuthenticationFAQ/accfaq_000.html",\n'
                    '  "nextNodeName": "伙伴计划",\n'
                    '  "nextNodeUrl": "zh/AscendFAQ/CommuFunc/Developer&partner/developerpartner_011.html"\n'
                    "}",
                    "caption": "地址有、且每篇不同；但这组字段只有当前页 + 邻篇，不是完整侧栏树。",
                },
            ),
            (
                "也没有备用的章节清单",
                "侧栏读不到时，如果网站地图或 llms.txt 里也没有按手册列出各章链接，AI 就只知道当前这一页写了什么，不知道整本手册还有哪些页",
                "在 llms.txt 或 Markdown 手册里再列一份「章节名 + 链接」，和侧栏目录互相补上",
            ),
        ],
        "preview_url": FAQ_CAMP,
    },
    "otab": {
        "title_short": "Tab 隐藏语义",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "aff_note": "内容型 Tab（各面板有独立说明 / 列表 / 步骤）须全量 SSR；纯交互或装饰型 Tab 入库剥离。型号 / 架构 / 安装方式等多维选型矩阵归选择块，不按本组件处理",
        "term": "Tab 隐藏语义",
        "definition": "非激活 Tab 面板被隐藏或未进首包时，默认抓取只得到当前面板，其它页签正文丢失",
        "sample_url": DOWNLOAD,
        "sample_label": "CANN 软件下载",
        "desc_extra": "社区首页有 o-tab 样例；CANN 下载为自定义 tab-*，亲和问题更重",
        "prompt": f'我在看 <a href="{DOWNLOAD}" target="_blank" rel="noopener">CANN 软件下载</a>，想给 Atlas 训练卡做离线安装，下载命令和安装说明在哪个 Tab？把完整命令原文给我。',
        "prompt_plain": f"我在看 CANN 软件下载（{DOWNLOAD}），想给 Atlas 训练卡做离线安装，下载命令和安装说明在哪个 Tab？把完整命令原文给我。",
        "answer": "根据当前静态 HTML，我能看到页壳和部分默认区卡片，但页签导航往往是空的，未激活面板与安装命令原文几乎不在首包。无法可靠列出「昇腾资源 / 三方资源」等全部页签，也给不出 Atlas 800 离线安装的完整命令——这些要等脚本跑完、点开对应页签才出现。",
        "insights": [
            ("NVIDIA tabpanel 全进首包", "partners 页 4 个 role=tabpanel 未切换也可抓各面板标题与说明"),
            ("昇腾 Tab 静态空壳", "下载页浏览器可见「昇腾资源 / 三方资源」，源码 o-tab-nav-list 常为空；未激活面板与配套说明靠脚本"),
            ("Mintlify 折叠面板同类", "pricing FAQ 关闭态 region 无答文，展开后才挂入 DOM"),
            ("未激活面板易丢", "只 SSR 默认页签时，RAG 答不出其它面板里的说明"),
        ],
        "root_cause": "人在浏览器里能看见「昇腾资源 / 三方资源」等页签，但「查看网页源代码」里页签导航常常是空的，未激活面板的正文也不在首包——不点切换就列不全页签、读不到其它面板里的说明",
        "root_evidence": {
            "title": "实测证据 · 浏览器页签 vs 静态源码",
            "shot": "assets/cases-html-ascend/download-edition-note.jpg",
            "shot_alt": "CANN 软件下载页浏览器可见昇腾资源 / 三方资源页签",
            "shot_label": "浏览器里能看见的页签",
            "code_label": "「查看网页源代码」里页签导航是空的",
            "code": "<!-- 查看网页源代码 / 禁 JS：页签导航常为空 -->\n"
            '<div class="o-tab">\n'
            '  <div class="o-tab-nav-list"></div>\n'
            "  <!-- 浏览器可见「昇腾资源 / 三方资源」，源码无页签名 -->\n"
            '  <div class="o-tab-pane o-tab-pane-active"><!-- 默认区或空 --></div>\n'
            "  <!-- 未激活「三方资源」面板正文通常不在首包 -->\n"
            "</div>",
            "caption": "左图是人眼看到的页签；右边是源码里实际抠到的导航——页签名基本不在。",
        },
        "subcauses": [
            (
                "页签名没有写进网页源码",
                "打开 CANN 软件下载页，用「查看网页源代码」核对：o-tab-nav-list 经常是空的。浏览器里有「昇腾资源 / 三方资源」，源码读不到这些名字——AI 甚至不知道这一页有哪些页签维度",
                "每个页签名称直接写进首包 HTML，使不执行脚本也能读到全部 Tab 名称",
                {
                    "title": "证据 · 页签导航本来应该长这样",
                    "code_label": "期望写进网页的页签名（示意）",
                    "code": '<div class="o-tab-nav-list">\n'
                    '  <span role="tab" aria-selected="true">昇腾资源</span>\n'
                    '  <span role="tab">三方资源</span>\n'
                    "</div>",
                    "caption": "页签名要进源码；只在浏览器里画出来不算达标。",
                },
            ),
            (
                "未激活面板的正文也不在首包",
                "默认面板下的部分卡片标题或许还能抓到，但未选中的「三方资源」等面板、以及要点击后才出现的安装 / 配套说明，常常不在源码里。所以既列不全其它页签内容，也答不出「Atlas 离线安装命令原文」",
                "每一个页签面板的正文都预先写进源码；可用 hidden / display:none 做视觉隐藏，禁止点击后才 JS 注入",
                {
                    "title": "证据 · 双面板都应进源码",
                    "code_label": "期望写进网页的面板正文（示意）",
                    "code": '<div role="tabpanel" id="pane-ascend">\n'
                    '  <div class="o-card-title">CANN</div>\n'
                    "  <div class=\"o-card-detail\">…</div>\n"
                    '  <a href="/document/…/cann">查看文档</a>\n'
                    "</div>\n"
                    '<div role="tabpanel" id="pane-third" hidden>\n'
                    "  …三方资源面板条目…\n"
                    "</div>",
                    "caption": "未激活面板可以藏起来，但文本必须还在首包里。",
                },
            ),
            (
                "没有不点 Tab 也能读到的说明",
                "安装步骤、下载链接等如果没有单独的文档页，也没有在 llms.txt 里按页签列出来，AI 就只能依赖这一页的交互——侧栏 / 源码读不到时就没有退路",
                "安装 / 下载类内容提供独立文档页，或在 llms.txt 中按页签列出要点与链接",
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
        "answer": "浏览器顶栏能看到「昇腾常见问题 › 产品与技术常见问题 › 昇腾产品形态说明」，祖先级开 JS 后也能点。但「查看网页源代码」里 server-breadcrumb 只有「文档中心 → 当前页」两条，中间祖先不在首包；「文档中心」还链到 sitemap XML，当前页被做成了自链。禁 JS 时答不出与可见 UI 一致的完整祖先链接清单。",
        "insights": [
            ("浏览器祖先可点", "开 JS 后可见「昇腾常见问题 / 产品与技术常见问题」可点"),
            ("首包仅 2 链且不对", "server-breadcrumb：文档中心→sitemap XML；当前页自链；缺中间祖先"),
            ("路径靠客户端补", "中间级在脚本数据 / breadcrumbs 接口，静态抓取列不全"),
            ("当前页宜非链", "末级应用纯文本，避免自链循环"),
        ],
        "root_cause": "人在浏览器里能看见完整面包屑、祖先也能点，但「查看网页源代码」里中间祖先没有写进首包链接——只有「文档中心 → 当前页」两条，还和可见路径对不上，所以爬虫和 AI 没法按人眼看到的层级一层层往上找",
        "root_evidence": {
            "title": "实测证据 · 浏览器面包屑 vs 静态源码",
            "shot": "assets/cases-html-ascend/faq-breadcrumb.jpg",
            "shot_alt": "昇腾产品形态说明页浏览器可见面包屑路径",
            "shot_label": "浏览器里能看见的面包屑",
            "code_label": "「查看网页源代码」里只有两条，且对不上",
            "code": "<!-- 查看网页源代码 / 禁 JS：server-breadcrumb 仅 2 个 a[href] -->\n"
            '<div class="o-breadcrumb server-breadcrumb">\n'
            '  <a href="/sitemap/sitemapdoc1.xml">文档中心</a>\n'
            '  <a href="…/hardwaredesc_0001.html">昇腾产品形态说明</a>\n'
            "</div>\n"
            "<!-- 浏览器可见「昇腾常见问题 › 产品与技术常见问题 › …」；中间祖先不在首包 -->",
            "caption": "左图祖先开 JS 后能点；右边源码只有「文档中心 → 当前页」，中间级不在。",
        },
        "subcauses": [
            (
                "源码里缺少与可见 UI 一致的祖先链",
                "打开昇腾产品形态说明页，用「查看网页源代码」核对：server-breadcrumb 没有「昇腾常见问题 / 产品与技术常见问题」。浏览器里这两级可以点，但要等脚本跑完才补进面包屑——禁 JS 时跟不到与人眼一致的上级文档",
                "首包直接输出与可见 UI 一致的完整祖先列表：每一级都是带真实文档地址的 a[href]，不要只靠客户端事后补",
                {
                    "title": "证据 · 祖先链本来应该长这样",
                    "code_label": "期望写进网页的面包屑（示意）",
                    "code": '<nav aria-label="Breadcrumb" class="o-breadcrumb">\n'
                    '  <a href="/document/detail/zh/AscendFAQ/…">昇腾常见问题</a>\n'
                    '  <a href="/document/detail/zh/AscendFAQ/ProduTech/…">产品与技术常见问题</a>\n'
                    '  <span aria-current="page">昇腾产品形态说明</span>\n'
                    "</nav>",
                    "caption": "祖先可跟链；末级当前页用纯文本，不要做成自链。",
                },
            ),
            (
                "首包那两条链接本身也不对",
                "源码里仅有的「文档中心」链到 `/sitemap/sitemapdoc1.xml`（站点地图，不是手册祖先页），「昇腾产品形态说明」又链回当前页自己。即便爬虫跟了这两条，也到不了「昇腾常见问题 / 产品与技术常见问题」，还会和可见路径文案错位",
                "祖先 href 指向真实文档页，文案与侧栏 / sitemap 一致；当前页改为纯文本，勿输出自链",
                {
                    "title": "证据 · 首包两条链的问题",
                    "code_label": "实测源码摘录",
                    "code": '<a href="/sitemap/sitemapdoc1.xml">文档中心</a>\n'
                    "<!-- ↑ 应是手册祖先，不是 sitemap XML -->\n"
                    '<a href="…/hardwaredesc_0001.html">昇腾产品形态说明</a>\n'
                    "<!-- ↑ 当前页自链；末级宜为纯文本 -->",
                    "caption": "有 a[href] 不等于达标：目标页和文案都要对上可见层级。",
                },
            ),
            (
                "也没有备用的祖先路径清单",
                "页面面包屑读不全时，如果 llms.txt 或 Markdown 里也没有写出「当前页 → 各级祖先」的链接，AI 就只知道这一页标题，无法沿手册结构往上找上下文",
                "在 llms.txt 或手册平行轨临时补一份祖先链；页面 SSR 达标后以页面为准，去掉重复维护",
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
        "answer": "浏览器右侧能看见章节目录（概述 / 使用说明 / 使用向导），但「查看网页源代码」里没有 document-anc 可跟链列表。正文 h4.sectiontitle 与 section id 已在首包，所以能按标题切片，却无法从右侧目录入口回答「概述对应哪一节、#id 是什么」——目录要等脚本补全。",
        "insights": [
            ("右侧目录首包缺失", "document-anc 浏览器可见，静态 HTML 无可跟链 nav"),
            ("正文 id 已在首包", "h4.sectiontitle 与 section id（如 …section10818103975019）可抓"),
            ("半成品态", "正文可切片、目录不可引；友商 Mintlify/NVIDIA 本篇目录带 #hash"),
            ("纯视觉选中态不足", "颜色变化对抓取无增量"),
        ],
        "root_cause": "人在浏览器里能看见右侧章节目录，但「查看网页源代码」里没有这些目录的 #hash 链接；正文标题 id 反而已经在首包——形成「能按标题切片、却不能从目录入口定位」的半成品，Agent 无法按目录证伪回答",
        "root_evidence": {
            "title": "实测证据 · 右侧目录缺失 vs 正文 id 已在",
            "code_label": "「查看网页源代码」对照（禁 JS）",
            "code": "<!-- ✗ 右侧本篇目录：首包无 document-anc 可跟链 nav -->\n"
            "<!-- 浏览器可见「概述 / 使用说明 / 使用向导」，要等脚本才出现 -->\n"
            "\n"
            "<!-- ✓ 正文标题与 id 已在首包： -->\n"
            '<section id="ZH-CN_TOPIC_0000002594808280__section10818103975019">\n'
            '  <h4 class="sectiontitle">概述</h4>\n'
            "</section>\n"
            '<section id="ZH-CN_TOPIC_0000002594808280__section20972124710220">\n'
            '  <h4 class="sectiontitle">使用说明</h4>\n'
            "</section>\n"
            '<section id="ZH-CN_TOPIC_0000002594808280__section1457612184710">\n'
            '  <h4 class="sectiontitle">使用向导</h4>\n'
            "</section>",
            "caption": "目录链不在源码；正文 id 在——半成品：能切片，不能从目录入口引。",
        },
        "subcauses": [
            (
                "右侧章节目录没有写进网页源码",
                "打开 CANN 算子库简介页，用「查看网页源代码」核对：没有 document-anc 里带 #hash 的目录列表。浏览器右侧能看到「概述 / 使用说明 / 使用向导」，但要等脚本跑完才出现——禁 JS 时列不出目录项，也给不出「概述」对应的入口链接",
                "首包直接输出右侧本篇目录：每一项为 a[href=\"#section-id\"] + 章节名，对齐 Mintlify On this page、NVIDIA page-toc",
                {
                    "title": "证据 · 本篇目录本来应该长这样",
                    "code_label": "期望写进网页的章节目录（示意）",
                    "code": '<nav class="document-anc" aria-label="本篇目录">\n'
                    '  <a href="#ZH-CN_TOPIC_…__section10818103975019">概述</a>\n'
                    '  <a href="#ZH-CN_TOPIC_…__section20972124710220">使用说明</a>\n'
                    '  <a href="#ZH-CN_TOPIC_…__section1457612184710">使用向导</a>\n'
                    "</nav>",
                    "caption": "目录项必须是带真实 #hash 的链接，并指向正文同名 section id。",
                },
            ),
            (
                "正文 id 已在，目录缺失，形成半成品",
                "同一页上，正文 h4.sectiontitle 与 section id 已经写进首包，按标题切片没问题；缺的是从右侧目录点进去的入口。所以 Agent 可能答得出「有一节叫概述」，却答不出「目录里的概述对应哪个 #id」——发现入口和正文锚点不同步",
                "目录与正文 id 同批 SSR；勿只写正文 id，而把章节目录留给客户端补全",
                {
                    "title": "证据 · 正文 id 已在首包",
                    "code_label": "实测正文摘录",
                    "code": '<section id="ZH-CN_TOPIC_0000002594808280__section10818103975019">\n'
                    '  <h4 class="sectiontitle">概述</h4>\n'
                    "  …\n"
                    "</section>\n"
                    "<!-- 正文可切片；缺的是指向该 id 的目录 a[href] -->",
                    "caption": "有正文 id 不等于目录可达；两边要一起进源码。",
                },
            ),
            (
                "也没有备用的本篇目录",
                "右侧目录读不到时，如果 Markdown 页头或 llms.txt 里也没有按章节列出「标题 + #锚点」，AI 就只剩正文标题可猜，没有稳定的本篇导航入口",
                "在 MD 页头或 llms.txt 临时平铺本篇章节（标题 + #id）；页面目录 SSR 达标后以页面为准",
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
        "sample_url": TECH_ARTICLES,
        "sample_label": "官方技术文章",
        "desc_extra": "技术文章列表底部分页（共 N 条 / 页码 / 前往）；页码须为可抓 URL，勿纯 button 切换",
        "prompt": f'我在看 <a href="{TECH_ARTICLES}" target="_blank" rel="noopener">官方技术文章</a> 列表页，第 2、3 页文章列表的官方 URL 分别是什么？请给出完整 href。',
        "prompt_plain": f"我在看官方技术文章（{TECH_ARTICLES}）列表页，第 2、3 页文章列表的官方 URL 分别是什么？请给出完整 href。",
        "answer": "技术文章列表在浏览器可见翻页（共 348 条、页码 1…35、前往），但静态 HTML 几乎无 page= 可跟链；分页多为 button / 客户端切换。我只能描述「还有下一页」但给不出第 2、3 页的可爬地址，后续页文章对 RAG 不可达。",
        "insights": [
            ("页码应是链接", "a[href] 带 page 参数"),
            ("昇腾列表翻页靠脚本", "techArticles 首包无稳定 ?page= 链"),
            ("纯 JS 翻页断链", "sitemap 难覆盖深页"),
            ("rel=next 可辅助", "机器发现下一页"),
        ],
        "root_cause": "人在浏览器里能看见「共 N 条 / 页码 / 前往」并翻到第 2、3 页，但「查看网页源代码」里几乎没有带 ?page= 的可跟链接——页码多是 button 或脚本切换，所以爬虫和 AI 给不出深页官方 URL，后面几页的文章进不了默认管道",
        "root_evidence": {
            "title": "实测证据 · 浏览器分页 vs 静态源码",
            "shot": "assets/cases-html-ascend/tech-articles-pagination.png",
            "shot_alt": "官方技术文章列表页浏览器可见底部分页",
            "shot_label": "浏览器里能看见的底部分页",
            "code_label": "「查看网页源代码」里几乎没有 ?page= 链",
            "code": "<!-- 查看网页源代码 / 禁 JS：几乎无稳定深页 URL -->\n"
            '<nav class="pagination"><!-- 示意：页码多为 button -->\n'
            "  <button>1</button>\n"
            "  <button>2</button>\n"
            "  <button>3</button>\n"
            "  <button>下一页</button>\n"
            "</nav>\n"
            "<!-- 无 <a href=\"…/techArticles?page=2\"> 这类可跟链 -->",
            "caption": "左图人能翻页；右边源码跟不到第 2、3 页官方地址。",
        },
        "subcauses": [
            (
                "页码是 button，没有真实 URL",
                "打开官方技术文章列表，用「查看网页源代码」核对：底部「1 / 2 / … / 35 / 前往」几乎不是带地址的 a[href]。浏览器里能点到第 2、3 页，但禁 JS 时给不出完整官方 URL——问「第 2、3 页 href 是什么」就答不上",
                "每一页码（及上一页 / 下一页）都写成带稳定 query 的真实链接，例如 ?page=2；不要只用 button / onClick 翻页",
                {
                    "title": "证据 · 页码本来应该长这样",
                    "code_label": "期望写进网页的分页链接（示意）",
                    "code": '<nav class="o-pagination" aria-label="分页">\n'
                    '  <a href="/developer/techArticles?page=1" aria-current="page">1</a>\n'
                    '  <a href="/developer/techArticles?page=2">2</a>\n'
                    '  <a href="/developer/techArticles?page=3">3</a>\n'
                    '  <a href="/developer/techArticles?page=2" rel="next">下一页</a>\n'
                    "</nav>",
                    "caption": "页码必须是可跟的 a[href]；query 稳定，便于引用和收录。",
                },
            ),
            (
                "深页内容只在翻页后才出现",
                "首包往往只有默认第 1 页附近的卡片；第 2 页及以后的文章标题与链接要等脚本跑完、点页码后才挂上。所以即便知道「一共 348 条」，也枚举不全深页条目，RAG 默认管道到不了后面几页",
                "服务端按页输出列表，或至少让每一页有独立可打开的 URL，打开该 URL 时首包就带上该页卡片标题与链接",
            ),
            (
                "也没有 sitemap / llms 兜底深页",
                "页码读不到时，如果 sitemap 或 llms.txt 里也没有 ?page=2、?page=3，或没有把文章「标题 + 链接」平铺出来，AI 就只知道当前这一屏，补不出整站技术文章清单",
                "在 sitemap / llms.txt 收录深页 URL，或平铺关键条目的标题与链接；页面分页达标后以页面为准，去掉重复维护",
            ),
        ],
        "preview_url": TECH_ARTICLES,
    },
    "ostep": {
        "title_short": "步骤说明不可抓",
        "badge_class": "badge-should",
        "badge_text": "需文本进源码",
        "term": "步骤说明不可抓",
        "definition": "步骤条上的标题与说明须写入 HTML 文本；步骤内示例代码也须为可读源码，否则 Agent 只能复述步骤名、抄不出代码",
        "sample_url": SIMT_MEMORY,
        "sample_label": "内存层级（SIMT）",
        "desc_extra": "CANN 文档「共享内存」静态/动态申请编号步骤；步骤标题与说明、示例代码须进源码文本",
        "prompt": f'我在看 <a href="{SIMT_MEMORY}" target="_blank" rel="noopener">内存层级</a>，共享内存「静态申请 / 动态申请」两步的标题和说明原文分别是什么？静态申请示例代码开头几行是什么？',
        "prompt_plain": f"我在看内存层级（{SIMT_MEMORY}），共享内存「静态申请 / 动态申请」两步的标题和说明原文分别是什么？静态申请示例代码开头几行是什么？",
        "answer": "步骤标题与说明（静态申请 / 动态申请）在首包 ol/li 文本里大致能读到；但步骤内的代码块、内联 code、部分链接在静态 HTML 中常变成 [object Object]，我给不出可复制的 __ubuf__ half static_buf[1024] 等示例原文。Mintlify Quickstart Steps 的 step-title + step-content 则完整可抓。",
        "insights": [
            ("友商 Steps 可抓全", "Mintlify quickstart Web editor 四步 step-title + step-content 在首包"),
            ("昇腾步骤文案在 ol", "内存层级页「静态申请 / 动态申请」标题与说明在 ol/li 首包"),
            ("步骤内代码 [object Object]", "mermaid/代码块/内联 code 多处未 SSR 成可读源码"),
            ("半成品态", "能复述步骤名，抄不出步骤内示例代码"),
        ],
        "root_cause": "人在浏览器里能看见编号步骤和示例代码，但「查看网页源代码」里步骤标题/说明已在 ol/li，步骤内的代码块与内联标记却常变成 [object Object]——Agent 答得出「静态申请 / 动态申请」，却抄不出可运行的示例原文",
        "root_evidence": {
            "title": "实测证据 · 浏览器步骤代码 vs 静态源码",
            "shot": "assets/cases-html-ascend/simt-memory-steps.png",
            "shot_alt": "内存层级页浏览器可见静态申请 / 动态申请步骤与代码",
            "shot_label": "浏览器里能看见的步骤与代码",
            "code_label": "「查看网页源代码」里代码变成占位",
            "code": "<!-- 步骤说明在首包 ol/li（可抓） -->\n"
            "<ol>\n"
            "  <li><p>静态申请：分配一段指定大小的内存空间…</p>\n"
            '    <div class="language-mermaid">[object Object]</div>\n'
            "    <!-- 浏览器可见 __ubuf__ half static_buf[1024]；源码是占位 -->\n"
            "  </li>\n"
            "  <li><p>动态申请：…</p>\n"
            '    <div class="language-mermaid">[object Object]</div>\n'
            "  </li>\n"
            "</ol>",
            "caption": "左图步骤+代码都看得见；右边说明在、代码块是 [object Object]。",
        },
        "subcauses": [
            (
                "步骤内代码未写成可读文本",
                "打开 CANN「内存层级」页，浏览器能看到静态申请示例（如 __ubuf__ half static_buf[1024]），但「查看网页源代码」里对应位置常是 language-mermaid / code 的 [object Object]，禁 JS 时抄不出步骤内代码",
                "步骤内代码块 SSR 为 pre/code 纯文本（或可解码的源码节点）；禁把示例渲染成 [object Object] 占位",
                {
                    "title": "证据 · 步骤内代码本来应该长这样",
                    "code_label": "期望写进网页的示例（示意）",
                    "code": "<pre><code class=\"language-cpp\">__global__ void add_custom(...)\n"
                    "{\n"
                    "    __ubuf__ half static_buf[1024];\n"
                    "    ...\n"
                    "}</code></pre>",
                    "caption": "步骤里的示例必须是可读源码，不能只在浏览器里画出来。",
                },
            ),
            (
                "标题说明已在，代码缺失，形成半成品",
                "同一页上，ol/li 已能抓到「静态申请 / 动态申请」说明，按步骤名复述没问题；缺的是步骤内可复制代码。所以问「两步标题是什么」大致能答，问「静态申请示例开头几行」就失败——发现步骤与交付示例不同步",
                "步骤标题、说明与示例代码同批 SSR；勿只保证 ol/li 文案，而把代码块留给客户端或错误序列化",
            ),
            (
                "也没有 MD / llms 平行步骤+代码",
                "页面步骤代码读不到时，如果 Markdown 或 llms.txt 里也没有按步写出「标题 + 说明 + 代码块」，AI 就只剩步骤名可猜，补不出可引用示例",
                "在 MD / llms 临时平铺逐步标题、短说明与关键代码；页面 SSR 达标后以页面为准，去掉重复维护",
            ),
        ],
        "preview_url": SIMT_MEMORY,
    },
    "onavigation": {
        "title_short": "主导航链接可发现性",
        "badge_class": "badge-should",
        "badge_text": "部分可抓",
        "term": "主导航链接可发现性",
        "definition": "顶栏/主导航中的信息架构入口是否以真实链接写入 HTML；语言、主题等纯交互可弱化入库",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "社区首页顶栏为 o-nav-* 体系；右侧「文档 / 在线开发 / 下载」为高频导流",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，昇腾社区主导航里，从首页能进「文档/开发者/下载」的官方链接文案和地址分别是什么？',
        "prompt_plain": f"我在看社区首页（{HOME}），昇腾社区主导航里，从首页能进「文档/开发者/下载」的官方链接文案和地址分别是什么？",
        "answer": "顶栏文案我能读到。一级里多数是 div 无 href，只有「支持与服务」→ /support；右侧「文档」→ /zh/document 可跟，但「在线开发」是无 href 的 a、「下载」是 div，列不出完整的「文档 / 开发者 / 下载」官方地址清单。",
        "insights": [
            ("友商顶栏可抓全", "Mintlify navbar、NVIDIA en-sg global-nav 一级与子项 href 均在首包"),
            ("一级多缺 href", "产品 / 解决方案 / 开发者与合作伙伴 为 div.o-nav-item-link，无 href"),
            ("导流半成品", "文档 → /zh/document 可跟；在线开发无 href；下载为 div"),
        ],
        "root_cause": "人在浏览器里能看见顶栏「产品 / 文档 / 在线开发 / 下载」等入口，但「查看网页源代码」里多数一级项是没有 href 的 div；「在线开发」「下载」也跟不到官方地址——AI 看得见文案，列不全可跟链清单",
        "root_evidence": {
            "title": "实测证据 · 浏览器顶栏 vs 静态源码",
            "shot": "assets/cases-html-ascend/home-top-nav.png",
            "shot_alt": "社区首页浏览器可见顶栏文档 / 在线开发 / 下载",
            "shot_label": "浏览器里能看见的顶栏入口",
            "code_label": "「查看网页源代码」里多数跟不到",
            "code": "<!-- 一级：文案在，地址不在 -->\n"
            '<div class="o-nav-item-link" title="产品"><span>产品</span></div>\n'
            '<div class="o-nav-item-link" title="解决方案">…</div>\n'
            '<a class="o-nav-item-link" href="/support">支持与服务</a>\n'
            "\n"
            "<!-- 右侧高频：文档可跟；另两项不行 -->\n"
            '<a class="doc-btn" href="/zh/document">文档</a>\n'
            '<a class="develop-btn" target="_blank"><span>在线开发</span></a>\n'
            "<!-- ↑ 无 href -->\n"
            '<div class="app-header-download-val">下载</div>',
            "caption": "左图人眼能点；右边源码里产品等无链，「在线开发 / 下载」也跟不到。",
        },
        "subcauses": [
            (
                "一级入口多为 div，没有 href",
                "打开社区首页，用「查看网页源代码」核对：o-nav 里「产品」「解决方案」「开发者与合作伙伴」是 div.o-nav-item-link，只有「支持与服务」→ /support。浏览器看得见文案，禁 JS 时跟不到落地页——友商 Mintlify Documentation / Get started、NVIDIA Shop / Drivers 在源码里就是 a[href]",
                "每一级站点入口一律用 OLink / a[href] 输出，文案与目标地址同时写进首包 HTML",
                {
                    "title": "证据 · 一级入口本来应该长这样",
                    "code_label": "期望写进网页的一级导航（示意）",
                    "code": '<nav class="o-nav-head">\n'
                    '  <a href="/product">产品</a>\n'
                    '  <a href="/solutions">解决方案</a>\n'
                    '  <a href="/developer">开发者与合作伙伴</a>\n'
                    '  <a href="/support">支持与服务</a>\n'
                    "</nav>",
                    "caption": "文案可以保留；底层必须是可跟的 a[href]，不能用 div 冒充。",
                },
            ),
            (
                "高频导流半成品：文档可跟，开发 / 下载不行",
                "探针问「文档 / 开发者 / 下载」时，源码里「文档」已有 a[href=/zh/document]，但「在线开发」是无 href 的 a、「下载」是 app-header-download-val 的 div。三件套对不齐，只能答出文档一条——形成半成品发现层",
                "「在线开发」「下载」改为带真实落地 URL 的顶栏 a[href]；若下载是下拉，面板内每一项也须首包写出完整链接，不要等点击才挂",
                {
                    "title": "证据 · 右侧三项实测对照",
                    "code_label": "实测源码摘录",
                    "code": '<!-- ✓ --> <a class="doc-btn" href="/zh/document">文档</a>\n'
                    '<!-- ✗ --> <a class="develop-btn" target="_blank">在线开发</a>\n'
                    "<!-- ✗ --> <div class=\"app-header-download-val\">下载</div>",
                    "caption": "有一项可跟不算达标；探针要的三件套须都能跟到官方地址。",
                },
            ),
            (
                "也没有备用的站点入口清单",
                "顶栏读不全时，如果 llms.txt 或站点地图里也没有列出「文档 / 开发者 / 下载」等官方入口链接，AI 就只剩当前页零散文案，没有退路补齐发现层",
                "在 llms.txt 显式列出顶栏关键入口（文案 + URL），与顶栏 SSR 双轨互证；页面达标后以页面为准",
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
        "desc_extra": "首页页脚五列 + 底栏法律链；友商表三站均已可抓全",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，页脚「关于昇腾 / 法律声明 / 联系我们」分别链到哪些官方 URL？',
        "prompt_plain": f"我在看社区首页（{HOME}），页脚「关于昇腾 / 法律声明 / 联系我们」分别链到哪些官方 URL？",
        "answer": "可以。页脚五列与底栏链都在首包：例如「关于昇腾」下昇腾计算产业概述 → /ecosystem/industry，法律声明 → /zh/legal/law，联系我们 → https://www.huawei.com/cn/contact-us。友商表判可抓全。若日后改版把页脚改回脚本注入，或 llms 未收录这些 URL，仍可能对不齐站图。",
        "insights": [
            ("三站均可抓全", "Mintlify / NVIDIA / 昇腾 footer 多列 href 均在首包"),
            ("页脚补顶栏", "顶栏缺链的文档 / 法律 / 支持入口，常在页脚才完整可跟"),
            ("html≠入库永不过期", "须守列名，并与 llms 互证"),
        ],
        "root_cause": "人在浏览器里滚到页脚能看见五列入口，「查看网页源代码」里列名与 a[href] 也都在——本页已可抓全；页脚仍是顶栏之外的第二发现层，一旦改版退化、列名漂移或 llms 未收录，Agent 仍会漏答探针问句",
        "root_evidence": {
            "title": "实测证据 · 页脚已在首包（可抓全）",
            "code_label": "「查看网页源代码」摘录（禁 JS 亦可跟）",
            "code": '<div class="footer-main">\n'
            '  <div class="link-group">\n'
            '    <h4 class="gp-name">关于昇腾</h4>\n'
            '    <a class="gp-link" href="/ecosystem/industry">昇腾计算产业概述</a>\n'
            "    …\n"
            "  </div>\n"
            '  <div class="link-group">\n'
            '    <h4 class="gp-name">支持与服务</h4>\n'
            '    <a href="/zh/document">文档</a>\n'
            '    <a href="/zh/feedback">技术工单</a>\n'
            "    …\n"
            "  </div>\n"
            "  …共五列…\n"
            "</div>\n"
            '<a href="/zh/legal/law">法律声明</a>\n'
            '<a href="/zh/legal/privacy">隐私政策</a>\n'
            '<a href="https://www.huawei.com/cn/contact-us">联系我们</a>',
            "caption": "与顶栏不同：页脚列名 + 链接已在源码。根因区重点是守住，并补 llms 互证。",
        },
        "subcauses": [
            (
                "当前已达标，须防改版退化",
                "打开社区首页，用「查看网页源代码」核对：footer-main 五列（关于昇腾 / 新闻与活动 / 交流与资讯 / 支持与服务 / 开源社区）与底栏法律声明 / 隐私政策 / 联系我们均带真实 href，友商表判「可抓全」。风险不在当前快照，而在后续改版若改成等 JavaScript 填充、或只剩社交图标无文字链，html 抓取会退化到顶栏同级问题",
                "维持每一列 gp-name + gp-link 服务端输出 a[href]；改版后复测本页探针，确保仍禁 JS 可答「法律声明 / 联系我们链到哪」",
                {
                    "title": "证据 · 探针问句在源码里可直接答",
                    "code_label": "实测可跟链（示意）",
                    "code": "关于昇腾 → /ecosystem/industry（列内链）\n"
                    "法律声明 → /zh/legal/law\n"
                    "联系我们 → https://www.huawei.com/cn/contact-us",
                    "caption": "当前快照能答满探针；改版后应用同一问句回归。",
                },
            ),
            (
                "页脚是顶栏缺口的第二发现层，列名漂移会错位",
                "顶栏一级多缺 href（见 ONavigation），文档 / 法律 / 支持等入口常靠页脚才完整可跟。html 可抓全不代表入库后永不过期：若「关于昇腾 / 支持与服务」等列名或锚文本随营销改版，已入库旧 chunk 对不上当前 HTML，Agent 检索会漏",
                "列名与关键锚文本保持稳定；必须改版时在 llms 或 changelog 写明新旧映射，并触发知识库重抓",
            ),
            (
                "也须与 llms 互证",
                "探针答案已在页脚 HTML；但若 llms.txt / sitemap 未收录这些 URL，仅靠 RAG 检索的 Agent 仍可能漏入口——这不反映在友商表「html 可抓取」列",
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
        "desc_extra": "首页首屏轮播各帧 CTA 多为 button.o-btn，无 href",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，首页上「立即查看 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。',
        "prompt_plain": f"我在看社区首页（{HOME}），首页上「立即查看 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。",
        "answer": "首屏轮播各帧标题我能读到（如「昇腾AI创新大赛2026」），但 CTA 是 button.o-btn.banner-actions-item，源码没有 href，跳转靠脚本。静态抓取给不出「了解更多 / 立即查看」的官方落地 URL，只能复述按钮文案。",
        "insights": [
            ("友商 CTA 可抓全", "Mintlify Get started、NVIDIA en-sg Read Blog 等首包有真实 href"),
            ("首页 banner 无 href", "立即查看 / 了解更多等为 button.o-btn，静态看不到落地 URL"),
            ("半成品", "帧标题在首包，CTA 地址不在——看得见活动名、跟不到报名/详情页"),
        ],
        "root_cause": "人在浏览器里能看见首屏「了解更多 / 立即查看」等按钮，但「查看网页源代码」里它们是没有 href 的 button，跳转靠 JavaScript——AI 只能复述文案，给不出官方落地 URL；友商 Mintlify Get started、NVIDIA en-sg Read Blog 在源码里就是 a[href]",
        "root_evidence": {
            "title": "实测证据 · 浏览器 CTA vs 静态源码",
            "shot": "assets/cases-html-ascend/home-banner-slides.jpg",
            "shot_alt": "社区首页首屏轮播浏览器可见了解更多按钮",
            "shot_label": "浏览器里能看见的跳转按钮",
            "code_label": "「查看网页源代码」里没有落地地址",
            "code": "<!-- 帧文案在首包，CTA 却是 button 无 href -->\n"
            '<p class="banner-title">昇腾AI创新大赛2026</p>\n'
            "<p>非同凡响 我要去闯</p>\n"
            '<button type="button" class="o-btn banner-actions-item">了解更多</button>\n'
            "<!-- ✗ 无 href；跳转靠 data-ha-clickid + JS -->",
            "caption": "左图人眼能点；右边源码只有按钮文案，没有官方 URL。",
        },
        "subcauses": [
            (
                "跳转型 CTA 写成了 button 伪链",
                "打开社区首页，用「查看网页源代码」核对：首屏 the-carouse-banner 各帧 CTA（了解更多 / 立即查看 / 立即填写 / 前往认证 / 立即参与等）都是 `button.o-btn.banner-actions-item`，带 data-ha-clickid，没有 href。探针问「带到哪个官方 URL」时只能复述文案——友商 Mintlify「Get started」、NVIDIA en-sg「Read Blog」在源码里就是可跟的 a[href]",
                "跳转型 CTA 一律用 OLink 或 `a[href]` + 可见文案；样式可保留按钮外观，底层须输出可爬 href",
                {
                    "title": "证据 · 跳转 CTA 本来应该长这样",
                    "code_label": "期望写进网页的首屏 CTA（示意）",
                    "code": '<p class="banner-title">昇腾AI创新大赛2026</p>\n'
                    '<a class="o-btn banner-actions-item" href="/activity/…">了解更多</a>\n'
                    "<!-- 文案 + 真实落地地址同时进首包 -->",
                    "caption": "看起来仍可像按钮；禁 JS 时也能跟到官方页。",
                },
            ),
            (
                "帧文案在、落地地址不在，形成半成品",
                "同一轮播里，各帧 banner-title / 副文案和 indicator（昇腾AI创新大赛2026 / 推理开发者认证等）已经写进首包，活动名能抓到；缺的是 CTA 的目标 URL。所以 Agent 可能答得出「有一场创新大赛」，却答不出「了解更多链到哪」——发现入口和落地页不同步",
                "标题与 CTA href 同批 SSR；勿只 SSR 营销文案，而把跳转留给点击后的脚本",
                {
                    "title": "证据 · 半成品对照",
                    "code_label": "实测：文案 ✓ · 地址 ✗",
                    "code": "<!-- ✓ 在首包 -->\n"
                    '<p class="banner-title">昇腾AI创新大赛2026</p>\n'
                    "<!-- ✗ 不在首包 -->\n"
                    '<button type="button" class="o-btn">了解更多</button>\n'
                    "<!-- 无对应 a[href=活动详情页] -->",
                    "caption": "有活动名不等于 CTA 可达；两边要一起进源码。",
                },
            ),
            (
                "跳转与操作按钮未分流，且无备用落地清单",
                "无 href 的「了解更多」若与「提交 / 关闭 / 我知道了」一类纯操作词混排入库，Agent 会把操作提示或空 CTA 文案当成可引用入口。同时若 llms.txt 也未列出各帧活动 / 认证的官方 URL，顶栏与页脚又补不全时，就没有退路",
                "跳转 CTA 输出 a[href]；纯操作 button 标 data-llm-exclude 或管道剥离。llms 可临时列出首屏关键活动落地链，页面 CTA SSR 达标后以页面为准",
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
        "desc_extra": "「大语言模型训练用户旅程」矩阵：浏览器可见链，首包无 a[href]，label+link 在 application/json",
        "prompt": f'我在看 <a href="{TRAINING_DEV}" target="_blank" rel="noopener">训练开发</a>（tab=tab1），「大语言模型训练用户旅程」表格里「软件介绍 / 安装指导 / 快速入门」这些链接的 href 原文是什么？有没有 javascript:void 或空链？',
        "prompt_plain": f"我在看训练开发（{TRAINING_DEV}），「大语言模型训练用户旅程」表格里「软件介绍 / 安装指导 / 快速入门」这些链接的 href 原文是什么？有没有 javascript:void 或空链？",
        "answer": "浏览器里矩阵「软件介绍 / 安装指导 / 快速入门」等带外链图标、看起来可点；但「查看网页源代码」里 tab-content 挂载点是空的，首包没有 a[href]。label+link 写在 hcomponent-ascend-user-journey 的 application/json 里，我只能从 JSON 片段复述地址，无法像正文 OLink 那样直接列出可跟链。",
        "insights": [
            ("友商正文链可抓全", "Mintlify Related topics、NVIDIA Quick Links 首包有 a[href]"),
            ("旅程矩阵无 a 节点", "训练开发页 label+link 只在 application/json；tab-content 空壳"),
            ("半成品", "JSON 里可能有 URL，但不是可跟的 a[href] 发现层"),
        ],
        "root_cause": "人在浏览器里能看见「大语言模型训练用户旅程」矩阵里的可点链，但「查看网页源代码」里几乎没有这些 a[href]——挂载点是空的，地址藏在 application/json 脚本里，要等 JavaScript 跑完才画出来，所以爬虫和 AI 默认跟不到官方落地页",
        "root_evidence": {
            "title": "实测证据 · 浏览器矩阵 vs 静态源码",
            "shot": "assets/cases-html-ascend/training-journey-matrix.jpg",
            "shot_alt": "训练开发页浏览器可见大语言模型训练用户旅程矩阵",
            "shot_label": "浏览器里能看见的旅程矩阵链",
            "code_label": "「查看网页源代码」里没有可跟 a[href]",
            "code": "<!-- 挂载点空壳：无矩阵 a[href] -->\n"
            '<div class="tab-content" id="vue_…"></div>\n'
            "\n"
            "<!-- 地址只在脚本数据里： -->\n"
            '<script type="application/json">\n'
            '{"title":"大语言模型训练用户旅程","data":[{\n'
            '  "columns":[{"label":"软件介绍",\n'
            '    "link":"https://gitcode.com/…/introduction.md"},\n'
            '    {"label":"安装指导","link":"…/install_guide.md"}]\n'
            "}]}\n"
            "</script>",
            "caption": "左图人眼能点；右边源码没有 a 标签，只有 JSON 里的 link 字段。",
        },
        "subcauses": [
            (
                "矩阵链没有写进网页源码",
                "打开训练开发页（tab=tab1），用「查看网页源代码」核对：hcomponent-ascend-user-journey 的 tab-content 几乎是空的。浏览器看得见「软件介绍 / 安装指导 / 快速入门」等带外链图标的格子，但要等脚本跑完才渲染——禁 JS 时列不出可跟链，也答不出探针要的 href 原文。友商 Mintlify Related topics、NVIDIA Quick Links 在源码里就是 a[href]",
                "矩阵内每一格导流链直接写成 OLink 或 `a[href]` + 可见文案进首包；展开收起不能代替链接",
                {
                    "title": "证据 · 矩阵链本来应该长这样",
                    "code_label": "期望写进网页的旅程矩阵（示意）",
                    "code": '<table class="user-journey">\n'
                    "  <tr>\n"
                    '    <td><a href="https://gitcode.com/…/introduction.md">软件介绍</a></td>\n'
                    '    <td><a href="…/install_guide.md">安装指导</a></td>\n'
                    '    <td><a href="…/quick_start.md">快速入门</a></td>\n'
                    "  </tr>\n"
                    "</table>",
                    "caption": "每格不同地址是对的；缺的是把它们写成真正的 a[href]。",
                },
            ),
            (
                "地址只在 JSON 里，形成半成品",
                "application/json 里往往已有 label + link（如 MindSpeed-LLM introduction.md、install_guide.md），数据并非完全缺失；缺的是首包 DOM 上的可跟 a 节点。标准 HTML 抓取 / 禁 JS 管道读不到这些链，只能靠特判解析脚本——和友商「源码即链」不在同一发现层",
                "JSON 若作数据源，构建时仍须把每条 link SSR 成可见 a[href]；勿把脚本数据当作唯一发现层",
                {
                    "title": "证据 · JSON 有地址 ≠ 可跟链",
                    "code_label": "实测脚本摘录（示意）",
                    "code": '{"label":"软件介绍",\n'
                    ' "link":"https://gitcode.com/Ascend/MindSpeed-LLM/…/introduction.md"}\n'
                    "<!-- ↑ 字段在；首包无对应 <a href=…>软件介绍</a> -->",
                    "caption": "能从 JSON 抠到 URL，不等于静态抓取能跟链。",
                },
            ),
            (
                "也没有备用的旅程链接清单",
                "矩阵读不到时，如果 llms.txt 或平行 Markdown 里也没有按「新手入门 / 进阶 / 高阶」列出「软件介绍 / 安装指导 / 快速入门」等官方 URL，AI 就只剩当前页零散文案，没有退路补齐发现层",
                "在 llms.txt 或 MD 临时平铺旅程矩阵（阶段名 + 链接）；页面 a[href] SSR 达标后以页面为准",
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
        "desc_extra": "标题旁「更多产品」下拉：浏览器可展开同品类机型，首包仅触发器、无 panel 内 a[href]",
        "prompt": f'我在看 <a href="{CLUSTER}" target="_blank" rel="noopener">集群产品页</a>，标题旁「更多产品」下拉里各款集群/超节点（如 Atlas 900 A2 PoD 集群基础单元、Atlas 900 SuperCluster AI 集群等）对应的落地页 URL 分别是什么？',
        "prompt_plain": f"我在看集群产品页（{CLUSTER}），标题旁「更多产品」下拉里各款集群/超节点（如 Atlas 900 A2 PoD 集群基础单元、Atlas 900 SuperCluster AI 集群等）对应的落地页 URL 分别是什么？",
        "answer": "标题旁我能读到「更多产品」触发器，当前机型名也在；但「查看网页源代码」里没有下拉面板内的各机型 a[href]。禁 JS 时列不出 Atlas 900 A2 PoD、SuperCluster AI 集群等同品类落地 URL——子项要等点击/悬停才挂出来。",
        "insights": [
            ("三站下拉均抓不全", "Mintlify Products mega menu、NVIDIA developer Resources JSON 菜单、昇腾「更多产品」panel 均未 SSR 子链"),
            ("触发器可见、子项丢失", "首包常见「更多产品」文案，panel 内 a[href] 缺失"),
            ("半成品", "当前机型标题在首包，同品类切换清单不在下拉旁"),
        ],
        "root_cause": "人在浏览器里点开「更多产品」能看见同品类机型清单，但「查看网页源代码」里只有触发器文案，没有各子项 a[href]——要等点击或悬停才挂出来，所以爬虫和 AI 默认列不全落地 URL",
        "root_evidence": {
            "title": "实测证据 · 浏览器下拉 vs 静态源码",
            "shot": "assets/cases-html-ascend/cluster-more-products.png",
            "shot_alt": "集群产品页标题旁浏览器可见更多产品触发器",
            "shot_label": "浏览器里能看见的「更多产品」",
            "code_label": "「查看网页源代码」里只有触发器",
            "code": "<!-- 当前机型名 + 触发器在首包 -->\n"
            '<p class="nav-text">Atlas 900 A3 SuperPoD</p>\n'
            '<span class="more-production">更多产品</span>\n'
            "<!-- ✗ 无 dropdown-panel 内各机型 a[href] 列表 -->\n"
            "<!-- 浏览器展开才见：Atlas 900 A2 PoD → /hardware/cluster?tag=900 等 -->",
            "caption": "左图触发器人眼能点；右边源码没有子项链接清单。",
        },
        "subcauses": [
            (
                "下拉子链没有写进网页源码",
                "打开集群产品页，用「查看网页源代码」核对：标题旁只有「更多产品」触发器（more-production），看不到 Atlas 900 A2 PoD / SuperCluster AI 集群等子项的 a[href]。浏览器展开后能点，但要等脚本挂载——禁 JS 时答不出探针要的同品类落地 URL。友商 Mintlify Products mega menu、NVIDIA developer Resources 下拉也是触发器在、子项后挂，同类问题",
                "SSR 输出完整下拉子项：每项可读机型名 + 真实 href；视觉可折叠，DOM 须保留 a 节点",
                {
                    "title": "证据 · 下拉子链本来应该长这样",
                    "code_label": "期望写进网页的「更多产品」面板（示意）",
                    "code": '<div class="more-products-panel">\n'
                    '  <a href="/hardware/cluster?tag=900">Atlas 900 A2 PoD 集群基础单元</a>\n'
                    '  <a href="/hardware/cluster?tag=900ai">Atlas 900 SuperCluster AI 集群</a>\n'
                    "  …\n"
                    "</div>",
                    "caption": "子项可以默认隐藏，但链接必须还在首包里。",
                },
            ),
            (
                "触发器在、清单不在，形成半成品",
                "当前机型标题（如 Atlas 900 A3 SuperPoD）和「更多产品」文案已经写进首包，人知道这是产品切换入口；缺的是面板里的同品类 URL 清单。所以 Agent 可能答得出「这一页是某款超节点」，却答不出「更多产品里还有哪些机型、链到哪」——发现入口和可跟清单不同步。Mintlify 悬停才挂 panel、NVIDIA 从 header-secondary.json fetch 再挂，同属半成品发现层",
                "触发器与子项同批 SSR；勿只输出「更多产品」文案，而把机型列表留给点击后注入",
                {
                    "title": "证据 · 半成品对照",
                    "code_label": "实测：触发器 ✓ · 子项 ✗",
                    "code": "<!-- ✓ --> <span class=\"more-production\">更多产品</span>\n"
                    "<!-- ✗ --> <!-- 无 Atlas 900 A2 PoD / SuperCluster… 的 a[href] 列表 -->",
                    "caption": "有触发器不等于下拉可达；两边要一起进源码。",
                },
            ),
            (
                "也没有备用的同品类产品清单",
                "页内下拉读不到时，如果 llms.txt 或产品目录页也没有按「集群 / 超节点」列出各机型官方 URL，AI 就只剩当前这一款标题，没有退路补齐同品类发现层",
                "在 llms.txt 或产品索引页临时平铺同品类机型（名称 + URL）；页面下拉 SSR 达标后以页面为准",
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
        "aff_note": "映射下载包 / 版本落地页的选型 Toggle（型号 / 架构 / 安装方式等）须把完整 option 矩阵写进首包，本页根因分析主要针对这类；纯表单筛选、不承载包表的 Toggle 入库宜标 data-llm-exclude 或剥离",
        "sample_url": FIRMWARE_DRIVERS,
        "sample_label": "固件与驱动",
        "desc_extra": "产品型号 / 架构 / 安装方式 Toggle：浏览器可见，首包无全量 option，选中态靠 ?ids= 与 __NUXT_DATA__",
        "prompt": f'我在看 <a href="{FIRMWARE_DRIVERS}" target="_blank" rel="noopener">固件与驱动</a>，产品型号 / 架构 / 安装方式等 Toggle 各选项对应的官方下载页或带 <code>ids=</code> 的 URL 分别是什么？',
        "prompt_plain": f"我在看固件与驱动（{FIRMWARE_DRIVERS}），产品型号 / 架构 / 安装方式等 Toggle 各选项对应的官方下载页或带 ids= 的 URL 分别是什么？",
        "answer": "浏览器里能看见型号 / 架构 / 安装方式筛选和当前包列表，但「查看网页源代码」里没有完整 Toggle option 矩阵。URL 上的 ?ids=… 与 __NUXT_DATA__ 只恢复当前选中组合，禁 JS 时列不全全部选项，也给不出各选项对应的官方下载 URL 清单。",
        "insights": [
            ("NVIDIA 矩阵在 props", "CUDA 下载页 OS/Architecture 全树嵌在 data-react-props，禁 JS 可解析"),
            ("昇腾仅当前 ids", "?ids= 编码选中态，首包无 option 文本全表"),
            ("半成品", "当前组合或许能恢复，全量选型矩阵不在发现层"),
        ],
        "root_cause": "人在浏览器里能看见固件与驱动页的型号 / 架构 / 安装方式 Toggle，但「查看网页源代码」里没有完整 option 矩阵——只有 ?ids= 与 __NUXT_DATA__ 恢复当前选中态，AI 列不全全部选项与对应下载 URL；友商 NVIDIA CUDA 下载页虽按钮靠 React 画，但 OS/Architecture 嵌套树已写在首包 data-react-props",
        "root_evidence": {
            "title": "实测证据 · 昇腾无全表 vs 友商首包有树",
            "shot": "assets/cases-html-nvidia/cuda-downloads-toggle.jpg",
            "shot_alt": "NVIDIA CUDA 下载页浏览器可见 Operating System / Architecture Toggle",
            "shot_label": "友商 NVIDIA：浏览器可见的选型 Toggle",
            "code_label": "「查看网页源代码」对照",
            "code": "<!-- ✗ 昇腾固件与驱动：无全量 option 列表 -->\n"
            "…/hardware/firmware-drivers?ids=d802,…,AArch64,online_apt_get\n"
            '<div id="__NUXT_DATA__">…</div>\n'
            "<!-- 浏览器看得见型号/架构/安装方式；源码无完整矩阵 -->\n"
            "\n"
            "<!-- ✓ NVIDIA CUDA：全树在首包 JSON -->\n"
            '<div data-react-class="NestedOptionSelector"\n'
            '     data-react-props=\'{"structure":{\n'
            '       "Linux":{"x86_64":{…},"arm64-sbsa":{…}},\n'
            '       "Windows":{…}},"releases":{…}}\'></div>',
            "caption": "左图友商 Toggle 人眼可见，且全树在源码 JSON；昇腾侧源码只有当前 ids，没有全表。",
        },
        "subcauses": [
            (
                "选型 option 矩阵没有写进网页源码",
                "打开固件与驱动页，用「查看网页源代码」核对：看不到产品型号 / 架构 / 安装方式的完整 option 文本列表。浏览器里能点切换，但选项要等脚本按当前 ?ids= 恢复——禁 JS 时枚举不了矩阵，也答不出探针要的「各选项对应下载 URL」。友商 NVIDIA CUDA 把 Operating System / Architecture 及嵌套 Distribution→Version→Installer 写在 data-react-props，禁 JS 仍可解析",
                "SSR 全量 Toggle option（可读 label + ids 或落地 href）；或像 NVIDIA 一样把完整矩阵 JSON 写进首包 data-*，并文档化解析方式",
                {
                    "title": "证据 · 矩阵本来应该长这样",
                    "code_label": "期望写进网页的选型矩阵（示意）",
                    "code": '<div class="download-toggles">\n'
                    '  <button type="button" data-ids="…">型号 A</button>\n'
                    '  <button type="button" data-ids="…">型号 B</button>\n'
                    "  …架构 / 安装方式同理…\n"
                    '  <a href="…/firmware-drivers?ids=…">当前组合包表</a>\n'
                    "</div>\n"
                    "<!-- 或首包 JSON：{options:[…], packages:[…]} -->",
                    "caption": "未选中项可以藏起来，但全量选项与映射必须还在首包。",
                },
            ),
            (
                "?ids= 只表达当前选中，形成半成品",
                "URL 上的 ?ids=d802,…,AArch64,online_apt_get 能恢复「此刻选了什么」，甚至 __NUXT_DATA__ 里可能带当前包片段；缺的是「还有哪些型号 / 架构 / 安装方式可选」的全表。所以 Agent 或许能描述当前组合，却列不出完整选型空间——发现层半成品。NVIDIA 用 target_os / target_arch 映射选中态，同时 structure 里仍有全树，两边齐全",
                "每项 option 附带人类可读 label 与 canonical URL（或 ids→包表映射）；勿只用编码 ids 承载信息架构",
                {
                    "title": "证据 · 当前 ids ≠ 全量矩阵",
                    "code_label": "实测选中态摘录",
                    "code": "?ids=d802,…,AArch64,online_apt_get\n"
                    "<!-- ↑ 当前组合编码 -->\n"
                    "<!-- ✗ 首包无：还有哪些型号 / 架构 / 安装方式？各对应哪张包表？ -->",
                    "caption": "能恢复选中态，不等于选型矩阵可发现。",
                },
            ),
            (
                "也没有备用的版本矩阵清单",
                "Toggle 读不全时，如果 llms.txt 或下载说明 MD 里也没有按「型号 × 架构 × 安装方式」列出选项与包 URL，AI 就只剩当前 ids 片段，没有退路补齐选型发现层",
                "在 llms.txt 或平行 MD 临时平铺版本矩阵（选项名 + ids/URL）；页面 option SSR 或首包 JSON 达标后以页面为准",
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
        "aff_note": "要做亲和的是「可搜索文档的发现层」（独立 URL + sitemap / llms），不是搜索框本身；输入框、结果列表、搜索 API 为纯交互黑盒，入库宜标 data-llm-exclude 或剥离",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "顶栏搜索（如 mindie 占位）三站实测皆抓不全；发现层须靠可爬 URL 与清单兜底",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，不用搜索框，能否从静态 HTML 列出所有 CANN 安装文档的官方 URL？',
        "prompt_plain": f"我在看社区首页（{HOME}），不用搜索框，能否从静态 HTML 列出所有 CANN 安装文档的官方 URL？",
        "answer": "不能只靠搜索框。顶栏搜索是纯交互，结果由 JS 返回，「查看网页源代码」里没有可枚举的文档命中列表——Mintlify、NVIDIA、昇腾三站搜索框实测皆抓不全。要不搜索也能列出 CANN 安装文档，须每篇有独立可爬 URL，并进 sitemap / llms 清单。",
        "insights": [
            ("三站搜索皆黑盒", "Mintlify Cmd+K、NVIDIA build 搜索、昇腾顶栏搜索：结果 JS 返回"),
            ("发现层不在搜索框", "亲和责任在独立 URL + sitemap / llms"),
            ("控件可 exclude", "搜索 UI 文案勿当正文知识入库"),
        ],
        "root_cause": "人在浏览器里能看见搜索框、也能搜出文档，但「查看网页源代码」里没有搜索结果清单——结果靠 JavaScript 返回，对爬虫是黑盒；若发现层只靠搜索、缺少可爬 URL 与 sitemap / llms，Agent 禁 JS 时就枚举不到全部文档",
        "root_evidence": {
            "title": "实测证据 · 浏览器搜索框 vs 静态源码",
            "shot": "assets/cases-html-ascend/home-top-nav.png",
            "shot_alt": "社区首页顶栏浏览器可见搜索框",
            "shot_label": "浏览器里能看见的搜索框",
            "code_label": "「查看网页源代码」里没有结果清单",
            "code": "<!-- 顶栏常见只有输入框 / 占位文案 -->\n"
            '<input type="search" placeholder="搜索…" />\n'
            "<!-- 或 mindie 等占位提示 -->\n"
            "\n"
            "<!-- ✗ 无：命中文档标题 + a[href] 结果列表 -->\n"
            "<!-- 结果要等 JS 请求搜索 API 后才出现 -->\n"
            "\n"
            "<!-- ✓ 发现层应在别处： -->\n"
            "<!-- sitemap.xml / llms.txt 列出各文档 URL -->\n"
            '<!-- 或导航 / 索引页 <a href="…/install/…">安装文档</a> -->',
            "caption": "左图人眼能搜；右边源码没有可枚举命中列表——搜索框本身不必改成可爬，缺的是 URL 清单。",
        },
        "subcauses": [
            (
                "搜索结果没有写进网页源码",
                "打开社区首页（及友商 Mintlify 文档站、NVIDIA build），用「查看网页源代码」核对：顶栏只有搜索输入框或占位文案，没有「标题 + 落地 URL」的命中列表。结果由前端请求返回——禁 JS 时既看不到列表，也不能把搜索框当成文档发现层。三站友商表均判搜索本身「抓不全」，这是预期，不是要把搜索改成 SSR",
                "搜索控件保持交互即可，标 data-llm-exclude 或入库剥离；不要指望把搜索结果列表做成首包可爬正文",
                {
                    "title": "证据 · 三站搜索同属黑盒",
                    "code_label": "友商对照（摘要）",
                    "code": "Mintlify：Search or ask / Ask Assistant → JS 返回\n"
                    "NVIDIA build：Search for models… → 客户端渲染\n"
                    "昇腾：顶栏搜索（mindie 占位）→ 结果靠 JS\n"
                    "<!-- 共性：源码无静态命中清单 -->",
                    "caption": "抓不全的是搜索产出；亲和要做的是旁边的发现层。",
                },
            ),
            (
                "有搜索框、无可枚举文档清单，形成半成品",
                "探针问「不用搜索框，能否从静态 HTML 列出全部 CANN 安装文档 URL」——若导航 / 索引页也列不全，而文档又只在搜到后才出现，发现层就是半成品：人靠搜索能到，Agent 禁 JS 枚举不到。搜索框在、sitemap / llms / 可爬索引不在，等于只给人开了门、没给爬虫地图",
                "每篇可搜索文档提供独立、稳定、可跟链的 URL；构建时生成 sitemap.xml，并维护 llms.txt / llms-full.txt 全量清单；搜索仅作人用补充",
                {
                    "title": "证据 · 发现层本来应该长这样",
                    "code_label": "期望的不靠搜索也能枚举的清单（示意）",
                    "code": "# llms.txt / sitemap 摘录\n"
                    "https://www.hiascend.com/document/…/install/…\n"
                    "https://www.hiascend.com/document/…/cann/…\n"
                    "…\n"
                    "<!-- 或索引页： -->\n"
                    '<nav aria-label="文档索引">\n'
                    '  <a href="…/install/…">CANN 安装</a>\n'
                    "</nav>",
                    "caption": "清单在 sitemap / llms / 索引页；不在搜索结果 DOM 里。",
                },
            ),
            (
                "检索范围与控件文案不能代替清单",
                "「搜索 CANN 文档」「mindie」等 placeholder、建议下拉、「搜索 / Ask」按钮若当唯一范围说明或混入知识 chunk，Agent 会把 UI 提示当成索引，并掩盖真正的 URL 清单缺失",
                "文档收录范围写进可引用正文或索引页；搜索控件文案剥离入库。以 sitemap / llms 与页面导航为发现层准绳",
            ),
        ],
        "preview_url": HOME,
    },
    "oselect": {
        "title_short": "选择器选项可抓性",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "aff_note": "映射下载 / 版本文档的 Select 选项须进首包（可读 label + ids/URL）；纯表单筛选入库剥离",
        "term": "选择器选项可抓性",
        "definition": "若选项映射文档/版本，选项文本与对应页应可抓；纯表单选择则不必入库",
        "sample_url": FIRMWARE_DRIVERS,
        "sample_label": "固件与驱动",
        "desc_extra": "固件与驱动页含产品型号/架构/安装方式 Select 筛选；静态未见完整 option",
        "prompt": f'我在看 <a href="{FIRMWARE_DRIVERS}" target="_blank" rel="noopener">固件与驱动</a>，产品型号 / 架构 / 安装方式等 Select 下拉里每个选项对应的官方下载页或带 <code>ids=</code> 的 URL 是什么？',
        "prompt_plain": f"我在看固件与驱动（{FIRMWARE_DRIVERS}），产品型号 / 架构 / 安装方式等 Select 下拉里每个选项对应的官方下载页或带 ids= 的 URL 是什么？",
        "answer": "浏览器里能看见型号 / 架构 / 安装方式筛选和当前包列表，但「查看网页源代码」里没有完整 Select option（实测无 select/option 标签）。URL 上的 ?ids=… 与 __NUXT_DATA__ 只恢复当前选中组合，禁 JS 时列不全全部选项，也给不出各选项对应的官方下载 URL 清单。",
        "insights": [
            ("友商版本选择器也抓不全", "NVIDIA Dynamo fern-version-selector：首包仅触发器，versions[] 在 __next_f"),
            ("昇腾仅当前 ids", "?ids= 编码选中态，首包无 option 文本全表"),
            ("半成品", "当前组合或许能恢复，全量选型空间不在发现层"),
        ],
        "root_cause": "人在浏览器里能看见固件与驱动页的型号 / 架构 / 安装方式 Select，但「查看网页源代码」里找不到完整 option——没有可读选项列表，只有 ?ids= 与 __NUXT_DATA__ 恢复当前选中；友商 NVIDIA Dynamo 文档版本选择器同样是首包只有触发器、版本清单藏在脚本 JSON，禁 JS 都列不全",
        "root_evidence": {
            "title": "实测证据 · 浏览器能开下拉 vs 源码无 option",
            "shot": "assets/cases-html-nvidia/dynamo-quickstart-version.png",
            "shot_alt": "NVIDIA Dynamo 文档页浏览器可见版本选择器下拉",
            "shot_label": "友商同类：浏览器可见的版本 Select",
            "code_label": "「查看网页源代码」对照",
            "code": "<!-- ✗ 昇腾固件与驱动：无 <select>/<option> 全表 -->\n"
            "…/hardware/firmware-drivers?ids=d802,…,AArch64,online_apt_get\n"
            '<div id="__NUXT_DATA__">…</div>\n'
            "<!-- 浏览器看得见型号/架构/安装方式；源码无完整 option -->\n"
            "\n"
            "<!-- ✗ NVIDIA Dynamo：首包只有触发器 -->\n"
            '<button class="fern-version-selector" data-state="closed">…</button>\n'
            "<!-- versions[] 在 __next_f JSON，菜单内无 a[href] -->",
            "caption": "左图友商下拉人眼可见；两边源码都缺「选项文本 + 可跟地址」的完整清单。",
        },
        "subcauses": [
            (
                "源码里没有完整的 Select option",
                "打开固件与驱动页，用「查看网页源代码」核对：找不到产品型号 / 架构 / 安装方式的完整 option 文本（实测首包无 select/option 标签）。浏览器里能点开下拉，但选项要等脚本按当前 ?ids= 画出来——禁 JS 时枚举不了矩阵，也答不出探针要的「各选项对应下载 URL」。友商 Dynamo 版本选择器同理：展开后可见 Latest / v1.3.0…，源码里却只有关闭态 button",
                "页面一出来就把全量 option 写进 HTML：每一项都是人类可读 label，并带 ids 或落地 href（原生 select/option，或等价列表链接）；展开动画不能代替选项进首包",
                {
                    "title": "证据 · option 本来应该长这样",
                    "code_label": "期望写进网页的选型 Select（示意）",
                    "code": "<label>产品型号\n"
                    '  <select name="product">\n'
                    '    <option value="d802" data-href="…?ids=d802,…">型号 A</option>\n'
                    '    <option value="…" data-href="…">型号 B</option>\n'
                    "  </select>\n"
                    "</label>\n"
                    "<!-- 架构 / 安装方式同理；或平铺为 a[href] 列表 -->",
                    "caption": "未选中项可以默认收起，但全量 option 与映射必须还在首包。",
                },
            ),
            (
                "?ids= 只表达当前选中，形成半成品",
                "URL 上的 ?ids=d802,…,AArch64,online_apt_get 能恢复「此刻选了什么」，__NUXT_DATA__ 里也可能带当前包片段；缺的是「还有哪些型号 / 架构 / 安装方式可选」的全表。所以 Agent 或许能描述当前组合，却列不出完整选型空间——发现层半成品。Dynamo 侧触发器文案能透露当前版本，versions[] 全表却不在可跟菜单里，同类半成品",
                "每项 option 附带人类可读 label 与 canonical URL（或 ids→包表映射）；勿只用编码 ids / 关闭态按钮文案承载信息架构",
                {
                    "title": "证据 · 当前选中 ≠ 全量 option",
                    "code_label": "实测选中态摘录",
                    "code": "?ids=d802,…,AArch64,online_apt_get\n"
                    "<!-- ↑ 当前组合编码 -->\n"
                    "<!-- ✗ 首包无：还有哪些型号 / 架构 / 安装方式？各对应哪张包表？ -->\n"
                    "\n"
                    "<!-- Dynamo 同类： -->\n"
                    "button[data-state=closed]  <!-- 当前版本文案 -->\n"
                    "<!-- versions[] 在 __next_f，无菜单 a[href] -->",
                    "caption": "能恢复选中态，不等于选项清单可发现。",
                },
            ),
            (
                "也没有备用的选项→包表清单",
                "Select 读不全时，如果 llms.txt 或下载说明 MD 里也没有按「型号 × 架构 × 安装方式」列出选项与包 URL，AI 就只剩当前 ids 片段，没有退路补齐选型发现层",
                "在 llms.txt 或平行 MD 临时平铺选项矩阵（选项名 + ids/URL）；页面 option SSR 达标后以页面为准",
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
        "aff_note": "跳转型手册 / 课程树节点须以「标题 + a[href]」进首包；纯同页折叠树若块正文已 SSR 可读，可另论",
        "term": "树形导航不可抓",
        "definition": "树节点为文档导航时须链接+标题进 HTML；展开子级源码可读或可爬，否则手册结构丢失",
        "sample_url": FAQ,
        "sample_label": "产品形态说明",
        "desc_extra": "FAQ 手册树场景；静态几乎无侧栏 a[href] 树，子级依赖客户端展开与 __NUXT_DATA__",
        "prompt": f'我在看 <a href="{FAQ}" target="_blank" rel="noopener">产品形态说明</a>，手册树里「产品与技术常见问题」下所有叶子文档的标题和 URL 是什么？',
        "prompt_plain": f"我在看产品形态说明（{FAQ}），手册树里「产品与技术常见问题」下所有叶子文档的标题和 URL 是什么？",
        "answer": "浏览器里能看见左侧手册树，但「查看网页源代码」里几乎没有侧栏 a[href] 列表——节点标题与 TOC 多在 __NUXT_DATA__，子级常要点击父节点才挂载。探针问「产品与技术常见问题」下全部叶子文档的标题与 URL 时，禁 JS 枚举不全。友商 Find Training 的 Filters 勾选树、昇腾教学资源课程侧栏同样是首包空壳。",
        "insights": [
            ("友商 Filters 也抓不全", "NVIDIA Find Training：LIBRARIAN 挂载，Introductory 等不在首包"),
            ("昇腾 TOC 在 NUXT", "FAQ / 教学资源侧栏首包几乎无 a[href] 树"),
            ("懒加载断发现层", "子级点击后才挂载，首包列不全叶子"),
            ("半成品", "当前页或许能恢复，整棵分类树不在发现层"),
        ],
        "root_cause": "人在浏览器里能看见左侧手册树，但「查看网页源代码」里几乎没有「标题 + a[href]」的完整节点——树要等 JavaScript 展开才挂出来，章节藏在 __NUXT_DATA__ 里，所以爬虫和 AI 默认沿树枚举不到全部叶子文档",
        "root_evidence": {
            "title": "实测证据 · 浏览器手册树 vs 静态源码",
            "shot": "assets/cases-html-ascend/faq-sidebar.jpg",
            "shot_alt": "昇腾 FAQ 文档页浏览器可见左侧手册树",
            "shot_label": "浏览器里能看见的手册树",
            "code_label": "「查看网页源代码」里几乎没有树节点链接",
            "code": "<!-- 查看网页源代码 / 禁 JS：几乎无手册树 a[href] -->\n"
            "<!-- 仅见零散文档链，例如： -->\n"
            '<a href="…/AscendFAQ/overview/index.html">常见问题</a>\n'
            '<a href="…/hardwaredesc_0001.html">产品形态说明</a>\n'
            "<!-- 无「产品与技术常见问题」下全部叶子标题 + URL 列表 -->\n"
            '<div id="__NUXT_DATA__">…</div>',
            "caption": "左图是人眼看到的树；右边是源码里实际能抠出来的链接——整棵分类树基本不在。",
        },
        "subcauses": [
            (
                "源码里没有完整的树节点链接",
                "打开产品形态说明页，用「查看网页源代码」核对：左侧手册树几乎找不到成排 a[href]。有的节点是要点击才懒加载的子级，有的只是可点文案而不是链接——「产品与技术常见问题」下的叶子文档地址要等脚本跑完才挂出来。禁 JS 时枚举不了该分类下全部标题与 URL。友商 Find Training Filters、教学资源课程侧栏同理：人眼可见树/勾选，首包无完整节点链",
                "页面一出来就把当前手册树写进 HTML：每个叶子（及需要跳转的父节点）都是「标题 + 真实地址」；展开图标可以保留，但不能代替链接；至少 SSR 当前页所在分支，理想全树可读",
                {
                    "title": "证据 · 树节点本来应该长这样",
                    "code_label": "期望写进网页的手册树（示意）",
                    "code": '<nav class="doc-tree">\n'
                    "  <ul>\n"
                    "    <li>产品与技术常见问题\n"
                    "      <ul>\n"
                    '        <li><a href="…/hardwaredesc_0001.html">产品形态说明</a></li>\n'
                    '        <li><a href="…/….html">……其它叶子</a></li>\n'
                    "      </ul>\n"
                    "    </li>\n"
                    "  </ul>\n"
                    "</nav>",
                    "caption": "未展开可以视觉折叠，但标题与 href 必须还在首包。",
                },
            ),
            (
                "脚本数据也补不出整棵分类树",
                "即便从 __NUXT_DATA__ 里抠当前页与上一篇 / 下一篇，也只能拿到邻接节点，看不到「产品与技术常见问题」下其余叶子。懒加载未点开的子树根本不在首包数据里。所以既列不全分类结构，也不能靠这段脚本补出完整发现层——半成品",
                "若脚本数据要作备用，须带完整子节点列表（标题 + URL），不能只有当前页和邻篇；子树勿等点击才请求",
                {
                    "title": "证据 · 邻篇 ≠ 分类全树",
                    "code_label": "页面脚本数据常见形态（示意）",
                    "code": '{\n'
                    '  "finalNodeName": "产品形态说明",\n'
                    '  "finalNodeUrl": "…/hardwaredesc_0001.html",\n'
                    '  "upNodeName": "…",\n'
                    '  "nextNodeName": "…"\n'
                    "}\n"
                    "<!-- ✗ 缺：「产品与技术常见问题」下全部叶子列表 -->",
                    "caption": "能定位当前页，不等于分类树可发现。",
                },
            ),
            (
                "也没有备用的目录清单",
                "手册树读不全时，如果 llms.txt 或 Markdown 里也没有按分类列出叶子标题与 URL，AI 就只知道当前这一页，无法确认「产品与技术常见问题」下还有哪些文档",
                "在 llms.txt 或平行 MD 再列一份嵌套目录（标题 + 链接），和侧栏树互相补上；页面树 SSR 达标后以页面为准",
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
        "aff_note": "作社会证明的评分数字须进首包；「我要评分」等操作 CTA 入库剥离。用户评分 ≠ 官方质量认证，认证说明应写在正文",
        "term": "评分与社会证明",
        "definition": "评分数字若作社会证明可抓；「我要评分」等操作文案入库可剥离",
        "sample_url": EDU_GROWTH,
        "sample_label": "学习路径",
        "desc_extra": "学习路径课程卡可见 5.0 星等评分；首包无 o-rate / 完整卡文案",
        "prompt": f'我在看 <a href="{EDU_GROWTH}" target="_blank" rel="noopener">学习路径</a>，「大模型开发全流程中级」课程卡的平均评分是多少？这个分数是不是官方质量认证？',
        "prompt_plain": f"我在看学习路径（{EDU_GROWTH}），「大模型开发全流程中级」课程卡的平均评分是多少？这个分数是不是官方质量认证？",
        "answer": "浏览器里课程卡能看见 5.0 星、时长与报名人数，但「查看网页源代码」里没有 o-rate，也找不到「大模型开发全流程中级」「5.0」等完整卡文案——课程卡靠脚本注入，禁 JS 时引用不了可证伪的评分数字。即便日后分数进了首包，用户评分也只是社会证明，不是官方质量认证。",
        "insights": [
            ("浏览器有 5.0 星", "学习路径课程卡可见评分 / 时长 / 报名人数"),
            ("首包无 o-rate", "无「大模型开发全流程中级」「5.0」完整卡文案，靠脚本注入"),
            ("分数 ≠ 认证", "用户评分只是社会证明，官方认证须正文另述"),
            ("半成品", "能复述壳层路径名，却给不出可引用评分"),
        ],
        "root_cause": "人在浏览器里能看见学习路径课程卡上的 5.0 星评分，但「查看网页源代码」里没有 o-rate、也抠不出「5.0」——整张课程卡要等 JavaScript 注入才出现，所以爬虫和 AI 默认引用不了社会证明数字；即便分数可读，也不等于官方质量认证",
        "root_evidence": {
            "title": "实测证据 · 浏览器课程卡评分 vs 静态源码",
            "shot": "assets/cases-html-ascend/edu-growth-course-card.png",
            "shot_alt": "学习路径页浏览器可见大模型开发全流程中级课程卡与 5.0 星评分",
            "shot_label": "浏览器里能看见的课程卡评分",
            "code_label": "「查看网页源代码」里没有评分数字",
            "code": "<!-- 查看网页源代码 / 禁 JS：无 o-rate、无「5.0」 -->\n"
            "<!-- /edu/growth 首包可见主题路径导语，课程卡空壳 -->\n"
            '<div class="o-card recommend-ocard">\n'
            '  <div class="o-card-content"><!--v-if--><!-- 空 --></div>\n'
            "</div>\n"
            '<div id="__NUXT_DATA__">…</div>\n'
            "<!-- ✗ 无：大模型开发全流程中级 / 5.0 / 10小时 / 662 -->",
            "caption": "左图是人眼看到的 5.0 星；右边是源码——评分与卡文案基本不在。",
        },
        "subcauses": [
            (
                "源码里没有可引用的评分数字",
                "打开学习路径页，用「查看网页源代码」核对：找不到 o-rate，也搜不到课程卡上的「5.0」。浏览器里「大模型开发全流程中级」卡清楚写着星级，但数字要等脚本把课程卡画出来才出现——探针问平均评分时，禁 JS 给不出可证伪的社会证明数字",
                "若评分作社会证明，页面一出来就把数字写进 HTML（如可读文本或 aria/SSR 的 rate 值）；纯交互打分控件可不入库，但展示用均分须进首包",
                {
                    "title": "证据 · 评分本来应该长这样",
                    "code_label": "期望写进网页的课程卡评分（示意）",
                    "code": '<article class="course-card">\n'
                    "  <h3>大模型开发全流程中级</h3>\n"
                    "  <p>中级课程主要介绍基于 MindSpeed-LLM…</p>\n"
                    '  <p class="rating" data-score="5.0">评分 5.0</p>\n'
                    '  <a href="…/course/…">进入课程</a>\n'
                    "</article>",
                    "caption": "标题、摘要、评分、链接同在首包，才可供引用。",
                },
            ),
            (
                "整张课程卡靠注入，形成半成品",
                "不只是星星：卡标题、标签（CANN / HCCL / 大模型开发）、简介、时长与报名人数也都不在首包。Agent 或许能复述「学习路径 / 大模型开发专区」壳层文案，却列不出具体课程卡，更谈不上引用其评分——发现层半成品",
                "课程列表 SSR：每张卡输出标题 + 短述 + 评分（若展示）+ 落地 a[href]；勿只留 o-card-content 空壳等客户端填充",
                {
                    "title": "证据 · 壳层有、课程卡无",
                    "code_label": "首包可抓 vs 卡内缺失",
                    "code": "<!-- ✓ 壳层 -->\n"
                    "主题路径推荐 / 大模型开发专区 …\n"
                    "<!-- ✗ 卡内 -->\n"
                    "大模型开发全流程中级 · 5.0 · 10小时 · 662\n"
                    "<!-- 上述卡文案首包均不在 -->",
                    "caption": "能介绍专区，不等于课程卡与评分可发现。",
                },
            ),
            (
                "也没有备用清单，且易与官方认证混淆",
                "评分读不全时，如果 llms.txt 或课程说明 MD 里也没有「课程名 + 均分」平行清单，AI 没有退路。即便日后分数进了首包，「我要评分」仍是操作 CTA；用户均分只是社会证明，不能当成官方质量认证唯一依据",
                "在 llms.txt 或平行 MD 临时列出课程名与展示用均分（若对外承诺可引用）；页面 SSR 达标后以页面为准。认证/等级说明写进正文，并过滤「我要评分」等操作文案",
            ),
        ],
        "preview_url": EDU_GROWTH,
    },
    "ocascader": {
        "title_short": "级联选项与路径",
        "badge_class": "badge-should",
        "badge_text": "未测试",
        "untested": True,
        "aff_note": "映射内容路径的级联选项须可读；纯地址 / 表单级联剥离",
        "term": "级联选项与路径",
        "definition": "级联若选文档路径/地域内容，各级选项文本应可抓；纯地址表单则不必入库",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "线上未找到 OCascader / 级联选择组件 DOM 样例，本页标注「未测试」，不做禁 JS 实测与友商对照",
        "prompt": "本次未测试：在昇腾社区线上页面中未定位到 OCascader（级联选择）组件样例，无法锚定 URL 做「各级选项是否对应可访问官方内容 URL」的禁 JS 探针。",
        "prompt_plain": "本次未测试：在昇腾社区线上页面中未定位到 OCascader（级联选择）组件样例，无法锚定 URL 做「各级选项是否对应可访问官方内容 URL」的禁 JS 探针。",
        "answer": "未测试。当前没有可复现的线上 OCascader 样例页，无法判断各级选项是否进首包、是否映射可跟 URL。若日后出现「选路径 / 选分类即跳文档」的级联，再按选项文本可读 + 落地链可证伪重测；纯省市区等地址表单级联不必当知识入库。",
        "insights": [
            ("结论：未测试", "线上未找到 o-cascader / 级联选择 DOM 样例"),
            ("无锚定 URL", "无法做禁 JS 探针与可证伪问句"),
            ("原则仍视情况", "内容路径级联须可读；纯表单级联剥离"),
        ],
        "root_cause": "待测试",
        "subcauses": [],
        "preview_url": None,
        "peer_empty": "线上未找到 OCascader 组件样例，本次未做友商对照实测。",
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
        "aff_note": "版本 / 状态 / 技术栈等语义标签须可读文本进首包，并在正文有定义依据；「热门 / 新品」等营销装饰标签入库剥离",
        "term": "标签语义",
        "definition": "标签若有版本/状态等语义，建议进 HTML 文本；装饰性标签可忽略",
        "sample_url": EDU_GROWTH,
        "sample_label": "学习路径",
        "desc_extra": "学习路径课程卡可见 CANN / HCCL / 大模型开发 等标签；首包无完整卡文案与 tag 文本",
        "prompt": f'我在看 <a href="{EDU_GROWTH}" target="_blank" rel="noopener">学习路径</a>，「大模型开发全流程中级」课程卡上的 CANN / HCCL / 大模型开发 标签分别代表什么官方含义？请引用正文或可抓标签原文。',
        "prompt_plain": f"我在看学习路径（{EDU_GROWTH}），「大模型开发全流程中级」课程卡上的 CANN / HCCL / 大模型开发 标签分别代表什么官方含义？请引用正文或可抓标签原文。",
        "answer": "浏览器里课程卡能看见 CANN / HCCL / 大模型开发 等标签，但「查看网页源代码」里没有这些 tag 文本，也找不到完整卡标题——课程卡靠脚本注入，禁 JS 时既复述不出标签原文，更给不出官方定义依据。友商 Mintlify API 页 Authorization 旁的 string / header / required 标签写在首包 field-info-pill，可直接引用。",
        "insights": [
            ("友商参数标签可抓全", "Mintlify Trigger deployment：string / header / required 在首包"),
            ("昇腾课程卡标签抓不全", "学习路径卡上 CANN / HCCL 等浏览器可见，源码无"),
            ("NVIDIA 教程卡同类", "DGX Spark 卡 tag 首包多为壳层"),
            ("语义 vs 装饰", "技术栈标签宜进首包并有正文定义；营销口号宜剥离"),
        ],
        "root_cause": "人在浏览器里能看见学习路径课程卡上的 CANN / HCCL / 大模型开发 标签，但「查看网页源代码」里抠不出这些字——整张卡要等 JavaScript 注入；即便日后标签进了首包，若只有色块口号、没有正文定义，也容易被当成规格事实误入库",
        "root_evidence": {
            "title": "实测证据 · 浏览器课程卡标签 vs 静态源码",
            "shot": "assets/cases-html-ascend/edu-growth-course-tags.png",
            "shot_alt": "学习路径页浏览器可见大模型开发全流程中级课程卡上的 CANN / HCCL / 大模型开发标签",
            "shot_label": "浏览器里能看见的课程卡标签",
            "code_label": "「查看网页源代码」里没有标签文本",
            "code": "<!-- 查看网页源代码 / 禁 JS：无课程卡 tag -->\n"
            "<!-- /edu/growth 首包可见主题路径导语，课程卡空壳 -->\n"
            '<div class="o-card recommend-ocard">\n'
            '  <div class="o-card-content"><!--v-if--><!-- 空 --></div>\n'
            "</div>\n"
            "<!-- ✗ 无：CANN / HCCL / 大模型开发 -->\n"
            "\n"
            "<!-- ✓ 友商 Mintlify API：参数标签在首包 -->\n"
            '<div data-component-part="field-info-pill"><span>string</span></div>\n'
            '<div data-component-part="field-info-pill"><span>header</span></div>\n'
            '<div data-component-part="field-required-pill">required</div>',
            "caption": "左图是人眼看到的标签；昇腾侧源码没有，友商参数 pill 写在首包。",
        },
        "subcauses": [
            (
                "源码里没有课程卡标签文本",
                "打开学习路径页，用「查看网页源代码」核对：搜不到「大模型开发全流程中级」卡上的 CANN / HCCL / 大模型开发。浏览器看得见色块标签，要等脚本把课程卡画出来——探针问「标签代表什么、原文是什么」时，禁 JS 给不出可引用文本。友商 Mintlify Authorization 的 string / header / required 写在 field-info-pill，禁 JS 仍可读",
                "语义标签（技术栈 / 版本 / 状态 / 必填等）页面一出来就写成可读文本（如 span/o-tag 内文字）；勿只靠客户端往空卡片里灌",
                {
                    "title": "证据 · 标签本来应该长这样",
                    "code_label": "期望写进网页的课程卡标签（示意）",
                    "code": '<article class="course-card">\n'
                    "  <h3>大模型开发全流程中级</h3>\n"
                    '  <ul class="tags">\n'
                    "    <li>CANN</li>\n"
                    "    <li>HCCL</li>\n"
                    "    <li>大模型开发</li>\n"
                    "  </ul>\n"
                    "</article>",
                    "caption": "标签字在首包，才能被引用；定义仍须正文可证伪。",
                },
            ),
            (
                "语义标签与装饰标签未分流",
                "即便标签进了首包，若「CANN」这类技术栈事实和「热门 / 新品」口号画成同级色块，管道会一并入库。探针要的是可证伪含义；营销装饰没有正文依据，不应当官方规格。Mintlify 的 required / string 是参数元数据，和口号 tag 不是一类",
                "语义标签：进首包 + 正文/文档给定义（或链到术语页）；装饰标签：data-llm-exclude 或策展剥离，勿与规格标签混排同级",
                {
                    "title": "证据 · 两类标签不要混成一种事实",
                    "code_label": "分流示意",
                    "code": "<!-- ✓ 语义：可读 + 可定义 -->\n"
                    '<span class="o-tag">CANN</span>  <!-- 正文说明 CANN 是什么 -->\n'
                    "<!-- ✗ 装饰：口号，宜剥离 -->\n"
                    '<span class="o-tag" data-llm-exclude>热门</span>',
                    "caption": "看得见字，不等于可以当规格引用。",
                },
            ),
            (
                "也没有备用的标签释义清单",
                "卡上标签读不全时，如果 llms.txt 或课程说明 MD 里也没有「标签文案 → 官方含义」对照，AI 既没有退路复述标签，也不能核定义。技术栈缩写尤其需要平行释义",
                "在 llms.txt 或平行 MD 临时列出课程卡展示用标签及一句话定义；页面 tag SSR 且正文有依据后以页面为准",
            ),
        ],
        "preview_url": EDU_GROWTH,
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
        "aff_note": "命名变更、开源公告、安装步骤等关键说明勿只放弹层；须进首包或正文双写。纯「知道了」确认框可剥离",
        "term": "对话框隐藏说明",
        "definition": "对话框若含安装步骤等关键说明，须在源码可读或同步到正文页；纯确认框不必入库",
        "sample_url": MINDX,
        "sample_label": "应用使能",
        "desc_extra": "应用使能公告弹层含 Mind 系列开源与模块更名说明；首包仅有「查看公告」短导语",
        "prompt": f'我在看 <a href="{MINDX}" target="_blank" rel="noopener">应用使能</a>，「应用使能公告」里写了哪些开源与命名变更？「应用使能 MindX」现在叫什么？请引用可抓原文。',
        "prompt_plain": f"我在看应用使能（{MINDX}），「应用使能公告」里写了哪些开源与命名变更？「应用使能 MindX」现在叫什么？请引用可抓原文。",
        "answer": "浏览器点「查看公告」能看见弹层：Mind 系列套件全量开源，以及「应用使能 MindX」更名为「应用使能」、「MindX SDK 领域套件」更名为「MindSDK AI应用软件开发套件」等；但「查看网页源代码」里只有短导语与「查看公告」入口，搜不到「应用使能公告」标题、完整更名段落和「知道了」——弹层正文未进首包，禁 JS 引用不了官方命名变更原文。友商 NVIDIA Skills 的 aiq-research 详情弹层同样抓不全。",
        "insights": [
            ("浏览器有完整公告弹层", "开源条目 + MindX→应用使能 / MindSDK 更名"),
            ("首包只有入口短导语", "「Mind系列…全量开源」「查看公告」；无弹层正文"),
            ("NVIDIA Skills 弹层同类", "安装命令与描述靠点开才见，首包多为壳层"),
            ("半成品", "知道有公告，复述不出更名原文"),
        ],
        "root_cause": "人在浏览器里能看见「应用使能公告」弹层里的开源与命名变更说明，但「查看网页源代码」里抠不出这些字——弹层要等点击「查看公告」才挂载；关键规格若只活在默认不可见的对话框里，禁 JS 永远读不到",
        "root_evidence": {
            "title": "实测证据 · 浏览器公告弹层 vs 静态源码",
            "shot": "assets/cases-html-ascend/mindx-announce-dialog.png",
            "shot_alt": "应用使能页浏览器可见应用使能公告弹层与开源、命名变更说明",
            "shot_label": "浏览器里能看见的公告弹层",
            "code_label": "「查看网页源代码」里没有弹层正文",
            "code": "<!-- 查看网页源代码 / 禁 JS：无弹层标题与更名段落 -->\n"
            "<!-- /developer/software/mindx 首包可见入口 -->\n"
            "开源开放 Mind系列应用使能套件全量开源。\n"
            "2025/12/27\n"
            "查看公告\n"
            "<!--teleport start--><!--teleport end-->\n"
            "<!-- ✗ 无：应用使能公告 / 应用使能MindX → 应用使能 / 知道了 -->\n"
            "\n"
            "<!-- 友商 NVIDIA Skills：详情弹层同样不在首包 -->\n"
            "<!-- ✗ 无：aiq-research / npx skills add … -->",
            "caption": "左图是人眼看到的公告；源码只有入口短句，更名说明不在。",
        },
        "subcauses": [
            (
                "源码里没有可引用的弹层正文",
                "打开应用使能页，用「查看网页源代码」核对：搜不到「应用使能公告」，也搜不到「应用使能 MindX」更名为「应用使能」等段落。浏览器点「查看公告」才看见完整说明——探针问开源范围与命名变更时，禁 JS 给不出可引用原文。NVIDIA Skills 点开 aiq-research 的安装命令与描述同理",
                "关键公告 / 命名变更 / 安装步骤页面一出来就写成可读文本（正文段落或 SSR 进首包的 dialog DOM，可用 CSS 隐藏，勿删文本）；勿只靠点击后 teleport/挂载",
                {
                    "title": "证据 · 公告本来应该长这样",
                    "code_label": "期望写进网页的公告（示意）",
                    "code": '<section aria-labelledby="mindx-announce-title">\n'
                    '  <h2 id="mindx-announce-title">应用使能公告</h2>\n'
                    "  <p>2025/12/27 · Mind系列应用使能套件全量开源…</p>\n"
                    "  <p>「应用使能 MindX」更名为「应用使能」；"
                    "「MindX SDK 领域套件」更名为「MindSDK AI应用软件开发套件」。</p>\n"
                    "</section>",
                    "caption": "标题与更名句同在首包，才可供引用；不必先点开弹层。",
                },
            ),
            (
                "关键说明唯一放在默认不可见的对话框",
                "即便日后弹层 DOM 进了首包，若默认 aria-hidden 且管道删除隐藏节点、或文案只在打开态才插入，爬虫仍读不到。命名变更属于规格事实，与「知道了」确认框不同，不能只活在交互层",
                "关键说明：正文双写，或 dialog 内容 SSR 保留文本节点；纯确认 / 礼貌提示标 data-llm-exclude 或策展剥离，勿与规格公告混成同一入库策略",
                {
                    "title": "证据 · 规格弹层 vs 确认框",
                    "code_label": "分流示意",
                    "code": "<!-- ✓ 规格：首包可读（可视觉隐藏） -->\n"
                    '<dialog id="announce">…MindX → 应用使能…</dialog>\n'
                    "<!-- ✗ 仅确认：可剥离 -->\n"
                    '<button data-llm-exclude>知道了</button>',
                    "caption": "看得见的弹层，不等于源码里有可引用规格。",
                },
            ),
            (
                "也没有备用的公告 / 更名清单",
                "弹层读不全时，如果 llms.txt 或平行 MD 里也没有「旧名 → 新名」与开源范围对照，AI 既复述不出公告，也容易继续用 MindX 旧名检索失败",
                "在 llms.txt 或平行 MD 临时列出公告日期、开源范围与模块更名对照；页面弹层/正文 SSR 后以页面为准",
            ),
        ],
        "preview_url": MINDX,
    },
    "ocard": {
        "title_short": "卡片摘要不可抓",
        "badge_class": "badge-should",
        "badge_text": "宜全量文本",
        "aff_note": "导流卡须首包输出标题 + 摘要 + a[href]；列表/Tab 下卡片勿等脚本注入；封面图不能代替文本",
        "term": "卡片摘要不可抓",
        "definition": "卡片标题、摘要、链接须写入 HTML；图需 alt/图注，否则列表发现层不完整",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "「昇腾万里」楼层资讯/活动 Tab 下卡片浏览器可见，首包 o-scroller-container 为空",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，「最新发布 / 精彩活动」等 Tab 下各张卡片的标题、摘要和落地页 URL 是什么？',
        "prompt_plain": f"我在看社区首页（{HOME}），「最新发布 / 精彩活动」等 Tab 下各张卡片的标题、摘要和落地页 URL 是什么？",
        "answer": "浏览器里「昇腾万里」楼层能看见金融 / SWA / CANN 等内容卡，但「查看网页源代码」里 o-tab-nav-list 常为空、pane 内 o-scroller-container 是空壳——卡片要等脚本注入。禁 JS 时列不出标题、摘要与落地 URL。同站开发者页「获取开发资源」三卡（HiDevLab 等）已有 o-card-title + o-card-detail + href，说明卡片可以写进首包；友商 NVIDIA DGX Cloud 四列卡、Mintlify 公司卡也是首包可抓。",
        "insights": [
            ("友商卡片可抓全", "NVIDIA DGX Cloud 四列卡、Mintlify 公司卡 title/说明/链在首包"),
            ("同站资源三卡可抓", "开发者页 HiDevLab 等 o-card-title + detail + href"),
            ("首页资讯卡空壳", "最新发布等 Tab：o-scroller-container 为空，靠脚本注入"),
            ("半成品", "楼层标题在，卡片列表不在发现层"),
        ],
        "root_cause": "人在浏览器里能看见首页资讯 / 活动卡片，但「查看网页源代码」里列表是空的——卡片要等 JavaScript 灌进 o-scroller-container；同站另一些楼层已经把标题 + 摘要 + 链接写进首包，说明不是做不到，而是这批列表卡没 SSR",
        "root_evidence": {
            "title": "实测证据 · 浏览器内容卡 vs 静态源码",
            "shot": "assets/cases-html-ascend/home-news-tabs.jpg",
            "shot_alt": "社区首页昇腾万里楼层浏览器可见最新发布等 Tab 与内容卡片",
            "shot_label": "浏览器里能看见的资讯/活动卡",
            "code_label": "「查看网页源代码」里卡片列表是空的",
            "code": "<!-- 查看网页源代码 / 禁 JS -->\n"
            '<h2 class="sec-title">昇腾万里，让智能无所不及</h2>\n'
            '<div class="o-tab">\n'
            '  <div class="o-tab-nav-list"></div>\n'
            '  <div class="o-tab-pane o-tab-pane-active">\n'
            '    <div class="o-scroller-container"><!--[--><!--]--></div>\n'
            "  </div>\n"
            "</div>\n"
            "<!-- ✗ 无：各卡标题 / 摘要 / a[href] -->\n"
            "\n"
            "<!-- ✓ 同站开发者页资源卡（对照） -->\n"
            '<div class="o-card-title">HiDevLab-在线开发</div>\n'
            '<div class="o-card-detail">…</div>\n'
            '<a href="…">…</a>',
            "caption": "左图是人眼看到的卡片；右边首页源码列表为空，同站另有楼层已写全三要素。",
        },
        "subcauses": [
            (
                "源码里没有卡片列表",
                "打开社区首页，用「查看网页源代码」核对「昇腾万里」楼层：最新发布 / 产业资讯 / 精彩活动 / 官方技术文章 的页签导航常为空，激活 pane 里 o-scroller-container 也是空注释。浏览器看得见的金融 / SWA / CANN 等卡要等脚本注入——探针问各卡标题、摘要、URL 时，禁 JS 列不出。开发者页 HiDevLab 三卡、友商 NVIDIA / Mintlify 导流卡则是标题 + 说明 + 链写在首包",
                "默认 Tab（及需要发现的其它 Tab）把每张卡 SSR 进 HTML：o-card-title + o-card-detail + a[href]；勿只留空 scroller 等客户端填充",
                {
                    "title": "证据 · 卡片本来应该长这样",
                    "code_label": "期望写进网页的内容卡（示意）",
                    "code": '<article class="o-card">\n'
                    '  <a href="/news/…">\n'
                    '    <h3 class="o-card-title">……标题</h3>\n'
                    '    <p class="o-card-detail">一句话摘要</p>\n'
                    "  </a>\n"
                    "</article>",
                    "caption": "未激活 Tab 可以视觉隐藏，但要发现的卡片文本与链接须还在首包。",
                },
            ),
            (
                "有壳无三要素，形成半成品",
                "即便有卡容器，若只有封面图 / icon、没有标题与摘要，或整卡 onclick 没有 a[href]，Agent 要么读不出文案，要么复述得出标题却给不出落地 URL。开发者页部分入口卡只有 resource-card-title + href、缺短述，也属于半成品——和 HiDevLab「title + detail + href」齐全写法不一致",
                "每张导流卡平铺三要素：可读标题 + 一句话摘要 + 真实 a[href]；封面补 alt；禁只用图或整卡脚本跳转代替链接",
                {
                    "title": "证据 · 缺一即残缺",
                    "code_label": "半成品 vs 齐全",
                    "code": "<!-- ✗ 半成品 -->\n"
                    '<div class="card" onclick="go(…)">\n'
                    '  <img src="cover.png" alt="">  <!-- 无标题/摘要/href -->\n'
                    "</div>\n"
                    "<!-- ✓ 齐全 -->\n"
                    '<a class="o-card" href="…">\n'
                    "  <span class=\"o-card-title\">…</span>\n"
                    "  <span class=\"o-card-detail\">…</span>\n"
                    "</a>",
                    "caption": "标题、摘要、链接缺一，发现层就不完整。",
                },
            ),
            (
                "也没有备用的卡片清单",
                "列表卡读不全时，如果 llms.txt 或平行 MD 里也没有「标题 + 摘要 + URL」清单，AI 只剩楼层口号，没有退路补齐资讯/活动发现层",
                "在 llms.txt 或 MD 临时平铺该楼层卡片（标题 + 短述 + 链接）；页面 SSR 达标后以页面为准",
            ),
        ],
        "preview_url": HOME,
    },
    "odatetable": {
        "title_short": "表格语义缺失",
        "badge_class": "badge-bad",
        "badge_text": "忌截图表",
        "aff_note": "规格 / 对照参数须用真实 table/th/td（或平行 Markdown 表）交付；配图大字报与空单元格不能当唯一规格源",
        "term": "表格语义缺失",
        "definition": "规格表须用真实 table/单元格文本，勿截图；表头语义清晰，md 用 Markdown 表",
        "sample_url": CLUSTER,
        "sample_label": "集群产品页",
        "desc_extra": "集群页可见规格摘要与特性卡；缺 Atlas 900 vs 800 对照矩阵，部分规格在配图内",
        "prompt": f'我在看 <a href="{CLUSTER}" target="_blank" rel="noopener">集群产品页</a>，Atlas 900 与 Atlas 800 的 CPU/内存/互联参数对照表原文是什么？请按表头列给出。',
        "prompt_plain": f"我在看集群产品页（{CLUSTER}），Atlas 900 与 Atlas 800 的 CPU/内存/互联参数对照表原文是什么？请按表头列给出。",
        "answer": "浏览器里能看见默认型号的「技术规格」摘要（形态 / NPU / CPU）和「产品特性」大字报，但「查看网页源代码」里没有一张「Atlas 900 | Atlas 800」多列对照表，也搜不到按表头展开的内存 / 互联对照行——摘要表只有单型号一列值，特性要点部分写在 feature PNG 里。友商 NVIDIA CUDA Linux 安装指南 Table 1–4、Mintlify Features 表、昇腾 FAQ 表1 都是真实 th/td，可按行列引用；本页探针要的对照原文给不出。",
        "insights": [
            ("友商规格表可抓全", "CUDA Table 1–4 / Mintlify Features / FAQ 表1 均有 th/td"),
            ("无 900 vs 800 对照表", "首包摘要表仅默认型号一列：形态 / NPU / CPU"),
            ("特性大字报在配图", "feature PNG 承载数字；第三张「超高可靠」等不全"),
            ("半成品", "能复述单型号三行摘要，拼不出对照矩阵"),
        ],
        "root_cause": "人在浏览器里能看见集群页的规格与特性展示，但「查看网页源代码」里抠不出探针要的「Atlas 900 vs Atlas 800 · CPU/内存/互联」对照表——没有多列表头与逐格参数，部分数字还画在配图里，所以 Agent 无法按表头逐格问答",
        "root_evidence": {
            "title": "实测证据 · 浏览器规格展示 vs 静态源码",
            "shot": "assets/cases-html-ascend/cluster-spec-summary.jpg",
            "shot_alt": "集群产品页浏览器可见技术规格摘要表与产品图",
            "shot_label": "浏览器里能看见的规格摘要",
            "code_label": "「查看网页源代码」里没有 900 vs 800 对照矩阵",
            "code": "<!-- 查看网页源代码 / 禁 JS：无 Atlas 900|800 对照表 -->\n"
            "<!-- /hardware/cluster 摘要表仅默认型号一列 -->\n"
            "<table>\n"
            "  <tr><td></td><td><img …产品图></td></tr>\n"
            "  <tr><td>形态</td><td>12 * 计算柜 …</td></tr>\n"
            "  <tr><td>NPU</td><td>最大支持 384 * 昇腾910</td></tr>\n"
            "  <tr><td>CPU</td><td>最大支持 192 * 鲲鹏920</td></tr>\n"
            "</table>\n"
            "<!-- ✗ 无：Atlas 800 列 / 内存行 / 互联行 -->\n"
            "\n"
            "<!-- ✓ 友商 CUDA：多列表格在首包 -->\n"
            "<table><caption>Table 1 Supported Linux Distributions</caption>\n"
            "  <tr><th>Distribution</th><th>Codename</th><th>Architecture</th></tr>\n"
            "  …\n"
            "</table>",
            "caption": "左图是人眼看到的规格区；源码只有单型号三行，对不上「900 vs 800」问句。",
        },
        "subcauses": [
            (
                "源码里没有可引用的对照表",
                "打开集群产品页，用「查看网页源代码」核对：没有「Atlas 900 | Atlas 800」表头，也没有内存 / 互联对照行。摘要 table 只有默认型号一列的形态 / NPU / CPU——探针问两款产品对照原文时，禁 JS 拼不出矩阵。友商 CUDA Table 1–4、FAQ 表1 是完整 th/td，可按行列引用",
                "产品对照写成语义化 HTML table（thead 列型号，tbody 行 CPU/内存/互联等）；每个规格格 SSR 可读文本，勿只留单型号摘要或等 Tab 后再灌",
                {
                    "title": "证据 · 对照表本来应该长这样",
                    "code_label": "期望写进网页的型号对照（示意）",
                    "code": "<table>\n"
                    "  <thead>\n"
                    "    <tr><th>参数</th><th>Atlas 900</th><th>Atlas 800</th></tr>\n"
                    "  </thead>\n"
                    "  <tbody>\n"
                    "    <tr><th scope=\"row\">CPU</th><td>…</td><td>…</td></tr>\n"
                    "    <tr><th scope=\"row\">内存</th><td>…</td><td>…</td></tr>\n"
                    "    <tr><th scope=\"row\">互联</th><td>…</td><td>…</td></tr>\n"
                    "  </tbody>\n"
                    "</table>",
                    "caption": "表头 + 全行单元格同在首包，才能按列问答。",
                },
            ),
            (
                "规格写进配图，表格语义被掏空",
                "「产品特性」浏览器可见超节点架构 / 超强性能等大字报，但关键数字常在 feature PNG 内；静态 HTML 仅部分 bullet，第三张「超高可靠」等还可能缺失。摘要表首行甚至是产品图单元格。图意无法当 th/td 检索，Agent 容易漏数或读成装饰",
                "规格数字与对照项写进 table/段落文本；配图仅装饰时 alt=\"\"，正文或表格复述同一组参数。禁止用截图表代替唯一规格源",
                {
                    "title": "证据 · 图内数字 ≠ 可抓单元格",
                    "shot": "assets/cases-html-ascend/cluster-features.jpg",
                    "shot_alt": "集群产品页产品特性卡与配图大字报",
                    "shot_label": "浏览器里的特性大字报",
                    "code_label": "首包特性区（示意）",
                    "code": '<img src="/_static3/feature26….png" class="o-figure-img">\n'
                    "<div class=\"title\">超节点架构</div>\n"
                    "<p>最大支持384*NPU高速互联…</p>\n"
                    "<!-- 大字报数字在 PNG；缺完整三卡 / 无对照表头 -->",
                    "caption": "看得见的特性图，不等于规格表已入库。",
                },
            ),
            (
                "也没有备用的 Markdown 对照表",
                "HTML 对不上「900 vs 800」时，若文档 MD / llms.txt 里也没有同文案的 Markdown 表，AI 没有退路，只能靠导语碎片猜测参数",
                "在平行 MD 或 llms.txt 镜像一份「表头 + 全行单元格」对照表，与页面承诺一致；页面 table SSR 达标后以页面为准",
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
        "aff_note": "路径节点状态、字段定义等说明勿只放悬停气泡；须进首包或正文双写。装饰性「即将上线」类提示可剥离，但节点名本身若作导航发现层须可读",
        "term": "气泡隐藏说明",
        "definition": "重要说明勿只放悬停/点击气泡；须在页面正文也有一份，否则禁 JS 抓取不到",
        "sample_url": EDU_GROWTH,
        "sample_label": "学习路径",
        "desc_extra": "「探索你的学习路径」应用开发节点悬停可见「内容即将上线」；节点名与气泡说明首包均无",
        "prompt": f'我在看 <a href="{EDU_GROWTH}" target="_blank" rel="noopener">学习路径</a>，「探索你的学习路径」里应用开发下有哪些节点？「AI4S应用」悬停提示写了什么？请引用可抓原文。',
        "prompt_plain": f"我在看学习路径（{EDU_GROWTH}），「探索你的学习路径」里应用开发下有哪些节点？「AI4S应用」悬停提示写了什么？请引用可抓原文。",
        "answer": "浏览器里能看见应用开发下 AI4S应用 / 具身智能 / RAG原理 等节点，悬停 AI4S应用 可出「内容即将上线，敬请期待」；但「查看网页源代码」里只有路径壳层（如「探索你的学习路径」「应用开发」），节点名与气泡文案都不在首包——整块路径图靠脚本注入，禁 JS 既列不全节点，也读不到悬停说明。友商 Mintlify Enterprise 流量图悬停月份气泡（5% agent share / 3.5M / 62.1M）与 NVIDIA DGX Spark 卡 +N 标签溢出气泡同样不在可读 DOM。",
        "insights": [
            ("浏览器有节点 + 气泡", "学习路径应用开发流：AI4S应用 悬停「内容即将上线」"),
            ("首包只有壳层", "探索你的学习路径 / 应用开发 可抓；节点名与气泡无"),
            ("友商图表/标签气泡也抓不全", "Mintlify Enterprise 月份悬停；NVIDIA Spark +N 溢出"),
            ("半成品", "能复述专区名，列不出路径节点与气泡原文"),
        ],
        "root_cause": "人在浏览器里能看见「探索你的学习路径」应用开发下的节点，以及悬停「AI4S应用」时的「内容即将上线，敬请期待」气泡，但「查看网页源代码」里抠不出节点名和气泡字——整块路径要等 JavaScript 注入；重要状态说明若只活在悬停层，禁 JS 永远读不到",
        "root_evidence": {
            "title": "实测证据 · 浏览器路径节点气泡 vs 静态源码",
            "shot": "assets/cases-html-ascend/edu-growth-learning-path.png",
            "shot_alt": "学习路径页浏览器可见探索你的学习路径应用开发节点与内容即将上线气泡",
            "shot_label": "浏览器里能看见的路径节点与气泡",
            "code_label": "「查看网页源代码」里没有节点名与气泡",
            "code": "<!-- 查看网页源代码 / 禁 JS：无路径节点、无气泡文案 -->\n"
            "<!-- /edu/growth 首包可见壳层 -->\n"
            "探索你的学习路径\n"
            "应用开发\n"
            "<!-- ✗ 无：AI4S应用 / 具身智能 / RAG原理 / 内容即将上线，敬请期待 -->\n"
            "\n"
            "<!-- 友商 Mintlify Enterprise：图例可抓，月份气泡文案不可抓 -->\n"
            "Over half your traffic is agents · Agents / Humans\n"
            "<!-- ✗ 无可读：October · 5% agent share · 3.5M / 62.1M -->",
            "caption": "左图是人眼看到的节点与气泡；昇腾与友商图表悬停层，关键数字说明都难在源码直接引用。",
        },
        "subcauses": [
            (
                "源码里没有路径节点与气泡文本",
                "打开学习路径页，用「查看网页源代码」核对：搜不到「AI4S应用」「RAG原理」，也搜不到「内容即将上线，敬请期待」。浏览器看得见节点与悬停气泡，要等脚本把路径图画出来——探针问「有哪些节点、气泡写了什么」时，禁 JS 给不出可引用原文。友商 Mintlify Enterprise 流量图同理：标题与 Agents/Humans 图例在首包，但悬停 October 才出现的「5% agent share / 3.5M / 62.1M」不在可读 DOM",
                "路径节点名与关键状态说明（含即将上线/下线）页面一出来就写成可读文本；勿只靠悬停层或客户端往空壳里灌。装饰气泡可剥离，但节点发现层须进首包",
                {
                    "title": "证据 · 节点与状态本来应该长这样",
                    "code_label": "期望写进网页的路径节点（示意）",
                    "code": '<section aria-label="应用开发学习路径">\n'
                    "  <h3>应用开发</h3>\n"
                    "  <ol>\n"
                    "    <li>AI4S应用 — 内容即将上线，敬请期待</li>\n"
                    "    <li>具身智能</li>\n"
                    "    <li>RAG原理</li>\n"
                    "  </ol>\n"
                    "</section>",
                    "caption": "节点名与状态同在首包，才可供引用；不必依赖悬停。",
                },
            ),
            (
                "关键说明唯一放在悬停气泡",
                "即便日后节点名进了首包，若「内容即将上线」只出现在 mouseenter 才挂载的 popover，爬虫和禁 JS 场景仍读不到上线状态。字段定义、路径可用性这类说明与装饰 tip 不同，不能只活在气泡里",
                "关键状态 / 字段定义：正文或节点旁可见文本双写，或 popover 内容 SSR 进首包（可用 CSS 隐藏，勿删 DOM）；纯装饰 tip 标 data-llm-exclude 或策展剥离",
                {
                    "title": "证据 · 气泡内容要能在首包找到",
                    "code_label": "SSR 气泡 vs 仅悬停挂载",
                    "code": "<!-- ✓ 首包即有说明（可视觉隐藏） -->\n"
                    '<button aria-describedby="tip-ai4s">AI4S应用</button>\n'
                    '<p id="tip-ai4s" class="sr-only">内容即将上线，敬请期待</p>\n'
                    "<!-- ✗ 仅 mouseenter 才插入 DOM -->\n"
                    "<!-- document.append(tooltip) -->",
                    "caption": "看得见的悬停层，不等于源码里有字。",
                },
            ),
            (
                "也没有备用的路径节点清单",
                "路径图读不全时，如果 llms.txt 或平行 MD 里也没有「应用开发 → 节点列表 + 上线状态」对照，AI 既列不出节点，也不能核「即将上线」是否官方表述",
                "在 llms.txt 或平行 MD 临时列出各主题路径下的节点名与状态一句；页面路径 SSR 后以页面为准",
            ),
        ],
        "preview_url": EDU_GROWTH,
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
        # Mintlify + NVIDIA + 昇腾：PEER_ROW_OVERRIDES（昇腾 → 教育科研教学资源侧栏）
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
        # NVIDIA Models + 昇腾官方技术文章：PEER_ROW_OVERRIDES
    ],
    "ostep": [
        # Mintlify + 昇腾：PEER_ROW_OVERRIDES
    ],
    "onavigation": [
        # Mintlify + NVIDIA + 昇腾：PEER_ROW_OVERRIDES
    ],
    "ofooternav": [
        ("Mintlify", "home", "footer-nav"),
        ("NVIDIA", "home", "footer-nav"),
        ("昇腾社区", "home", "footer-nav"),
    ],
    "obutton": [
        # Mintlify + NVIDIA + 昇腾：PEER_ROW_OVERRIDES（NVIDIA → en-sg 首屏 CTA）
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
        # Mintlify + NVIDIA + 昇腾：PEER_ROW_OVERRIDES（NVIDIA → Dynamo 版本选择器）
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
        # Mintlify + NVIDIA + 昇腾：与 OMenu 同构，走 PEER_ROW_OVERRIDES（昇腾 → 教学资源侧栏）
    ],
    "oupload": [
        ("Mintlify", "docs-editor", "layout-img"),
        ("NVIDIA", "build", "promos"),
        ("昇腾社区", "download", "software-cards"),
    ],
    "orate": [
        # Mintlify + NVIDIA 证言可抓全；昇腾 → 学习路径课程卡评分（PEER_ROW_OVERRIDES）
    ],
    "ocascader": [
        # 线上未找到 OCascader 样例 → PEER_ROW_OVERRIDES 空表，页内标「未测试」
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
        # Mintlify + 昇腾走楼层；NVIDIA → build spark 教程卡标签（PEER_ROW_OVERRIDES）
    ],
    "obadge": [
        ("Mintlify", "home", "hero-traffic-num"),
        ("NVIDIA", "home", "gtc"),
        ("昇腾社区", "ccae", "banner-title"),
    ],
    "odialog": [
        # Mintlify + 昇腾保留；NVIDIA → Skills 详情弹层（PEER_ROW_OVERRIDES）
    ],
    "ocard": [
        ("Mintlify", "home", "companies"),
        ("NVIDIA", "dgx-cloud", "usecases"),
        ("昇腾社区", "developer", "dev-resource-cards"),
    ],
    "odatetable": [
        # 三站规格表对照：PEER_ROW_OVERRIDES（NVIDIA → CUDA Linux 安装指南 Table 1–4）
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
        # Mintlify + NVIDIA 保留；昇腾 → 学习路径节点气泡（PEER_ROW_OVERRIDES）
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
    "omenu": [
        {
            "peer_label": "NVIDIA", "case_key": "find-training",
            "case_name": "Find Training",
            "case_url": FIND_TRAINING,
            "object": "左侧竖向 menu", "badge": "Filters",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见 Filters：Level / Format / Topics 勾选树，但首包仅为 LIBRARIAN.Home.mount 空壳（preSelectedFilters 空）；Introductory 等选项不在静态 HTML、无筛选项 a[href]，禁 JS 列不全。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "edu-teaching",
            "case_name": "教学资源",
            "case_url": EDU_TEACHING,
            "object": "左侧竖向 menu", "badge": "课程侧栏",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「教学课程 / 创新实践课」及 openEuler智能调优（A-Tune）等课程项，但静态 HTML 无侧栏 a[href] 树；选中态靠 URL resourceType/subTab 与 __NUXT_DATA__，禁 JS 列不全课程入口。",
        },
    ],
    "otrees": [
        {
            "peer_label": "NVIDIA", "case_key": "find-training",
            "case_name": "Find Training",
            "case_url": FIND_TRAINING,
            "object": "左侧竖向 menu", "badge": "Filters",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见 Filters：Level / Format / Topics 勾选树，但首包仅为 LIBRARIAN.Home.mount 空壳（preSelectedFilters 空）；Introductory 等选项不在静态 HTML、无筛选项 a[href]，禁 JS 列不全。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "edu-teaching",
            "case_name": "教学资源",
            "case_url": EDU_TEACHING,
            "object": "左侧竖向 menu", "badge": "课程侧栏",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「教学课程 / 创新实践课」及 openEuler智能调优（A-Tune）等课程项，但静态 HTML 无侧栏 a[href] 树；选中态靠 URL resourceType/subTab 与 __NUXT_DATA__，禁 JS 列不全课程入口。",
        },
    ],
    "opagination": [
        {
            "peer_label": "NVIDIA", "case_key": "build",
            "case_name": "Models",
            "case_url": "https://build.nvidia.com/models",
            "object": "列表底部分页", "badge": "页码导航",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见 Items per page 与页码 1…6 / of N pages，但页码为前端切换、静态 HTML 无稳定 ?page= 可跟链；深页模型卡对禁 JS 抓取不可达。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "tech-articles",
            "case_name": "官方技术文章",
            "case_url": "https://www.hiascend.com/developer/techArticles",
            "object": "列表底部分页", "badge": "页码导航",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「共 N 条 / 页码 / 前往」分页，但静态 HTML 几乎无 ?page= 可跟链；页码多为 button / 客户端切换，深页列表对禁 JS 抓取不可达。",
        },
    ],
    "ostep": [
        {
            "peer_label": "Mintlify", "case_key": "quickstart",
            "case_name": "Quickstart",
            "case_url": "https://www.mintlify.com/docs/quickstart",
            "object": "Web editor 步骤条", "badge": "Steps",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "Web editor Tab 内 Steps：Open the web editor / Edit a page / Publish / View live 四步标题与说明均在首包 HTML（step-title + step-content）。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "simt-memory",
            "case_name": "内存层级",
            "case_url": (
                "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/latest/programug/"
                "Ascendcopdevg/docs/guide/%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97/"
                "%E7%BC%96%E7%A8%8B%E6%A8%A1%E5%9E%8B/AI-Core-SIMT%E7%BC%96%E7%A8%8B/"
                "%E5%86%85%E5%AD%98%E5%B1%82%E7%BA%A7.md"
            ),
            "object": "共享内存申请步骤", "badge": "编号步骤",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "「静态申请 / 动态申请」步骤标题与说明在 ol/li 首包可抓；但步骤内代码块、内联 code、配图多处为 [object Object]，示例源码不可引用。",
        },
    ],
    "onavigation": [
        {
            "peer_label": "Mintlify", "case_key": "docs",
            "case_name": "文档站",
            "case_url": "https://www.mintlify.com/docs",
            "object": "顶部主导航", "badge": "navbar",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "文档站顶栏 navbar：Documentation / API reference / Changelog / Talk to us / Get started 一级链均带真实 href；Learn 下拉子项（Customers / Blog 等）亦在首包 HTML。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "home",
            "case_name": "NVIDIA 官网",
            "case_url": "https://www.nvidia.com/en-sg/",
            "object": "顶部主导航", "badge": "global-nav",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "顶栏 Products / Solutions / Industries / Shop / Drivers / Support 等入口与大量子项 a[href] 写在首包 HTML，静态可跟链。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "home",
            "case_name": "社区首页",
            "case_url": "https://www.hiascend.com/zh",
            "object": "顶部主导航", "badge": "部分可抓",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "顶栏 o-nav 一级项（产品 / 解决方案 / 开发者与合作伙伴）文案在首包可见，但多为 div 无 href，仅「支持与服务」→ /support；右侧「文档」→ /zh/document 可跟，「在线开发」a 无 href、「下载」为 div。",
        },
    ],
    "obutton": [
        {
            "peer_label": "Mintlify", "case_key": "home",
            "case_name": "首页",
            "case_url": "https://www.mintlify.com/",
            "object": "首屏 CTA 按钮", "badge": "按钮链接",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "「Get started」「Sign up with Google」按钮文案与真实 href（signup / Google discovery）写在静态 HTML，可抓全。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "home",
            "case_name": "NVIDIA 官网",
            "case_url": "https://www.nvidia.com/en-sg/",
            "object": "首屏 CTA 按钮", "badge": "hero CTA",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "首屏轮播各帧 CTA（如 Automotive「Read Blog」、Data Center「Learn More」等）为真实 a[href]，按钮文案与落地地址在首包 HTML 可跟。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "home",
            "case_name": "社区首页",
            "case_url": "https://www.hiascend.com/zh",
            "object": "首屏轮播 CTA", "badge": "button 无 href",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "首屏轮播各帧 CTA（立即查看 / 了解更多 / 立即填写 / 前往认证 / 立即参与等）为 button.o-btn，源码无 href，跳转靠 JS；探针问落地 URL 时只能复述文案。",
        },
    ],
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
    "oselect": [
        {
            "peer_label": "Mintlify", "case_key": "pricing",
            "case_name": "定价",
            "case_url": "https://www.mintlify.com/pricing",
            "object": "套餐名可读 · 价格动效", "badge": "选型对照",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "套餐名（Starter / Pro 等）可抓，但标价以 0–9 滚轮 + transform 呈现，源码无完整可读价格数字。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "dynamo-quickstart",
            "case_name": "Dynamo Quickstart",
            "case_url": "https://docs.nvidia.com/dynamo/dev/cli/getting-started/quickstart",
            "object": "文档版本选择器", "badge": "version dropdown",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可展开 fern-version-selector，见 Latest (v1.3.0) / dev / v1.3.0…v0.9.1 等；首包仅触发器 button（data-state=closed），版本清单在 __next_f JSON 的 versions[]，无菜单内 a[href]，禁 JS 列不全各版本文档 URL。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "firmware-drivers",
            "case_name": "固件与驱动",
            "case_url": "https://www.hiascend.com/hardware/firmware-drivers",
            "object": "型号 / 架构 / 安装方式选项", "badge": "动态筛选",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见产品型号/架构/安装方式筛选与包列表，但静态 HTML 无完整 option 矩阵；选中态靠 ?ids= 与 __NUXT_DATA__ 恢复，禁 JS 抓不全。",
        },
    ],
    "orate": [
        {
            "peer_label": "昇腾社区", "case_key": "edu-growth",
            "case_name": "学习路径",
            "case_url": EDU_GROWTH,
            "object": "课程卡评分", "badge": "社会证明",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「大模型开发全流程中级」等课程卡上的 5.0 星评分、时长与报名人数，但首包无 o-rate / 完整卡文案（无「大模型开发全流程中级」「5.0」），课程卡靠脚本注入，禁 JS 抓不到可引用评分数字。",
        },
    ],
    "ocascader": [],
    "otag": [
        {
            "peer_label": "Mintlify", "case_key": "api-trigger",
            "case_name": "Trigger deployment",
            "case_url": MINTLIFY_API_TRIGGER,
            "object": "Authorization 参数标签", "badge": "string / header / required",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "Authorization 旁 field-info-pill（string / header）与 field-required-pill（required）及 Bearer 说明均在首包 HTML；禁 JS 可读类型、位置与必填语义。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "build-spark",
            "case_name": "DGX Spark",
            "case_url": BUILD_SPARK,
            "object": "教程卡标签", "badge": "tag",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「RAG Application in AI Workbench」卡上的 dgx 等标签与 +1，但首包多为 WAF/壳层，卡标题与 tag 文案不在静态 HTML；禁 JS 列不全标签语义。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "edu-growth",
            "case_name": "学习路径",
            "case_url": EDU_GROWTH,
            "object": "课程卡标签", "badge": "CANN / HCCL 等",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「大模型开发全流程中级」卡上 CANN / HCCL / 大模型开发 等标签，但首包无完整卡文案与 tag 文本，课程卡靠脚本注入，禁 JS 读不到标签语义。",
        },
    ],
    "opopover": [
        {
            "peer_label": "Mintlify", "case_key": "enterprise",
            "case_name": "Enterprise",
            "case_url": "https://www.mintlify.com/enterprise",
            "object": "流量占比图气泡", "badge": "月份悬停",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器悬停 October 柱可见「5% agent share of traffic / Agents 3.5M / Humans 62.1M」；首包有标题与 Agents/Humans 图例及柱高样式，但月份气泡文案不在可读 DOM（仅埋在脚本数据里），禁 JS 引用不了该月份额说明。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "build-spark",
            "case_name": "DGX Spark",
            "case_url": BUILD_SPARK,
            "object": "标签溢出气泡", "badge": "+N 展开",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器「Build Knowledge Graphs with txt2kg」卡可见 station / +6，悬停可展开 vllm / dgx spark / ollama 等完整标签；首包多为 WAF/壳层，卡文案与溢出气泡不在静态 HTML，禁 JS 读不到。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "edu-growth",
            "case_name": "学习路径",
            "case_url": EDU_GROWTH,
            "object": "路径节点气泡", "badge": "即将上线提示",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器「探索你的学习路径」可见应用开发下 AI4S应用 / RAG原理 等节点，悬停可出「内容即将上线，敬请期待」；首包仅有路径壳层文案，节点名与气泡说明不在静态 HTML，禁 JS 读不到。",
        },
    ],
    "odatetable": [
        {
            "peer_label": "Mintlify", "case_key": "custom-portal",
            "case_name": "Custom developer portals",
            "case_url": "https://www.mintlify.com/docs/deploy/custom-portal",
            "object": "Custom portal 功能表", "badge": "对照正文",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "Features 三列表格（Feature / What ships / Backed by）10 行功能对照与 Backed by 说明均在静态 HTML table/th/td 中，禁 JS 可逐行抓取，非截图表。",
        },
        {
            "peer_label": "NVIDIA", "case_key": "cuda-installation-guide-linux",
            "case_name": "CUDA Linux 安装指南",
            "case_url": "https://docs.nvidia.com/cuda/cuda-installation-guide-linux/",
            "object": "OS/编译器规格表", "badge": "多表正文",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "Table 1–4（Supported Linux Distributions / Validated OS Versions for CUDA 13.3 Update 1 / Supported Compilers / Installation Compatibility Matrix）均为真实 HTML table/th/td；含 Ubuntu 26.04、Codename·Kernel·GCC·GLIBC 等单元格可逐行抓取，非截图表。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "faq",
            "case_name": "AscendFAQ",
            "case_url": "https://www.hiascend.com/document/detail/zh/AscendFAQ/ProduTech/productform/hardwaredesc_0001.html",
            "object": "表1 昇腾产品系列", "badge": "参数表",
            "grab": "可抓全", "tag_cls": "peer-tag-ok",
            "reason": "表1 含 Atlas 350 等型号，完整 table 在静态 HTML。",
        },
    ],
    "odialog": [
        {
            "peer_label": "NVIDIA", "case_key": "build-skills",
            "case_name": "Skills",
            "case_url": BUILD_SKILLS,
            "object": "Skill 详情弹层", "badge": "安装命令",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器点开 aiq-research 可见弹层：安装命令 npx skills add …、描述、developer 等标签与 Copy Skill；首包多为 WAF/壳层，技能卡与弹层正文不在静态 HTML，禁 JS 读不到弹层说明与命令。",
        },
        {
            "peer_label": "昇腾社区", "case_key": "mindx",
            "case_name": "应用使能",
            "case_url": MINDX,
            "object": "应用使能公告弹层", "badge": "命名/开源说明",
            "grab": "抓不全", "tag_cls": "peer-tag-partial",
            "reason": "浏览器可见「应用使能公告」弹层（Mind 系列全量开源、MindX→应用使能 / MindSDK 更名等）；首包仅有「查看公告」入口与短导语，弹层正文与「知道了」不在静态 HTML，禁 JS 读不到完整公告与命名变更说明。",
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
        "tech-articles": "官方技术文章",
        "simt-memory": "内存层级",
        "firmware-drivers": "固件与驱动",
        "edu-teaching": "教学资源",
        "edu-growth": "学习路径",
        "mindx": "应用使能",
        "build-spark": "DGX Spark",
        "build-skills": "Skills",
        "api-trigger": "Trigger deployment",
        "cluster": "集群", "ccae": "CCAE", "edu": "教育", "pricing": "定价",
        "docs": "文档站", "quickstart": "Quickstart", "docs-editor": "文档编辑器", "docs-tabs": "Tabs 组件", "blog": "博客", "score": "Score",
        "enterprise": "Enterprise",
        "dgx-cloud": "DGX Cloud", "industries": "行业", "automotive": "汽车",
        "cuquantum-release-notes": "Release Notes",
        "build": "Build", "partners": "伙伴", "news": "新闻", "events": "活动",
        "cuda-downloads": "CUDA 下载",
        "devzone": "开发者站",
        "dynamo-quickstart": "Dynamo Quickstart",
        "find-training": "Find Training",
    }
    return labels.get(case_key, title or case_key)


def _render_peer_override_rows(slug: str) -> list[str]:
    rows: list[str] = []
    index = _load_peer_case_index()
    for row in PEER_ROW_OVERRIDES[slug]:
        case = index.get((row["peer_label"], row["case_key"]), {})
        case_url = row.get("case_url") or case.get("leftUrl") or case.get("rightUrl") or ""
        title = (case.get("title") or row["case_key"]).split("·")[0].split("/")[0].strip()
        case_name = (
            row.get("case_name")
            or case.get("pageName")
            or case.get("leftLabel")
            or _case_label(row["case_key"], title)
        )
        object_title = html.escape(row["object"])
        badge = row.get("badge") or ""
        floor_label = f'<span class="peer-object-name">{object_title}</span>'
        if badge:
            floor_label += f'<span class="peer-floor-badge">{html.escape(badge)}</span>'
        if case_url:
            case_cell = f'<td><a href="{html.escape(case_url)}" target="_blank" rel="noopener">{html.escape(case_name)}</a></td>'
            floor_cell = (
                f'<td><a class="peer-object-link" href="{html.escape(case_url)}" target="_blank" rel="noopener" '
                f'title="该页{object_title}所在的友商线上页面">{floor_label}</a></td>'
            )
        else:
            case_cell = f"<td>{html.escape(case_name)}</td>"
            floor_cell = f'<td><span class="peer-object-link">{floor_label}</span></td>'
        rows.append(
            f'            <tr><td>{row["peer_label"]}</td>'
            f"{case_cell}{floor_cell}"
            f'<td><span class="peer-tag {row["tag_cls"]}">{html.escape(row["grab"])}</span></td>'
            f'<td class="peer-reason">{html.escape(row["reason"])}</td></tr>'
        )
    return rows


def render_peer_section(slug: str) -> str:
    probe = PROBES.get(slug, {})
    if probe.get("untested"):
        note = probe.get("peer_empty") or "线上未找到组件样例，本次未做友商对照实测。"
        return _wrap_peer_section(slug, [], empty_note=note)
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


def _wrap_peer_section(slug: str, rows: list[str], empty_note: str | None = None) -> str:
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
        msg = empty_note or (
            f"暂无 {slug} 组件友商对照数据；"
            "请先在 citability-html 案例 JSON 中补全对应楼层。"
        )
        body = f'        <p class="peer-test-empty">{html.escape(msg)}</p>'
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
if "overflow-anchor" not in CSS:
    CSS += "\n  .comp-sidebar { overflow-anchor: none; }\n"
if ".evidence-block" not in CSS:
    CSS += """
  .evidence-block {
    margin: 12px 0 0;
    border: 1px solid var(--line);
    border-radius: 8px;
    background: var(--panel2);
    overflow: hidden;
  }
  .evidence-block-title {
    margin: 0;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 700;
    color: var(--muted);
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  .section .evidence-block > .evidence-block-title {
    margin: 0;
    color: var(--muted);
  }
  .evidence-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    padding-top: 0;
  }
  .evidence-grid--single {
    grid-template-columns: 1fr;
  }
  @media (max-width: 900px) {
    .evidence-grid { grid-template-columns: 1fr; }
  }
  .evidence-pane {
    min-width: 0;
    padding: 12px;
  }
  .evidence-pane + .evidence-pane {
    border-left: 1px solid var(--line);
  }
  @media (max-width: 900px) {
    .evidence-pane + .evidence-pane {
      border-left: none;
      border-top: 1px solid var(--line);
    }
  }
  .evidence-pane-label {
    margin: 0 0 12px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text);
  }
  .section .evidence-pane > .evidence-pane-label {
    margin: 0 0 12px;
    color: var(--text);
  }
  .evidence-pane img {
    display: block;
    width: auto;
    max-width: 100%;
    height: auto;
    margin: 0;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: #fff;
  }
  .evidence-pane pre {
    margin: 0;
    padding: 10px 12px;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: #0f172a;
    color: #e2e8f0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 11.5px;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 220px;
    overflow: auto;
  }
  .evidence-caption {
    margin: 12px 0 0;
    padding: 0;
    font-size: 12.5px;
    line-height: 19px;
    color: var(--muted);
    text-align: left;
  }
  .section .evidence-pane > .evidence-caption {
    margin: 12px 0 0;
    color: var(--muted);
  }
"""

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

SIDEBAR_SCROLL_SCRIPT = """<script>
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
    if (Date.now() - t0 > 800) clearInterval(iv);
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

SCRIPT_BLOCK = SCRIPT_BLOCK + SIDEBAR_SCROLL_SCRIPT



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
    if probe.get("no_aff") or probe.get("badge_text") == "不需要亲和":
        return "不需要", "aff-no"
    if probe.get("badge_text") in ("视情况", "未测试") or probe.get("untested"):
        return "视情况", "aff-maybe"
    return "需要", "aff-need"


# 组件清单「是否需要做亲和」列：与原则页场景判断 / 一句话原则对齐
CATALOG_AFF: dict[str, tuple[str, str]] = {
    "omenu": (
        "需要",
        "跳转型侧栏目录须首包 <code>a[href]</code>；同页切换内容块归树组件。详见<a href=\"principles-omenu.html\">亲和原则</a>",
    ),
    "otab": (
        "视情况",
        "内容型 Tab 各面板须全量 SSR；纯交互 / 装饰型入库剥离。详见<a href=\"principles-otab.html\">亲和原则</a>",
    ),
    "obreadcrumb": (
        "需要",
        "祖先页做成可爬 <code>a[href]</code>；当前页可用纯文本；路径文案与 sitemap 对齐",
    ),
    "oanchor": (
        "需要",
        "本篇目录用真实 <code>#id</code> 与 <code>href</code>；正文标题保留对应 id",
    ),
    "opagination": (
        "需要",
        "公开列表底部分页须为可抓 URL（如 <code>?page=2</code>）；后台表格分页入库剥离",
    ),
    "ostep": (
        "需要",
        "公开流程步骤标题与说明写入源码；进行中 / 完成态勿只靠颜色；后台向导剥离",
    ),
    "onavigation": (
        "需要",
        "站点入口与展开子链须进首包可跟；搜索 / 换肤 / 语言等纯操作控件剥离",
    ),
    "ofooternav": (
        "需要",
        "页脚多列链接进源码；列名稳定，并与 llms / sitemap 互证",
    ),
    "obutton": (
        "视情况",
        "跳转型 CTA 做成可抓链接；纯提交 / 关闭 / 弹层按钮入库剥离",
    ),
    "olink": (
        "需要",
        "导流链接须带真实 <code>href</code>；锚文本宜自描述；禁 JSON / onclick 伪链",
    ),
    "odropdown": (
        "需要",
        "下拉子项须在首包可读（链接 + 文案）；勿悬停才挂链",
    ),
    "otoggle": (
        "视情况",
        "映射下载 / 版本的选型矩阵须进首包；纯 UI 筛选剥离",
    ),
    "oradio": ("不需要", "表单选项态，非内容载体；勿把选项文案当知识库正文"),
    "ocheckbox": ("不需要", "同上，交互控件；说明文字应写在旁侧正文而非只靠勾选态"),
    "oswitch": ("不需要", "开关态对抓取无信息增量"),
    "oscrollbar": ("不需要", "纯样式，与亲和无关"),
    "osearch": (
        "视情况",
        "要做亲和的是发现层：可搜文档须有独立 URL 并进 sitemap；搜索框本身剥离",
    ),
    "oselect": (
        "视情况",
        "映射文档 / 下载的选项文本与落地页须可证伪；纯表单筛选剥离",
    ),
    "otrees": (
        "需要",
        "同页内容树节点可无 URL，但各内容块须首包可读；跳转型手册目录见菜单",
    ),
    "orate": (
        "视情况",
        "评分数字若作社会证明须可读进首包；「我要评分」等操作 CTA 剥离",
    ),
    "ocascader": (
        "视情况",
        "线上暂无 DOM 样例（实测页标「未测试」）；若映射内容路径，各级选项须可读；纯地址 / 表单级联剥离",
    ),
    "oinput": ("不需要", "输入控件本身不承载官网知识；占位符勿写关键说明"),
    "otextarea": ("不需要", "同上；长说明应放正文段落而非 textarea 占位"),
    "odatepicker": ("不需要", "日期控件，非内容知识"),
    "otimepicker": ("不需要", "时间控件，非内容知识"),
    "oupload": ("不需要", "上传交互；限制说明可进旁注正文，控件本身无需亲和改造"),
    "oslider": ("不需要", "数值滑条，非叙述内容"),
    "otag": (
        "视情况",
        "版本 / 状态语义标签须进 HTML 文本并有定义依据；营销装饰标签剥离",
    ),
    "odivider": ("不需要", "视觉分隔，md 用 --- 即可"),
    "obadge": ("不需要", "未读角标对知识抓取无价值"),
    "ocarousel": (
        "视情况",
        "白名单产品 / 文档入口帧须标题+摘要+链接；运营 / 活动口号帧默认剥离。详见<a href=\"principles-ocarousel.html\">亲和原则</a>",
    ),
    "odialog": (
        "视情况",
        "命名变更 / 开源公告 / 安装步骤勿只放弹层，须进首包或正文双写；纯确认框剥离",
    ),
    "ocard": (
        "需要",
        "标题、摘要、链接写入 HTML；图需 alt / 图注；禁空壳卡后注入",
    ),
    "odatetable": (
        "需要",
        "规格 / 对照用真实 table/th/td 或平行 MD 表；忌截图表与空单元格",
    ),
    "opopover": (
        "视情况",
        "路径节点状态 / 字段定义勿只放悬停气泡，须进首包或正文双写；装饰 tip 剥离",
    ),
    "oprogress": ("不需要", "进度展示，非知识正文"),
    "omessage": ("不需要", "瞬时反馈；重要错误说明应落到正文 / 文档页"),
    "otoast": ("不需要", "轻提示瞬时，勿承载唯一说明"),
    "oloading": ("不需要", "加载态，与内容亲和无关"),
}


def aff_cls_for(label: str) -> str:
    return {"需要": "aff-need", "视情况": "aff-maybe", "不需要": "aff-no"}.get(label, "aff-need")


def render_aff_tag(slug: str) -> str:
    label, cls = aff_status(slug)
    return f'<span class="aff {cls}">{label}</span>'


# 有 UI 小样（设计示例为可视化 render-frame）的组件：侧边栏名称后加一个蓝色圆点标记
DESIGN_CHANGED_SLUGS = {
    # principles 页设计栏有 UI 小样（render-frame）的组件
    "omenu", "obreadcrumb", "oanchor", "ostep", "onavigation", "ofooternav",
    "obutton", "olink", "odropdown",
    "osearch", "otrees", "orate", "otag",
    "ocarousel", "ocard", "odatetable", "opopover",
}


def render_design_dot(slug: str) -> str:
    if slug in DESIGN_CHANGED_SLUGS:
        return '<span class="comp-dot" title="有 UI 小样" aria-hidden="true"></span>'
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
        f'<span class="comp-nav-label">{html.escape(sidebar_label(name))}</span>{render_design_dot(slug)}</a></li>'
    )


def render_sidebar(active: str | None, *, principles: bool = False) -> str:
    lines = ['  <aside class="comp-sidebar" aria-label="组件列表">', '    <div class="comp-sidebar-title">组件列表</div>', '    <nav class="comp-nav">']
    for group, items in GROUPS:
        lines.append(f'      <div class="comp-group-label">{group}</div>')
        lines.append("      <ul>")
        for slug, name in items:
            if principles:
                href = f"principles-{slug}.html"
            else:
                href = f"problems-{slug}.html"
            lines.append(render_nav_item(name, href, slug, active=active == slug))
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
    label = "未测试" if probe.get("untested") or probe.get("badge_text") == "未测试" else "视情况"
    return f'      <span class="page-desc-line"><strong>{label}</strong>：{html.escape(note)}</span>\n'


def guide_aff_note(probe: dict) -> str:
    note = probe.get("aff_note", "").strip()
    if not note:
        return ""
    if note[-1] not in "。！？；":
        note += "。"
    if probe.get("untested") or probe.get("badge_text") == "未测试":
        return ""
    return f"""
      <div class="content-unit">
        <p><strong>视情况</strong>：{html.escape(note)}</p>
      </div>"""


def render_guide_section(probe: dict, sub_html: str, root_evidence: str) -> str:
    """Root-cause block; untested pages collapse to a single「待测试」line."""
    if probe.get("untested") or probe.get("badge_text") == "未测试":
        return """    <section class="section" id="guide">
      <h2 id="solution">根因分析</h2>
      <div class="content-unit">
        <p><strong style="color:var(--text)">待测试</strong>。</p>
      </div>
    </section>"""
    return f"""    <section class="section" id="guide">
      <h2 id="solution">根因分析</h2>{guide_aff_note(probe)}
      <div class="content-unit">
        <p><strong>{probe["term"]}</strong>的核心原因：<strong style="color:var(--text)">{probe["root_cause"]}</strong>。</p>
      </div>{root_evidence}{sub_html}
    </section>"""


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


def render_evidence(evidence: dict | None) -> str:
    """Optional proof block: browser shot + static HTML/JSON excerpt."""
    if not evidence:
        return ""
    title = html.escape(evidence.get("title") or "实测证据")
    shot = evidence.get("shot")
    shot_alt = html.escape(evidence.get("shot_alt") or "浏览器可见侧栏")
    shot_label = html.escape(evidence.get("shot_label") or "浏览器可见")
    code = evidence.get("code") or ""
    code_label = html.escape(evidence.get("code_label") or "静态源码摘录")
    caption = evidence.get("caption")
    cap_html = (
        f'\n          <p class="evidence-caption">{html.escape(caption)}</p>'
        if caption
        else ""
    )
    panes: list[str] = []
    if shot:
        # caption sits under the shot so it left-aligns with the image
        panes.append(
            f"""        <div class="evidence-pane">
          <p class="evidence-pane-label">{shot_label}</p>
          <img src="{html.escape(shot)}" alt="{shot_alt}" loading="lazy" />{cap_html}
        </div>"""
        )
        cap_html = ""
    if code:
        panes.append(
            f"""        <div class="evidence-pane">
          <p class="evidence-pane-label">{code_label}</p>
          <pre>{html.escape(code)}</pre>{cap_html}
        </div>"""
        )
        cap_html = ""
    if not panes:
        return ""
    grid_cls = "evidence-grid" if len(panes) > 1 else "evidence-grid evidence-grid--single"
    return f"""
      <div class="evidence-block">
        <p class="evidence-block-title">{title}</p>
        <div class="{grid_cls}">
{chr(10).join(panes)}
        </div>
      </div>"""


def render_fix_body(fix: str) -> str:
    s = _sentence(fix).rstrip("。")
    return f"<p>{_inline_code(s)}。</p>"


def render_page(slug: str, name: str, probe: dict) -> str:
    comp_label = name.split()[0] if name else slug
    sub_html = ""
    for i, item in enumerate(probe["subcauses"], 1):
        title, desc, fix = item[0], item[1], item[2]
        evidence = item[3] if len(item) > 3 else None
        sub_html += f"""
      <div class="content-unit">
        <h3>{i}. {html.escape(title)}</h3>
        <div class="issue-body">
        {render_issue_body(desc)}
        </div>{render_evidence(evidence)}
        <div class="fix-suggestion">
          <h4>修改建议</h4>
          {render_fix_body(fix)}
        </div>
      </div>"""

    root_evidence = render_evidence(probe.get("root_evidence"))

    sidebar = render_sidebar(slug)
    principles_href = f"principles-{slug}.html"
    peer_section = render_peer_section(slug)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
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
    <a href="{principles_href}">亲和原则</a>
    <a href="problems-{slug}.html" class="active">实测问题</a>
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

{render_guide_section(probe, sub_html, root_evidence)}
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
    changed = False
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
        text = patched
        changed = True
    else:
        text = patched
    if "geo-comp-sidebar-scroll" not in text:
        injected = text.replace("</body>", SIDEBAR_SCROLL_SCRIPT + "\n</body>", 1)
        if injected != text:
            text = injected
            changed = True
    if "overflow-anchor: none" not in text and ".comp-sidebar {" in text:
        anchored = text.replace(
            ".comp-sidebar {\n",
            ".comp-sidebar {\n    overflow-anchor: none;\n",
            1,
        )
        if anchored != text:
            text = anchored
            changed = True
    if ".comp-nav .comp-dot" not in text and "</style>" in text:
        dot_css = (
            "\n  .comp-nav .comp-dot {\n"
            "    flex-shrink: 0;\n"
            "    width: 8px; height: 8px; border-radius: 50%;\n"
            "    background: #2563eb;\n"
            "  }\n"
        )
        with_dot = text.replace("</style>", dot_css + "</style>", 1)
        if with_dot != text:
            text = with_dot
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


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
    """Renumber community-ui rows and refresh section counts (keep 需要/视情况/不需要)."""
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    removed = 0

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

    catalog_count = len(re.findall(r'<tr data-aff="', text))
    text = re.sub(r"共 \d+ 个组件", f"共 {catalog_count} 个组件", text, count=1)

    # Ensure 不需要 filter option exists (unchecked by default)
    if 'value="不需要"' not in text:
        text = re.sub(
            r'(<label><input type="checkbox" name="aff" value="视情况" checked />视情况</label>\s*)',
            r'\1<label><input type="checkbox" name="aff" value="不需要" />不需要</label>\n      ',
            text,
            count=1,
        )

    section_ids = {
        "导航类": "cat-nav",
        "操作类": "cat-action",
        "输入类": "cat-input",
        "展示类": "cat-display",
        "容器类": "cat-container",
        "反馈类": "cat-feedback",
    }
    for sid in section_ids.values():
        m = re.search(
            rf'<section class="cat-card" aria-labelledby="{sid}">(.*?)</section>',
            text,
            flags=re.DOTALL,
        )
        if not m:
            continue
        n = len(re.findall(r'<tr data-aff="', m.group(1)))
        text = re.sub(
            rf'(<h2 id="{sid}">[^<]+<span class="count">)\d+(</span></h2>)',
            rf"\g<1>{n}\g<2>",
            text,
            count=1,
        )

    path.write_text(text, encoding="utf-8")
    if REPORT.joinpath("community-ui.html").exists() or path.exists():
        shutil.copy2(path, REPORT / "community-ui.html")
    return removed, catalog_count



def update_community_ui_samples() -> int:
    """No-op: 样例URL column removed from community-ui.html."""
    return 0


def update_community_ui_aff_column() -> int:
    """Refresh data-aff + 「是否需要做亲和」文案，与 CATALOG_AFF / 原则页对齐。"""
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    name_to_slug = {name: slug for _, slug, name in all_components()}
    count = 0
    for name, slug in name_to_slug.items():
        entry = CATALOG_AFF.get(slug)
        if not entry:
            continue
        label, reason = entry
        cls = aff_cls_for(label)
        cell = (
            f'<span class="aff {cls}">{label}</span>'
            f'<span class="aff-reason">{reason}</span>'
        )
        pattern = (
            rf'(<tr data-aff=")[^"]+("><td class="col-num">\d+</td>'
            rf'<td class="col-name">{re.escape(name)}</td><td class="col-aff">)'
            rf'.*?'
            rf'(</td><td class="col-detail">)'
        )
        repl = rf'\g<1>{label}\g<2>{cell}\g<3>'
        new_text, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
        if n:
            text = new_text
            count += 1
    # fix broken section open tags if any
    text = re.sub(
        r'<section class="cat-card" aria-labelledby="(cat-[a-z]+)"\s*\n',
        r'<section class="cat-card" aria-labelledby="\1">\n',
        text,
    )
    path.write_text(text, encoding="utf-8")
    return count


def detail_href_for_slug(slug: str) -> str:
    """Catalog「查看详情」默认进亲和原则；无原则页时回落到实测问题。"""
    principles = DOCS / f"principles-{slug}.html"
    if principles.exists():
        return f"principles-{slug}.html"
    return f"problems-{slug}.html"


def update_community_ui() -> int:
    path = DOCS / "community-ui.html"
    text = path.read_text(encoding="utf-8")
    name_to_slug = {name: slug for _, slug, name in all_components()}
    count = 0
    for name, slug in name_to_slug.items():
        if f'<td class="col-name">{name}</td>' not in text:
            continue
        href = detail_href_for_slug(slug)
        pattern = (
            rf'(<tr[^>]*>.*?{re.escape(name)}.*?</td><td class="col-detail">)'
            rf'(?:<span class="detail-empty">查看详情</span>|'
            rf'<a href="(?:problems|principles)-{slug}\.html">查看详情</a>)'
            rf'(</td></tr>)'
        )
        new_detail = rf'\1<a href="{href}">查看详情</a>\2'
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
    for extra in ("community-ui.html", "principles-affinity.html", "principles-ocarousel.html"):
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

    ocarousel_principles = DOCS / "principles-ocarousel.html"
    if ocarousel_principles.exists() and patch_sidebar_in_file(
        ocarousel_principles, "ocarousel", principles=True
    ):
        sidebars_patched += 1

    links_updated = update_community_ui()
    aff_updated = update_community_ui_aff_column()
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
    print(f"community-ui aff column updated: {aff_updated} rows")
    print(f"community-ui sample URLs updated: {samples_updated} rows")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
