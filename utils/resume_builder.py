"""履歴書PDF新規作成モジュール（fpdf2 + 日本語フォント）"""
import os
from fpdf import FPDF
from PIL import Image

FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
FONT_BOLD_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"


class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.add_font("jp", "", FONT_PATH)
        self.add_font("jp", "B", FONT_BOLD_PATH)
        self.margin_x = 15
        self.table_w = 180


def build_resume_pdf(
    output_path: str,
    name: str = "",
    furigana: str = "",
    gender: str = "男",
    birthday: str = "",
    age: int = 0,
    address: str = "",
    nationality: str = "",
    reg_number: str = "",
    education: list = None,
    work: list = None,
    photo_path: str = None,
) -> str:
    """履歴書PDFを新規作成"""
    pdf = ResumePDF()
    pdf.add_page()
    mx = pdf.margin_x

    # ===== タイトル =====
    pdf.set_font("jp", "B", 18)
    pdf.set_xy(mx, 10)
    pdf.cell(180, 12, "履　歴　書", align="C", new_x="LMARGIN", new_y="NEXT")

    y = 25
    rh = 8  # 行高さ

    # ===== 基本情報テーブル =====
    # 左側の幅
    label_w = 22
    name_w = 85
    # 右側
    right_label_w = 28
    right_val_w = 45

    # --- フリガナ行 ---
    pdf.set_font("jp", "", 7)
    pdf.set_xy(mx, y)
    pdf.cell(label_w, rh, " フリガナ", border=1)
    pdf.cell(name_w, rh, f" {furigana}", border=1)
    gender_text = f" {gender}" if gender else ""
    pdf.cell(right_label_w, rh, gender_text, border=1, align="C")
    pdf.cell(right_val_w, rh, "", border=1)
    y += rh

    # --- 氏名行（2行分） ---
    pdf.set_font("jp", "", 7)
    pdf.set_xy(mx, y)
    pdf.cell(label_w, rh * 2, " 氏名", border=1)
    pdf.set_font("jp", "B", 16)
    pdf.cell(name_w, rh * 2, f" {name}", border=1)

    # 右側: 国籍 + 登録番号
    pdf.set_font("jp", "", 8)
    pdf.set_xy(mx + label_w + name_w, y)
    pdf.cell(right_label_w, rh, " 国籍", border=1)
    pdf.cell(right_val_w, rh, f" {nationality}", border=1)
    pdf.set_xy(mx + label_w + name_w, y + rh)
    pdf.cell(right_label_w, rh, " 登録番号", border=1)
    pdf.cell(right_val_w, rh, f" {reg_number}", border=1)
    y += rh * 2

    # --- 生年月日行 ---
    pdf.set_font("jp", "", 8)
    pdf.set_xy(mx, y)
    pdf.cell(label_w, rh, " 生年月日", border=1)
    bday_text = f" {birthday}  生　（{age}歳）" if birthday else ""
    pdf.cell(name_w, rh, bday_text, border=1)
    pdf.cell(right_label_w + right_val_w, rh, "", border=1)
    y += rh

    # --- 住所行（2行分） ---
    pdf.set_xy(mx, y)
    pdf.cell(label_w, rh * 2, " 現住所", border=1)
    pdf.set_font("jp", "", 11)
    pdf.cell(name_w + right_label_w + right_val_w, rh * 2, f" {address}", border=1)
    y += rh * 2

    # ===== 顔写真 =====
    if photo_path and os.path.exists(photo_path):
        photo_x = mx + label_w + name_w + right_label_w + right_val_w + 3
        photo_y = 25
        photo_w = 28
        photo_h = 36
        # 写真枠内に収まるように配置（テーブルの右外）
        # テーブル幅を超える場合は右上に配置
        photo_x = mx + 180 - photo_w - 2
        photo_y = 26
        try:
            img = Image.open(photo_path)
            img_w, img_h = img.size
            ratio = min(photo_w / (img_w * 0.264583), photo_h / (img_h * 0.264583))
            actual_w = img_w * 0.264583 * ratio
            actual_h = img_h * 0.264583 * ratio
            offset_x = (photo_w - actual_w) / 2
            offset_y = (photo_h - actual_h) / 2
            pdf.image(photo_path, photo_x + offset_x, photo_y + offset_y, actual_w, actual_h)
        except Exception:
            pass

    # ===== 学歴・職歴テーブル =====
    y += 3
    col_year = 15
    col_month = 10
    col_content = 130
    col_status = 25
    entry_h = 7

    pdf.set_font("jp", "", 8)

    # ヘッダー
    pdf.set_xy(mx, y)
    pdf.cell(col_year, entry_h, "年", border=1, align="C")
    pdf.cell(col_month, entry_h, "月", border=1, align="C")
    pdf.cell(col_content, entry_h, "学　歴・職　歴", border=1, align="C")
    pdf.cell(col_status, entry_h, "", border=1)
    y += entry_h

    # --- 学歴 ---
    pdf.set_xy(mx, y)
    pdf.cell(col_year, entry_h, "", border=1)
    pdf.cell(col_month, entry_h, "", border=1)
    pdf.set_font("jp", "B", 8)
    pdf.cell(col_content, entry_h, "学歴", border=1, align="C")
    pdf.cell(col_status, entry_h, "", border=1)
    y += entry_h
    pdf.set_font("jp", "", 8)

    if education:
        for edu in education:
            if y > 260:
                break
            yr = edu.get("year", "")
            mo = edu.get("month", "")
            school = edu.get("school", "")
            status = edu.get("status", "")
            pdf.set_xy(mx, y)
            pdf.cell(col_year, entry_h, str(yr), border=1, align="C")
            pdf.cell(col_month, entry_h, str(mo), border=1, align="C")
            pdf.cell(col_content, entry_h, f" {school}", border=1)
            pdf.cell(col_status, entry_h, status, border=1, align="C")
            y += entry_h

    # 空行
    pdf.set_xy(mx, y)
    pdf.cell(col_year, entry_h, "", border=1)
    pdf.cell(col_month, entry_h, "", border=1)
    pdf.cell(col_content, entry_h, "", border=1)
    pdf.cell(col_status, entry_h, "", border=1)
    y += entry_h

    # --- 職歴 ---
    pdf.set_xy(mx, y)
    pdf.cell(col_year, entry_h, "", border=1)
    pdf.cell(col_month, entry_h, "", border=1)
    pdf.set_font("jp", "B", 8)
    pdf.cell(col_content, entry_h, "職　歴", border=1, align="C")
    pdf.cell(col_status, entry_h, "", border=1)
    y += entry_h
    pdf.set_font("jp", "", 8)

    if work:
        for w in work:
            if y > 270:
                break
            yr = w.get("year", "")
            mo = w.get("month", "")
            company = w.get("company", "")
            status = w.get("status", "")
            detail = w.get("detail", "")
            pdf.set_xy(mx, y)
            pdf.cell(col_year, entry_h, str(yr), border=1, align="C")
            pdf.cell(col_month, entry_h, str(mo), border=1, align="C")
            pdf.cell(col_content, entry_h, f" {company}", border=1)
            pdf.cell(col_status, entry_h, status, border=1, align="C")
            y += entry_h
            if detail:
                pdf.set_xy(mx, y)
                pdf.cell(col_year, entry_h, "", border=1)
                pdf.cell(col_month, entry_h, "", border=1)
                pdf.cell(col_content, entry_h, f" {detail}", border=1)
                pdf.cell(col_status, entry_h, "", border=1)
                y += entry_h

    # 現在に至る
    pdf.set_xy(mx, y)
    pdf.cell(col_year, entry_h, "", border=1)
    pdf.cell(col_month, entry_h, "", border=1)
    pdf.cell(col_content, entry_h, " 現在に至る", border=1)
    pdf.cell(col_status, entry_h, "", border=1)
    y += entry_h

    # 空行で埋める
    while y < 280:
        pdf.set_xy(mx, y)
        pdf.cell(col_year, entry_h, "", border=1)
        pdf.cell(col_month, entry_h, "", border=1)
        pdf.cell(col_content, entry_h, "", border=1)
        pdf.cell(col_status, entry_h, "", border=1)
        y += entry_h

    pdf.output(output_path)
    return output_path
