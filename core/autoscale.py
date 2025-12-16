def auto_scale(img, font_ratio=0.55, target_width=160):
    w, h = img.size
    aspect = h / w
    scale = max(1, int((w / target_width) * font_ratio * aspect))
    return scale
