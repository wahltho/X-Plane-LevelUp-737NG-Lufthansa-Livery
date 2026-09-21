# Supported variants

| File | 737-700 | 737-900ER | Purpose |
|---|:---:|:---:|---|
| `737_70NG_icon11.png` | Yes | No | Aircraft selection icon |
| `737_70NG_icon11_thumb.png` | Yes | No | Icon thumbnail |
| `737_9ENG_icon11.png` | No | Yes | Aircraft selection icon |
| `737_9ENG_icon11_thumb.png` | No | Yes | Icon thumbnail |
| `objects/737_70NG/737_70NG_fuselage.png` | Yes | No | 737-700 fuselage |
| `objects/737_9ENG/737_9ENG_fuselage.png` | No | Yes | 737-900ER fuselage |
| `objects/737_9ENG/737_9ENG_fuselage2.png` | No | Yes | Additional 737-900ER fuselage section |
| `objects/737cfm56.dds` | Yes | Yes | Shared engine texture |
| `objects/737tail.png` | Yes | Yes | Shared tail texture |

The depicted registration is `D-ABXN` for both variants. The package is an
unofficial fictional application of the Lufthansa design to these LevelUp
aircraft variants.

One combined package is intentional: the aircraft-specific files already live
in distinct subdirectories, while the engine and tail textures are shared.
Separate ZIP files would duplicate shared assets and create two sources for the
same livery.
