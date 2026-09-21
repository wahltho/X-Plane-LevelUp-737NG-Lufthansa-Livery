#!/usr/bin/env python3
"""Build deterministic livery release assets from the canonical source tree."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import tempfile
from pathlib import Path

from release_common import (
    ReleaseError,
    build_zip,
    canonical_json_bytes,
    load_json,
    make_manifest,
    sha256_file,
    validate_source,
    verify_archive,
    verify_checksum_file,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release-date",
        required=True,
        help="Release date in YYYY-MM-DD format; explicit input keeps builds reproducible.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPOSITORY_ROOT / "dist",
        help="Output directory (default: dist below the repository root).",
    )
    parser.add_argument(
        "--check-reproducible",
        action="store_true",
        help="Build a second time and require byte-identical outputs.",
    )
    return parser.parse_args()


def validate_release_date(value: str) -> str:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as error:
        raise ReleaseError(f"Invalid release date {value!r}; expected YYYY-MM-DD") from error
    if parsed.isoformat() != value:
        raise ReleaseError(f"Release date is not canonical: {value!r}")
    return value


def build_outputs(output_dir: Path, release_date: str) -> list[Path]:
    metadata = load_json(REPOSITORY_ROOT / "metadata" / "package.json")
    source_root = REPOSITORY_ROOT / "src" / metadata["release"]["archiveRoot"]
    files = validate_source(source_root, metadata)

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / metadata["release"]["assetFileName"]
    manifest_path = output_dir / metadata["release"]["manifestFileName"]
    checksum_path = output_dir / "SHA256SUMS.txt"

    build_zip(archive_path, source_root, metadata["release"]["archiveRoot"], files)
    manifest = make_manifest(metadata, release_date, archive_path, files)
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    checksum_path.write_text(
        f"{sha256_file(archive_path)}  {archive_path.name}\n"
        f"{sha256_file(manifest_path)}  {manifest_path.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    verify_archive(archive_path, manifest)
    verify_checksum_file(checksum_path, [archive_path, manifest_path])
    return [archive_path, manifest_path, checksum_path]


def main() -> int:
    args = parse_args()
    release_date = validate_release_date(args.release_date)
    outputs = build_outputs(args.output_dir.resolve(), release_date)

    if args.check_reproducible:
        with tempfile.TemporaryDirectory(prefix="livery-release-") as temporary:
            second = build_outputs(Path(temporary), release_date)
            for first_path, second_path in zip(outputs, second, strict=True):
                if first_path.read_bytes() != second_path.read_bytes():
                    raise ReleaseError(f"Non-reproducible output: {first_path.name}")

    print(f"Built and verified {outputs[0].name}")
    print(f"Archive SHA-256: {sha256_file(outputs[0])}")
    if args.check_reproducible:
        print("Reproducibility check: byte-identical")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, ReleaseError) as error:
        raise SystemExit(f"error: {error}") from error
