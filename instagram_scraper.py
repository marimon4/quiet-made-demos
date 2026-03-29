#!/usr/bin/env python3
"""
Instagram画像スクレイパー for Quiet Made
工房のInstagramから画像を自動取得・リネーム保存
"""

import streamlit as st
import instaloader
import os
import shutil
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

st.set_page_config(page_title="Instagram Scraper – Quiet Made", layout="centered")

st.title("📸 Instagram 画像スクレイパー")
st.caption("工房のInstagramから画像を自動取得してデモ用にリネーム保存します")

# ──────────────────────────────────────────────
# 入力フォーム
# ──────────────────────────────────────────────
with st.form("scrape_form"):
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input(
            "InstagramユーザーID",
            placeholder="例: showen_kumihimo",
            help="URLの @ 以降の部分"
        )
    with col2:
        workshop_name = st.text_input(
            "工房の短縮名",
            placeholder="例: showen",
            help="保存ファイル名のプレフィックスになります"
        )

    num_images = st.slider("取得枚数", min_value=3, max_value=12, value=8)

    st.markdown("---")
    st.markdown("**ログイン情報**（非公開アカウントや高解像度取得に必要）")
    ig_user = st.text_input("Instagramユーザー名", placeholder="your_instagram_id")
    ig_pass = st.text_input("Instagramパスワード", type="password")

    submitted = st.form_submit_button("🚀 画像を取得する", use_container_width=True)

# ──────────────────────────────────────────────
# スクレイピング実行
# ──────────────────────────────────────────────
if submitted:
    if not username or not workshop_name:
        st.error("ユーザーIDと工房名を入力してください")
        st.stop()

    username = username.strip().lstrip("@")
    workshop_name = workshop_name.strip().lower().replace(" ", "-")

    # 一時保存フォルダ
    tmp_dir = OUTPUT_DIR / f"_tmp_{workshop_name}"
    tmp_dir.mkdir(exist_ok=True)

    with st.spinner(f"@{username} から画像を取得中..."):
        try:
            L = instaloader.Instaloader(
                download_pictures=True,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                post_metadata_txt_pattern="",
                filename_pattern="{date_utc:%Y%m%d_%H%M%S}",
            )

            # ログイン（入力がある場合）
            if ig_user and ig_pass:
                try:
                    L.login(ig_user, ig_pass)
                    st.success("✅ ログイン成功")
                except Exception as e:
                    st.warning(f"ログイン失敗（未ログインで続行）: {e}")

            # プロフィール取得
            profile = instaloader.Profile.from_username(L.context, username)
            st.info(f"✅ アカウント確認: @{username}（{profile.followers}フォロワー）")

            # 投稿から画像を取得
            collected = []
            for post in profile.get_posts():
                if len(collected) >= num_images:
                    break
                if post.typename == "GraphImage":
                    collected.append(post.url)
                elif post.typename == "GraphSidecar":
                    # カルーセル投稿の最初の1枚
                    for node in post.get_sidecar_nodes():
                        if not node.is_video:
                            collected.append(node.display_url)
                            break

            if not collected:
                st.error("画像が見つかりませんでした。アカウントが非公開の可能性があります。")
                st.stop()

            # 画像をダウンロード＆リネーム
            import requests
            headers = {"User-Agent": "Mozilla/5.0"}

            saved_files = []
            for i, url in enumerate(collected):
                if i == 0:
                    filename = f"{workshop_name}-hero.jpg"
                elif i == 1:
                    filename = f"{workshop_name}-story.jpg"
                else:
                    filename = f"{workshop_name}-{i-1}.jpg"

                save_path = OUTPUT_DIR / filename
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(r.content)
                    saved_files.append(filename)

            # 一時フォルダ削除
            shutil.rmtree(tmp_dir, ignore_errors=True)

            # 結果表示
            st.success(f"✅ {len(saved_files)}枚の画像を保存しました！")

            st.markdown("**保存されたファイル：**")
            for fname in saved_files:
                role = ""
                if "hero" in fname:
                    role = "← ヒーロー背景に使用"
                elif "story" in fname:
                    role = "← ストーリーセクションに使用"
                else:
                    role = "← 作品グリッドに使用"
                st.code(f"{fname}  {role}")

            # プレビュー
            st.markdown("---")
            st.markdown("**プレビュー：**")
            import base64
            cols = st.columns(3)
            for i, fname in enumerate(saved_files[:6]):
                with cols[i % 3]:
                    img_path = OUTPUT_DIR / fname
                    if img_path.exists():
                        with open(img_path, "rb") as img_f:
                            b64 = base64.b64encode(img_f.read()).decode()
                        st.markdown(
                            f'<img src="data:image/jpeg;base64,{b64}" style="width:100%;border-radius:6px;margin-bottom:4px"><small>{fname}</small>',
                            unsafe_allow_html=True
                        )

        except instaloader.exceptions.ProfileNotExistsException:
            st.error(f"@{username} が見つかりません。ユーザーIDを確認してください。")
        except instaloader.exceptions.LoginRequiredException:
            st.error("このアカウントは非公開です。ログイン情報を入力してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

st.markdown("---")
st.caption("💡 ヒント: 取得順は最新投稿から順番です。hero→story→1〜6の順で保存されます。")
