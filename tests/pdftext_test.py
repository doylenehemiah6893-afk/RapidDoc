import os

import pytest
from pdftext.extraction import plain_text_output, dictionary_output

PDF_PATH = r"D:\file\text-pdf\img\default - 副本.pdf"


def test_plain_text_output():
    """文本导出测试（本地文件缺失时跳过）"""
    if not os.path.exists(PDF_PATH):
        pytest.skip("测试文件不存在，跳过该测试。")
    text0 = plain_text_output(PDF_PATH, sort=False, hyphens=False)
    assert isinstance(text0, str)


def test_dictionary_output():
    """结构化导出测试（本地文件缺失时跳过）"""
    if not os.path.exists(PDF_PATH):
        pytest.skip("测试文件不存在，跳过该测试。")
    text = dictionary_output(PDF_PATH, sort=False, keep_chars=False)
    assert isinstance(text, dict)
