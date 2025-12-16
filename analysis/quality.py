import numpy as np

def ascii_quality(ascii_art: str) -> float:
    """
    Heuristic quality score:
    - variety of symbols
    - local contrast
    """
    lines = ascii_art.splitlines()
    if not lines:
        return 0.0

    chars = "".join(lines)
    unique = len(set(chars))

    # contrast approximation
    diffs = 0
    for y in range(len(lines) - 1):
        for x in range(min(len(lines[y]), len(lines[y+1]))):
            diffs += abs(ord(lines[y][x]) - ord(lines[y+1][x]))

    return unique * 2 + diffs * 0.01
