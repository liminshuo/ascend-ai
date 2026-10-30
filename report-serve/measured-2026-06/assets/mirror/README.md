# 测试页面本地镜像

昇腾文档站禁止外站 iframe 嵌入在线 URL。抽屉使用精简版 `ascend-c-test-embed.html`（从完整镜像提取正文，图片仍指向官方 CDN）。

| 文件 | 用途 |
|------|------|
| `ascend-c-test-embed.html` | 什么是 Ascend C · 抽屉内嵌（推荐） |
| `ascend-c-test-page.html` | 完整页面镜像（依赖 Nuxt JS，iframe 内易空白） |
| `helloworld-link-snippet.html` | 链接语义 · LINK 占位符示意 |
| `helloworld-tab-snippet.html` | Tab 隐藏 · 全站 Tab 组件风险示意（非 HelloWorld 实页 UI） |
| `env-collapse-snippet.html` | 折叠面板 · 默认收起示意 |
| `helloworld-code-snippet.html` | 代码语义 · highlighttable 示意 |
| `add-operator-table-snippet.html` | 表格的结构语义 · Add 表1 设计规格示意 |
| `programming-model-table-snippet.html` | （旧）编程模型表1 · 保留作对照 |
| `env-note-snippet.html` | 注意提示 / 单文档结构 · 环境准备步骤嵌套 Note 示意 |
| `discovery-probe-snippet.html` | 机器发现层 · llms / robots / sitemap 探测示意 |

## 更新镜像

```bash
curl -sL "https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/900/programug/Ascendcopdevg/atlas_ascendc_map_10_0002.html" \
  -o assets/mirror/ascend-c-test-page.html
```

然后重新生成 embed（在项目根目录执行 Python 提取脚本，或手动更新 `ascend-c-test-embed.html`）。

## 本地预览

需通过 HTTP 服务打开：

```bash
python3 -m http.server 8080
```

访问 `http://localhost:8080/problems-content-image.html`。
