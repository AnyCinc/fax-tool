"""新規履歴書作成ページ - 入力情報から履歴書PDF+手紙を生成"""
import os
import sys
import tempfile
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.resume_builder import build_resume_pdf
from utils.pdf_generator import image_to_pdf, merge_pdfs
from utils.template_manager import (
    list_letter_templates, get_regions, get_industries, get_nationalities, BASE_DIR,
)

st.title("🆕 新規履歴書作成")
st.markdown("情報を入力して、履歴書PDF + 手紙を一括生成します。")

OUTPUT_DIR = BASE_DIR / "output" / "fax_documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== 基本情報 =====
st.header("1. 基本情報")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("氏名（ローマ字）", placeholder="例: HOANG THI HUONG")
    furigana = st.text_input("フリガナ", placeholder="例: ホアン ティ フォン")
    nationality = st.selectbox("国籍", get_nationalities())
    age = st.number_input("年齢", min_value=18, max_value=65, value=25)
with col2:
    reg_number = st.text_input("登録番号", placeholder="例: CR2820")
    gender = st.selectbox("性別", ["女", "男"])
    birthday = st.text_input("生年月日", placeholder="例: 2000年3月20日")
    address = st.text_input("住所", placeholder="例: 東京都")

# ===== 顔写真 =====
st.header("2. 顔写真")
photo_file = st.file_uploader("顔写真（JPEG/PNG）", type=["jpg", "jpeg", "png"])
photo_path = None
if photo_file:
    tmp_photo = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(photo_file.name)[1])
    tmp_photo.write(photo_file.read())
    tmp_photo.close()
    photo_path = tmp_photo.name
    st.image(photo_path, width=150)

# ===== 学歴 =====
st.header("3. 学歴")
if "edu_count" not in st.session_state:
    st.session_state.edu_count = 2

education = []
for i in range(st.session_state.edu_count):
    cols = st.columns([1, 1, 4, 1])
    with cols[0]:
        yr = st.number_input("年", min_value=1990, max_value=2030, value=2020, key=f"edu_yr_{i}")
    with cols[1]:
        mo = st.number_input("月", min_value=1, max_value=12, value=4, key=f"edu_mo_{i}")
    with cols[2]:
        school = st.text_input("学校名", key=f"edu_school_{i}")
    with cols[3]:
        status = st.selectbox("区分", ["入学", "卒業", "中退"], key=f"edu_st_{i}")
    if school:
        education.append({"year": yr, "month": mo, "school": school, "status": status})

c1, c2 = st.columns(2)
with c1:
    if st.button("＋ 学歴追加"):
        st.session_state.edu_count += 1
        st.rerun()
with c2:
    if st.session_state.edu_count > 1 and st.button("－ 学歴削除"):
        st.session_state.edu_count -= 1
        st.rerun()

# ===== 職歴 =====
st.header("4. 職歴")
if "work_count" not in st.session_state:
    st.session_state.work_count = 1

work = []
for i in range(st.session_state.work_count):
    st.markdown(f"**職歴 {i + 1}**")
    cols = st.columns([1, 1, 4, 1])
    with cols[0]:
        yr = st.number_input("年", min_value=1990, max_value=2030, value=2023, key=f"wk_yr_{i}")
    with cols[1]:
        mo = st.number_input("月", min_value=1, max_value=12, value=4, key=f"wk_mo_{i}")
    with cols[2]:
        company = st.text_input("会社名", key=f"wk_co_{i}")
    with cols[3]:
        status = st.selectbox("区分", ["入社", "退社"], key=f"wk_st_{i}")
    detail = st.text_input("業務内容", key=f"wk_detail_{i}", placeholder="例: 接客、調理、発注管理")
    if company:
        work.append({"year": yr, "month": mo, "company": company, "status": status, "detail": detail})

c1, c2 = st.columns(2)
with c1:
    if st.button("＋ 職歴追加"):
        st.session_state.work_count += 1
        st.rerun()
with c2:
    if st.session_state.work_count > 1 and st.button("－ 職歴削除"):
        st.session_state.work_count -= 1
        st.rerun()

