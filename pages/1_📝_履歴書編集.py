"""履歴書編集ページ"""
import os
import sys
import tempfile
from datetime import datetime
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.excel_handler import (
    read_resume, write_resume, calculate_age, format_display_name,
    ResumeData, EducationEntry, WorkEntry,
)
from utils.template_manager import list_resume_templates, get_nationalities, BASE_DIR

st.title("📝 履歴書編集")
st.markdown("履歴書Excelの内容を編集して保存します。")

# --- ファイル選択 ---
st.header("1. 履歴書を選択")
resume_templates = list_resume_templates()

source = st.radio(
    "選択方法", ["テンプレートから選択", "ファイルをアップロード"], horizontal=True
)

resume_path = None
if source == "テンプレートから選択":
    if resume_templates:
        selected = st.selectbox(
            "テンプレート", resume_templates,
            format_func=lambda t: f"{t.name} ({t.region}/{t.industry})" if t.region else t.name
        )
        if selected:
            resume_path = selected.path
    else:
        st.warning("テンプレートが未登録です。")
else:
    uploaded = st.file_uploader("履歴書Excel", type=["xlsx"])
    if uploaded:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(uploaded.read())
        tmp.close()
        resume_path = tmp.name

if not resume_path:
    st.stop()

# --- 読み込み ---
try:
    data = read_resume(resume_path)
except Exception as e:
    st.error(f"読み込みエラー: {e}")
    st.stop()

# --- 基本情報編集 ---
st.header("2. 基本情報")
col1, col2 = st.columns(2)
with col1:
    data.name = st.text_input("氏名", value=data.name)
    data.furigana = st.text_input("フリガナ", value=data.furigana)
    nationalities = get_nationalities()
    nat_idx = nationalities.index(data.nationality) if data.nationality in nationalities else -1
    if nat_idx >= 0:
        data.nationality = st.selectbox("国籍", nationalities, index=nat_idx)
    else:
        data.nationality = st.text_input("国籍", value=data.nationality)

with col2:
    data.gender = st.text_input("性別", value=data.gender)
    data.address = st.text_input("住所", value=data.address)
    data.reg_number = st.text_input("登録番号", value=data.reg_number)
    if data.birthday:
        data.birthday = st.date_input("生年月日", value=data.birthday)
        data.birthday = datetime.combine(data.birthday, datetime.min.time())

# 名前統一プレビュー
age = calculate_age(data.birthday) if data.birthday else 0
if data.name and data.nationality and age:
    display_name = format_display_name(data.name, data.nationality, age)
    st.info(f"📋 表示用名前: **{display_name}**")

# --- 学歴編集 ---
st.header("3. 学歴")
edu_count = len(data.education)
if edu_count == 0:
    data.education = [EducationEntry()]
    edu_count = 1

for i in range(edu_count):
    col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
    with col1:
        data.education[i].year = st.number_input(
            "年", value=data.education[i].year or 2020,
            min_value=1990, max_value=2030, key=f"edu_year_{i}"
        )
    with col2:
        data.education[i].month = st.number_input(
            "月", value=data.education[i].month or 4,
            min_value=1, max_value=12, key=f"edu_month_{i}"
        )
    with col3:
        data.education[i].school = st.text_input(
            "学校名", value=data.education[i].school, key=f"edu_school_{i}"
        )
    with col4:
        data.education[i].status = st.selectbox(
            "区分", ["入学", "卒業", "中退", ""],
            index=["入学", "卒業", "中退", ""].index(data.education[i].status)
            if data.education[i].status in ["入学", "卒業", "中退", ""] else 3,
            key=f"edu_status_{i}"
        )

col_add, col_del = st.columns(2)
with col_add:
    if st.button("＋ 学歴を追加", key="add_edu"):
        data.education.append(EducationEntry())
        st.rerun()
with col_del:
    if edu_count > 1 and st.button("－ 最後の学歴を削除", key="del_edu"):
        data.education.pop()
        st.rerun()

# --- 職歴編集 ---
st.header("4. 職歴")
work_count = len(data.work)
if work_count == 0:
    data.work = [WorkEntry()]
    work_count = 1

for i in range(work_count):
    st.markdown(f"**職歴 {i + 1}**")
    col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
    with col1:
        data.work[i].year = st.number_input(
            "年", value=data.work[i].year or 2023,
            min_value=1990, max_value=2030, key=f"work_year_{i}"
        )
    with col2:
        data.work[i].month = st.number_input(
            "月", value=data.work[i].month or 4,
            min_value=1, max_value=12, key=f"work_month_{i}"
        )
    with col3:
        data.work[i].company = st.text_input(
            "会社名", value=data.work[i].company, key=f"work_company_{i}"
        )
    with col4:
        data.work[i].status = st.selectbox(
            "区分", ["入社", "退社", ""],
            index=["入社", "退社", ""].index(data.work[i].status)
            if data.work[i].status in ["入社", "退社", ""] else 2,
            key=f"work_status_{i}"
        )
    data.work[i].detail = st.text_input(
        "業務内容", value=data.work[i].detail, key=f"work_detail_{i}"
    )

col_add, col_del = st.columns(2)
with col_add:
    if st.button("＋ 職歴を追加", key="add_work"):
        data.work.append(WorkEntry())
        st.rerun()
with col_del:
    if work_count > 1 and st.button("－ 最後の職歴を削除", key="del_work"):
        data.work.pop()
        st.rerun()

# --- 保存 ---
st.divider()
st.header("5. 保存")

save_option = st.radio(
    "保存先", ["上書き保存", "新しいファイルとして保存"], horizontal=True
)

if st.button("💾 保存", type="primary", use_container_width=True):
    try:
        if save_option == "上書き保存":
            result = write_resume(resume_path, data)
            st.success(f"保存しました: {result}")
        else:
            output_dir = str(BASE_DIR / "output")
            os.makedirs(output_dir, exist_ok=True)
            new_name = f"履歴書_{data.name}_{data.nationality}_{age}歳.xlsx"
            output_path = os.path.join(output_dir, new_name)
            result = write_resume(resume_path, data, output_path)
            st.success(f"新規保存しました: {result}")

            with open(result, "rb") as f:
                st.download_button(
                    "📥 Excelをダウンロード", f.read(),
                    file_name=new_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")
