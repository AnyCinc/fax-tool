"""テンプレート管理ページ"""
import os
import sys
import tempfile
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.template_manager import (
    list_letter_templates, list_resume_templates,
    add_letter_template, add_resume_template,
    remove_letter_template, remove_resume_template,
    get_regions, get_industries,
)

st.title("📁 テンプレート管理")

tab1, tab2 = st.tabs(["📨 手紙テンプレート", "📄 履歴書テンプレート"])

# ====== 手紙テンプレート ======
with tab1:
    st.header("手紙テンプレート一覧")
    letters = list_letter_templates()

    if letters:
        for t in letters:
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                tags = ""
                if t.region:
                    tags += f" 🏷️{t.region}"
                if t.industry:
                    tags += f" 🏷️{t.industry}"
                st.markdown(f"**{t.name}**{tags}")
                st.caption(t.filename)
            with col2:
                # プレビュー
                ext = os.path.splitext(t.filename)[1].lower()
                if ext in (".jpg", ".jpeg", ".png"):
                    st.image(t.path, width=150)
            with col3:
                if st.button("🗑️ 削除", key=f"del_letter_{t.filename}"):
                    remove_letter_template(t.filename)
                    st.rerun()
        st.divider()
    else:
        st.info("手紙テンプレートが登録されていません。")

    st.subheader("新規追加")
    with st.form("add_letter_form"):
        letter_name = st.text_input("テンプレート名", placeholder="例: 飲食業向け手紙")
        col1, col2 = st.columns(2)
        with col1:
            letter_region = st.selectbox("地域", [""] + get_regions(), key="letter_region")
        with col2:
            letter_industry = st.selectbox("業種", [""] + get_industries(), key="letter_industry")

        letter_file = st.file_uploader(
            "ファイル（PDF / JPEG / PNG）",
            type=["pdf", "jpg", "jpeg", "png"],
            key="letter_upload"
        )

        if st.form_submit_button("追加", type="primary"):
            if not letter_name:
                st.error("テンプレート名を入力してください。")
            elif not letter_file:
                st.error("ファイルをアップロードしてください。")
            else:
                tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=os.path.splitext(letter_file.name)[1]
                )
                tmp.write(letter_file.read())
                tmp.close()
                add_letter_template(
                    tmp.name, letter_name,
                    region=letter_region, industry=letter_industry
                )
                st.success(f"「{letter_name}」を追加しました。")
                st.rerun()

# ====== 履歴書テンプレート ======
with tab2:
    st.header("履歴書テンプレート一覧")
    resumes = list_resume_templates()

    if resumes:
        for t in resumes:
            col1, col2 = st.columns([5, 1])
            with col1:
                tags = ""
                if t.region:
                    tags += f" 🏷️{t.region}"
                if t.industry:
                    tags += f" 🏷️{t.industry}"
                st.markdown(f"**{t.name}**{tags}")
                st.caption(t.filename)
            with col2:
                if st.button("🗑️ 削除", key=f"del_resume_{t.filename}"):
                    remove_resume_template(t.filename)
                    st.rerun()
        st.divider()
    else:
        st.info("履歴書テンプレートが登録されていません。")

    st.subheader("新規追加")
    with st.form("add_resume_form"):
        resume_name = st.text_input("テンプレート名", placeholder="例: 関東_飲食業")
        col1, col2 = st.columns(2)
        with col1:
            resume_region = st.selectbox("地域", [""] + get_regions(), key="resume_region")
        with col2:
            resume_industry = st.selectbox("業種", [""] + get_industries(), key="resume_industry")

        resume_file = st.file_uploader(
            "ファイル（.xlsx）",
            type=["xlsx"],
            key="resume_upload"
        )

        if st.form_submit_button("追加", type="primary"):
            if not resume_name:
                st.error("テンプレート名を入力してください。")
            elif not resume_file:
                st.error("ファイルをアップロードしてください。")
            else:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                tmp.write(resume_file.read())
                tmp.close()
                add_resume_template(
                    tmp.name, resume_name,
                    region=resume_region, industry=resume_industry
                )
                st.success(f"「{resume_name}」を追加しました。")
                st.rerun()
