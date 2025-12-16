from core.renderer import render_ascii
from analysis.quality import ascii_quality

def find_best_preset(img, presets, charset):
    best_score = -1
    best_name = None

    for name, p in presets.items():
        try:
            art = render_ascii(img, p, charset)
            score = ascii_quality(art)
            if score > best_score:
                best_score = score
                best_name = name
        except Exception:
            continue

    return best_name
