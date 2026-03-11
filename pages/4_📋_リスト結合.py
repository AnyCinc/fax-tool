"""複数Excelリストの結合ページ"""
import os
import sys
import tempfile
from io import BytesIO
import streamlit as st
import openpyxl
from openpyxl.utils import get_column_letter
from copy import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.title("📋 リスト結合")
st.caption("複数のExcelファイルを1つに結合します（列はそのまま維持）")

# --- ファイルアップロード ---
uploaded_files = st.file_uploader(
    "Excelファイルを複数選択",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"📁 {len(uploaded_files)}件のファイルを選択中")

    # ヘッダー行の扱い
    header_row = st.number_input("ヘッダー行（1行目がヘッダーなら1）", min_value=0, max_value=10, value=1)
    skip_header = st.checkbox("2つ目以降のファイルのヘッダーをスキップする", value=True)

    # プレビュー
    if st.button("📊 プレビュー", use_container_width=True):
        total_rows = 0
        for i, f in enumerate(uploaded_files):
            wb = openpyxl.load_workbook(BytesIO(f.read()), data_only=True)
            f.seek(0)
            ws = wb.active

            # 最終データ行を検出
            last_row = 0
            for row in range(ws.max_row, 0, -1):
                if any(ws.cell(row, c).value for c in range(1, ws.max_column + 1)):
                    last_row = row
                    break

            data_start = (header_row + 1) if header_row > 0 else 1
            data_rows = last_row - data_start + 1 if last_row >= data_start else 0

            st.markdown(f"**{i+1}. {f.name}** — {data_rows}行 × {ws.max_column}列")
            total_rows += data_rows

            # ヘッダー表示
            if header_row > 0 and i == 0:
                headers = [ws.cell(header_row, c).value or "" for c in range(1, ws.max_column + 1)]
                st.write("ヘッダー:", headers)

        st.success(f"**合計: {total_rows}行** のデータが結合されます")

    st.divider()

    # 出力ファイル名
    output_name = st.text_input("出力ファイル名", value="結合リスト.xlsx")

    # --- 結合実行 ---
    if st.button("🔗 結合して生成", type="primary", use_container_width=True):
        with st.spinner("結合中..."):
            try:
                result_wb = openpyxl.Workbook()
                result_ws = result_wb.active
                result_ws.title = "結合データ"
                current_row = 1

                for i, f in enumerate(uploaded_files):
                    wb = openpyxl.load_workbook(BytesIO(f.read()), data_only=True)
                    f.seek(0)
                    ws = wb.active

                    # 最終データ行を検出
                    last_row = 0
                    for row in range(ws.max_row, 0, -1):
                        if any(ws.cell(row, c).value for c in range(1, ws.max_column + 1)):
                            last_row = row
                            break

                    # 開始行を決定
                    if i == 0:
                        # 最初のファイルはヘッダー含めて全部コピー
                        start_row = 1
                    else:
                        # 2つ目以降
                        if skip_header and header_row > 0:
                            start_row = header_row + 1
                        else:
                            start_row = 1

                    # データコピー
                    for src_row in range(start_row, last_row + 1):
                        for col in range(1, ws.max_column + 1):
                            src_cell = ws.cell(src_row, col)
                            dest_cell = result_ws.cell(current_row, col)
                            dest_cell.value = src_cell.value

                            # スタイルコピー
                            if src_cell.has_style:
                                dest_cell.font = copy(src_cell.font)
                                dest_cell.fill = copy(src_cell.fill)
                                dest_cell.border = copy(src_cell.border)
                                dest_cell.alignment = copy(src_cell.alignment)
                                dest_cell.number_format = src_cell.number_format

                        current_row += 1

                    # 最初のファイルから列幅をコピー
                    if i == 0:
                        for col in range(1, ws.max_column + 1):
                            letter = get_column_letter(col)
                            if ws.column_dimensions[letter].width:
                                result_ws.column_dimensions[letter].width = ws.column_dimensions[letter].width

                # 保存
                output_buffer = BytesIO()
                result_wb.save(output_buffer)
                output_buffer.seek(0)

                total = current_row - 1
                st.success(f"結合完了！ {total}行のデータ")

                st.download_button(
                    label="📥 結合Excelをダウンロード",
                    data=output_buffer.getvalue(),
                    file_name=output_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"結合に失敗しました: {e}")
else:
    st.markdown("""
    ### 使い方
    1. 上のエリアにExcelファイルを**複数**ドラッグ＆ドロップ
    2. 「プレビュー」で内容を確認
    3. 「結合して生成」で1つのファイルに結合

    > 💡 1つ目のファイルのヘッダーが使われ、2つ目以降のデータが下に追加されます
    """)
