import numpy as np
from core.tile_analysis_fast import analyze_tile_fast


def compute_auto_scale(
    img,
    min_scale=0.05,
    max_scale=0.4
):
    """
    Smart auto-scale based on image detail density
    """

    arr = np.array(img)

    h, w = arr.shape[:2]

    # sample grid (fast)
    step = max(4, min(w, h) // 64)
    edges = []

    for y in range(0, h, step):
        for x in range(0, w, step):
            tile = arr[y:y+step, x:x+step]
            if tile.size == 0:
                continue
            _, _, edge = analyze_tile_fast(tile)
            edges.append(edge)

    if not edges:
        return 0.15

    edge_density = sum(edges) / (len(edges) * 255.0)

    # base scale from size
    size_factor = min(w, h) / 800
    base_scale = 0.18 / max(size_factor, 0.4)

    # detail adjustment
    detail_factor = 1.0 + edge_density * 1.2

    scale = base_scale * detail_factor

    return max(min_scale, min(max_scale, scale))
