import json
import os
import re

import pytest
from bs4 import BeautifulSoup

def clean_text_for_embedding(text: str) -> str:
    """
    清洗文本用于向量化：
    - 移除所有 <img> 标签
    - HTML 表格 → 纯文本表格（| 分隔）
    - 移除其他 HTML 标签
    - 连续的多余点替换为固定的三个点 "..."
    - 压缩所有空白为单个空格
    """
    if not text:
        return ""

    soup = BeautifulSoup(text, "html.parser")

    # 移除所有 <img> 标签
    for img in soup.find_all("img"):
        img.decompose()

    # 处理 HTML 表格
    tables = soup.find_all("table")
    for table in tables:
        rows_text = []

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            cols_text = [" ".join(col.get_text(separator=" ").split()) for col in cols]
            row_text = " | ".join(cols_text)
            rows_text.append(row_text)

        table_text = "\n".join(rows_text)

        # 用纯文本表格替换 HTML 表格
        table.replace_with(table_text)

    # 移除所有剩余 HTML 标签
    text = soup.get_text(separator=" ")

    # 替换连续的点为 "..."
    text = re.sub(r"\.{4,}", "...", text)

    # 压缩所有空白，包括换行、tab
    text = " ".join(text.split())

    return text.strip()


def test_chunker_basic():
    """分块流程测试（缺少本地文件时跳过）"""
    markdown_path = (
        r"D:\CodeProjects\doc\RapidAI\RapidDoc\output\ea6c0a89-dd49-4d72-b8c0-4e774d24d9dc"
        r"\auto\ea6c0a89-dd49-4d72-b8c0-4e774d24d9dc.md"
    )
    middle_json_path = (
        r"D:\CodeProjects\doc\RapidAI\RapidDoc\output\ea6c0a89-dd49-4d72-b8c0-4e774d24d9dc"
        r"\auto\ea6c0a89-dd49-4d72-b8c0-4e774d24d9dc_middle.json"
    )
    if not os.path.exists(markdown_path) or not os.path.exists(middle_json_path):
        pytest.skip("测试文件不存在，跳过该测试。")

    from chunker.text_splitters import MarkdownTextSplitter, num_tokens_from_string
    from chunker.get_bbox_page_fast import get_bbox_for_chunk, get_blocks_from_middle

    with open(markdown_path, "r", encoding="utf-8") as handle:
        markdown_document = handle.read()

    with open(middle_json_path, "r", encoding="utf-8") as handle:
        middle_json_content = json.load(handle)

    text_splitter = MarkdownTextSplitter(
        chunk_token_num=512, min_chunk_tokens=50
    )
    chunk_list = text_splitter.split_text(markdown_document)
    assert chunk_list

    max_tokens = 0
    max_chunk = None

    for chunk in chunk_list:
        tokens = num_tokens_from_string(clean_text_for_embedding(chunk))
        if tokens > max_tokens:
            max_tokens = tokens
            max_chunk = chunk

    max_chunk_txt = clean_text_for_embedding(max_chunk)
    txt_tokens = num_tokens_from_string(max_chunk_txt)
    assert txt_tokens > 0

    block_list = get_blocks_from_middle(middle_json_content)
    matched_global_indices = set()
    for chunk in chunk_list:
        position_int_temp = get_bbox_for_chunk(chunk.strip(), block_list, matched_global_indices)
        assert position_int_temp is not None
