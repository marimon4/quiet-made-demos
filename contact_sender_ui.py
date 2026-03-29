#!/opt/homebrew/bin/python3
"""
Quiet Made 送信UI - スマホ対応Streamlitアプリ
起動: python3 -m streamlit run ~/Desktop/quietmade/contact_sender_ui.py --server.port 8504
スマホアクセス: http://192.168.3.2:8504 (同一WiFi)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import streamlit as st
import pandas as pd
from contact_sender import (
    get_sheet_data,
    generate_sales_message,
    update_j_column,
    find_contact_page,
    has_no_sales_notice,
    fill_and_submit_form,
)

st.set_page_config(page_title="Quiet Made 送信", page_icon="📨", layout="centered")
st.title("📨 Quiet Made 送信ツール")
st.caption("📱 スマホからアクセス: http://192.168.3.2:8504 (同一WiFi)")

# ── セッション状態の初期化 ──
defaults = {
    "step": 1,
    "workshops": [],
    "messages": {},     # idx -> str
    "decisions": {},    # idx -> "send" | "skip"
    "review_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── STEP 1: シート読み込み ───────────────────────────────────
if st.session_state.step == 1:
    st.subheader("Step 1: 対象工房を読み込む")
    if st.button("📋 Googleシートから読み込む", type="primary", use_container_width=True):
        with st.spinner("読み込み中..."):
            try:
                _sheet, targets = get_sheet_data()
                st.session_state.workshops = targets
                st.session_state.step = 2
                st.session_state.review_idx = 0
                st.session_state.decisions = {}
                st.session_state.messages = {}
                st.rerun()
            except Exception as e:
                st.error(f"読み込みエラー: {e}")


# ─── STEP 2: プレビュー & 承認 ────────────────────────────────
elif st.session_state.step == 2:
    workshops = st.session_state.workshops
    total = len(workshops)

    if total == 0:
        st.info("対象工房がありません（J列が全てTRUE）")
        if st.button("← 戻る", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        st.stop()

    idx = st.session_state.review_idx

    # 全件レビュー完了 → Step 3 へ
    if idx >= total:
        st.session_state.step = 3
        st.rerun()

    ws = workshops[idx]

    # プログレス
    st.progress(idx / total, text=f"{idx + 1} / {total} 件目")

    # メッセージ生成（未生成なら）
    if idx not in st.session_state.messages:
        with st.spinner(f"「{ws['name']}」の営業文を生成中..."):
            msg = generate_sales_message(ws["name"], ws["product"])
            st.session_state.messages[idx] = msg

    msg = st.session_state.messages[idx]

    # 工房情報ヘッダー
    st.markdown(f"### {ws['name']}")
    st.caption(ws["url"])

    # 編集フラグ
    edit_key = f"edit_{idx}"
    if edit_key not in st.session_state:
        st.session_state[edit_key] = False

    if st.session_state[edit_key]:
        # ── 編集モード ──
        edited = st.text_area("本文を編集", value=msg, height=420, key=f"ta_{idx}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ この内容で送信", type="primary", use_container_width=True):
                st.session_state.messages[idx] = edited
                st.session_state.decisions[idx] = "send"
                st.session_state[edit_key] = False
                st.session_state.review_idx += 1
                st.rerun()
        with c2:
            if st.button("← キャンセル", use_container_width=True):
                st.session_state[edit_key] = False
                st.rerun()
    else:
        # ── プレビューモード ──
        st.text_area("メッセージ", value=msg, height=350, disabled=True, key=f"preview_{idx}")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ 送信", type="primary", use_container_width=True):
                st.session_state.decisions[idx] = "send"
                st.session_state.review_idx += 1
                st.rerun()
        with c2:
            if st.button("✏️ 編集", use_container_width=True):
                st.session_state[edit_key] = True
                st.rerun()
        with c3:
            if st.button("⏭️ スキップ", use_container_width=True):
                st.session_state.decisions[idx] = "skip"
                st.session_state.review_idx += 1
                st.rerun()

    # 判断済み件数の表示
    n_done = len(st.session_state.decisions)
    if n_done:
        n_send = sum(1 for v in st.session_state.decisions.values() if v == "send")
        st.caption(f"判断済み: {n_done}件（送信予定: {n_send}件）")


# ─── STEP 3: 送信実行 ─────────────────────────────────────────
elif st.session_state.step == 3:
    workshops = st.session_state.workshops
    decisions = st.session_state.decisions
    messages = st.session_state.messages

    to_send = [(workshops[i], messages[i]) for i, d in decisions.items() if d == "send"]
    to_skip = [workshops[i] for i, d in decisions.items() if d == "skip"]

    st.subheader("Step 3: 送信実行")
    c1, c2 = st.columns(2)
    c1.metric("送信予定", f"{len(to_send)}件")
    c2.metric("スキップ", f"{len(to_skip)}件")

    if not to_send:
        st.info("送信予定の工房がありません")
    else:
        if st.button("▶️ 送信開始", type="primary", use_container_width=True):
            from playwright.sync_api import sync_playwright

            progress_bar = st.progress(0)
            results_placeholder = st.empty()
            results = []
            total_send = len(to_send)

            # シートを再取得（セッション状態に保存できないため再認証）
            sheet, _ = get_sheet_data()

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                )
                page = ctx.new_page()

                for i, (ws, msg) in enumerate(to_send, 1):
                    progress_bar.progress(i / total_send, text=f"[{i}/{total_send}] {ws['name']}")

                    try:
                        page.goto(ws["url"], timeout=20000, wait_until="domcontentloaded")
                        time.sleep(2)

                        body_text = page.inner_text("body") if page.locator("body").count() > 0 else ""
                        found, kw = has_no_sales_notice(body_text)

                        if found:
                            status = "スキップ（営業禁止）"
                            update_j_column(sheet, ws["row"], "スキップ")
                        else:
                            contact_url = find_contact_page(page, ws["url"])
                            if not contact_url:
                                status = "フォームなし"
                                update_j_column(sheet, ws["row"], "フォームなし")
                            else:
                                page.goto(contact_url, timeout=20000, wait_until="domcontentloaded")
                                time.sleep(2)

                                body_text2 = page.inner_text("body") if page.locator("body").count() > 0 else ""
                                found2, _ = has_no_sales_notice(body_text2)

                                if found2:
                                    status = "スキップ（営業禁止）"
                                    update_j_column(sheet, ws["row"], "スキップ")
                                elif page.locator(".g-recaptcha, iframe[src*='recaptcha'], [class*='captcha']").count() > 0:
                                    status = "⚠️ CAPTCHA（手動対応）"
                                    update_j_column(sheet, ws["row"], "手動対応")
                                else:
                                    ok, reason = fill_and_submit_form(page, ws["name"], ws["product"], msg)
                                    if ok:
                                        status = "✅ 送信成功"
                                        update_j_column(sheet, ws["row"], "TRUE")
                                    else:
                                        status = f"❌ {reason}"
                                        update_j_column(sheet, ws["row"], f"エラー: {reason}")

                    except Exception as e:
                        status = f"エラー: {str(e)[:50]}"
                        update_j_column(sheet, ws["row"], f"エラー: {str(e)[:30]}")

                    results.append({"工房名": ws["name"], "結果": status})
                    results_placeholder.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

                    if i < total_send:
                        time.sleep(3)

                browser.close()

            progress_bar.progress(1.0, text="✅ 完了")
            st.success("送信処理が完了しました")
            st.balloons()

    st.divider()
    if st.button("← 最初に戻る", use_container_width=True):
        for k in list(defaults.keys()):
            del st.session_state[k]
        st.rerun()
