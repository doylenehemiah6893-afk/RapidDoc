import os

import pytest


def test_orientation_basic():
    """方向识别测试（缺少本地文件时跳过）"""
    img_path = "table_90.png"
    if not os.path.exists(img_path):
        pytest.skip("测试文件不存在，跳过该测试。")

    import cv2
    from rapid_orientation import RapidOrientation

    orientation_engine = RapidOrientation()
    img = cv2.imread(img_path)
    cls_result, _ = orientation_engine(img)
    assert cls_result is not None
