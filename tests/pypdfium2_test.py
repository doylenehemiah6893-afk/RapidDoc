from pathlib import Path
import os

import pytest
import pypdfium2 as pdfium


def test_pdfium_text_extract():
    """使用 pypdfium2 提取 PDF 文本。"""
    # 允许通过环境变量传入本地测试 PDF 路径
    pdf_path = os.environ.get("RAPIDDOC_TEST_PDF")
    if not pdf_path:
        pytest.skip("未设置 RAPIDDOC_TEST_PDF 环境变量，跳过本地 PDF 测试。")

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        pytest.skip(f"PDF 文件不存在: {pdf_file}")

    pdf = pdfium.PdfDocument(str(pdf_file))
    assert len(pdf) > 0

    page = pdf[0]
    textpage = page.get_textpage()
    text = textpage.get_text_range()
    assert isinstance(text, str)
