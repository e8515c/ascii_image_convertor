import configparser
from pathlib import Path

PRESETS_FILE = Path(__file__).parent / "presets.ini"


def load_all():
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str  # preserve case
    cfg.read(PRESETS_FILE, encoding="utf-8")

    # ---------- CHARSETS ----------
    charsets = {}
    if cfg.has_section("CHARSETS"):
        for name, value in cfg["CHARSETS"].items():
            charsets[name] = value

    # ---------- PRESETS ----------
    presets = {}
    for section in cfg.sections():
        if not section.startswith("PRESET:"):
            continue

        name = section.split("PRESET:", 1)[1]
        p = {}

        for k, v in cfg[section].items():
            if k in ("scale", "contrast", "brightness", "sharpness"):
                p[k] = float(v)
            elif k in ("tile", "width"):
                p[k] = int(v)
            elif k == "invert":
                p[k] = v.lower() == "true"
            else:
                p[k] = v

        presets[name] = p

    return charsets, presets


def save_preset(name: str, preset: dict):
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str
    cfg.read(PRESETS_FILE, encoding="utf-8")

    section = f"PRESET:{name}"
    if not cfg.has_section(section):
        cfg.add_section(section)

    for k, v in preset.items():
        cfg.set(section, k, str(v))

    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def delete_preset(name: str):
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str
    cfg.read(PRESETS_FILE, encoding="utf-8")

    section = f"PRESET:{name}"
    if cfg.has_section(section):
        cfg.remove_section(section)

    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)
