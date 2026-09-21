# Maintainer release procedure

Release creation, tagging, pushing, and publication are separate maintainer
decisions. The commands below only prepare and verify local assets.

## 1. Review metadata

- Confirm `version` in `metadata/package.json`.
- Confirm the changelog entry.
- Confirm all source file sizes and SHA-256 values.
- Choose the actual release date in `YYYY-MM-DD` format.

## 2. Build

From the repository root:

```sh
python3 scripts/build_release.py --release-date YYYY-MM-DD --check-reproducible
```

The command creates `dist/` containing:

- `X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip`
- `X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.manifest.json`
- `SHA256SUMS.txt`

PNG and DDS files are already compressed formats. The builder therefore uses
stored ZIP members instead of platform-dependent recompression. It fixes member
order, timestamps, and Unix file attributes for reproducible output.

## 3. Verify

```sh
python3 scripts/verify_release.py \
  dist/X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip \
  dist/X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.manifest.json \
  --checksums dist/SHA256SUMS.txt
```

The verifier reopens the ZIP and checks its complete file set, root directory,
per-file sizes and SHA-256 values, archive size and SHA-256, total uncompressed
size, and forbidden metadata.

## 4. Prepare CI artifacts

The manual `Prepare release assets` workflow performs the same build and
verification and uploads a workflow artifact. It does not create a tag or a
GitHub Release. Publication remains a distinct, explicit step.
