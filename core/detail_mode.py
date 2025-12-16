def apply_detail_mode(brightness, contrast, edge, mode: str):
    """
    Modifies tile metrics depending on detail mode
    """

    if mode == "anime":
        # сильні краї, приглушена яскравість
        brightness *= 0.85
        edge *= 1.4

    elif mode == "lineart":
        brightness *= 0.7
        edge *= 1.8

    elif mode == "soft":
        edge *= 0.6
        contrast *= 0.7

    # photo = default (нічого не робимо)

    return brightness, contrast, edge
