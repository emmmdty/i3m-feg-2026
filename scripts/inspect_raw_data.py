#!/usr/bin/env python3
"""Create a lightweight manifest for files under data/raw."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {".txt", ".json", ".jsonl", ".csv", ".md"}
BINARY_OR_LARGE_SUFFIXES = {
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".pt",
    ".pth",
    ".bin",
    ".safetensors",
    ".gguf",
}
SAMPLE_BYTES = 8192


def guess_format(path: Path, sample: bytes | None) -> str:
    suffix = path.suffix.lower()
    if suffix in BINARY_OR_LARGE_SUFFIXES:
        return suffix.lstrip(".") or "binary"
    if suffix not in TEXT_SUFFIXES:
        return suffix.lstrip(".") or "unknown"

    if sample is None:
        return suffix.lstrip(".") or "text"

    stripped = sample.lstrip()
    if suffix in {".json", ".jsonl"}:
        if stripped.startswith((b"{", b"[")):
            return suffix.lstrip(".")
        return "text-like"
    if suffix == ".csv":
        return "csv"
    if suffix == ".md":
        return "markdown"
    return "text"


def inspect_file(path: Path, raw_dir: Path) -> dict[str, Any]:
    stat = path.stat()
    suffix = path.suffix.lower()
    sample: bytes | None = None
    sample_status = "not_sampled_binary_or_large"

    if suffix in TEXT_SUFFIXES:
        try:
            with path.open("rb") as fh:
                sample = fh.read(SAMPLE_BYTES)
            sample_status = f"sampled_first_{len(sample)}_bytes"
        except OSError as exc:
            sample_status = f"sample_failed:{exc.__class__.__name__}"

    return {
        "relative_path": path.relative_to(raw_dir).as_posix(),
        "suffix": suffix,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 6),
        "maybe_format": guess_format(path, sample),
        "sample_status": sample_status,
    }


def build_manifest(raw_dir: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    if raw_dir.exists():
        for path in sorted(raw_dir.rglob("*")):
            if path.is_file():
                files.append(inspect_file(path, raw_dir))

    return {
        "raw_dir": raw_dir.as_posix(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "num_files": len(files),
        "files": files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("outputs/raw_data_manifest.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.raw_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote raw data manifest: {args.out} ({manifest['num_files']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
