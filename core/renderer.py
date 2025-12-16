import numpy as np
from PIL import Image

from image.preprocess import preprocess
from core.supersample import supersample_image
from core.tile_analysis_fast import analyze_tile_fast
from core.charset_picker import pick_charset_subset


# ---------- AUTO SCALE ----------

def compute_auto_scale(img: Image.Image, target_cols=160):
    w, _ = img.size
    return max(0.01, min(1.0, target_cols / float(w)))


# ---------- RENDER ----------

def render_ascii(
    img: Image.Image,
    preset: dict,
    charset: str,
    supersample: int = 1,
    adaptive: bool = True
):
    # ---------- preprocess ----------
    img = preprocess(img, preset)

    # ---------- supersampling ----------
    img = supersample_image(img, supersample)

    # ---------- scale ----------
    if preset.get("auto_scale", False):
        scale = compute_auto_scale(img)
    else:
        scale = float(preset.get("scale", 0.15))

    w, h = img.size
    new_w = max(1, int(w * scale))
    aspect = h / w
    new_h = max(1, int(new_w * aspect * 0.5))

    img = img.resize((new_w, new_h), Image.BICUBIC)
    arr = np.array(img)

    # ---------- parameters ----------
    tile = max(1, int(preset.get("tile", 1)))
    gamma = float(preset.get("gamma", 1.6))
    edge_bias = float(preset.get("edge_bias", 0.15))

    out_lines = []

    # ---------- main loop ----------
    for y in range(0, arr.shape[0], tile):
        line = []
        for x in range(0, arr.shape[1], tile):
            tile_arr = arr[y:y + tile, x:x + tile]
            if tile_arr.size == 0:
                continue

            brightness, contrast, edge = analyze_tile_fast(tile_arr)

            # --- brightness base ---
            b = brightness / 255.0
            b = b ** (1.0 / gamma)

            # --- soft edge boost ---
            e = min(edge / 255.0, 1.0)
            b += e * edge_bias

            # --- tiny contrast influence (very subtle) ---
            c = min(contrast / 128.0, 1.0)
            b -= c * 0.05

            b = max(0.0, min(1.0, b))

            # adaptive charset
            if adaptive:
                local = pick_charset_subset(
                    charset,
                    brightness,
                    contrast,
                    edge
                )
            else:
                local = charset

            if not local or len(local) < 2:
                local = charset[:2] if len(charset) >= 2 else "##"

            idx = int(b * (len(local) - 1))
            idx = max(0, min(idx, len(local) - 1))

            line.append(local[idx])

        out_lines.append("".join(line))

    return "\n".join(out_lines)
