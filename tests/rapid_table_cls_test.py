import os

import pytest

from rapid_doc.model.table.rapid_table_self import ModelType, RapidTableInput, EngineType as TableEngineType
from rapid_doc.model.table.rapid_table_self.table_cls import TableCls


def test_table_cls():
    """表格分类测试（缺少本地文件时跳过）"""
    img_path = (
        r"D:\CodeProjects\doc\RapidAI\RapidDoc\output3\比亚迪财报\auto\images"
        r"\2a18af309c8ea0e9419ab8ea69d24868ef86288da9d7d57de6e19a769c2d2630.jpg"
    )
    if not os.path.exists(img_path):
        pytest.skip("测试文件不存在，跳过该测试。")

    input_args = RapidTableInput(
        model_type=ModelType.Q_CLS,
        engine_type=TableEngineType.ONNXRUNTIME,
    )

    table_cls = TableCls(input_args)

    cls, elasp = table_cls([img_path], batch_size=1)
    assert elasp >= 0
    assert cls
