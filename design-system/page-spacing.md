# 页面标题 Padding / 邻接 Margin / 表格 Padding

原则页与文档内页的排版间距。站点页：设计模式 → **UI 规范**（`docs/design-guide-ui.html`）。Token 写在 `docs/assets/css/tokens.css`。

## 原则

1. **Padding 是标题盒子内部的上下留白**，不承担盒子与盒子之间的空隙。
2. **相邻盒子之间另加 16px margin**（`--space-stack`）。Margin 与标题 padding **同时生效、不互相替代**。
3. **只在一侧写 16px**（上一块 `margin-bottom` 或下一块 `margin-top`）。相邻外边距折叠后仍为 16，避免双边各 16 且不折叠时变成 32。
4. **量的是边框盒之间的空隙**，不是文字到文字。文字到文字 = 上一块 padding-bottom + margin + 下一块 padding-top。
5. 组件 mock、侧栏、顶栏可用局部尺寸，不占用正文规格。

## 标题 Padding

| 层级 | Token | 上 / 下 | 选择器 |
|------|--------|---------|--------|
| H1 | `--space-h1-pad-y` | **32 / 32** | `.page-header > h1` |
| H2 | `--space-h2-pad-y` | **16 / 16** | `.section h2` |
| H3 | `--space-h3-pad-y` | **16 / 16** | `.section h3` / `h3.fn-h3` |
| H4 | `--space-h4-pad-y` | **16 / 16** | `.section h4` / `h4.fn-h4` |
| H5 | `--space-h5-pad-y` | **16 / 16** | `.section h5` / `h5.fn-h5` |

## 邻接 Margin（`--space-stack: 16px`）

| 相邻盒子 | Margin | 实现 |
|----------|--------|------|
| `main` 顶 → H1 盒子 | 16px | `--content-main-pad-top`（main 的 padding-top） |
| H1 盒子 → 首个 H2 盒子 | 16px | `.page-header { margin-bottom: 16px }`；H1 仍保留 32px 下 padding |
| H2 盒子 → 紧随正文 | 16px | `.section > h2 { margin-bottom: 16px }`；正文自身 margin 为 0 |
| 上节末块 → 下一节 H2 盒子 | 16px | 上节 `.section { margin-bottom: 16px }`；下一 H2 仍保留上 padding |
| 分组说明 → 下一 H4 盒子 | 16px | `.fn-h3-desc + h4.fn-h4 { margin-top: 16px }` |
| 折叠按钮条 → 展开卡片 | 16px | `.ex-fold-panel { margin-top: 16px }`；`[hidden]` 不占位 |
| 折叠按钮条 → 下一 H3 / H4 盒子 | 16px | `.ex-fold-bar { margin-bottom: 16px }`；示例组之间 `margin-top: 16px` |

## 表格 Padding

原则页对照表（`.aj`）。Padding 是单元格内部留白，与标题 `--space-hN-pad-y` 同一套量法。

| 区域 | Token | 上 / 下 | 左 / 右 | 选择器 |
|------|--------|---------|---------|--------|
| 表体单元格 | `--table-cell-pad` | **16 / 16** | **16 / 16** | `.aj td`、`.aj .aj-label` |
| 表头 | `--table-head-pad-y` / `--table-head-pad-x` | **12 / 12** | **16 / 16** | `.aj thead th` |
