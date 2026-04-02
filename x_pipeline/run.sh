#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== X投稿生成パイプライン ==="
echo ""

echo "1. バズ収集..."
python3 "$SCRIPT_DIR/fetch_buzz.py"
echo ""

echo "2. 傾向分析..."
python3 "$SCRIPT_DIR/analyze.py"
echo ""

echo "3. 投稿生成..."
python3 "$SCRIPT_DIR/generate_posts.py"
echo ""

echo "=== 完了 ==="
echo "output/ フォルダを確認してください。"