# ===== 手紙選択 =====
st.header("5. 手紙を選択")
letter_templates = list_letter_templates()

letter_source = st.radio(
    "手紙の選択方法",
    ["ファイルをアップロード", "テンプレートから選択"],
    horizontal=True,
    key="new_letter_source"
)

letter_path = None
if letter_source == "テンプレートから選択":
    if letter_templates:
        selected = st.selectbox(
            "手紙テンプレート",
            letter_templates,
            format_func=lambda t: f"{t.name} ({t.region}/{t.industry})" if t.region else t.name,
            key="new_letter_tmpl"
        )
        if selected:
            letter_path = selected.path
    else:
        st.warning("テンプレート未登録。直接アップロードしてください。")
else:
    letter_file = st.file_uploader("手紙（JPEG/PNG/PDF）", type=["jpg", "jpeg", "png", "pdf"], key="new_letter_upload")
    if letter_file:
        tmp_letter = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(letter_file.name)[1])
        tmp_letter.write(letter_file.read())
        tmp_letter.close()
        letter_path = tmp_letter.name

# ===== 出力設定 =====
st.header("6. 出力設定")
col1, col2 = st.columns(2)
with col1:
    region = st.selectbox("地域", [""] + get_regions(), key="new_region")
with col2:
    industry = st.selectbox("業種", [""] + get_industries(), key="new_industry")

parts = [p for p in [region, industry, nationality, f"{age}歳" if age else ""] if p]
filename = "FAX_" + "_".join(parts) + ".pdf" if parts else "FAX_output.pdf"
st.markdown(f"**出力ファイル名**: `{filename}`")

# ===== 生成ボタン =====
st.divider()
col_resume, col_fax = st.columns(2)

with col_resume:
    if st.button("📄 履歴書PDFだけ生成", use_container_width=True):
        if not name:
            st.error("氏名を入力してください。")
        else:
            with st.spinner("履歴書を生成中..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        resume_pdf = build_resume_pdf(
                            output_path=tmp.name,
                            name=name, furigana=furigana, gender=gender,
                            birthday=birthday, age=age, address=address,
                            nationality=nationality, reg_number=reg_number,
                            education=education, work=work, photo_path=photo_path,
                        )
                    st.success("履歴書PDFを生成しました！")
                    with open(resume_pdf, "rb") as f:
                        st.download_button("📥 履歴書PDFダウンロード", f.read(),
                                           file_name=f"履歴書_{name}.pdf", mime="application/pdf",
                                           use_container_width=True)
                except Exception as e:
                    st.error(f"生成失敗: {e}")

with col_fax:
    if st.button("🖨️ FAX PDF生成（手紙+履歴書）", type="primary", use_container_width=True):
        if not name:
            st.error("氏名を入力してください。")
        elif not letter_path:
            st.error("手紙を選択してください。")
        else:
            output_path = str(OUTPUT_DIR / filename)
            with st.spinner("FAX文書を生成中..."):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # 履歴書PDF生成
                        resume_pdf = build_resume_pdf(
                            output_path=os.path.join(tmpdir, "resume.pdf"),
                            name=name, furigana=furigana, gender=gender,
                            birthday=birthday, age=age, address=address,
                            nationality=nationality, reg_number=reg_number,
                            education=education, work=work, photo_path=photo_path,
                        )
                        # 手紙をPDFに変換（画像の場合）
                        letter_ext = os.path.splitext(letter_path)[1].lower()
                        if letter_ext in (".jpg", ".jpeg", ".png"):
                            letter_pdf = image_to_pdf(letter_path, os.path.join(tmpdir, "letter.pdf"))
                        else:
                            letter_pdf = letter_path

                        # 結合
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        merge_pdfs([letter_pdf, resume_pdf], output_path)

                    st.success("FAX文書を生成しました！")
                    with open(output_path, "rb") as f:
                        st.download_button("📥 FAX PDFダウンロード", f.read(),
                                           file_name=filename, mime="application/pdf",
                                           use_container_width=True)
                except Exception as e:
                    st.error(f"生成失敗: {e}")
