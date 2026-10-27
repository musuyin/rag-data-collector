#!/usr/bin/env python3
"""Build an offline report from public inventories, without raw-data downloads."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from modality_inventory import LABELS, aggregate

ROOT = Path(__file__).resolve().parents[1]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evidence(path: Path, locator: str):
    return {"path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "locator": locator}


def build() -> dict:
    state = read(ROOT / "data/collection_state.json")
    hf_path = ROOT / "data/collection_metadata/COLLECT-MMAUD-HF-INVENTORY.json"
    hf = read(hf_path)
    m = hf["metadata"]
    drone_path = ROOT / "data/collection_metadata/COLLECT-DRONERF-MENDELEY.json"
    drone = read(drone_path)
    anti_path = ROOT / "datasets/member2_multimodal_datasets/validation_records/Anti-UAV300/Anti-UAV300_download_validation.json"
    anti = read(anti_path)
    attempt_path = ROOT / "data/collection_attempts/COLLECT-ANTI-UAV300-ZIP-DIRECTORY.json"
    attempt = read(attempt_path) if attempt_path.exists() else {"status": "not_recorded"}
    # Historical aggregate: do not invent per-file sizes from the total archive size.
    categories = [{"category": kind, "label": LABELS[kind], "count": anti["detected_extensions"][ext],
                   "bytes": 0, "unknown_sizes": anti["detected_extensions"][ext]}
                  for kind, ext in [("annotation", ".json"), ("video", ".mp4"), ("code", ".py")]]
    if sum(c["count"] for c in categories) != anti["archive_file_count"]:
        raise ValueError("Anti-UAV historical counts disagree")
    anti_inv = {"file_count": anti["archive_file_count"], "known_bytes": 0,
                "unknown_sizes": anti["archive_file_count"], "categories": categories,
                "extensions": anti["detected_extensions"]}
    drone_files = [{"path": f["name"], "size": f["size"]} for f in drone["metadata"]["files"]]
    if drone["metadata"]["version_returned"] != 1: raise ValueError("DroneRF version changed")
    return {
        "generated_at": datetime.now(UTC).isoformat(), "raw_payload_downloaded": False,
        "basis": "public file inventories; not decoded samples, frames, tokens or information content",
        "datasets": [
            {"id": "MMAUD", "name": "MMAUD", "status": "在线元数据", "status_kind": "live",
             "scope": "官方页面链接的 Hugging Face 发布清单；全目录视图含文档、校准、容器和已展开文件。",
             "checked_at": state["COLLECT-MMAUD-HF-INVENTORY"]["checked_at"],
             "license": m.get("license") or "CC BY-NC-SA 4.0",
             "views": [{"id": "all", "label": "全部发布文件（存储视图）", "inventory": m["logical_inventory"]},
                       {"id": "extracted", "label": "已展开传感器文件（局部视图）", "inventory": m["extracted_inventory"]}],
             "notes": ["ROS bag 内部各模态比例未知，单列为混合传感器容器；不能把 bag 当视频。",
                       "大文件的 3 个字节分片合计为 1 个逻辑 bag；物理文件数为 " + str(m["physical_inventory"]["file_count"]) + "。",
                       "已展开视图仅含 V1/filesystem_format 与 V2_V3/audio，不能代表所有版本的解码内容。",
                       "全目录包含同一内容的 bag 和已展开表示；存储占比没有做语义去重。",
                       "图片包含独立 PNG；视频 0 表示该清单没有独立视频文件，不表示 bag 内没有图像流。",
                       "按路径识别 LiDAR、Radar 和 ground_truth；未对 NPY 内容进行语义复验。"],
             "links": [{"label": "官方项目页", "url": "https://ntu-aris.github.io/MMAUD/"},
                       {"label": "发布目录", "url": "https://huggingface.co/datasets/Yuan-Shenghai/MMAUD/tree/" + m["revision"]},
                       {"label": "文件布局说明", "url": "https://huggingface.co/datasets/Yuan-Shenghai/MMAUD/blob/" + m["revision"] + "/ASSET_LAYOUT.md"}],
             "evidence": [evidence(hf_path, "metadata.logical_inventory / extracted_inventory")],
             "revision": m["revision"], "metadata_response_bytes": m["response_bytes"]},
            {"id": "Anti-UAV300", "name": "Anti-UAV300", "status": "历史清单 · 在线目录未取得",
             "status_kind": "historical", "scope": "已有成员验收记录中的 Anti-UAV-RGBT.zip 全包目录，非本次在线实测。",
             "checked_at": anti["validation_time"], "license": "数据集级许可未确认",
             "views": [{"id": "all", "label": "历史全包目录（文件数）", "inventory": anti_inv}],
             "notes": ["本次核对官方页：300 版包含 RGB 和红外视频；网页未提供逐文件大小。",
                       "本次远程目录请求返回 HTTP 200，已拒绝读取正文，没有下载完整 ZIP 或绕过确认页。",
                       "图中数量来自 2026-09-29 的上游验收记录，可能已过期；本次未独立复验。",
                       "639 个 JSON 是标注 / 元数据，不能当作 639 篇自然语言文本。",
                       "历史目录记录 318 组序列与 636 个视频；产品名 300 不用于推算实际文件数。",
                       "包压缩大小 6.038 GB；历史解包大小 6.720 GB。缺少分类字节数，不绘制大小比例。"],
             "links": [{"label": "官方说明", "url": "https://github.com/ZhaoJ9014/Anti-UAV#data-preparation"},
                       {"label": "官方链接的数据包", "url": "https://drive.google.com/file/d/1NPYaop35ocVTYWHOYQQHn8YHsM9jmLGr/view"}],
             "evidence": [evidence(anti_path, "detected_extensions / archive_file_count")],
             "latest_metadata_attempt": attempt},
            {"id": "DroneRF", "name": "DroneRF", "status": "在线 API 已核对", "status_kind": "live",
             "scope": "Mendeley v1 全部发布包；以压缩包为文件单位，以压缩存储大小为字节单位。",
             "checked_at": state["COLLECT-DRONERF-MENDELEY"]["checked_at"], "license": "CC BY 4.0",
             "views": [{"id": "all", "label": "官方 v1 发布包（压缩视图）", "inventory": aggregate(drone_files, "DroneRF")}],
             "notes": ["发布清单均为 RF 数据 RAR 包，按官方数据说明分类为射频信号；不是文本语料或视频。",
                       "100% 表示已发布数据包的类型分布；不宣称本次列举或解码了每一个包内 CSV。",
                       "CSV 中的数值属于 RF 采样信号；视频录制是设备运行状态，不代表包含视频文件。",
                       "API 元数据本次核对未变化，沿用已归档的 v1 文件清单；未下载 RAR 载荷。"],
             "links": [{"label": "官方数据页", "url": "https://data.mendeley.com/datasets/f4c2b4n755/1"},
                       {"label": "公开文件 API", "url": drone["metadata"]["api_url"]}],
             "evidence": [evidence(drone_path, "metadata.files")], "version": 1},
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=ROOT / "data/reports/dataset_modality_report.html")
    parser.add_argument("--json", type=Path, default=ROOT / "data/normalized/dataset_modality_summary.json")
    args = parser.parse_args()
    for output in (args.html, args.json):
        if output.resolve().is_relative_to(ROOT / "datasets"):
            parser.error("datasets/ is read-only")
    report = build()
    template = (ROOT / "templates/modality_report.html").read_text(encoding="utf-8")
    payload = json.dumps(report, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028")
    args.html.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.html.write_text(template.replace("__REPORT_JSON__", payload), encoding="utf-8")
    print(json.dumps({"html": str(args.html), "json": str(args.json), "raw_payload_downloaded": False}))


if __name__ == "__main__":
    main()
