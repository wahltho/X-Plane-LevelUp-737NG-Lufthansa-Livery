#!/usr/bin/env python3
"""Shared deterministic package and verification helpers."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
MTK_CONTRACT_FIELDS = (
    "schemaVersion",
    "packageType",
    "packageId",
    "packageVersion",
    "releaseTag",
    "channel",
    "repository",
    "supportedProducts",
    "supportedVariants",
    "installScope",
    "targetDirectory",
    "archiveRoot",
    "restartRequired",
)


class ReleaseError(RuntimeError):
    """Raised when source or release validation fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ReleaseError(f"Expected a JSON object: {path}")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def is_forbidden(path: str) -> bool:
    pure = PurePosixPath(path)
    return (
        path.startswith("/")
        or "\\" in path
        or ".." in pure.parts
        or "__MACOSX" in pure.parts
        or pure.name == ".DS_Store"
        or pure.name.startswith("._")
        or pure.suffix.lower() == ".cfg"
    )


def is_relative_payload_path(path: str, archive_root: str) -> bool:
    pure = PurePosixPath(path)
    return (
        bool(path)
        and not path.startswith("/")
        and "\\" not in path
        and ".." not in pure.parts
        and pure.parts[0] != archive_root
        and not is_forbidden(path)
    )


def expected_manifest_contract(metadata: dict[str, Any]) -> dict[str, Any]:
    configured = metadata.get("manifestContract")
    if not isinstance(configured, dict):
        raise ReleaseError("metadata/package.json has no manifestContract object")
    contract = {
        "schemaVersion": metadata["schemaVersion"],
        "packageVersion": metadata["version"],
        **configured,
    }
    validate_manifest_contract(contract, require_payload=False)
    if contract["releaseTag"] != f"v{contract['packageVersion']}":
        raise ReleaseError("releaseTag must equal 'v' plus packageVersion")
    if contract["targetDirectory"] != contract["archiveRoot"]:
        raise ReleaseError("targetDirectory and archiveRoot must match for this livery")
    return contract


def validate_manifest_contract(
    manifest: dict[str, Any], *, require_payload: bool = True
) -> None:
    missing = [field for field in MTK_CONTRACT_FIELDS if field not in manifest]
    if missing:
        raise ReleaseError(f"Manifest is missing MTK contract fields: {missing}")
    if manifest["schemaVersion"] != 1:
        raise ReleaseError("Unsupported manifest schemaVersion")
    for field in (
        "packageType",
        "packageId",
        "packageVersion",
        "releaseTag",
        "channel",
        "repository",
        "installScope",
        "targetDirectory",
        "archiveRoot",
    ):
        if not isinstance(manifest[field], str) or not manifest[field]:
            raise ReleaseError(f"Manifest field {field} must be a non-empty string")
    if not SEMVER_PATTERN.fullmatch(manifest["packageVersion"]):
        raise ReleaseError("packageVersion must be semantic version major.minor.patch")
    if manifest["releaseTag"] != f"v{manifest['packageVersion']}":
        raise ReleaseError("releaseTag does not match packageVersion")
    if "/" in manifest["archiveRoot"] or manifest["archiveRoot"] in {".", ".."}:
        raise ReleaseError("archiveRoot must be one portable directory name")
    if "/" in manifest["targetDirectory"] or manifest["targetDirectory"] in {".", ".."}:
        raise ReleaseError("targetDirectory must be one portable directory name")
    for field in ("supportedProducts", "supportedVariants"):
        value = manifest[field]
        if (
            not isinstance(value, list)
            or not value
            or any(not isinstance(item, str) or not item for item in value)
            or len(value) != len(set(value))
        ):
            raise ReleaseError(f"Manifest field {field} must contain unique strings")
    if not isinstance(manifest["restartRequired"], bool):
        raise ReleaseError("restartRequired must be boolean")

    if not require_payload:
        return
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ReleaseError("Manifest has no files")
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ReleaseError("Invalid manifest file entry")
        path = item["path"]
        if not is_relative_payload_path(path, manifest["archiveRoot"]):
            raise ReleaseError(f"Manifest file path is not relative to archiveRoot: {path}")
        if path in seen:
            raise ReleaseError(f"Duplicate manifest file path: {path}")
        seen.add(path)


def verify_manifest_against_metadata(
    manifest: dict[str, Any], metadata: dict[str, Any]
) -> None:
    validate_manifest_contract(manifest)
    expected = expected_manifest_contract(metadata)
    actual = {field: manifest[field] for field in MTK_CONTRACT_FIELDS}
    if actual != expected:
        raise ReleaseError(
            "Manifest MTK contract does not match package metadata; "
            f"expected={expected}, actual={actual}"
        )
    if manifest.get("archive", {}).get("fileName") != metadata["release"]["assetFileName"]:
        raise ReleaseError("Manifest archive filename does not match package metadata")


