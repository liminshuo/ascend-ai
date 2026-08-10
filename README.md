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

GitHub Pages：https://liminshuo.github.io/ascend-ai/

源码目录：`report-serve/`（发布副本：`docs/`）。Pages 使用分支 `main` / 目录 `/docs`。
