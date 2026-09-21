# Maintenance Toolkit integration contract

The generated release manifest exposes these stable top-level fields for the
Maintenance Toolkit:

| Field | Value |
|---|---|
| `schemaVersion` | `1` |
| `packageType` | `livery` |
| `packageId` | `wahltho.levelup-737ng.livery.lufthansa` |
| `packageVersion` | `1.0.0` |
| `releaseTag` | `v1.0.0` |
| `channel` | `stable` |
| `repository` | `https://github.com/wahltho/X-Plane-LevelUp-737NG-Lufthansa-Livery` |
| `supportedProducts` | `["levelup-737ng"]` |
| `supportedVariants` | `["737-700", "737-900ER"]` |
| `installScope` | `aircraftLivery` |
| `targetDirectory` | `Lufthansa` |
| `archiveRoot` | `Lufthansa` |
| `restartRequired` | `true` |

## Path contract

Every `files[].path` is relative to `archiveRoot`. Examples:

- `737_70NG_icon11.png`
- `objects/737_70NG/737_70NG_fuselage.png`

The physical ZIP member names are formed as `archiveRoot + "/" + path`, so the
same examples appear in the archive as:

- `Lufthansa/737_70NG_icon11.png`
- `Lufthansa/objects/737_70NG/737_70NG_fuselage.png`

The ZIP contains exactly one root directory, `Lufthansa/`. An installer using
the `aircraftLivery` scope should install that directory below the selected
LevelUp aircraft's `liveries` directory. `targetDirectory` is the final folder
name and must not be appended twice.

## Release files

- `X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.zip`
- `X-Plane-LevelUp-737NG-Lufthansa-Livery-v1.0.0.manifest.json`
- `SHA256SUMS.txt`

The manifest is external to the ZIP so it can contain the final ZIP size and
SHA-256 without creating a self-reference. `SHA256SUMS.txt` covers both the ZIP
and the external manifest.
