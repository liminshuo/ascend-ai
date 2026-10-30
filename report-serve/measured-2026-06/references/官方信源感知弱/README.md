# 官方信源感知弱 · 参考对话导出

> 关联页面：[problems-answer-search.html](../../problems-answer-search.html)（检索阶段）；三模型原始回答 HTML 仍保留 `problems-answer-*.html`。

本目录存放「官方信源感知弱」主题下，三模型同 prompt 问答的导出与溯源分析。

## 文件清单

| 文件 | 模型 | 原始链接 |
|------|------|----------|
| [claude-对话.md](./claude-对话.md) | Claude AI | [打开](https://claude.ai/share/6bb1473b-7493-40d5-97b2-37523a95fa8b) |
| [claudeai-回答.md](./claudeai-回答.md) | Claude AI（Pages 导出） | [打开](https://claude.ai/share/0bd836f0-e4f6-4e90-acd7-c2d0b8a14885) · 段末含 `(URL:…)` 人工标注 |
| [claude-检索网页.md](./claude-检索网页.md) | Claude AI · 检索阶段 | 同左 · 联网检索 19 条 URL |
| [deepseek-对话.md](./deepseek-对话.md) | DeepSeek | [打开](https://chat.deepseek.com/share/ykxj9g8tu1kf468q8g) |
| [deepseek-回答.md](./deepseek-回答.md) | DeepSeek（Pages 导出） | 同左 · 段末含 `(URL:…)` 人工标注 |
| [deepseek-检索网页.md](./deepseek-检索网页.md) | DeepSeek · 检索阶段 | 同左 · 联网浏览 27 条 URL |
| [千问-对话.md](./千问-对话.md) | 通义千问 | [打开](https://www.qianwen.com/share/chat/5a2ecf85711544d698f85380f54721c4)（显示标注版 · 段级溯源详表） |
| [千问-回答.md](./千问-回答.md) | 通义千问（Pages 导出） | 同左 · 脚注版 `[^1]–[^13]` 正文 |
| [千问-检索网页.md](./千问-检索网页.md) | 通义千问 · 检索/参考链接 | 同左 · 脚注对应 13 条 URL |

## 站点内浏览

- Claude 对话页：[problems-answer-claude.html](../../problems-answer-claude.html)
- DeepSeek 对话页：[problems-answer-deepseek.html](../../problems-answer-deepseek.html)
- 千问 对话页：[problems-answer-qwen.html](../../problems-answer-qwen.html)

## 导出方法

1. 在浏览器打开 Claude / DeepSeek / 千问分享链接  
2. 复制完整对话正文  
3. 粘贴到对应 `.md` 文件的「对话正文」区块  
4. 刷新站点页面查看更新

## Claude 段级溯源标注

Claude 分享页不提供段级 citation，需在 `claude-对话.md` 中人工维护：

1. **检索源索引** — 「联网检索源」表格 #1–#17，引用时写 `[src:N]`
2. **段级溯源表** — 「来源溯源摘要」中填写判定、严格依据、可能来源、标注说明
3. **正文溯源块** — 各段首的 `> **溯源** · …` 块（与表格同步）；你提供的 URL 即**人工标注**
4. **判定口径** — 按标注 URL 站点归类（`hiascend.com` → 官方，其余第三方）；**模型内化**仅用于未标注段落

DeepSeek 正文含 `[reference:N]`，但分享页不展示可点击 URL；段级对照 URL 由人工标注写入 `deepseek-对话.md`（与 Claude 同 workflow）。
