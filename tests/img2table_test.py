import os

import pytest


def test_img2table_extract():
    """表格抽取测试（缺少本地文件时跳过）"""
    pdf_path = r"D:\file\text-pdf\比亚迪财报.pdf"
    if not os.path.exists(pdf_path):
        pytest.skip("测试文件不存在，跳过该测试。")

    from img2table.document import PDF

    pdf = PDF(src=pdf_path)
    extracted_tables = pdf.extract_tables(
        ocr=None,
        implicit_rows=False,
        borderless_tables=False,
        min_confidence=50,
    )

    assert extracted_tables
