import os

import pytest
import pypdfium2 as pdfium

PDF_PATH = r"D:\file\text-pdf\a-practical-guide-to-building-agents.pdf"


def test_pdf_text_extract():
    """PDF 文本提取测试（本地文件缺失时跳过）"""
    if not os.path.exists(PDF_PATH):
        pytest.skip("测试文件不存在，跳过该测试。")
    pdf = pdfium.PdfDocument(PDF_PATH)
    for i in range(len(pdf)):
        page = pdf[i]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        assert isinstance(text, str)
