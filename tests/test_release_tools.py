from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from release_common import (  # noqa: E402
    MTK_CONTRACT_FIELDS,
    ReleaseError,
    build_zip,
    expected_manifest_contract,
    expected_source_files,
    load_json,
    make_manifest,
    validate_source,
    verify_archive,
    verify_manifest_against_metadata,
)


class ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata = load_json(REPOSITORY_ROOT / "metadata" / "package.json")

    def test_mtk_contract_has_required_values(self) -> None:
        contract = expected_manifest_contract(self.metadata)
        self.assertEqual(
            contract,
            {
                "schemaVersion": 1,
                "packageType": "livery",
                "packageId": "wahltho.levelup-737ng.livery.lufthansa",
                "packageVersion": "1.0.0",
                "releaseTag": "v1.0.0",
                "channel": "stable",
                "repository": "https://github.com/wahltho/X-Plane-LevelUp-737NG-Lufthansa-Livery",
                "supportedProducts": ["levelup-737ng"],
                "supportedVariants": ["737-700", "737-900ER"],
                "installScope": "aircraftLivery",
                "targetDirectory": "Lufthansa",
                "archiveRoot": "Lufthansa",
                "restartRequired": True,
            },
        )
        self.assertEqual(set(contract), set(MTK_CONTRACT_FIELDS))

    def test_schema_requires_mtk_contract_and_relative_paths(self) -> None:
        schema = json.loads(
            (REPOSITORY_ROOT / "schema" / "release-manifest.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(set(MTK_CONTRACT_FIELDS).issubset(schema["required"]))
        self.assertEqual(schema["properties"]["archiveRoot"]["const"], "Lufthansa")
        self.assertEqual(schema["properties"]["packageVersion"]["const"], "1.0.0")
        self.assertEqual(schema["properties"]["releaseTag"]["const"], "v1.0.0")
        pattern = schema["properties"]["files"]["items"]["properties"]["path"][
            "pattern"
        ]
        self.assertIn("?!Lufthansa/", pattern)

    def test_release_file_names_are_stable(self) -> None:
        self.assertEqual(
            self.metadata["release"]["assetFileName"],
            "X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip",
        )
        self.assertEqual(
            self.metadata["release"]["manifestFileName"],
            "X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.manifest.json",
        )

    def test_canonical_payload_is_unchanged(self) -> None:
        source_root = REPOSITORY_ROOT / "src" / "Lufthansa"
        files = validate_source(source_root, self.metadata)
        self.assertEqual(len(files), 9)
        self.assertEqual(sum(item["size"] for item in files), 128058204)

    def test_manifest_paths_are_relative_to_lufthansa(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / self.metadata["release"]["assetFileName"]
            archive_path.write_bytes(b"placeholder")
            manifest = make_manifest(
                self.metadata,
                "2026-06-26",
                archive_path,
                expected_source_files(self.metadata),
            )
        verify_manifest_against_metadata(manifest, self.metadata)
        self.assertTrue(
            all(not item["path"].startswith("Lufthansa/") for item in manifest["files"])
        )
        self.assertIn(
            "objects/737_70NG/737_70NG_fuselage.png",
            {item["path"] for item in manifest["files"]},
        )

    def test_archive_has_exactly_one_lufthansa_root(self) -> None:
        payload = b"livery"
        file_entry = {
            "path": "objects/payload.bin",
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "variants": ["737-700"],
            "required": True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            (source / "objects").mkdir(parents=True)
            (source / file_entry["path"]).write_bytes(payload)
            archive_path = root / self.metadata["release"]["assetFileName"]
            build_zip(archive_path, source, "Lufthansa", [file_entry])
            manifest = make_manifest(
                self.metadata, "2026-06-26", archive_path, [file_entry]
            )
            verify_archive(archive_path, manifest)

    def test_archive_rejects_a_different_root(self) -> None:
        payload = b"livery"
        file_entry = {
            "path": "payload.bin",
            "size": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "variants": ["737-700"],
            "required": True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / file_entry["path"]).write_bytes(payload)
            archive_path = root / self.metadata["release"]["assetFileName"]
            build_zip(archive_path, source, "WrongRoot", [file_entry])
            manifest = make_manifest(
                self.metadata, "2026-06-26", archive_path, [file_entry]
            )
            with self.assertRaises(ReleaseError):
                verify_archive(archive_path, manifest)

    def test_manifest_rejects_archive_prefixed_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = Path(temporary) / self.metadata["release"]["assetFileName"]
            archive_path.write_bytes(b"placeholder")
            manifest = make_manifest(
                self.metadata,
                "2026-06-26",
                archive_path,
                expected_source_files(self.metadata),
            )
        manifest["files"][0]["path"] = f"Lufthansa/{manifest['files'][0]['path']}"
        with self.assertRaises(ReleaseError):
            verify_manifest_against_metadata(manifest, self.metadata)


if __name__ == "__main__":
    unittest.main()
