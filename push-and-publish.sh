#!/usr/bin/env bash
# 推送并触发 GitHub Pages 上线（需本机已能访问 liminshuo/ascend-ai）
set -euo pipefail
cd "$(dirname "$0")"

echo "→ git push origin main"
git push -u origin main

echo "→ 启用 GitHub Pages（需已安装 gh 并登录）"
if command -v gh >/dev/null 2>&1; then
  gh api -X POST "repos/liminshuo/ascend-ai/pages" \
    -f build_type=workflow \
    2>/dev/null || true
  gh api -X PUT "repos/liminshuo/ascend-ai/pages" \
    -f build_type=workflow \
    -f source[branch]=main \
    -f source[path]=/docs \
    2>/dev/null || true
  echo "Actions: https://github.com/liminshuo/ascend-ai/actions"
  echo "Site:    https://liminshuo.github.io/ascend-ai/"
else
  echo "未检测到 gh。请在网页开启 Pages："
  echo "  Settings → Pages → Build and deployment → GitHub Actions"
  echo "推送后打开: https://liminshuo.github.io/ascend-ai/"
fi
