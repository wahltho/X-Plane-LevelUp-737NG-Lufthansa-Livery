# Lufthansa Livery for the LevelUp 737NG Series

Unofficial Lufthansa freeware livery by **wahltho** for these LevelUp aircraft:

- Boeing 737-700 (`737_70NG`)
- Boeing 737-900ER (`737_9ENG`)

Both variants are supplied in one directly installable `Lufthansa` folder. The
shared registration is `D-ABXN`; this is an unofficial, fictional application
for these variants.

## Installation

1. Download the release ZIP.
2. Extract the contained `Lufthansa` folder.
3. Copy that folder to:

   `<LevelUp aircraft folder>/liveries/Lufthansa`

The resulting layout must contain the icon files directly below `Lufthansa`
and the aircraft textures below `Lufthansa/objects`. See
[`docs/INSTALL.md`](docs/INSTALL.md) for the complete layout and platform notes.

## Repository layout

- `src/Lufthansa/` is the only canonical package source.
- `metadata/package.json` describes every required source file and its SHA-256.
- `scripts/` builds and verifies deterministic release assets.
- `tests/` validates the MTK contract, canonical payload, and archive layout.
- `schema/` contains the JSON Schema for generated release manifests.
- `docs/` contains installation, variant, provenance, release, and verification
  documentation.
- `dist/` is generated locally and is intentionally not version controlled.

The published X-Plane.org ZIP is retained as provenance, not as a second source
tree. Its nine functional files are represented byte-for-byte in `src`; macOS
metadata from the original archive is deliberately excluded.

## Release asset

The planned first repository release is `v1.0.0` with this asset:

`X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip`

The ZIP root is `Lufthansa/`, so the package can be extracted directly into the
LevelUp `liveries` directory. The external manifest and `SHA256SUMS.txt` are
generated alongside the archive.

## Maintenance Toolkit contract

The generated manifest identifies this package as
`wahltho.levelup-737ng.livery.lufthansa`, targets the Maintenance Toolkit
product `levelup-737ng`, and uses the `aircraftLivery` install scope. Manifest
file paths are relative to the declared `Lufthansa` archive root; the ZIP itself
still contains that root directory. See
[`docs/MTK_INTEGRATION.md`](docs/MTK_INTEGRATION.md) for the complete contract.

## Rights and trademarks

The livery artwork is authored and maintained by **wahltho** and is distributed
as freeware. It is not open-source software; see
[`LICENSE-ASSETS.md`](LICENSE-ASSETS.md). No separate software license has been
selected for the packaging utilities; see
[`LICENSE-CODE.md`](LICENSE-CODE.md).

This project is not affiliated with or endorsed by Lufthansa, Boeing, LevelUp,
Laminar Research, or X-Plane. Product names and trademarks belong to their
respective owners. See [`NOTICE.md`](NOTICE.md).

## Support

When reporting a package problem, include the release version, operating
system, LevelUp aircraft version, affected aircraft variant, and the result of
the verification command documented in [`docs/VERIFICATION.md`](docs/VERIFICATION.md).
