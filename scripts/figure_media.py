#!/usr/bin/env python3
"""Validate local result-media records and extract frames with SHA256 provenance (FFmpeg required)."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate(data, path.parent)
    return data


def validate(data: dict, base: Path) -> None:
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    if data.get("evidence_scope") not in {"production", "held-out", "illustrative"}:
        raise ValueError("evidence_scope must be production, held-out or illustrative")
    records = data.get("media")
    if not isinstance(records, list) or not records:
        raise ValueError("media must be a nonempty list")
    seen, paired = set(), {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each media record must be an object")
        name = record.get("id", "")
        if not isinstance(name, str) or not ID.fullmatch(name) or name in seen:
            raise ValueError(f"invalid or duplicate media id: {name!r}")
        seen.add(name)
        for field in ("path", "source", "world", "case", "attempt", "status", "role"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"{name}: missing {field}; use 'unknown' when unavailable")
        media = base / record["path"]
        if not media.is_file():
            raise ValueError(f"{name}: local media not found: {media}")
        kind = record.get("kind")
        if kind not in ("video", "image"):
            raise ValueError(f"{name}: kind must be video or image")
        if kind == "video":
            times = record.get("timestamps")
            if not isinstance(times, list) or not times:
                raise ValueError(f"{name}: video requires timestamps in seconds")
            if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or t < 0 for t in times):
                raise ValueError(f"{name}: timestamps must be finite nonnegative seconds")
            if any(b <= a for a, b in zip(times, times[1:])):
                raise ValueError(f"{name}: timestamps must be strictly chronological")
        if record.get("pair_id"):
            pair = record["pair_id"]
            if not isinstance(pair, str) or not ID.fullmatch(pair):
                raise ValueError(f"{name}: invalid pair_id")
            identity = tuple(record[f] for f in ("world", "case", "attempt"))
            if "unknown" in identity:
                raise ValueError(f"{name}: paired examples require known world/case/attempt")
            if pair in paired and paired[pair] != identity:
                raise ValueError(f"{pair}: mismatched world/case/attempt")
            paired[pair] = identity


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def extract(path: Path, out: Path, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe") -> dict:
    data = load_manifest(path)
    # Validate every duration and all dependencies before creating output.
    durations = {}
    if any(r["kind"] == "video" for r in data["media"]):
        for executable in (ffmpeg, ffprobe):
            if not shutil.which(executable):
                raise ValueError(f"required executable not found: {executable}")
        for r in data["media"]:
            if r["kind"] != "video":
                continue
            source = (path.parent / r["path"]).resolve()
            probe = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height:format=duration", "-of", "json", str(source)],
                                   check=True, capture_output=True, text=True)
            info = json.loads(probe.stdout)
            duration = float(info["format"]["duration"])
            if not info.get("streams") or not math.isfinite(duration) or duration <= 0:
                raise ValueError(f"{r['id']}: video stream/duration unavailable")
            if any(t >= duration for t in r["timestamps"]):
                raise ValueError(f"{r['id']}: timestamp outside video duration {duration}")
            durations[r["id"]] = duration
    out.mkdir(parents=True, exist_ok=False)
    frames = []
    for r in data["media"]:
        source = (path.parent / r["path"]).resolve()
        source_hash = sha256(source)
        for index, timestamp in enumerate(r.get("timestamps", []) if r["kind"] == "video" else [None]):
            target = out / (f"{r['id']}-{index:02d}.png" if timestamp is not None else f"{r['id']}{source.suffix}")
            if timestamp is None:
                shutil.copy2(source, target)
            else:
                subprocess.run([ffmpeg, "-v", "error", "-i", str(source), "-ss", str(timestamp), "-frames:v", "1",
                                "-update", "1", str(target)], check=True, capture_output=True)
            if not target.is_file() or not target.stat().st_size:
                raise ValueError(f"{r['id']}: no decoded frame at {timestamp}")
            frames.append({**r, "media_id": r["id"], "id": f"{r['id']}-{index:02d}", "path": target.name,
                           "timestamp_seconds": timestamp, "duration_seconds": durations.get(r["id"]),
                           "source_path": str(source), "source_sha256": source_hash,
                           "sha256": sha256(target)})
    result = {"evidence_scope": data["evidence_scope"], "timestamp_semantics": "requested seek time in seconds; nearest decoded frame, not measured presentation timestamp", "frames": frames}
    (out / "source_frames.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "extract"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "check":
            data = load_manifest(args.manifest)
            print(json.dumps({"valid": True, "media_count": len(data["media"])}))
        else:
            if args.out is None:
                raise ValueError("extract requires --out (a new directory)")
            result = extract(args.manifest, args.out)
            print(json.dumps({"frame_count": len(result["frames"]), "manifest": str(args.out / "source_frames.json")}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"{exc}\n")

if __name__ == "__main__":
    raise SystemExit(main())
