# 参考对话导出目录

本目录用于存放从 Claude 导出的对话内容，供研究报告与 HTML 站点引用、填充。

## 如何从 Claude 导出对话

1. 在浏览器中打开对应的 Claude 分享链接
2. 在对话页面右上角点击 **「…」** 或 **Share** 菜单
3. 选择 **Export** / **复制对话** / **Download**
4. 将内容粘贴到本目录下对应的 `.md` 文件中「对话正文」区块
5. 保存后告知 Cursor Agent，即可自动解析并更新 HTML 站点

## 文件清单

| 文件 | 对话主题 | 关联 HTML 模块 | Claude 链接 |
|------|----------|----------------|-------------|
| [07-官方信源感知弱/](./官方信源感知弱/) | 官方信源感知弱 · 三模型对话 | problems-answer-search.html | [Claude 打开](https://claude.ai/share/6bb1473b-7493-40d5-97b2-37523a95fa8b) |
| [01-文档内容对比分析.md](./claude-conversations/01-文档内容对比分析.md) | Ascend-C 文档内容对比分析 | problems.html | [打开](https://claude.ai/share/3f2d4c30-6210-4259-9a9b-de7943cf6fff) |
| [02-读取AscendC文档内容.md](./claude-conversations/02-读取AscendC文档内容.md) | 读取 Ascend C 文档内容 | background.html | [打开](https://claude.ai/share/d11287e8-ffd5-41f0-9b1d-b2d76b20a84c) |
| [03-知识库与大模型集成方案.md](./claude-conversations/03-知识库与大模型集成方案.md) | 知识库与大模型的集成方案 | solutions.html | [打开](https://claude.ai/share/272104cc-2681-453e-9cbd-5ac25f16e999) |
| [04-AscendC是什么.md](./claude-conversations/04-AscendC是什么.md) | Ascend C 是什么 | background.html | [打开](https://claude.ai/share/4091dd7f-2949-4197-ace5-ed546d108fb4) |
| [05-AscendC语言学习指南.md](./claude-conversations/05-AscendC语言学习指南.md) | Ascend C 语言学习指南 | background.html / principles.html | [打开](https://claude.ai/share/ea0e9a83-f5d6-448a-a53b-59d30392d83f) |
| [06-静态Tensor编程内容解读.md](./claude-conversations/06-静态Tensor编程内容解读.md) | 静态 Tensor 编程内容解读 | principles.html | [打开](https://claude.ai/share/6290a369-81d8-4064-b473-d9151e1ccd89) |
| [hiascend-discovery-probe.md](./机器发现层探测/hiascend-discovery-probe.md) | 昇腾社区机器发现层探测（llms.txt / robots / sitemap） | problems-structure-llms.html | — |
| [hiascend-metadata-probe.md](./元数据论证/hiascend-metadata-probe.md) | 昇腾文档页元数据探测（title / version / doc_id） | problems-structure-metadata.html | — |

## 目录结构

```
references/
├── README.md                          ← 本说明
├── 官方信源感知弱/                    ← 官方信源感知弱 · 三模型对话导出
│   ├── README.md
│   └── claude-对话.md
├── claude-conversations/              ← Claude 对话导出（粘贴区）
│   ├── 01-文档内容对比分析.md
│   ├── 02-读取AscendC文档内容.md
│   ├── 03-知识库与大模型集成方案.md
│   ├── 04-AscendC是什么.md
│   ├── 05-AscendC语言学习指南.md
│   └── 06-静态Tensor编程内容解读.md
├── 机器发现层探测/                    ← 站点配置 HTTP 探测复现脚本
│   └── hiascend-discovery-probe.md
├── 元数据论证/                        ← 页面元数据存在形态探测
│   └── hiascend-metadata-probe.md
└── module-exports/                    ← 研究报告分模块导出
    ├── 01-研究背景.md
    ├── 02-当前问题.md
    ├── 03-解决方案.md
    └── 04-亲和原则.md
```

## 更新 HTML 工作流

```
Claude 对话 → 粘贴到 claude-conversations/*.md → Agent 解析 → 更新 HTML 对应模块
```
