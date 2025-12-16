def pick_charset_subset(charset: str, brightness: float, contrast: float, edge: float):
    n = len(charset)

    contrast_n = min(contrast / 64.0, 1.0)
    edge_n = min(edge / 32.0, 1.0)
    complexity = max(contrast_n, edge_n)

    if complexity < 0.25:
        size = int(n * 0.35)
    elif complexity < 0.5:
        size = int(n * 0.55)
    elif complexity < 0.75:
        size = int(n * 0.75)
    else:
        size = n

    size = max(2, min(size, len(charset)))
    return charset[:size]

