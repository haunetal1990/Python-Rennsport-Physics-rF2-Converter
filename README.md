# Python Rennsport Physics rF2 Converter

Convert the car physics of **Rennsport** into **rFactor 2** files – `.hdv`, chassis, engine, gears, tyres (`.tbc` + `.tgm`) and electric motors for hybrid/EV cars.

> ⚠️ **Only works with the game version before November 2025.**
>
> You can download this version via the Steam console:
> 1. Press `Win + R` and enter `steam://open/console`
> 2. In the Steam console, run:
>    ```
>    download_depot 2077750 2077751 8977428734768596951
>    ```

## Requirements

- Windows, Python 3.8+ (no extra packages needed)
- [`rennsport_unpak.py`](https://github.com/haunetal1990/Python-Rennsport-Car-Extractor) from the **Python Rennsport Car Extractor** and the game's **AES key**

## 1. Unpack the physics

Only the physics configs are needed (fast and small):

```
python rennsport_unpak.py "C:\Path\To\Rennsport-Windows.pak" --filter "*/Blueprints/Configs/*"
```

Leave out `--filter` to unpack everything (also needed for the Blender extractor).

## 2. Convert to rFactor 2

```
python rennsport_rf2.py BMW_M4_GT3_2022 -o rF2_Export
```

On the first start you are asked for the unpacked folder (saved to `rennsport_rf2.ini`).<br />
Result: `rF2_Export\BMW_M4_GT3_2022\` with `.hdv`, `_Chassis.ini`, `_Engine.ini`, `_Gears.ini`, `.tbc`, `.tgm` (+ `_Motor.ini` for hybrid/EV).

| Option | |
|---|---|
| `--list` | show all cars |
| `--all` | convert all cars |
| `<name> <name> …` | several cars at once (part of the name is enough) |
| `"<path to car folder>"` | convert a specific physics folder (`…\Content\Blueprints\Configs\Cars\<Brand>\<Car>`) |
| `-o <folder>` | output folder (default `rF2_Export`) |
| `--content <folder>` | use another unpacked folder |
| `--json` | additionally dump all raw Rennsport values |

## Notes

- Values without an rF2 counterpart (balance of performance, battery curves, …) are kept as comments.
- Pit menu and plugin sections don't exist in Rennsport and use rF2 defaults.
- Rennsport's own tyre lookup tables are left out – rF2 calculates them on first load.
- AES key and game files are **not** included.
- Not affiliated with the developers of Rennsport or rFactor 2. Use only with a legally owned copy of the game.
