def export_txt(path, ascii_art):
    with open(path, "w", encoding="utf-8") as f:
        f.write(ascii_art)

def export_md(path, ascii_art):
    with open(path, "w", encoding="utf-8") as f:
        f.write("```\n")
        f.write(ascii_art)
        f.write("\n```")
