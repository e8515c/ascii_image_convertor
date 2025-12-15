# ASCII Converter e8515c PRO
# Added:
# 1) Supersampling (2x/3x downscale for extra sharpness)
# 2) Export TXT / HTML
# 3) More presets (photos/anime/contrast)
# Presets never lock manual tuning; user presets persist (presets.json)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import json, os

PRESET_FILE = "presets.json"

# ===================== CHARSETS =====================
CHARSETS = {
    "Emoji Dense": " ⠂⠆⠖⠶⠷⠿⣿",
    "Ultra Dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Blocks": " ░▒▓█",
    "Dots": " .:-=+*#%@",
}

# ===================== BUILTIN PRESETS (MORE) =====================
BUILTIN_PRESETS = {
    # --- Core ---
    "e8515c Ultra": dict(w=150,g=1.25,c=1.45,s=1.9,e=1.6,inv=False,thr=False,col=False,cs="Emoji Dense",ss=2),
    "High Detail": dict(w=170,g=1.20,c=1.55,s=2.1,e=1.9,inv=False,thr=False,col=False,cs="Ultra Dense",ss=2),
    "High Contrast": dict(w=160,g=1.40,c=1.80,s=2.0,e=1.8,inv=False,thr=True,col=False,cs="Ultra Dense",ss=2),
    "Minimal": dict(w=100,g=1.00,c=1.00,s=1.0,e=1.0,inv=False,thr=False,col=False,cs="Blocks",ss=1),

    # --- Anime ---
    "Anime Soft": dict(w=140,g=1.15,c=1.25,s=1.4,e=1.2,inv=False,thr=False,col=False,cs="Emoji Dense",ss=2),
    "Anime Line": dict(w=150,g=1.35,c=1.60,s=2.2,e=2.0,inv=False,thr=True,col=False,cs="Ultra Dense",ss=2),
    "Anime Dark": dict(w=160,g=1.45,c=1.70,s=2.0,e=1.8,inv=False,thr=True,col=False,cs="Blocks",ss=2),
    "Anime Clean": dict(w=145,g=1.20,c=1.35,s=1.6,e=1.4,inv=False,thr=False,col=False,cs="Dots",ss=2),

    # --- Photo ---
    "Photo Soft": dict(w=120,g=1.00,c=1.10,s=1.0,e=1.0,inv=False,thr=False,col=False,cs="Blocks",ss=1),
    "Photo Sharp": dict(w=135,g=1.20,c=1.40,s=1.8,e=1.5,inv=False,thr=False,col=False,cs="Ultra Dense",ss=2),
    "Photo HDR": dict(w=150,g=1.10,c=1.60,s=2.0,e=1.8,inv=False,thr=False,col=False,cs="Ultra Dense",ss=3),

    # --- Extras ---
    "Invert Clean": dict(w=140,g=1.20,c=1.40,s=1.6,e=1.4,inv=True,thr=False,col=False,cs="Emoji Dense",ss=2),
    "Color ASCII": dict(w=120,g=1.10,c=1.20,s=1.3,e=1.2,inv=False,thr=False,col=True,cs="Emoji Dense",ss=2),
}

# ===================== IMAGE CORE =====================
def unsharp(img, amount=1.5, radius=1.0):
    blur = img.filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(img, blur, 1-amount)

def adaptive_threshold(arr):
    mean = arr.mean()
    return np.where(arr > mean, 255, 0).astype(np.uint8)

def supersample_resize(img, target_w, ss):
    if ss <= 1:
        return img.resize((target_w, int(img.height/img.width*target_w*0.55)), Image.LANCZOS)
    big_w = target_w * ss
    big = img.resize((big_w, int(img.height/img.width*big_w*0.55)), Image.LANCZOS)
    return big.resize((target_w, int(big.height/ss)), Image.LANCZOS)

