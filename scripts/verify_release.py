#!/usr/bin/env python3
"""Verify a livery ZIP against its external release manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from release_common import (
    ReleaseError,
    load_json,
    verify_archive,
    verify_checksum_file,
    verify_manifest_against_metadata,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Release ZIP to verify")
    parser.add_argument("manifest", type=Path, help="Generated JSON manifest")
    parser.add_argument("--checksums", type=Path, help="Optional SHA256SUMS.txt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive = args.archive.resolve()
    manifest_path = args.manifest.resolve()
    manifest = load_json(manifest_path)
    metadata = load_json(REPOSITORY_ROOT / "metadata" / "package.json")
    verify_manifest_against_metadata(manifest, metadata)
    verify_archive(archive, manifest)
    if args.checksums is not None:
        verify_checksum_file(args.checksums.resolve(), [archive, manifest_path])
    print(
        f"Verified {archive.name}: "
        f"{manifest['totals']['fileCount']} files, "
        f"{manifest['totals']['uncompressedBytes']} uncompressed bytes"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, OSError, ReleaseError) as error:
        raise SystemExit(f"error: {error}") from error
