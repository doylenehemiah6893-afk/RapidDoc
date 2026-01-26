import os

import pytest
from rapidocr import RapidOCR, EngineType, OCRVersion
from rapidocr.ch_ppocr_det import TextDetector
from rapidocr.ch_ppocr_det.utils import DetPreProcess


def new_get_preprocess(self, max_wh: int) -> DetPreProcess:
    """自定义预处理逻辑"""
    limit_side_len = self.limit_side_len
    return DetPreProcess(limit_side_len, self.limit_type, self.mean, self.std)


def test_rapidocr_basic():
    """文字识别测试（默认跳过，需要环境变量开启）"""
    if os.environ.get("RAPIDDOC_RUN_HEAVY_TESTS") != "1":
        pytest.skip("未开启耗时测试，跳过该测试。")

    img_path = "b896a7ebfc79e0a7916429bb58b7791c25e2c79f83817f9a94decc6cbd844de2.jpg"
    if not os.path.exists(img_path):
        pytest.skip("测试文件不存在，跳过该测试。")

    TextDetector.get_preprocess = new_get_preprocess

    default_params = {
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Det.ocr_version": OCRVersion.PPOCRV5,
        "Rec.ocr_version": OCRVersion.PPOCRV5,
        "Det.limit_side_len": 960,
        "Det.limit_type": "max",
        "Det.std": [0.229, 0.224, 0.225],
        "Det.mean": [0.485, 0.456, 0.406],
        "Det.box_thresh": 0.3,
        "Det.use_dilation": True,
        "Det.unclip_ratio": 1.6,
    }

    engine = RapidOCR(params=default_params)
    result = engine(img_path, return_word_box=False)
    assert result is not None