def preprocess(img, st):
    color_img = supersample_resize(img, st["w"], st.get("ss",1))
    gray = color_img.convert("L")

    if st["g"] != 1.0:
        lut = [pow(i/255, 1/st["g"])*255 for i in range(256)]
        gray = gray.point(lut)

    gray = ImageEnhance.Contrast(gray).enhance(st["c"])
    gray = ImageEnhance.Sharpness(gray).enhance(st["s"])

    if st["e"] > 1.0:
        gray = unsharp(gray, st["e"], 1.0)

    arr = np.array(gray)
    if st["thr"]:
        arr = adaptive_threshold(arr)

    if st["inv"]:
        arr = 255 - arr

    return arr, np.array(color_img)

def ascii_from_array(arr, charset):
    chars = CHARSETS[charset]
    scale = (len(chars)-1)/255
    return "\n".join("".join(chars[int(px*scale)] for px in row) for row in arr)

def color_ascii(arr, col, charset):
    chars = CHARSETS[charset]
    scale = (len(chars)-1)/255
    out=[]
    for y,row in enumerate(arr):
        line=[]
        for x,px in enumerate(row):
            r,g,b = col[y,x]
            ch = chars[int(px*scale)]
            line.append(f"\033[38;2;{r};{g};{b}m{ch}")
        out.append("".join(line)+"\033[0m")
    return "\n".join(out)

def ascii_html(arr, col, charset):
    chars = CHARSETS[charset]
    scale = (len(chars)-1)/255
    rows=[]
    for y,row in enumerate(arr):
        line=[]
        for x,px in enumerate(row):
            r,g,b = col[y,x]
            ch = chars[int(px*scale)]
            line.append(f"<span style='color:rgb({r},{g},{b})'>{ch}</span>")
        rows.append("".join(line))
    body = "<br>".join(rows)
    return f"<html><body style='background:#111;font-family:monospace;white-space:pre'>{body}</body></html>"

