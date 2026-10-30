---
title: 官方信源感知弱 · Claude 回答（Pages 导出）
claude_share: https://claude.ai/share/0bd836f0-e4f6-4e90-acd7-c2d0b8a14885
export_source: Apple Pages 导出（claudeai-回答.pages）
html_page: problems-answer-claude.html
html_module: problems-answer-search.html
status: 已导出
export_date: 2026-06-06
---

# 官方信源感知弱 · Claude 回答（Pages 导出）

> **Claude 对话**：[打开原始分享](https://claude.ai/share/0bd836f0-e4f6-4e90-acd7-c2d0b8a14885)  
> **关联模块**：当前问题 · 官方信源感知弱  
> **测试问题**：「基于官方资料，介绍一下 Ascend C 算子开发」  
> **说明**：由 `claudeai-回答.pages` 导出；正文段末含人工标注 `(URL:…)`，与 [claude-对话.md](./claude-对话.md) 完整对话版互为补充。

## 来源溯源摘要

**标注说明**

- 段末 `(URL:…)` 为 Pages 文档中保留的人工标注，按 URL 站点归类：`hiascend.com` → 昇腾社区官方，其余 → 第三方教程。
- 本导出共 **17** 个带 URL 的信息单元：昇腾社区官方 **35%**（6/17），第三方 **65%**（11/17）。
- 与 Claude 分享页原文对比：本版段末均显式写出 URL，**严格 URL 口径**为 **100%**（17/17 段含可核对链接）；分享页正文几乎不含 `hiascend.com` 直链。

| 段 | 内容单元 | 判定 | 标注 URL |
|----|----------|------|----------|
| 1 | 一、什么是 Ascend C · 发布会 | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/653737107) |
| 2 | 一、语言定位 | **昇腾社区官方** | [CANN 社区版导读](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/index/index.html) |
| 3 | 一、NPU / CANN | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/653737107) |
| 4 | 二、核心优势 | **昇腾社区官方** | [CANN 社区版导读](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/index/index.html) |
| 5 | 二、API 分层 | **昇腾社区官方** | [Ascend C 入口](https://www.hiascend.com/cann/ascend-c) |
| 6 | 三、核函数与多核 · 首段 | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/653497102) |
| 7 | 三、Global / Local Memory | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/653497102) |
| 8 | 四、流水线范式 · 导语 | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/687359397) |
| 9 | 四、Init / Process | 第三方教程 | [博客园 ZOMI](https://www.cnblogs.com/ZOMI/articles/18560677) |
| 10 | 四、TQue / Tensor | 第三方教程 | [博客园 ZOMI](https://www.cnblogs.com/ZOMI/articles/18560677) |
| 11 | 五、API 体系 | 第三方教程 | [阿里云](https://developer.aliyun.com/article/1644105) |
| 12 | 六、Tiling 机制 | 第三方教程 | [CSDN](https://blog.csdn.net/weixin_66366070/article/details/140343119) |
| 13 | 七、孪生调试 · 导语 | **昇腾社区官方** | [Ascend C 入口](https://www.hiascend.com/cann/ascend-c) |
| 14 | 七、CPU / NPU 域调试 | 第三方教程 | [知乎专栏](https://zhuanlan.zhihu.com/p/653497102) |
| 15 | 八、开发流程 | 第三方教程 | [博客园](https://www.cnblogs.com/taixian/p/18329141) |
| 16 | 八、核函数定义 | 第三方教程 | [腾讯云](https://cloud.tencent.com/developer/article/2476178) |
| 17 | 九、学习路径 | **昇腾社区官方** | [Ascend C 入口](https://www.hiascend.com/cann/ascend-c) |

---

## 对话正文

以下是基于官方资料和权威社区文档对 Ascend C 算子开发的系统介绍：

### Ascend C 算子开发概览

#### 一、什么是 Ascend C

2023 年 5 月 6 日，在昇腾 AI 开发者峰会上，华为正式发布了面向算子开发场景的昇腾 Ascend C 编程语言。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/653737107)

Ascend C 是面向算子开发场景的编程语言，原生支持 C 和 C++ 标准规范，最大化匹配用户开发习惯；通过多层接口抽象、自动并行计算、孪生调试等关键技术，极大提高算子开发效率，助力 AI 开发者低成本完成算子开发和模型调优部署。  
标注：[CANN 社区版导读](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/index/index.html)

和 CUDA 开发的算子运行在 GPU 上一样，基于 Ascend C 开发的算子，可以通过异构计算架构 CANN（Compute Architecture for Neural Networks）运行在昇腾 AI 处理器（NPU）上。CANN 是使能昇腾 AI 处理器的一个软件栈，通过软硬件协同优化，能够充分发挥昇腾 AI 处理器的强大算力。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/653737107)

#### 二、核心优势

使用 Ascend C 进行自定义算子开发的突出优势有：C/C++ 原语编程；编程模型屏蔽硬件差异；编程范式提高开发效率；类库 API 封装。  
标注：[CANN 社区版导读](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/index/index.html)

开发者采用标准 C++ 语法和类库 API 进行编程。类库 API 分为两种：基础 API 和高阶 API。基础 API 实现对硬件能力的抽象，开放芯片的能力，保证完备性和兼容性；高阶 API 通常会调用多种基础 API 实现常用的计算算法，用于提高开发效率。  
标注：[Ascend C 入口](https://www.hiascend.com/cann/ascend-c)

#### 三、编程模型：核函数与多核并行

使用 Ascend C 开发的算子运行在 AI Core 上，AI Core 是昇腾 NPU 硬件平台的计算核心，NPU 内部有多个 AI Core。Ascend C 编程过程中会将需要处理的数据拆分，同时在多个 AI Core 上运行，从而获取更高的性能。多个 AI Core 共享相同的指令代码，每个核上的运行实例唯一的区别是 block_idx 不同，开发者只需要关注单核上的处理程序，也就是核函数。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/653497102)

要完成 AI Core 上的数据计算，输入数据需要先从外部存储 Global Memory 搬运进 AI Core 的内部存储 Local Memory，然后使用计算接口完成计算，得到最终结果，再搬出到外部存储 Global Memory 上。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/653497102)

#### 四、编程范式：流水线并行

Ascend C 编程范式是一种流水线式的编程范式，把算子核内的处理程序分成多个流水任务（Stage），以张量（Tensor）为数据载体，通过队列（Queue）完成任务间通信和同步，并通过统一的内存管理模块（Pipe）管理任务间通信内存。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/687359397)

自定义向量算子核心部分一般由两个函数组成，分别是 Init() 函数（初始化函数）与 Process() 函数（执行函数）。Init() 函数完成板外数据定位以及板上内存初始化工作；Process() 函数完成向量算子的实现，分成三个流水任务：CopyIn、Compute、CopyOut。CopyIn 负责板外数据搬入，Compute 负责向量计算，CopyOut 负责板上数据搬出。  
标注：[博客园 ZOMI](https://www.cnblogs.com/ZOMI/articles/18560677)

流水线任务之间存在数据依赖，需要进行数据传递。Ascend C 中使用 TQue 队列完成任务之间的数据通信和同步，提供 EnQue、DeQue 等基础 API；TQue 队列管理不同层级的物理内存时，用一种抽象的逻辑位置（TPosition）来表达各级别的存储，代替了片上物理存储的概念，开发者无需感知硬件架构。另外，Ascend C 使用 GlobalTensor 和 LocalTensor 作为数据的基本操作单元。  
标注：[博客园 ZOMI](https://www.cnblogs.com/ZOMI/articles/18560677)

#### 五、API 体系

基础 API 包括计算类、数据搬运、内存管理和任务同步等，使用基础 API 自由度更高，可以通过 API 组合实现自己的算子逻辑。具体包括：计算类 API（标量计算、向量计算、矩阵计算 API）；数据搬运 API（如 DataCopy 接口，负责 Global Memory 与 Local Memory 之间的数据搬运）；内存管理 API（如 AllocTensor、FreeTensor 接口，用于动态管理板上内存）。  
标注：[阿里云](https://developer.aliyun.com/article/1644105)

#### 六、Tiling 机制

由于 NPU 中 AI Core 内部存储无法完全容纳算子输入输出的所有数据，需要每次搬运一部分输入数据进行计算然后搬出，再搬运下一部分输入数据进行计算，这个过程就称之为 Tiling。切分数据的算法称为 Tiling 算法或 Tiling 策略。由于 Tiling 实现中完成的均为标量计算，AI Core 并不擅长，所以将其独立出来放在 Host 侧 CPU 上执行。  
标注：[CSDN](https://blog.csdn.net/weixin_66366070/article/details/140343119)

#### 七、孪生调试

Ascend C 直击算子开发痛点，大幅提升算子调试效率。既可以在 CPU 域进行调试调优，又可以在 NPU 侧进行调优验证，通过 CPU 域与 NPU 域相结合的方式，降低调试难度，提升调试效率。  
标注：[Ascend C 入口](https://www.hiascend.com/cann/ascend-c)

基于 NPU 域算子的调用接口编写程序，通过毕昇编译器编译后运行，可以完成算子 NPU 域的运行验证；基于 CPU 域算子的调用接口编写程序，通过标准的 GCC 编译器进行编译后运行，并通过 GDB 通用调试工具进行单步调试，精准验证程序执行流程是否符合预期。孪生调试的能力，大大提升了算子的调试效率。  
标注：[知乎专栏](https://zhuanlan.zhihu.com/p/653497102)

#### 八、算子开发基本流程

开发基本流程包括：环境准备（安装 CANN 开发套件包）、算子分析（分析算子的数学表达式、输入输出数据类型和计算逻辑）、核函数开发，以及后续的编译与验证。  
标注：[博客园](https://www.cnblogs.com/taixian/p/18329141)

在完成算子分析后，可以正式开始开发算子代码，第一步应该完成对核函数的定义和封装。核函数使用 `__global__` 函数类型限定符来标识可被调用，使用 `__aicore__` 函数类型限定符来标识该核函数在设备端 AI Core 上执行。  
标注：[腾讯云](https://cloud.tencent.com/developer/article/2476178)

#### 九、学习路径（官方推荐）

官方提供三个学习层次：HelloWorld 快速上手（完成矢量算子核函数和基础调用能力）；开发流程全面掌握（完成 Tiling 开发，并进行单算子、网络中算子调用）；高性能编程深度驾驭（开发高性能的复杂算子，充分发挥硬件能力，包括矩阵/融合算子编程）。  
标注：[Ascend C 入口](https://www.hiascend.com/cann/ascend-c)

## 标注 URL 索引

| # | 站点类型 | URL |
|---|----------|-----|
| 1 | 第三方 | https://zhuanlan.zhihu.com/p/653737107 |
| 2 | 昇腾社区官方 | https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/910beta1/index/index.html |
| 3 | 昇腾社区官方 | https://www.hiascend.com/cann/ascend-c |
| 4 | 第三方 | https://zhuanlan.zhihu.com/p/653497102 |
| 5 | 第三方 | https://zhuanlan.zhihu.com/p/687359397 |
| 6 | 第三方 | https://www.cnblogs.com/ZOMI/articles/18560677 |
| 7 | 第三方 | https://developer.aliyun.com/article/1644105 |
| 8 | 第三方 | https://blog.csdn.net/weixin_66366070/article/details/140343119 |
| 9 | 第三方 | https://www.cnblogs.com/taixian/p/18329141 |
| 10 | 第三方 | https://cloud.tencent.com/developer/article/2476178 |
