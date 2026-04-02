"""
バズ投稿の傾向分析スクリプト
buzz_cache.json を読み込み、Claude API で構文・トピック・トーンを分析する。
"""

import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PIPELINE_DIR = Path(__file__).parent
CACHE_FILE = PIPELINE_DIR / "buzz_cache.json"
ANALYSIS_FILE = PIPELINE_DIR / "analysis_result.json"

load_dotenv(PIPELINE_DIR / ".env")


def load_cache() -> list[dict]:
    """キャッシュファイルから投稿を読み込む。"""
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"{CACHE_FILE.name} が見つかりません。先に fetch_buzz.py を実行してください。")

    data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    if not posts:
        raise ValueError("キャッシュに投稿がありません。buzz_input.txt に投稿を追加してください。")
    return posts


def analyze_with_claude(posts: list[dict]) -> dict:
    """Claude API で投稿の傾向を分析する。"""
    client = anthropic.Anthropic()

    posts_text = "\n\n---\n\n".join(p["text"] for p in posts)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""以下はXでバズった投稿の一覧です。傾向を分析してJSON形式で返してください。

【分析項目】
1. syntax_patterns: よく使われる構文パターン（箇条書き型、数字型、ストーリー型など）とその出現割合
2. opening_hooks: 冒頭の言葉の傾向（例：「〇〇が変わった」「正直に言う」）
3. popular_topics: よく出るトピック・キーワード
4. length_tendency: 文章の長さの傾向（短文/中文/長文、平均的な文字数）
5. emotional_tones: 感情トーン（驚き・共感・批判・教育など）とその割合

【投稿一覧】
{posts_text}

JSONのみを返してください。説明文は不要です。"""
        }]
    )

    result_text = response.content[0].text.strip()

    # JSON部分を抽出（```json ... ``` で囲まれている場合に対応）
    if result_text.startswith("```"):
        lines = result_text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.startswith("```") and not inside:
                inside = True
                continue
            elif line.startswith("```") and inside:
                break
            elif inside:
                json_lines.append(line)
        result_text = "\n".join(json_lines)

    return json.loads(result_text)


def main():
    print("=== 傾向分析 ===")

    posts = load_cache()
    print(f"  分析対象: {len(posts)}件の投稿")

    result = analyze_with_claude(posts)

    ANALYSIS_FILE.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  結果: {ANALYSIS_FILE.name} に保存")

    # サマリー表示
    print("\n  [分析サマリー]")
    if "syntax_patterns" in result:
        print("  構文パターン:")
        for item in result["syntax_patterns"] if isinstance(result["syntax_patterns"], list) else [result["syntax_patterns"]]:
            print(f"    - {item}")
    if "opening_hooks" in result:
        hooks = result["opening_hooks"]
        if isinstance(hooks, list):
            print(f"  冒頭フック: {', '.join(str(h) for h in hooks[:5])}")
    if "popular_topics" in result:
        topics = result["popular_topics"]
        if isinstance(topics, list):
            print(f"  人気トピック: {', '.join(str(t) for t in topics[:5])}")


if __name__ == "__main__":
    main()
