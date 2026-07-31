#!/usr/bin/env bash
# 推送并提示开启 GitHub Pages（docs/）
set -euo pipefail
cd "$(dirname "$0")"

git remote set-url origin https://github.com/liminshuo/ascend-ai.git
echo "→ git push origin main"
git push -u origin main

echo
echo "Pages 源：Settings → Pages → Deploy from a branch → main / docs"
echo "站点：https://liminshuo.github.io/ascend-ai/"
