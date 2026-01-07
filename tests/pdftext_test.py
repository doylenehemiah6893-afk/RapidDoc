from pathlib import Path
import os

import pytest
from pdftext.extraction import plain_text_output


def test_plain_text_output():
    """读取 PDF 并输出纯文本。"""
    # 允许通过环境变量传入本地测试 PDF 路径
    pdf_path = os.environ.get("RAPIDDOC_TEST_PDF")
    if not pdf_path:
        pytest.skip("未设置 RAPIDDOC_TEST_PDF 环境变量，跳过本地 PDF 测试。")

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        pytest.skip(f"PDF 文件不存在: {pdf_file}")

    text = plain_text_output(str(pdf_file), sort=False, hyphens=False)
    assert isinstance(text, str)
