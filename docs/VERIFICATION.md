# Package verification

## Automated verification

Run from the repository root after building:

```sh
python3 scripts/verify_release.py \
  dist/X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip \
  dist/X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.manifest.json \
  --checksums dist/SHA256SUMS.txt
```

A successful run exits with status 0 and prints a concise summary. Any missing,
extra, renamed, damaged, or forbidden archive member causes a nonzero exit.
The verifier also rejects missing or inconsistent MTK contract fields and any
manifest file path that includes the `Lufthansa/` archive-root prefix.

## Manual review

Before publication, also confirm:

- the ZIP has exactly one root directory named `Lufthansa`;
- every manifest `files[].path` is relative to that root;
- both aircraft variants have their two icon files;
- both aircraft-specific fuselage areas are present;
- the shared engine and tail textures are present only once;
- no `.cfg`, `.DS_Store`, `._*`, or `__MACOSX` entry is present;
- extraction produces the layout shown in `docs/INSTALL.md`;
- the livery is visually checked in X-Plane for both supported variants.

Archive validation proves package integrity and reproducibility. It does not
prove that X-Plane loaded the livery or that every surface is visually correct;
those are separate simulator checks.
