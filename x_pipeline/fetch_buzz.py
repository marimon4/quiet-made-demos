"""
バズ投稿収集スクリプト
buzz_input.txt から手動コピペされた投稿を読み込み、buzz_cache.json に変換する。
"""

import json
import os
from datetime import datetime
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent
INPUT_FILE = PIPELINE_DIR / "buzz_input.txt"
CACHE_FILE = PIPELINE_DIR / "buzz_cache.json"


def parse_buzz_input(filepath: Path) -> list[dict]:
    """buzz_input.txt を --- 区切りでパースして投稿リストを返す。"""
    if not filepath.exists():
        print(f"[INFO] {filepath.name} が見つかりません。空のキャッシュを作成します。")
        return []

    content = filepath.read_text(encoding="utf-8").strip()
    if not content:
        print("[INFO] buzz_input.txt は空です。")
        return []

    raw_blocks = content.split("---")
    posts = []
    for block in raw_blocks:
        text = block.strip()
        if text:
            posts.append({
                "text": text,
                "engagement": None,
                "source": "manual_input"
            })

    return posts


def load_existing_cache(filepath: Path) -> list[dict]:
    """既存のキャッシュがあれば読み込む。"""
    if not filepath.exists():
        return []
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        return data.get("posts", [])
    except (json.JSONDecodeError, KeyError):
        return []


def save_cache(filepath: Path, posts: list[dict]) -> None:
    """キャッシュファイルに保存する。"""
    cache = {
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "post_count": len(posts),
        "posts": posts
    }
    filepath.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    print("=== バズ投稿収集 ===")

    new_posts = parse_buzz_input(INPUT_FILE)
    existing_posts = load_existing_cache(CACHE_FILE)

    # 重複排除（テキスト完全一致）
    existing_texts = {p["text"] for p in existing_posts}
    unique_new = [p for p in new_posts if p["text"] not in existing_texts]

    merged = existing_posts + unique_new
    save_cache(CACHE_FILE, merged)

    print(f"  新規: {len(unique_new)}件")
    print(f"  合計: {len(merged)}件 → {CACHE_FILE.name}")

    if unique_new:
        print("\n  [追加された投稿プレビュー]")
        for p in unique_new[:3]:
            preview = p["text"][:60].replace("\n", " ")
            print(f"    - {preview}...")


if __name__ == "__main__":
    main()
