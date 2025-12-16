import numpy as np

def analyze_tile_fast(tile: np.ndarray):
    brightness = float(tile.mean())
    contrast = float(tile.std())
    edge = float(np.mean(np.abs(np.diff(tile, axis=0)))) if tile.shape[0] > 1 else 0.0
    return brightness, contrast, edge