# ===================== GUI =====================
class App:
    def __init__(s, r):
        s.r=r; r.title("ASCII Converter e8515c"); r.geometry("1920x1080")
        s.img=None; s.user={}
        s.load_user(); s.ui()

    def ui(s):
        p=ttk.Panedwindow(s.r,orient="horizontal"); p.pack(fill="both",expand=1)
        L=ttk.Frame(p,width=320); R=ttk.Frame(p); p.add(L); p.add(R,weight=1)

        ttk.Button(L,text="Load Image",command=s.load).pack(fill="x")
        ttk.Button(L,text="Auto Preset",command=s.auto).pack(fill="x",pady=3)

        s.pv=tk.StringVar()
        s.pc=ttk.Combobox(L,textvariable=s.pv,state="readonly")
        s.refresh_presets(); s.pc.pack(fill="x")
        s.pc.bind("<<ComboboxSelected>>",s.apply)

        ttk.Button(L,text="Save Preset",command=s.save_p).pack(fill="x",pady=2)
        ttk.Button(L,text="Delete Preset",command=s.del_p).pack(fill="x")

        s.ctrl={}
        def sl(n,a,b,d,st=0.05):
            ttk.Label(L,text=n).pack()
            v=tk.DoubleVar(value=d)
            ttk.Scale(L,from_=a,to=b,variable=v,command=lambda e:s.render()).pack(fill="x")
            s.ctrl[n]=v
        sl("Width",60,260,150,1)
        sl("Gamma",0.5,2.5,1.25)
        sl("Contrast",0.5,3.0,1.45)
        sl("Sharpness",0.5,3.0,1.9)
        sl("Edge",1.0,3.0,1.6)

        ttk.Label(L,text="Supersampling").pack()
        s.ss=tk.IntVar(value=2)
        ttk.Combobox(L,textvariable=s.ss,values=[1,2,3],state="readonly").pack(fill="x")

        s.inv=tk.BooleanVar(); ttk.Checkbutton(L,text="Invert",variable=s.inv,command=s.render).pack()
        s.thr=tk.BooleanVar(); ttk.Checkbutton(L,text="Adaptive Threshold",variable=s.thr,command=s.render).pack()
        s.col=tk.BooleanVar(); ttk.Checkbutton(L,text="Color ASCII",variable=s.col,command=s.render).pack()

        s.cs=tk.StringVar(value="Emoji Dense")
        ttk.Combobox(L,textvariable=s.cs,values=list(CHARSETS),state="readonly").pack(fill="x")

        ttk.Button(L,text="Render",command=s.render).pack(fill="x",pady=6)

        # Export
        ttk.Button(L,text="Export TXT",command=s.export_txt).pack(fill="x")
        ttk.Button(L,text="Export HTML",command=s.export_html).pack(fill="x")

        s.txt=tk.Text(R,wrap="none",font=("Consolas",7),bg="#111",fg="#eee")
        s.txt.pack(fill="both",expand=1)
        ttk.Button(R,text="Copy",command=s.copy).pack(fill="x")

    def state(s):
        return dict(
            w=int(s.ctrl["Width"].get()),
            g=s.ctrl["Gamma"].get(),
            c=s.ctrl["Contrast"].get(),
            s=s.ctrl["Sharpness"].get(),
            e=s.ctrl["Edge"].get(),
            inv=s.inv.get(),
            thr=s.thr.get(),
            col=s.col.get(),
            cs=s.cs.get(),
            ss=s.ss.get(),
        )

    def load(s):
        p=filedialog.askopenfilename(filetypes=[("Images","*.png *.jpg *.jpeg *.webp")])
        if p: s.img=Image.open(p); s.render()

    def render(s):
        if s.img is None: return
        st=s.state()
        arr,col=preprocess(s.img,st)
        out = color_ascii(arr,col,st["cs"]) if st["col"] else ascii_from_array(arr,st["cs"])
        s.txt.delete("1.0","end"); s.txt.insert("end",out)

    def copy(s):
        s.r.clipboard_clear(); s.r.clipboard_append(s.txt.get("1.0","end"))

    # -------- Export --------
    def export_txt(s):
        if s.img is None: return
        p=filedialog.asksaveasfilename(defaultextension=".txt")
        if not p: return
        with open(p,"w",encoding="utf8") as f:
            f.write(s.txt.get("1.0","end"))

    def export_html(s):
        if s.img is None: return
        p=filedialog.asksaveasfilename(defaultextension=".html")
        if not p: return
        st=s.state(); arr,col=preprocess(s.img,st)
        html = ascii_html(arr,col,st["cs"])
        with open(p,"w",encoding="utf8") as f: f.write(html)

    # -------- presets --------
    def refresh_presets(s):
        s.pc["values"]=list(BUILTIN_PRESETS)+list(s.user)
        if s.pc["values"]: s.pc.current(0)

    def apply(s,_):
        n=s.pv.get(); d=BUILTIN_PRESETS.get(n) or s.user.get(n)
        if not d: return
        s.ctrl["Width"].set(d["w"])
        s.ctrl["Gamma"].set(d["g"])
        s.ctrl["Contrast"].set(d["c"])
        s.ctrl["Sharpness"].set(d["s"])
        s.ctrl["Edge"].set(d["e"])
        s.inv.set(d["inv"]); s.thr.set(d["thr"]); s.col.set(d["col"])
        s.cs.set(d["cs"]); s.ss.set(d.get("ss",1))
        s.render()

    def save_p(s):
        n=simpledialog.askstring("Save preset","Name")
        if not n: return
        s.user[n]=s.state(); s.save_user(); s.refresh_presets()

    def del_p(s):
        n=s.pv.get()
        if n in s.user:
            del s.user[n]; s.save_user(); s.refresh_presets()

    def auto(s):
        if s.img is None: return
        arr=np.array(s.img.convert("L")); c=arr.std()
        name = "High Contrast" if c>70 else "Anime Line" if c>50 else "e8515c Ultra"
        s.pv.set(name); s.apply(None)

    def load_user(s):
        if os.path.exists(PRESET_FILE):
            with open(PRESET_FILE,"r",encoding="utf8") as f: s.user=json.load(f)

    def save_user(s):
        with open(PRESET_FILE,"w",encoding="utf8") as f: json.dump(s.user,f,indent=2)

# =====================
if __name__=="__main__":
    r=tk.Tk(); App(r); r.mainloop()
