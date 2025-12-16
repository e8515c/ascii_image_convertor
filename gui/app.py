import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

from presets.manager import load_all, save_preset, delete_preset
from core.renderer import render_ascii
from image.loader import load_image


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Converter e8515c")
        self.root.state("zoomed")

        self._preview_job = None

        # data
        self.img = None
        self.charsets, self.presets = load_all()

        self.current_preset = tk.StringVar()
        self.current_charset = tk.StringVar()

        # parameters
        self.vars = {
            "auto_scale": tk.BooleanVar(value=False),
            "scale": tk.DoubleVar(value=0.15),
            "contrast": tk.DoubleVar(value=1.0),
            "brightness": tk.DoubleVar(value=1.0),
            "sharpness": tk.DoubleVar(value=1.0),
            "tile": tk.IntVar(value=1),
            "invert": tk.BooleanVar(value=False),
            "gamma": tk.DoubleVar(value=1.6),
            "edge_bias": tk.DoubleVar(value=0.15),
        }

        self.supersample = tk.IntVar(value=2)
        self.adaptive = tk.BooleanVar(value=True)

        self.build_ui()

    # ---------------- UI ----------------

    def build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=6, pady=6)

        ttk.Button(top, text="Open", command=self.open).pack(side="left")
        ttk.Button(top, text="Render", command=self.render).pack(side="left", padx=4)
        ttk.Button(top, text="Save preset", command=self.save).pack(side="left")
        ttk.Button(top, text="Delete preset", command=self.delete).pack(side="left")

        ttk.Label(top, text="Preset").pack(side="left", padx=6)
        self.preset_box = ttk.Combobox(
            top,
            values=list(self.presets.keys()),
            textvariable=self.current_preset,
            state="readonly",
            width=18
        )
        self.preset_box.pack(side="left")
        self.preset_box.bind("<<ComboboxSelected>>", self.on_preset)

        ttk.Label(top, text="Charset").pack(side="left", padx=6)
        self.charset_box = ttk.Combobox(
            top,
            values=list(self.charsets.keys()),
            textvariable=self.current_charset,
            state="readonly",
            width=18
        )
        self.charset_box.pack(side="left")
        self.charset_box.bind("<<ComboboxSelected>>", self.schedule_preview)

        # controls
        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=6)

        self._add_slider(controls, "scale", 0.01, 1.0)
        self._add_slider(controls, "gamma", 0.8, 2.6)
        self._add_slider(controls, "edge_bias", 0.0, 0.4)
        self._add_slider(controls, "contrast", 0.2, 3.0)
        self._add_slider(controls, "brightness", 0.2, 3.0)
        self._add_slider(controls, "sharpness", 0.2, 3.0)
        self._add_slider(controls, "tile", 1, 8)

        ttk.Checkbutton(
            controls,
            text="Invert",
            variable=self.vars["invert"],
            command=self.schedule_preview
        ).pack(side="left", padx=8)

        ttk.Checkbutton(
            controls,
            text="Adaptive charset",
            variable=self.adaptive,
            command=self.schedule_preview
        ).pack(side="left", padx=8)

        ttk.Checkbutton(
            controls,
            text="Auto Scale",
            variable=self.vars["auto_scale"],
            command=self.schedule_preview
        ).pack(side="left", padx=8)

        ttk.Label(controls, text="SS").pack(side="left", padx=6)
        ttk.Combobox(
            controls,
            values=[1, 2, 3],
            width=3,
            textvariable=self.supersample,
            state="readonly"
        ).pack(side="left")

        # preview
        self.text = tk.Text(
            self.root,
            font=("Consolas", 8),
            wrap="none"
        )
        self.text.pack(fill="both", expand=True)

    def _add_slider(self, parent, key, mn, mx):
        frame = ttk.Frame(parent)
        frame.pack(side="left", padx=4)

        ttk.Label(frame, text=key).pack()
        ttk.Scale(
            frame,
            from_=mn,
            to=mx,
            variable=self.vars[key],
            orient="horizontal",
            command=lambda *_: self.schedule_preview()
        ).pack()

        ttk.Entry(frame, textvariable=self.vars[key], width=6).pack()

    # ---------------- Logic ----------------

    def open(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        self.img = load_image(path)

        if not self.current_charset.get() and self.charsets:
            self.current_charset.set(next(iter(self.charsets)))

        if not self.current_preset.get() and self.presets:
            name = next(iter(self.presets))
            self.current_preset.set(name)
            self.apply_preset(name)

        self.render()

    def collect_preset(self):
        d = {k: v.get() for k, v in self.vars.items()}
        d["charset"] = self.current_charset.get()
        return d

    def apply_preset(self, name):
        if name not in self.presets:
            return

        p = self.presets[name]
        for k in self.vars:
            if k in p:
                self.vars[k].set(p[k])

        if "charset" in p and p["charset"] in self.charsets:
            self.current_charset.set(p["charset"])

    def render(self):
        if not self.img:
            return

        charset = self.charsets.get(self.current_charset.get(), "")
        if len(charset) < 2:
            messagebox.showerror("Error", "Invalid charset")
            return

        art = render_ascii(
            self.img,
            self.collect_preset(),
            charset,
            supersample=self.supersample.get(),
            adaptive=self.adaptive.get()
        )

        self.text.delete("1.0", "end")
        self.text.insert("1.0", art)

    # ---------------- Live preview ----------------

    def schedule_preview(self, *_):
        if self._preview_job:
            self.root.after_cancel(self._preview_job)
        self._preview_job = self.root.after(180, self.render)

    # ---------------- Presets ----------------

    def save(self):
        name = simpledialog.askstring("Preset name", "Preset name:")
        if not name:
            return
        save_preset(name, self.collect_preset())
        self.reload_presets()
        self.current_preset.set(name)

    def delete(self):
        name = self.current_preset.get()
        if not name:
            return
        delete_preset(name)
        self.reload_presets()
        self.current_preset.set("")

    def reload_presets(self):
        self.charsets, self.presets = load_all()
        self.preset_box["values"] = list(self.presets.keys())
        self.charset_box["values"] = list(self.charsets.keys())

    # ---------------- Events ----------------

    def on_preset(self, _=None):
        self.apply_preset(self.current_preset.get())
        self.schedule_preview()


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()
