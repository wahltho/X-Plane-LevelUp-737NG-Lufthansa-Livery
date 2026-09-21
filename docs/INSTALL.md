# Installation

## Requirements

- X-Plane 12
- A compatible LevelUp 737NG Series installation containing the 737-700 and/or
  737-900ER aircraft

## Install the combined package

The release archive has exactly one top-level directory: `Lufthansa`.

Extract or copy that directory to:

`<LevelUp aircraft folder>/liveries/Lufthansa`

For an installation whose LevelUp directory is named `LU 737NG Series`, the
result is:

`<X-Plane>/Aircraft/LU 737NG Series/liveries/Lufthansa`

Older LevelUp distributions may use a different aircraft-folder name, such as
`737NG Series_V2.S1`. The stable part of the target is always
`liveries/Lufthansa` inside the LevelUp aircraft folder.

The same installed `Lufthansa` folder serves both supported variants. Do not
split or rename its `objects/737_70NG` and `objects/737_9ENG` directories.

## Expected layout

```text
<LevelUp aircraft folder>/
└── liveries/
    └── Lufthansa/
        ├── 737_70NG_icon11.png
        ├── 737_70NG_icon11_thumb.png
        ├── 737_9ENG_icon11.png
        ├── 737_9ENG_icon11_thumb.png
        └── objects/
            ├── 737_70NG/
            │   └── 737_70NG_fuselage.png
            ├── 737_9ENG/
            │   ├── 737_9ENG_fuselage.png
            │   └── 737_9ENG_fuselage2.png
            ├── 737cfm56.dds
            └── 737tail.png
```

No `.cfg` file belongs to this release. Aircraft-specific normal maps and lit
textures are inherited from the LevelUp aircraft installation.

## Platform notes

The package uses portable relative paths and works with the same directory
layout on macOS, Windows, and Linux. Preserve filename case on every platform;
Linux filesystems are normally case-sensitive.
