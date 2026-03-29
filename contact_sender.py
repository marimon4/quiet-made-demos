#!/opt/homebrew/bin/python3
"""
Quiet Made お問い合わせフォーム自動送信スクリプト
- Google Sheets から J列が FALSE の工房を取得
- 各工房サイトのお問い合わせフォームを探して送信
- 結果を J列に書き戻す
"""

import os
import time
import re
import gspread
import anthropic
from google.oauth2.service_account import Credentials
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ── 設定 ──────────────────────────────────────────────
SPREADSHEET_ID = "12r7zEZvjwZ2KTxVaF6X-elEwODi7y51fwEEzsAgR09g"
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# 送信者情報（フォームに入力する自社情報）
SENDER_NAME = "Marika Kotani"
SENDER_COMPANY = "Quiet Made"
SENDER_EMAIL = "hello@quiet-made.jp"

# 営業お断りキーワード
NO_SALES_KEYWORDS = [
    "営業メール不可", "営業お断り", "営業メールお断り", "広告・営業お断り",
    "セールスお断り", "営業目的のお問い合わせはお断り", "業者からのお問い合わせはご遠慮",
    "営業活動はご遠慮", "勧誘はお断り",
]

# お問い合わせページを示すキーワード
CONTACT_KEYWORDS = [
    "お問い合わせ", "contact", "問い合わせ", "コンタクト",
    "ご連絡", "お問合せ", "問合せ",
]

# ─────────────────────────────────────────────────────


def get_sheet_data():
    """スプレッドシートから J列がFALSEの工房リストを取得"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    all_rows = sheet.get_all_values()
    header = all_rows[0]  # 1行目はヘッダー

    targets = []
    for i, row in enumerate(all_rows[1:], start=2):  # 2行目から（1-indexed for Sheets API）
        # 列が足りない行はスキップ
        while len(row) < 10:
            row.append("")

        name = row[0].strip()   # A列: 事業者名
        url = row[1].strip()    # B列: URL
        product = row[2].strip()  # C列: 商材
        j_val = row[9].strip()  # J列: 送信済み

        # URLなし・名前なしはスキップ
        if not name or not url:
            continue

        # J列が空 or FALSE（未チェック）のみ対象
        if j_val.upper() in ("", "FALSE"):
            targets.append({
                "row": i,
                "name": name,
                "url": url,
                "product": product,
            })

    return sheet, targets


def update_j_column(sheet, row_index, value):
    """J列（10列目）を更新"""
    sheet.update_cell(row_index, 10, value)
    print(f"  → 行{row_index} J列を「{value}」に更新")


def has_no_sales_notice(text):
    """営業お断り表記があるか確認"""
    for kw in NO_SALES_KEYWORDS:
        if kw in text:
            return True, kw
    return False, None


def find_contact_page(page, base_url):
    """お問い合わせページのURLを探す（ナビ・フッターから）"""
    try:
        links = page.eval_on_selector_all(
            "a",
            """els => els.map(el => ({
                href: el.href,
                text: el.textContent.trim()
            }))"""
        )
    except Exception:
        return None

    for link in links:
        text = link.get("text", "").lower()
        href = link.get("href", "")
        if not href or href.startswith("javascript") or href.startswith("mailto"):
            continue
        for kw in CONTACT_KEYWORDS:
            if kw.lower() in text or kw.lower() in href.lower():
                # 相対URLを絶対URLに変換
                if href.startswith("http"):
                    return href
                elif href.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(base_url)
                    return f"{parsed.scheme}://{parsed.netloc}{href}"
    return None


MESSAGE_TEMPLATE = """はじめまして。Quiet Made の小谷と申します。

突然のご連絡をお許しください。貴工房の{craft_phrase}を拝見し、今の見せ方より何倍もの価値で届けられると感じて、ご連絡しました。

私は日本の工芸・ものづくりを欧米市場に向けて発信する仕事をしており、海外の購買層が何に惹かれ、何に対してお金を払うかを実務として見ています。その目線から言うと、貴工房のような仕事は、伝え方を整えるだけで、まったく違う層に、まったく違う価格で届く可能性があります。

問題はほぼいつも同じです。作品の良さに対して、それが伝わる構造になっていない。言語の問題だけでなく、「なぜこれが特別なのか」の文脈が、日本の外では自明ではないということです。

Quiet Made では、その文脈ごと設計し直すお手伝いをしています。ホームページの構成・英語対応・海外向けの見せ方を一体で行っており、他工房向けに作成したデモをご参考までにご覧いただけます。
https://quiet-made.jp/demos.html

