"""
X投稿文生成スクリプト
analysis_result.json の傾向分析をもとに、Claude API で投稿候補を生成する。
"""

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PIPELINE_DIR = Path(__file__).parent
ANALYSIS_FILE = PIPELINE_DIR / "analysis_result.json"
OUTPUT_DIR = PIPELINE_DIR / "output"

load_dotenv(PIPELINE_DIR / ".env")

SYSTEM_PROMPT = """あなたはXで個人開発・AI活用・マネタイズを発信する日本人女性のSNSマネージャーです。

発信者のプロフィール：
- 女性ソロ起業家、匿名
- Claude Codeを使って複数アプリを並行開発している
- Etsy/Shopifyで海外販売も運営
- 海外Indie Hackerの情報を日本語に翻訳して届けることが差別化
- 「AIすごい！」ではなく「私はこれで稼いだ」というスタンス

投稿の4軸：
1. Claude Tips（実践的な使い方）
2. 海外翻訳（Indie Hacker/Product Huntなどの知見を日本語で）
3. マネタイズ（収益・売却・数字のリアル）
4. 個人開発リアル（日々の進捗・失敗・気づき）

条件：
- 各投稿は140文字を超えてもOK（スレッド形式も可）
- 4軸からバランスよく選ぶ
- 「AIすごい」「革命」「衝撃」などの驚き系ワードは使わない
- 数字・具体的事実を必ず1つ以上入れる
- 最後の一行は問いかけか、静かな主張で締める"""


def load_analysis() -> dict:
    """分析結果を読み込む。"""
    if not ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            f"{ANALYSIS_FILE.name} が見つかりません。先に analyze.py を実行してください。"
        )
    return json.loads(ANALYSIS_FILE.read_text(encoding="utf-8"))


def generate_with_claude(analysis: dict) -> str:
    """Claude API で投稿文を生成する。"""
    client = anthropic.Anthropic()

    analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""バズ投稿の傾向分析結果：
{analysis_text}

上記の傾向を参考にしながら、この発信者のスタイルで投稿を5本生成してください。

以下のフォーマットで出力してください：

---
【軸】Claude Tips / 海外翻訳 / マネタイズ / 個人開発リアル
【タイプ】箇条書き / ストーリー / 数字 / 翻訳引用
【投稿文】
（本文）
---

また、最後にJSON形式でも出力してください：
```json
[
  {{
    "text": "投稿本文",
    "axis": "軸名",
    "type": "タイプ名",
    "scheduled_for": null
  }}
]
```"""
        }]
    )

    return response.content[0].text


def save_outputs(content: str) -> tuple[Path, Path | None]:
    """テキストファイルとJSONファイルに保存する。"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")

    # テキスト版
    txt_path = OUTPUT_DIR / f"posts_{today}.txt"
    txt_path.write_text(content, encoding="utf-8")

    # JSON版を抽出
    json_path = None
    if "```json" in content:
        json_start = content.index("```json") + len("```json")
        json_end = content.index("```", json_start)
        json_text = content[json_start:json_end].strip()
        try:
            posts_data = json.loads(json_text)
            json_path = OUTPUT_DIR / f"posts_{today}.json"
            json_path.write_text(
                json.dumps(posts_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except json.JSONDecodeError:
            print("  [WARN] JSON抽出に失敗。テキスト版のみ保存します。")

    return txt_path, json_path


def main():
    print("=== 投稿文生成 ===")

    analysis = load_analysis()
    print("  傾向分析を読み込みました")

    print("  Claude APIで生成中...")
    content = generate_with_claude(analysis)

    txt_path, json_path = save_outputs(content)
    print(f"  テキスト: {txt_path}")
    if json_path:
        print(f"  JSON: {json_path}")

    # プレビュー
    print("\n" + "=" * 50)
    print(content[:500])
    if len(content) > 500:
        print(f"\n  ... ({len(content)}文字) 全文は {txt_path} を確認")


if __name__ == "__main__":
    main()
