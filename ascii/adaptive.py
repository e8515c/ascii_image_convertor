def pick_charset(brightness, charsets):
    if brightness < 85:
        return charsets["dense"]
    elif brightness < 170:
        return charsets["mid"]
    else:
        return charsets["light"]
