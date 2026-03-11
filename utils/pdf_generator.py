"""PDF変換・結合モジュール"""
import os
import subprocess
import tempfile
import platform
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter, PdfReader


def image_to_pdf(image_path: str, output_path: str = None) -> str:
    """画像(JPEG/PNG)をA4サイズのPDFに変換"""
    if output_path is None:
        base = Path(image_path).stem
        output_path = os.path.join(os.path.dirname(image_path), f"{base}.pdf")

    img = Image.open(image_path)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # A4サイズ（ポイント）: 595.28 x 841.89
    a4_width, a4_height = 595.28, 841.89
    img_w, img_h = img.size
    dpi = max(img_w / (a4_width / 72), img_h / (a4_height / 72))

    img.save(output_path, "PDF", resolution=dpi)
    return output_path


def excel_to_pdf(excel_path: str, output_path: str = None) -> str:
    """ExcelファイルをPDFに変換（macOS: qlmanage / Linux: LibreOffice）"""
    if output_path is None:
        base = Path(excel_path).stem
        output_path = os.path.join(os.path.dirname(excel_path), f"{base}.pdf")

    with tempfile.TemporaryDirectory() as tmpdir:
        if platform.system() == "Darwin":
            # macOS: Quick Lookで画像変換 → PDF
            result = subprocess.run(
                ["qlmanage", "-t", "-s", "3508", "-o", tmpdir, excel_path],
                capture_output=True, text=True, timeout=30
            )
            png_files = [f for f in os.listdir(tmpdir) if f.endswith(".png")]
            if not png_files:
                raise RuntimeError(f"Excel→画像変換に失敗しました: {result.stderr}")
            png_path = os.path.join(tmpdir, png_files[0])
            image_to_pdf(png_path, output_path)
        else:
            # Linux: LibreOfficeで直接PDF変換
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf",
                 "--outdir", tmpdir, excel_path],
                capture_output=True, text=True, timeout=60
            )
            pdf_files = [f for f in os.listdir(tmpdir) if f.endswith(".pdf")]
            if not pdf_files:
                raise RuntimeError(f"Excel→PDF変換に失敗しました: {result.stderr}")
            import shutil
            shutil.copy2(os.path.join(tmpdir, pdf_files[0]), output_path)

    return output_path


def merge_pdfs(pdf_paths: list, output_path: str) -> str:
    """複数のPDFを結合"""
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path
