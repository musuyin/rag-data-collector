"""Aggregate public file inventories without downloading images, bags, or signals."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import PurePosixPath

LABELS = {
    "image": "图片", "video": "视频", "audio": "音频", "lidar": "激光雷达点云",
    "radar": "毫米波雷达点云", "rf": "射频信号", "trajectory": "轨迹 / 真值",
    "text": "文本 / 文档", "annotation": "标注 / 结构化元数据", "code": "代码",
    "mixed": "混合传感器容器", "archive": "未展开归档", "unknown": "其他 / 未知",
}


def classify(path: str, dataset: str = "") -> str:
    p = PurePosixPath(path.lower())
    suffix, parts = p.suffix, p.parts
    if suffix == ".bag" or re.search(r"\.bag\.part\d+$", p.name):
        return "trajectory" if "ground_truth" in parts else "mixed"
    if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".gif", ".svg"}:
        return "image"
    if suffix in {".mp4", ".avi", ".mov", ".mkv", ".webm"}: return "video"
    if suffix in {".wav", ".flac", ".mp3", ".ogg", ".m4a"}: return "audio"
    if dataset == "DroneRF" and suffix in {".rar", ".csv"}: return "rf"
    if "ground_truth" in parts or "interpolated" in p.name: return "trajectory"
    if suffix in {".npy", ".pcd", ".ply"}:
        if any("radar" in part for part in parts): return "radar"
        if any("lidar" in part or "livox" in part for part in parts): return "lidar"
        return "unknown"
    if "sha256" in p.name or "checksums" in p.name: return "annotation"
    if suffix in {".txt", ".md", ".pdf", ".html", ".rst", ".bib"}: return "text"
    if suffix in {".json", ".jsonl", ".csv", ".yaml", ".yml", ".xml", ".toml"}: return "annotation"
    if suffix in {".py", ".sh", ".m", ".ipynb", ".cpp", ".h"}: return "code"
    if suffix in {".zip", ".rar", ".7z", ".gz", ".bz2", ".tar"}: return "archive"
    return "unknown"


def aggregate(files: list[dict], dataset: str = "") -> dict:
    buckets: dict[str, dict] = {}
    extensions: Counter = Counter()
    for f in files:
        path = f["path"]
        category = classify(path, dataset)
        b = buckets.setdefault(category, {"category": category, "label": LABELS[category],
                                           "count": 0, "bytes": 0, "unknown_sizes": 0})
        b["count"] += 1
        size = f.get("size")
        if isinstance(size, int) and not isinstance(size, bool) and size >= 0:
            b["bytes"] += size
        else:
            b["unknown_sizes"] += 1
        extensions[PurePosixPath(path).suffix.lower() or "(无扩展名)"] += 1
    return {"file_count": len(files), "known_bytes": sum(b["bytes"] for b in buckets.values()),
            "unknown_sizes": sum(b["unknown_sizes"] for b in buckets.values()),
            "categories": sorted(buckets.values(), key=lambda b: (-b["count"], b["category"])),
            "extensions": dict(sorted(extensions.items()))}


def summarize_huggingface(record: dict) -> dict:
    siblings = record.get("siblings")
    if not isinstance(siblings, list) or not siblings:
        raise ValueError("Hugging Face API did not return a nonempty siblings inventory")
    if not record.get("sha"): raise ValueError("dataset revision is missing")
    files = [{"path": item["rfilename"], "size": item.get("size", (item.get("lfs") or {}).get("size"))}
             for item in siblings]
    if len({f["path"] for f in files}) != len(files): raise ValueError("duplicate inventory paths")
    # A bag stored as byte parts is ONE logical recording. Physical totals remain explicit.
    parts = [f for f in files if ".bag.part" in PurePosixPath(f["path"]).name and
             not f["path"].endswith(".json")]
    logical = [f for f in files if f not in parts]
    groups: dict[str, list] = {}
    for f in parts:
        original = f["path"].split(".bag.part", 1)[0] + ".bag"
        groups.setdefault(original, []).append(f)
    for path, items in groups.items():
        sizes = [f["size"] for f in items]
        logical.append({"path": path, "size": sum(sizes) if all(isinstance(s, int) for s in sizes) else None})
    # Never add bag representations and extracted representations into one semantic denominator.
    extracted = [f for f in logical if f["path"].startswith("V1/filesystem_format/") or
                 f["path"].startswith("V2_V3/audio/")]
    roots = sorted({f["path"].split("/", 1)[0] for f in logical})
    return {"repository": record.get("id"), "revision": record["sha"],
            "last_modified": record.get("lastModified"), "license": (record.get("cardData") or {}).get("license"),
            "physical_inventory": aggregate(files), "logical_inventory": aggregate(logical),
            "extracted_inventory": aggregate(extracted),
            "top_level": {root: aggregate([f for f in logical if f["path"].split("/", 1)[0] == root])
                          for root in roots},
            "bag_part_groups": [{"logical_path": path, "parts": len(items)} for path, items in groups.items()],
            "limitations": ["API metadata only; no raw payload was downloaded or decoded.",
                            "ROS bag topic-level modality proportions are UNKNOWN.",
                            "Extracted V1 and V2/V3 audio are a view of the release, not every decoded recording.",
                            "Stored extracted files and bags can represent the same observations."]}
