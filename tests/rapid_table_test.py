import os
import time

import pytest
from rapidocr import RapidOCR, EngineType, OCRVersion

from rapid_doc.model.table.rapid_table_self import ModelType, RapidTable, RapidTableInput


def test_table_pipeline():
    """表格端到端测试（默认跳过，需要环境变量开启）"""
    if os.environ.get("RAPIDDOC_RUN_HEAVY_TESTS") != "1":
        pytest.skip("未开启耗时测试，跳过该测试。")

    default_params = {
        "Global.use_cls": False,
        "Det.engine_type": EngineType.OPENVINO,
        "Rec.engine_type": EngineType.OPENVINO,
        "Det.ocr_version": OCRVersion.PPOCRV5,
        "Rec.ocr_version": OCRVersion.PPOCRV5,
        "Det.limit_side_len": 960,
        "Det.limit_type": "max",
        "Det.std": [0.229, 0.224, 0.225],
        "Det.mean": [0.485, 0.456, 0.406],
        "Det.box_thresh": 0.3,
        "Det.use_dilation": True,
        "Det.unclip_ratio": 1.8,
    }

    img_path = (
        "https://raw.githubusercontent.com/RapidAI/RapidTable/refs/heads/main/tests/test_files/table.jpg"
    )

    ocr_engine = RapidOCR(params=default_params)
    input_args = RapidTableInput(
        model_type=ModelType.UNET,
    )
    table_engine = RapidTable(input_args)

    ori_ocr_res = ocr_engine(img_path)
    ocr_results = [ori_ocr_res.boxes, ori_ocr_res.txts, ori_ocr_res.scores]
    start_time = time.time()
    results = table_engine(img_path, ocr_results=ocr_results)
    assert results is not None
    assert time.time() - start_time >= 0
