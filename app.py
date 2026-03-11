"""FAX営業用ドキュメント自動生成ツール"""
import os
import sys
import tempfile
from datetime import date, timedelta
import streamlit as st

st.set_page_config(
    page_title="FAX営業ツール",
    page_icon="📠",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(__file__))
from utils.pdf_generator import image_to_pdf, excel_to_pdf, merge_pdfs
from utils.template_manager import (
    list_letter_templates, get_regions, get_industries, get_nationalities, BASE_DIR,
)

OUTPUT_DIR = BASE_DIR / "output" / "fax_documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Google Drive親フォルダID
GDRIVE_PARENT_FOLDER_ID = "1hHuzNJzmQm2PtWVFezBmxgp90MzJ3ecq"

# Google Drive連携チェック
try:
    from utils.gdrive_uploader import is_configured, upload_to_drive, create_week_folders
    gdrive_available = is_configured()
except ImportError:
    gdrive_available = False

st.title("📠 FAX文書生成")
st.caption("履歴書（Excel/PDF）+ 手紙（JPEG/PDF）→ FAX送信用PDFを生成")

# --- 1. 履歴書選択 ---
st.header("1. 履歴書を選択")
uploaded_resume = st.file_uploader(
    "履歴書（PDF または Excel）",
    type=["pdf", "xlsx", "xls"]
)

resume_path = None
if uploaded_resume:
    suffix = os.path.splitext(uploaded_resume.name)[1]
    tmp_resume = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_resume.write(uploaded_resume.read())
    tmp_resume.close()

    if suffix.lower() in (".xlsx", ".xls"):
        with st.spinner("Excel → PDF変換中..."):
            resume_pdf = excel_to_pdf(tmp_resume.name)
            resume_path = resume_pdf
            st.success("Excelを変換しました")
    else:
        resume_path = tmp_resume.name

# --- 2. 手紙選択 ---
st.header("2. 手紙を選択")
letter_templates = list_letter_templates()

letter_source = st.radio(
    "手紙の選択方法",
    ["ファイルをアップロード", "テンプレートから選択"],
    horizontal=True
)

letter_path = None
if letter_source == "テンプレートから選択":
    if letter_templates:
        selected = st.selectbox(
            "手紙テンプレート",
            letter_templates,
            format_func=lambda t: f"{t.name} ({t.region} / {t.industry})" if t.region else t.name
        )
        if selected:
            letter_path = selected.path
            ext = os.path.splitext(selected.filename)[1].lower()
            if ext in (".jpg", ".jpeg", ".png"):
                st.image(selected.path, width=300)
    else:
        st.warning("テンプレート未登録。「テンプレート管理」から追加するか、直接アップロードしてください。")
else:
    uploaded_letter = st.file_uploader(
        "手紙ファイル（JPEG / PNG / PDF）",
        type=["jpg", "jpeg", "png", "pdf"]
    )
    if uploaded_letter:
        tmp_letter = tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_letter.name)[1]
        )
        tmp_letter.write(uploaded_letter.read())
        tmp_letter.close()
        letter_path = tmp_letter.name
        if uploaded_letter.type.startswith("image"):
            st.image(letter_path, width=300)

# --- 3. 出力設定 ---
st.header("3. 出力設定")
col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox("地域", [""] + get_regions())
with col2:
    industry = st.selectbox("業種", [""] + get_industries())
with col3:
    nationality_out = st.selectbox("国籍", [""] + get_nationalities())

age_input = st.number_input("年齢", min_value=0, max_value=99, value=0)

parts = [p for p in [region, industry, nationality_out, f"{age_input}歳" if age_input else ""] if p]
filename = "FAX_" + "_".join(parts) + ".pdf" if parts else "FAX_output.pdf"
st.markdown(f"**出力ファイル名**: `{filename}`")

# --- 4. Google Drive 保存設定 ---
st.header("4. Google Drive 保存")
if gdrive_available:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        start_date = st.date_input("開始日", value=monday, key="gd_start")
    with col_d2:
        default_end = monday + timedelta(days=6)
        end_date = st.date_input("終了日", value=default_end, key="gd_end")

    pc_number = st.selectbox("PC番号", list(range(1, 24)), key="gd_pc")

    folder_preview = f"{start_date.month}/{start_date.day}~{end_date.month}/{end_date.day} / {pc_number}"
    st.markdown(f"**保存先**: `{folder_preview} / {filename}`")

    upload_to_gdrive = st.checkbox("Google Driveにも保存する", value=True)
else:
    upload_to_gdrive = False
    st.warning("Google Drive未設定。`credentials/client_secret.json` を配置してください。")

# --- 生成ボタン ---
st.divider()
if st.button("🖨️ FAX PDF を生成", type="primary", use_container_width=True):
    if not resume_path:
        st.error("履歴書をアップロードしてください。")
    elif not letter_path:
        st.error("手紙を選択してください。")
    else:
        output_path = str(OUTPUT_DIR / filename)
        with st.spinner("FAX文書を生成中..."):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    letter_ext = os.path.splitext(letter_path)[1].lower()
                    if letter_ext in (".jpg", ".jpeg", ".png", ".bmp"):
                        letter_pdf = image_to_pdf(letter_path, os.path.join(tmpdir, "letter.pdf"))
                    else:
                        letter_pdf = letter_path

                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    # 履歴書 → 手紙 の順で結合
                    merge_pdfs([resume_path, letter_pdf], output_path)

                st.success("FAX文書を生成しました！")

                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 PDFをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )

                # Google Driveアップロード
                if upload_to_gdrive and gdrive_available:
                    with st.spinner("Google Driveにアップロード中..."):
                        result = upload_to_drive(
                            output_path,
                            GDRIVE_PARENT_FOLDER_ID,
                            start_date,
                            end_date,
                            pc_number,
                        )
                        st.success("Google Driveに保存しました！")

            except Exception as e:
                st.error(f"生成に失敗しました: {e}")
