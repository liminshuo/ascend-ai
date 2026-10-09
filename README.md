# 昇腾社区 AI 亲和原则研究

静态研究报告站（HTML），对照 Mintlify / NVIDIA / Ascend 的可达性与可引用性（md / html）。

## 本地预览

```bash
# 推荐：禁缓存，避免侧栏切换仍看到旧页
python3 docs/serve.py -p 8080

# 或手动（可能被浏览器缓存旧 HTML）
# cd docs && python3 -m http.server 8080
```

打开 http://127.0.0.1:8080/

## 在线

GitHub Pages：https://liminshuo.github.io/geo-affinity-principles/

仓库（新建）：`https://github.com/liminshuo/geo-affinity-principles`

首次发布到该仓库：

```bash
# 在 GitHub 网页创建空仓库 geo-affinity-principles（不要勾选 README）
git remote add geo-affinity-principles https://github.com/liminshuo/geo-affinity-principles.git
git push -u geo-affinity-principles main
```

然后在仓库 **Settings → Pages**：Source 选 `Deploy from a branch`，Branch `main`，Folder **`/docs`**。

源码目录：`report-serve/`（发布副本：`docs/`）。Pages 使用分支 `main` / 目录 `/docs`。

旧站（可选保留）：https://liminshuo.github.io/ascend-ai/
