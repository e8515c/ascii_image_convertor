def compute_tile_size(preset: dict):
    t = int(preset.get("tile", 1))
    return max(1, t), max(1, t)
