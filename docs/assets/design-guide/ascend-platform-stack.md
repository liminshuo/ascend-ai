> ## 建议稿（非线上实文件）
> 本文件为设计指导用平行 Markdown 示例：陈述首页平台栈架构图中的层级关系与产品链路，供 Agent / 爬虫读取。

# 昇腾 AI 基础软硬件平台

> 昇腾AI基础软硬件平台，构筑智能世界的基石——以下陈述栈关系，不背书营销视觉。

## 栈关系（自上而下）

行业应用依赖应用使能；应用使能依赖 AI 框架；AI 框架依赖硬件使能（CANN）；CANN 依赖昇腾系列硬件。MindStudio 与 CCAE 纵向贯穿应用使能、AI 框架与硬件使能层。

```
行业应用
  ↑ 依赖
应用使能
  ↑ 依赖
AI 框架
  ↑ 依赖
硬件使能（CANN）
  ↑ 依赖
昇腾系列硬件
```

## 各层内容

### 行业应用

- 互联网 · 金融 · 智慧城市 · 制造 · 能源 · 交通 · 教育（及更多行业场景）

### 应用使能

| 区块 | 产品 / 能力 |
|------|-------------|
| 云与服务 | ModelArts · HiAi Service · 第三方平台与服务 |
| 开发套件 | MindSDK（AI 应用软件开发套件） |
| 训练与推理 | MindSpeed（训练加速库）· MindIE（推理引擎） |
| 集群与端边 | MindCluster（集群使能）· MindEdge（端边使能） |

### AI 框架

- MindSpore 昇思（主框架）
- 并行支持：PyTorch · 飞桨 · TensorFlow（及更多）

### 硬件使能

- CANN 异构计算架构：https://www.hiascend.com/cann

### 昇腾系列硬件

- 集群：https://www.hiascend.com/hardware/cluster
- 服务器：https://www.hiascend.com/hardware/ai-server
- 加速卡：https://www.hiascend.com/hardware/accelerator-card
- 加速模块：https://www.hiascend.com/hardware/accelerator-module-A2
- 伙伴硬件

### 纵向贯穿

| 组件 | 作用 |
|------|------|
| MindStudio | 全流程工具链，覆盖应用使能 / 框架 / 硬件使能 |
| CCAE | 集群自智引擎，覆盖同上各层：https://www.hiascend.com/software/ccae |

## 相关链接

- 视觉楼层来源：https://www.hiascend.com/zh
