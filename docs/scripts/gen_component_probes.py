#!/usr/bin/env python3
"""Generate problems-component-probe HTML pages for community UI catalog."""

from __future__ import annotations

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
FAQ = "https://www.hiascend.com/document/detail/zh/AscendFAQ/overview/index.html"

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
        ("oradio", "ORadio 单选框"),
        ("ocheckbox", "OCheckbox 多选框"),
        ("oswitch", "OSwitch 开关"),
        ("oscrollbar", "OScrollbar 滚动条"),
        ("otoggle", "OToggle 选择块"),
    ]),
    ("输入类", [
        ("oinput", "OInput 输入框"),
        ("otextarea", "OTextarea 多行文本输入框"),
        ("osearch", "OSearch 搜索框"),
        ("oselect", "OSelect 选择器"),
        ("odatepicker", "DatePicker 日期选择器"),
        ("otimepicker", "TimePicker 时间选择器"),
        ("otrees", "Trees 树"),
        ("oupload", "OUpload 上传"),
        ("orate", "ORate 评分"),
        ("ocascader", "OCascader 级联选择"),
        ("oslider", "OSlider 滑动条"),
    ]),
    ("展示类", [
        ("odivider", "ODivider 分割线"),
        ("otag", "OTag 标签"),
        ("obadge", "OBadge 徽标"),
    ]),
    ("容器类", [
        ("ocarousel", "OCarousel 幻灯片"),
        ("odialog", "ODialog 对话框"),
        ("ocard", "OCard 卡片"),
        ("odatetable", "Odate-table 数据表格"),
    ]),
    ("反馈类", [
        ("oprogress", "OProgress 进度条"),
        ("omessage", "OMessage 消息提示"),
        ("otoast", "OToast 轻提示"),
        ("opopover", "气泡卡片"),
        ("oloading", "OLoading 加载"),
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
            ("样本未见 OMenu", "社区首页与 FAQ 静态 DOM 均无 o-menu；首页顶栏是 o-nav，不能冒充 OMenu 样例"),
            ("侧栏树不在首包", "FAQ 类手册目录几乎依赖前端注入，禁 JS 后层级导航不可达"),
            ("发现层缺口", "无 SSR 目录时，爬虫与 Agent 只能靠 sitemap/llms，失去「当前手册内」结构线索"),
        ],
        "root_cause": "把文档发现依赖在前端注入的侧栏树上，而静态 HTML 未输出可爬的层级链接",
        "subcauses": [
            ("设计组件与线上 DOM 错位", "清单按 OMenu 设计，但线上常见 o-nav 或自定义树，样例无法锚定", "样例列未确认 DOM 前标「—」；侧栏树统一 SSR 为真实 a[href]"),
            ("目录仅客户端渲染", "首包无 sibling/子树链接", "输出当前手册完整目录或至少当前分支；并用 MD/llms 清单补缺口"),
            ("链接不可机读", "节点无稳定 URL，仅有点击态", "每个可导航节点必须是带绝对或站内路径的链接文本"),
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
            ("首页有真 OTab", "www.hiascend.com/zh 存在 o-tab DOM，可作组件样例"),
            ("下载页自定义 Tab 更糟", "CANN 下载页 tab-list 静态正文偏壳，安装命令不在首包"),
            ("多轴叠加丢失", "选型 × 折叠时 RAG 易只答默认面板"),
        ],
        "root_cause": "关键步骤只放在交互切换的面板里，且未 SSR 全量，导致禁 JS 抓取残缺",
        "subcauses": [
            ("非激活面板不可见", "display:none 或未输出 DOM", "各面板 SSR 全量；视觉隐藏不得删除文本节点"),
            ("Tab 维度未进标题", "抓取后无法区分「在线/离线」", "面板标题写成 H3 或元数据；机器层按 Tab 展开"),
            ("无备用平铺轨", "只靠点击切换", "提供预展开 MD 或独立安装页，RAG 优先可读轨"),
        ],
        "preview_url": DOWNLOAD,
    },
    "obreadcrumb": {
        "title_short": "路径链断裂",
        "badge_class": "badge-should",
        "badge_text": "需可爬链",
        "term": "路径链断裂",
        "definition": "面包屑应把当前页在站点中的祖先路径做成可爬链接；若只有纯文本或 JS 渲染，Agent 无法沿路径回溯上下文",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；设计期望 ancestors 为 a[href]，当前页为纯文本",
        "prompt": "我在看昇腾社区相关页面（组件：OBreadcrumb 面包屑，暂无确认 DOM 样例 URL），当前页在站点层级中的完整路径是什么？每一级祖先页的可点击链接分别是什么？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OBreadcrumb 面包屑，暂无确认 DOM 样例 URL），当前页在站点层级中的完整路径是什么？每一级祖先页的可点击链接分别是什么？",
        "answer": "没有锚定到含 o-breadcrumb 的样例页，我无法从静态 HTML 验证路径链。若面包屑仅渲染当前页标题或祖先不可链，我会丢失「从首页到本文档」的结构线索。",
        "insights": [
            ("样例未确认", "社区 UI 清单样例列为 —，需补真实文档页"),
            ("祖先须可链", "纯文本路径无法被爬虫沿链扩展"),
            ("当前页宜非链", "避免循环；但祖先 href 必须稳定"),
        ],
        "root_cause": "面包屑未把祖先页输出为真实链接，路径语义无法被机器沿链消费",
        "subcauses": [
            ("祖先渲染为 span", "无 href", "祖先项一律 a[href] 指向可爬 URL"),
            ("路径仅客户端算", "首包缺失", "SSR 输出完整 breadcrumb 列表"),
            ("文案与 sitemap 不一致", "Agent 对不上站图", "列名与链接文案保持稳定"),
        ],
        "preview_url": None,
    },
    "oanchor": {
        "title_short": "锚点目录不可达",
        "badge_class": "badge-should",
        "badge_text": "需 id 对齐",
        "term": "锚点目录不可达",
        "definition": "长文页侧栏/顶栏锚点须用真实 #id 与 href 对齐正文标题；否则 RAG 无法按章节切片回答",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；md 轨可用标题层级替代",
        "prompt": "我在看昇腾社区长文档页（组件：OAnchor 锚点，暂无确认 DOM 样例 URL），右侧章节目录里「安装步骤」对应正文哪一节？给出该节标题与 #id。",
        "prompt_plain": "我在看昇腾社区长文档页（组件：OAnchor 锚点，暂无确认 DOM 样例 URL），右侧章节目录里「安装步骤」对应正文哪一节？给出该节标题与 #id。",
        "answer": "未锚定含 o-anchor 的样例时，我只能猜章节结构。若锚点链接是 javascript: 或 id 与正文 h2/h3 不对齐，我无法可靠映射「目录项 → 正文块」。",
        "insights": [
            ("href 须对齐 id", "锚点与标题 id 不一致则 chunk 切不准"),
            ("二级锚点需缩进语义", "嵌套目录应反映层级"),
            ("纯视觉选中态不足", "颜色变化对抓取无增量"),
        ],
        "root_cause": "锚点导航未与正文 heading id 稳定绑定，章节级问答无法证伪",
        "subcauses": [
            ("锚点用 click 非 hash", "无 #id", "a[href=\"#section-id\"] 对齐 h2/h3 id"),
            ("标题缺 id", "目录悬空", "每个可导航标题输出稳定 id"),
            ("仅 JS 生成目录", "首包无锚点列表", "SSR 输出完整 anchor nav"),
        ],
        "preview_url": None,
    },
    "opagination": {
        "title_short": "分页 URL 不可达",
        "badge_class": "badge-should",
        "badge_text": "需可爬页码",
        "term": "分页 URL 不可达",
        "definition": "列表/搜索结果分页须为可抓 URL；纯前端翻页会导致下一页内容对爬虫不可达",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；设计期望页码为真实链接",
        "prompt": "我在看昇腾社区列表页（组件：OPagination 分页，暂无确认 DOM 样例 URL），第 2、3 页列表项的官方 URL 分别是什么？请给出完整 href。",
        "prompt_plain": "我在看昇腾社区列表页（组件：OPagination 分页，暂无确认 DOM 样例 URL），第 2、3 页列表项的官方 URL 分别是什么？请给出完整 href。",
        "answer": "若无样例页或分页仅 button/onClick 切换，静态抓取看不到 page=2 的 URL，我只能描述「还有下一页」但给不出可爬地址，后续页内容对 RAG 不可达。",
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
        "preview_url": None,
    },
    "ostep": {
        "title_short": "步骤说明不可抓",
        "badge_class": "badge-should",
        "badge_text": "需文本进源码",
        "term": "步骤说明不可抓",
        "definition": "步骤条上的标题与说明须写入 HTML 文本；进行中/完成态勿只靠颜色，否则安装/认证流程对 RAG 不完整",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；md 可用有序列表表达",
        "prompt": "我在看昇腾社区流程页（组件：OStep 步骤条，暂无确认 DOM 样例 URL），这个三步流程每一步的标题和说明原文是什么？当前进行到哪一步？",
        "prompt_plain": "我在看昇腾社区流程页（组件：OStep 步骤条，暂无确认 DOM 样例 URL），这个三步流程每一步的标题和说明原文是什么？当前进行到哪一步？",
        "answer": "没有含 o-step 的样例页时，若步骤文案只在图标/颜色态里、说明依赖 tooltip，静态 HTML 可能只有「1、2、3」而无正文，我无法复述完整流程说明。",
        "insights": [
            ("步骤标题须可见文本", "勿只靠数字圈"),
            ("状态勿只靠颜色", "aria/文本标注进行中"),
            ("说明宜在步骤旁", "非悬停才见"),
        ],
        "root_cause": "流程知识绑在视觉步骤态上，未平铺为可引用正文",
        "subcauses": [
            ("说明在 tooltip", "首包无文本", "每步标题+说明 SSR 输出"),
            ("动态 current 步", "其余步文案剥离", "全部步骤 DOM 保留"),
            ("无 md 平行轨", "HTML 残缺", "流程页出 MD 版安装/认证说明"),
        ],
        "preview_url": None,
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
        "answer": "首页 o-nav 一级链接多数在首包可见，我能列出文档/开发者等入口文案。若二级菜单依赖悬停注入或 button 跳转，子级 href 可能缺失，答案会不完整。",
        "insights": [
            ("一级链多可见", "o-nav 文本链接通常在首包"),
            ("二级或有悬停门", "下拉子项需同样进源码"),
            ("纯交互可剥离", "换肤/语言切换不必当知识正文入库"),
        ],
        "root_cause": "导航子级若依赖悬停注入，发现层不完整",
        "subcauses": [
            ("子菜单未 SSR", "悬停才挂链", "全部导航 a[href] 进首包 HTML"),
            ("按钮冒充链接", "无 href 的 click 跳转", "跳转一律用链接组件"),
            ("入库噪声", "主题切换等文案进库", "管道可过滤 data-llm-exclude 的纯 UI"),
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
        "answer": "页脚链接多数在静态 HTML 中可见，我能列出主要列与 href。若某列仅图标或链接被 JS 后填，对应入口会对齐 sitemap 时丢失。",
        "insights": [
            ("页脚是第二发现层", "补全顶栏未覆盖入口"),
            ("列标题宜稳定", "便于站图分组"),
            ("勿纯图标无文本", "链接需可读 anchor text"),
        ],
        "root_cause": "页脚作为站点地图补充层，若链接不全或文案漂移，深页发现受损",
        "subcauses": [
            ("链接 JS 注入", "首包空列", "页脚各列 SSR 全量 a[href]"),
            ("文案年度改版", "旧 chunk 误导", "列名稳定或做重定向说明"),
            ("与 llms 未对齐", "Agent 漏入口", "llms 清单含页脚关键链"),
        ],
        "preview_url": HOME,
    },
    "obutton": {
        "title_short": "按钮与链接角色混淆",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "按钮与链接角色混淆",
        "definition": "跳转型控件应是可抓链接；纯提交/弹层按钮文案入库时宜剥离，避免被当成正文结论",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页大量 CTA 按钮",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，首页上「立即下载 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。',
        "prompt_plain": f"我在看社区首页（{HOME}），首页上「立即下载 / 了解更多」这类按钮分别会带到哪个官方 URL？把 href 给我。",
        "answer": "若 CTA 是 button + JS 跳转而非 a[href]，静态抓取看不到目标地址，我只能复述按钮文案，给不出可靠落地 URL。",
        "insights": [
            ("跳转应用链接", "可抓 href"),
            ("提交类宜剥离", "「提交/关闭」勿当知识"),
            ("文案需可证伪", "与真实落地一致"),
        ],
        "root_cause": "把导航做成不可抓的按钮点击，导致入口 URL 丢失",
        "subcauses": [
            ("button 伪链", "无 href", "跳转型改 a 或带 href 的组件"),
            ("文案入库噪声", "操作词进 chunk", "管道过滤纯操作按钮"),
            ("弹层唯一说明", "点开才见", "关键说明同步正文"),
        ],
        "preview_url": HOME,
    },
    "olink": {
        "title_short": "链接 href 缺失",
        "badge_class": "badge-bad",
        "badge_text": "需真实 href",
        "term": "链接 href 缺失",
        "definition": "正文与导航中的链接必须带真实 href；伪链、javascript: 或空 href 会导致 Agent 无法跟进深页",
        "sample_url": HOME,
        "sample_label": "社区首页",
        "desc_extra": "首页正文与导航含大量 OLink",
        "prompt": f'我在看 <a href="{HOME}" target="_blank" rel="noopener">社区首页</a>，正文里「查看文档」这类链接的 href 原文是什么？有没有 javascript:void 或空链？',
        "prompt_plain": f"我在看社区首页（{HOME}），正文里「查看文档」这类链接的 href 原文是什么？有没有 javascript:void 或空链？",
        "answer": "多数官方入口有正常 href，我能列出文档/下载等链接。若部分链是 # 或 onclick，静态管道无法跟随，我会错误地认为「没有官方文档页」。",
        "insights": [
            ("href 必须可爬", "站内用绝对或根相对路径"),
            ("外链宜标注", "rel/title 辅助"),
            ("md 用标准语法", "[text](url)"),
        ],
        "root_cause": "链接组件退化为点击处理器，URL 语义未进入 HTML",
        "subcauses": [
            ("span 冒充链接", "无 a 标签", "可导航一律 OLink/a"),
            ("href=\"#\"", "占位链", "未就绪勿渲染假链"),
            ("相对路径混乱", "镜像抓取失败", "统一 canonical 绝对 URL"),
        ],
        "preview_url": HOME,
    },
    "odropdown": {
        "title_short": "下拉项悬停才可见",
        "badge_class": "badge-should",
        "badge_text": "子项须进源码",
        "term": "下拉项悬停才可见",
        "definition": "下拉菜单内导航项须在源码或可展开结构中可读；勿悬停/点击才注入子链，否则发现层断裂",
        "sample_url": CLUSTER,
        "sample_label": "集群产品页",
        "desc_extra": "集群页等含产品线下拉/筛选",
        "prompt": f'我在看 <a href="{CLUSTER}" target="_blank" rel="noopener">集群产品页</a>，顶部下拉里「Atlas 900 / Atlas 800」等产品线选项对应的落地页 URL 分别是什么？',
        "prompt_plain": f"我在看集群产品页（{CLUSTER}），顶部下拉里「Atlas 900 / Atlas 800」等产品线选项对应的落地页 URL 分别是什么？",
        "answer": "若下拉项不在首包 HTML、仅 hover 挂载，禁 JS 时我只能看到触发器文案，无法列出各产品线 href。",
        "insights": [
            ("子菜单应 SSR", "全部 a[href] 可见"),
            ("触发器非唯一信息", "项内文案要完整"),
            ("与 OMenu 勿混", "组件语义不同"),
        ],
        "root_cause": "下拉面板内容依赖交互才挂载，静态抓取看不到子导航",
        "subcauses": [
            ("display:none 空壳", "无 li/a", "SSR 输出完整 menu 列表"),
            ("portal 延迟挂", "首包无节点", "关键子链写入 body 静态区"),
            ("仅图标选项", "缺文本", "每项可读 label + href"),
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
        "title_short": "选择块与落地页",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "选择块与落地页",
        "definition": "若 Toggle 选项代表文档分类/筛选项且对应落地页，选项须可链可抓；纯筛选 UI 则不必入库",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；视选项是否映射可爬页面而定",
        "prompt": "我在看昇腾社区相关页面（组件：OToggle 选择块，暂无确认 DOM 样例 URL），每个 Toggle 选项是否对应独立官方文档 URL？请给出 href。",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OToggle 选择块，暂无确认 DOM 样例 URL），每个 Toggle 选项是否对应独立官方文档 URL？请给出 href。",
        "answer": "若无样例，我无法验证。若 Toggle 只是前端筛选当前页列表而无独立 URL，我不应把选项文案当站点 IA；若选项应对应分类页，则每项需 a[href]。",
        "insights": [
            ("映射页则须可链", "选项=入口"),
            ("纯筛选则剥离", "勿当知识"),
            ("态勿唯一", "选中项仍须 DOM 全量"),
        ],
        "root_cause": "Toggle 选项角色未区分「导航入口」与「纯 UI 筛选」",
        "subcauses": [
            ("选项无 URL", "却承载 IA", "分类改真实链接"),
            ("仅 client filter", "却进库", "纯筛选标注 exclude"),
            ("未选中项隐藏", "文本丢失", "全部选项 SSR"),
        ],
        "preview_url": None,
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
        "answer": "搜索框本身不提供文档列表；若 sitemap/导航/llms 不完整，仅靠搜索 API 对禁 JS 管道不可达。搜索是补充，不能替代可爬 URL。",
        "insights": [
            ("搜索非 sitemap", "不能唯一发现层"),
            ("结果页宜可链", "若有 SSR 结果 URL"),
            ("文档须平行可达", "llms/导航补全"),
        ],
        "root_cause": "把搜索当成文档唯一入口，忽视静态可爬链路",
        "subcauses": [
            ("无 sitemap", "深页不可达", "维护 llms/sitemap"),
            ("搜索仅 client", "首包无范围说明", "检索范围写文档"),
            ("结果无稳定 URL", "不可分享/抓取", "SSR 搜索结果页"),
        ],
        "preview_url": HOME,
    },
    "oselect": {
        "title_short": "选择器选项可抓性",
        "badge_class": "badge-should",
        "badge_text": "视情况",
        "term": "选择器选项可抓性",
        "definition": "若选项映射文档/版本，选项文本与对应页应可抓；纯表单选择则不必入库",
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 DOM 样例；视是否映射文档版本",
        "prompt": "我在看昇腾社区相关页面（组件：OSelect 选择器，暂无确认 DOM 样例 URL），下拉里每个 CANN 版本选项对应的文档/下载页 URL 是什么？",
        "prompt_plain": "我在看昇腾社区相关页面（组件：OSelect 选择器，暂无确认 DOM 样例 URL），下拉里每个 CANN 版本选项对应的文档/下载页 URL 是什么？",
        "answer": "若无样例，我无法验证。若 select 只是表单字段而无链接，选项不必当知识；若选项代表版本文档，则每项应有可爬落地页或在旁注列出映射。",
        "insights": [
            ("版本选型须可证伪", "选项→URL"),
            ("纯表单则剥离", "勿进库"),
            ("option 文本要完整", "非 value 隐藏"),
        ],
        "root_cause": "Select 选项角色未区分「版本导航」与「表单字段」",
        "subcauses": [
            ("选项无映射", "却承载 IA", "版本改链接或旁注表"),
            ("options JS 拉取", "首包空", "SSR 关键 option"),
            ("value 不可读", "仅数字 id", "text 用人类可读版本号"),
        ],
        "preview_url": None,
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
        "sample_url": None,
        "sample_label": None,
        "desc_extra": "暂无确认 o-trees DOM 样例；与 OMenu 类似，文档树宜 SSR",
        "prompt": "我在看昇腾文档站（组件：Trees 树，暂无确认 DOM 样例 URL），手册树里「算子开发」下所有叶子文档的标题和 URL 是什么？",
        "prompt_plain": "我在看昇腾文档站（组件：Trees 树，暂无确认 DOM 样例 URL），手册树里「算子开发」下所有叶子文档的标题和 URL 是什么？",
        "answer": "若树形目录由前端懒加载，静态 HTML 只有根节点或空壳，我无法列出「算子开发」下叶子 URL。这与 OMenu/侧栏 SSR 问题同类。",
        "insights": [
            ("树=发现层", "须全量或 sibling 链"),
            ("懒加载断 RAG", "子级不在首包"),
            ("md 可嵌套列表", "补 HTML 缺口"),
        ],
        "root_cause": "文档树依赖客户端展开，静态管道看不到子节点链接",
        "subcauses": [
            ("懒加载子树", "首包空", "SSR 当前分支或全树"),
            ("节点非链接", "仅 click", "叶子 a[href]"),
            ("无 llms 补", "Agent 迷路", "目录 MD 平行轨"),
        ],
        "preview_url": None,
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
        "answer": "若卡片标题/摘要/链接在静态 HTML 中，我能列表回答。若只有封面图无 alt、链接是 onclick，卡片内容对 RAG 残缺。",
        "insights": [
            ("三要素须齐", "标题+摘要+href"),
            ("图需 alt", "图意转写"),
            ("md 可标题+段落+链", "平行轨"),
        ],
        "root_cause": "卡片把发现信息绑在图+点击态，未平铺为可引用文本链",
        "subcauses": [
            ("仅图片无 alt", "图意丢失", "补 alt/figcaption"),
            ("摘要 JS 拉", "首包空", "SSR 卡片列表"),
            ("整卡 onclick", "无 href", "标题链 a[href]"),
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
        "answer": "若有真实 table 且单元格为文本，我能按行列回答。若是图片表或 div 伪表无 th/td 语义，静态抓取无法可靠还原参数对照。",
        "insights": [
            ("真 table", "th/td 语义"),
            ("忌截图表", "图表格无法问答"),
            ("md 平行表", "RAG 友好"),
        ],
        "root_cause": "参数知识以非语义表格或图片交付，单元格不可问答",
        "subcauses": [
            ("参数图代替表", "不可抓", "改 HTML/Markdown 表"),
            ("div 伪表", "无 th", "用语义 table"),
            ("合并单元格滥用", "列错位", "规范表头"),
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

SKIP_CONTENT = {"ocarousel"}  # preserve hand-written page

CSS_BLOCK = Path(DOCS / "problems-omenu.html").read_text(encoding="utf-8")
CSS = CSS_BLOCK.split("<style>")[1].split("</style>")[0]

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


def render_sidebar(active: str | None, *, principles: bool = False) -> str:
    lines = ['  <aside class="comp-sidebar" aria-label="组件列表">', '    <div class="comp-sidebar-title">组件列表</div>', '    <nav class="comp-nav">']
    for group, items in GROUPS:
        lines.append(f'      <div class="comp-group-label">{group}</div>')
        lines.append("      <ul>")
        for slug, name in items:
            if principles and slug == "ocarousel":
                cls = ' class="active"' if active == "ocarousel" else ""
                lines.append(f'        <li><a href="principles-affinity.html"{cls}>{name}</a></li>')
            else:
                href = f"problems-{slug}.html"
                cls = ' class="active"' if active == slug else ""
                lines.append(f'        <li><a href="{href}"{cls}>{name}</a></li>')
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


def render_page(slug: str, name: str, probe: dict) -> str:
    comp_label = name.split()[0] if name else slug
    insights_html = "\n".join(
        f'          <li><strong>{t}</strong>：{d}。</li>' for t, d in probe["insights"]
    )
    sub_html = ""
    for i, (title, desc, fix) in enumerate(probe["subcauses"], 1):
        sub_html += f"""
      <div class="content-unit">
        <h3>{i}. {title}</h3>
        <p>{desc}。</p>
        <div class="fix-suggestion">
          <h4>修改建议</h4>
          <p>{fix}。</p>
        </div>
      </div>"""

    sidebar = render_sidebar(slug)
    principles_href = "principles-affinity.html" if slug == "ocarousel" else f"principles-{slug}.html"

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
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="index.html">社区 <span>AI 亲和原则</span></a>
    <nav class="site-nav" aria-label="主导航">
      <a href="index.html">首页</a>
      <a href="mintlify.html">友商对照</a>
      <a href="reachability.html">社区诊断</a>
      <a href="community-ui.html" class="active">组件亲和</a>
    </nav>
  </div>
</div>

<div class="subnav" aria-label="组件详情二级导航">
  <div class="subnav-inner">
    <a class="subnav-back" href="community-ui.html">← 返回</a>
    <nav class="subnav-tabs">
      <a href="problems-{slug}.html" class="active">实测问题</a>
      <a href="{principles_href}">亲和原则</a>
    </nav>
  </div>
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
{desc_line2(probe)}
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
      <div class="content-unit">
        <h3>3. 问题洞察</h3>
        <p>大模型的回答指向以下结论：</p>
        <ul>
{insights_html}
        </ul>
      </div>
    </section>

    <section class="section" id="guide">
      <h2 id="solution">根因分析</h2>
      <div class="content-unit">
        <p>{comp_label}相关问题的核心原因是：<strong style="color:var(--text)">{probe["root_cause"]}</strong>。</p>
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
    generated: list[str] = []
    skipped: list[str] = []

    for _, slug, name in all_components():
        out = DOCS / f"problems-{slug}.html"
        if slug in SKIP_CONTENT:
            skipped.append(out.name)
            continue
        if out.exists():
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
    copy_to_report_serve()

    print(f"Generated: {len(generated)}")
    for f in sorted(generated):
        print(f"  {f}")
    print(f"Skipped existing/hand-written: {len(skipped)}")
    print(f"Sidebars patched: {sidebars_patched}")
    print(f"community-ui detail links updated: {links_updated} rows")
    print(f"Copied to {REPORT}")


if __name__ == "__main__":
    main()