def expected_source_files(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    payload = metadata.get("payloadFiles")
    if not isinstance(payload, list) or not payload:
        raise ReleaseError("metadata/package.json has no payloadFiles")
    archive_root = expected_manifest_contract(metadata)["archiveRoot"]
    seen: set[str] = set()
    for item in payload:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ReleaseError("Invalid payload file entry")
        path = item["path"]
        if path in seen:
            raise ReleaseError(f"Duplicate metadata path: {path}")
        if not is_relative_payload_path(path, archive_root):
            raise ReleaseError(f"Invalid metadata payload path: {path}")
        seen.add(path)
    return sorted(payload, key=lambda item: item["path"])


def validate_source(source_root: Path, metadata: dict[str, Any]) -> list[dict[str, Any]]:
    expected = expected_source_files(metadata)
    expected_paths = {item["path"] for item in expected}
    actual_paths = {
        path.relative_to(source_root).as_posix()
        for path in source_root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    missing = sorted(expected_paths - actual_paths)
    extra = sorted(actual_paths - expected_paths)
    if missing or extra:
        raise ReleaseError(f"Source file-set mismatch; missing={missing}, extra={extra}")

    for item in expected:
        path = source_root / item["path"]
        if path.is_symlink():
            raise ReleaseError(f"Symlinks are not allowed: {item['path']}")
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != item["size"]:
            raise ReleaseError(
                f"Size mismatch for {item['path']}: expected {item['size']}, got {size}"
            )
        if digest != item["sha256"]:
            raise ReleaseError(
                f"SHA-256 mismatch for {item['path']}: expected {item['sha256']}, got {digest}"
            )
    return expected


def build_zip(
    archive_path: Path,
    source_root: Path,
    archive_root: str,
    files: list[dict[str, Any]],
) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for item in files:
            member_name = f"{archive_root}/{item['path']}"
            info = zipfile.ZipInfo(member_name, FIXED_ZIP_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            info.internal_attr = 0
            with (source_root / item["path"]).open("rb") as stream:
                archive.writestr(info, stream.read())


def make_manifest(
    metadata: dict[str, Any],
    release_date: str,
    archive_path: Path,
    files: list[dict[str, Any]],
) -> dict[str, Any]:
    contract = expected_manifest_contract(metadata)
    manifest_files = [
        {
            "path": item["path"],
            "size": item["size"],
            "sha256": item["sha256"],
            "variants": item["variants"],
            "required": item["required"],
        }
        for item in files
    ]
    return {
        **contract,
        "releaseDate": release_date,
        "source": metadata["source"],
        "aircraft": metadata["aircraft"],
        "livery": metadata["livery"],
        "rights": metadata["rights"],
        "archive": {
            "fileName": archive_path.name,
            "size": archive_path.stat().st_size,
            "sha256": sha256_file(archive_path),
            "method": metadata["release"]["zipMethod"],
        },
        "files": manifest_files,
        "totals": {
            "fileCount": len(manifest_files),
            "uncompressedBytes": sum(item["size"] for item in manifest_files),
        },
        "validation": {
            "forbiddenPatterns": metadata["forbiddenPatterns"],
        },
    }


def verify_archive(archive_path: Path, manifest: dict[str, Any]) -> None:
    validate_manifest_contract(manifest)
    archive_meta = manifest["archive"]
    if archive_path.name != archive_meta["fileName"]:
        raise ReleaseError("Archive filename does not match manifest")
    if archive_path.stat().st_size != archive_meta["size"]:
        raise ReleaseError("Archive size does not match manifest")
    if sha256_file(archive_path) != archive_meta["sha256"]:
        raise ReleaseError("Archive SHA-256 does not match manifest")

    archive_root = manifest["archiveRoot"]
    expected = {f"{archive_root}/{item['path']}": item for item in manifest["files"]}
    with zipfile.ZipFile(archive_path, "r") as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ReleaseError(f"ZIP CRC check failed: {bad_member}")
        all_infos = archive.infolist()
        roots = {PurePosixPath(info.filename).parts[0] for info in all_infos if info.filename}
        if roots != {archive_root}:
            raise ReleaseError(
                f"ZIP must contain exactly the root {archive_root!r}; found {sorted(roots)}"
            )
        infos = [info for info in all_infos if not info.is_dir()]
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ReleaseError("ZIP contains duplicate member names")
        if set(names) != set(expected):
            missing = sorted(set(expected) - set(names))
            extra = sorted(set(names) - set(expected))
            raise ReleaseError(f"ZIP file-set mismatch; missing={missing}, extra={extra}")
        for info in infos:
            if is_forbidden(info.filename):
                raise ReleaseError(f"Forbidden ZIP member: {info.filename}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise ReleaseError(f"Unexpected compression method: {info.filename}")
            data = archive.read(info.filename)
            item = expected[info.filename]
            if len(data) != item["size"]:
                raise ReleaseError(f"Size mismatch inside ZIP: {info.filename}")
            if sha256_bytes(data) != item["sha256"]:
                raise ReleaseError(f"SHA-256 mismatch inside ZIP: {info.filename}")

    total = sum(item["size"] for item in expected.values())
    if manifest["totals"]["fileCount"] != len(expected):
        raise ReleaseError("Manifest file count is inconsistent")
    if manifest["totals"]["uncompressedBytes"] != total:
        raise ReleaseError("Manifest uncompressed byte total is inconsistent")


def verify_checksum_file(checksum_path: Path, files: list[Path]) -> None:
    expected = {path.name: sha256_file(path) for path in files}
    actual: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, name = line.split("  ", 1)
        except ValueError as error:
            raise ReleaseError(f"Malformed checksum line: {line!r}") from error
        actual[name] = digest
    if actual != expected:
        raise ReleaseError(f"Checksum file mismatch; expected={expected}, actual={actual}")