今すぐ海外展開をお考えでなくても構いません。現状のホームページで何が課題になっているか、率直にお伝えできます。

ご興味があれば、お気軽にご返信ください。

株式会社 Revarise / Quiet Made
小谷麻梨香
https://quiet-made.jp/lp.html"""


def generate_craft_phrase(workshop_name, product):
    """工房の商材を一言で表すフレーズを生成（例: 「備前焼の花入れ」「漆の椀」）"""
    if not ANTHROPIC_API_KEY:
        return product or "作品"

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = f"""以下の工房情報から、「貴工房の〇〇を拝見し」に入る自然な一言フレーズを生成してください。

【工房名】{workshop_name}
【商材カテゴリ】{product}

条件：
- 10〜25文字程度の具体的な表現
- 例: 「備前焼の花入れと酒器」「漆を用いた日常の器」「鍛造による包丁と刃物」
- 工房名は含めない
- フレーズのみ出力（前後の説明不要）"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_sales_message(workshop_name, product):
    """商材フレーズを生成してテンプレートに埋め込む"""
    craft_phrase = generate_craft_phrase(workshop_name, product)
    return MESSAGE_TEMPLATE.format(craft_phrase=craft_phrase)


def preview_and_confirm(workshop_name, message):
    """メッセージをプレビューし、送信可否を確認する。
    戻り値: 'send' | 'skip' | 'edit' | 'quit'
    """
    print(f"\n{'─'*50}")
    print(f"【プレビュー: {workshop_name}】")
    print('─'*50)
    print(message)
    print('─'*50)

    while True:
        choice = input("[y]送信 / [n]スキップ / [e]本文を編集 / [q]終了 > ").strip().lower()
        if choice == "y":
            return "send", message
        elif choice == "n":
            return "skip", message
        elif choice == "q":
            return "quit", message
        elif choice == "e":
            print("新しい本文を入力してください（入力完了後、空行を2回押して確定）:")
            lines = []
            blank_count = 0
            while blank_count < 2:
                line = input()
                if line == "":
                    blank_count += 1
                else:
                    blank_count = 0
                lines.append(line)
            edited = "\n".join(lines).rstrip()
            return "send", edited
        else:
            print("  y / n / e / q で入力してください")


def fill_and_submit_form(page, workshop_name, product, sales_message):
    """フォームのフィールドを検出して入力・送信"""

    # ── 名前フィールド ──
    name_selectors = [
        'input[name*="name" i]', 'input[placeholder*="名前" i]',
        'input[placeholder*="氏名" i]', 'input[placeholder*="お名前" i]',
        'input[placeholder*="name" i]', 'input[id*="name" i]',
        'input[class*="name" i]',
    ]
    for sel in name_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.fill(SENDER_NAME)
                break
        except Exception:
            continue

    # ── 会社名フィールド ──
    company_selectors = [
        'input[name*="company" i]', 'input[name*="organization" i]',
        'input[placeholder*="会社" i]', 'input[placeholder*="組織" i]',
        'input[placeholder*="company" i]',
    ]
    for sel in company_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.fill(SENDER_COMPANY)
                break
        except Exception:
            continue

    # ── メールフィールド ──
    email_selectors = [
        'input[type="email"]', 'input[name*="email" i]',
        'input[placeholder*="メール" i]', 'input[placeholder*="mail" i]',
        'input[id*="email" i]',
    ]
    for sel in email_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.fill(SENDER_EMAIL)
                break
        except Exception:
            continue

    # ── 件名フィールド（あれば） ──
    subject_selectors = [
        'input[name*="subject" i]', 'input[placeholder*="件名" i]',
        'input[placeholder*="subject" i]', 'input[id*="subject" i]',
    ]
    for sel in subject_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.fill(f"海外展開支援のご提案 - Quiet Made")
                break
        except Exception:
            continue

    # ── メッセージ本文 ──
    message_selectors = [
        'textarea[name*="message" i]', 'textarea[name*="body" i]',
        'textarea[name*="content" i]', 'textarea[placeholder*="メッセージ" i]',
        'textarea[placeholder*="お問い合わせ" i]', 'textarea[placeholder*="内容" i]',
        'textarea[id*="message" i]', 'textarea',
    ]
    filled_message = False
    for sel in message_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible():
                el.fill(sales_message)
                filled_message = True
                break
        except Exception:
            continue

    if not filled_message:
        return False, "メッセージフィールドが見つからない"

    # ── 送信ボタン ──
    submit_selectors = [
        'button[type="submit"]', 'input[type="submit"]',
        'button:has-text("送信")', 'button:has-text("送る")',
        'button:has-text("Submit")', 'button:has-text("send")',
        '*[class*="submit"]',
    ]
    for sel in submit_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible():
                btn.click()
                time.sleep(3)
                return True, "送信完了"
        except Exception:
            continue

    return False, "送信ボタンが見つからない"


def process_workshop(page, workshop, preview=True):
    """1つの工房を処理"""
    name = workshop["name"]
    url = workshop["url"]
    product = workshop["product"]

    print(f"\n{'='*50}")
    print(f"処理中: {name}")
    print(f"URL: {url}")

    # ── サイトにアクセス ──
    try:
        page.goto(url, timeout=20000, wait_until="domcontentloaded")
        time.sleep(2)
    except Exception as e:
        return f"エラー: サイト接続失敗 ({str(e)[:50]})"

    # ── トップページで営業禁止チェック ──
    page_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
    found, keyword = has_no_sales_notice(page_text)
    if found:
        print(f"  ⚠️ 営業禁止キーワード検出: {keyword}")
        return "スキップ"

    # ── お問い合わせページを探す ──
    contact_url = find_contact_page(page, url)
    if not contact_url:
        print("  ⚠️ お問い合わせページが見つからない")
        return "フォームなし"

    print(f"  お問い合わせページ: {contact_url}")

    # ── お問い合わせページに移動 ──
    try:
        page.goto(contact_url, timeout=20000, wait_until="domcontentloaded")
        time.sleep(2)
    except Exception as e:
        return f"エラー: お問い合わせページ接続失敗 ({str(e)[:50]})"

    # ── お問い合わせページでも営業禁止チェック ──
    page_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
    found, keyword = has_no_sales_notice(page_text)
    if found:
        print(f"  ⚠️ 営業禁止キーワード検出（お問い合わせページ）: {keyword}")
        return "スキップ"

    # ── CAPTCHAチェック ──
    if page.locator(".g-recaptcha, iframe[src*='recaptcha'], [class*='captcha']").count() > 0:
        print("  ⚠️ CAPTCHA 検出")
        return "手動対応"

    # ── 営業文生成 ──
    print(f"  営業文を生成中...")
    sales_message = generate_sales_message(name, product)
    print(f"  生成完了（{len(sales_message)}文字）")

    # ── プレビュー確認 ──
    if preview:
        action, sales_message = preview_and_confirm(name, sales_message)
        if action == "skip":
            return "スキップ（手動）"
        elif action == "quit":
            raise KeyboardInterrupt("ユーザーが終了を選択")

    # ── フォーム入力・送信 ──
    success, reason = fill_and_submit_form(page, name, product, sales_message)

    if success:
        print(f"  ✅ 送信成功")
        return "TRUE"
    else:
        print(f"  ❌ 送信失敗: {reason}")
        return f"エラー: {reason}"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Quiet Made 営業フォーム自動送信")
    parser.add_argument("--no-preview", action="store_true", help="プレビュー確認をスキップして自動送信")
    args = parser.parse_args()
    preview = not args.no_preview

    print("Quiet Made 営業フォーム自動送信スクリプト")
    print("=" * 50)
    if preview:
        print("📋 プレビューモード: 各工房の送信前に確認します")
    else:
        print("⚡ 自動送信モード: 確認なしで送信します")

    if not ANTHROPIC_API_KEY:
        print("⚠️ ANTHROPIC_API_KEY が未設定のためフォールバックテンプレートを使用します")

    # シートデータ取得
    print("スプレッドシートを読み込み中...")
    sheet, targets = get_sheet_data()
    print(f"対象工房数: {len(targets)}件")

    if not targets:
        print("対象工房がありません（J列が全てTRUEまたは設定済み）")
        return

    # 対象一覧を表示
    for t in targets:
        print(f"  - 行{t['row']}: {t['name']} ({t['url']})")

    print("\n処理を開始します...")
    time.sleep(2)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = context.new_page()

        try:
            for workshop in targets:
                result = process_workshop(page, workshop, preview=preview)
                update_j_column(sheet, workshop["row"], result)
                time.sleep(3)  # サイト間のインターバル
        except KeyboardInterrupt:
            print("\n⏹ 処理を中断しました")
        finally:
            browser.close()

    print("\n✅ 全処理完了")


if __name__ == "__main__":
    main()
