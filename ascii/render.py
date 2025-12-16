import numpy as np
from ascii.adaptive import pick_charset


def to_ascii(img, charset_map, adaptive=False):
    arr = np.array(img)
    h, w = arr.shape

    lines = []
    for y in range(h):
        row = ""
        for x in range(w):
            v = arr[y, x]

            if adaptive:
                chars = pick_charset(v, charset_map)
            else:
                chars = charset_map["base"]

            idx = int(v / 255 * (len(chars) - 1))
            row += chars[idx]

        lines.append(row)

    return "\n".join(lines)
