import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import json, os, math

PRESET_FILE = "presets.json"

# ===================== CHARSETS =====================
CHARSETS = {
    "Emoji Dense": " ⠂⠆⠖⠶⠷⠿⣿",
    "Ultra Dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Blocks": " ░▒▓█"
}

# ===================== BUILTIN PRESETS (10) =====================
BUILTIN_PRESETS = {
    "e8515c Ultra": dict(w=150,g=1.25,c=1.45,s=1.9,e=1.6,inv=False,thr=False,col=False,cs="Emoji Dense"),
    "Anime Soft": dict(w=140,g=1.15,c=1.25,s=1.4,e=1.2,inv=False,thr=False,col=False,cs="Emoji Dense"),
    "Anime Line": dict(w=150,g=1.35,c=1.6,s=2.2,e=2.0,inv=False,thr=True,col=False,cs="Ultra Dense"),
    "Anime Dark": dict(w=160,g=1.45,c=1.7,s=2.0,e=1.8,inv=False,thr=True,col=False,cs="Blocks"),
    "Photo Soft": dict(w=120,g=1.0,c=1.1,s=1.0,e=1.0,inv=False,thr=False,col=False,cs="Blocks"),
    "Photo Sharp": dict(w=130,g=1.2,c=1.4,s=1.8,e=1.5,inv=False,thr=False,col=False,cs="Ultra Dense"),
    "High Contrast": dict(w=150,g=1.4,c=1.8,s=2.0,e=1.8,inv=False,thr=True,col=False,cs="Ultra Dense"),
    "Minimal": dict(w=100,g=1.0,c=1.0,s=1.0,e=1.0,inv=False,thr=False,col=False,cs="Blocks"),
    "Invert Clean": dict(w=140,g=1.2,c=1.4,s=1.6,e=1.4,inv=True,thr=False,col=False,cs="Emoji Dense"),
    "Color ASCII": dict(w=120,g=1.1,c=1.2,s=1.3,e=1.2,inv=False,thr=False,col=True,cs="Emoji Dense"),
}

# ===================== IMAGE CORE =====================
def unsharp(img, amount=1.5, radius=1.0):
    blur = img.filter(ImageFilter.GaussianBlur(radius))
    return Image.blend(img, blur, 1-amount)

def adaptive_threshold(arr):
    mean = arr.mean()
    return np.where(arr > mean, 255, 0).astype(np.uint8)

def preprocess(img, st):
    color_img = img.resize((st["w"], int(img.height/img.width*st["w"]*0.55)), Image.LANCZOS)
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

def auto_preset(img):
    arr = np.array(img.convert("L"))
    contrast = arr.std()
    if contrast > 70: return "High Contrast"
    if contrast > 50: return "Anime Line"
    if contrast > 35: return "e8515c Ultra"
    return "Anime Soft"

# ===================== GUI =====================
class App:
    def __init__(s, r):
        s.r=r; r.title("ASCII Converter e8515c PRO"); r.geometry("1150x720")
        s.img=None; s.user={}
        s.load_user()
        s.ui()

    def ui(s):
        p=ttk.Panedwindow(s.r,orient="horizontal"); p.pack(fill="both",expand=1)
        L=ttk.Frame(p,width=300); R=ttk.Frame(p); p.add(L); p.add(R,weight=1)

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

        s.inv=tk.BooleanVar(); ttk.Checkbutton(L,text="Invert",variable=s.inv,command=s.render).pack()
        s.thr=tk.BooleanVar(); ttk.Checkbutton(L,text="Adaptive Threshold",variable=s.thr,command=s.render).pack()
        s.col=tk.BooleanVar(); ttk.Checkbutton(L,text="Color ASCII",variable=s.col,command=s.render).pack()

        s.cs=tk.StringVar(value="Emoji Dense")
        ttk.Combobox(L,textvariable=s.cs,values=list(CHARSETS),state="readonly").pack(fill="x")

        ttk.Button(L,text="Render",command=s.render).pack(fill="x",pady=6)

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
            cs=s.cs.get()
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
        s.r.clipboard_clear()
        s.r.clipboard_append(s.txt.get("1.0","end"))

    # -------- presets --------
    def refresh_presets(s):
        s.pc["values"]=list(BUILTIN_PRESETS)+list(s.user)
        if s.pc["values"]: s.pc.current(0)

    def apply(s,_):
        n=s.pv.get()
        d=BUILTIN_PRESETS.get(n) or s.user.get(n)
        if not d: return
        s.ctrl["Width"].set(d["w"])
        s.ctrl["Gamma"].set(d["g"])
        s.ctrl["Contrast"].set(d["c"])
        s.ctrl["Sharpness"].set(d["s"])
        s.ctrl["Edge"].set(d["e"])
        s.inv.set(d["inv"]); s.thr.set(d["thr"]); s.col.set(d["col"]); s.cs.set(d["cs"])
        s.render()

    def save_p(s):
        n=simpledialog.askstring("Save preset","Name")
        if not n: return
        s.user[n]=s.state()
        s.save_user(); s.refresh_presets()

    def del_p(s):
        n=s.pv.get()
        if n in s.user:
            del s.user[n]; s.save_user(); s.refresh_presets()

    def auto(s):
        if s.img is None: return
        p=auto_preset(s.img)
        s.pv.set(p); s.apply(None)

    def load_user(s):
        if os.path.exists(PRESET_FILE):
            with open(PRESET_FILE,"r",encoding="utf8") as f: s.user=json.load(f)

    def save_user(s):
        with open(PRESET_FILE,"w",encoding="utf8") as f: json.dump(s.user,f,indent=2)

# =====================
if __name__=="__main__":
    r=tk.Tk(); App(r); r.mainloop()
