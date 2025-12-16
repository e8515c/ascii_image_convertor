# ASCII Converter e8515c

A **high-quality image → ASCII art converter** focused on **maximum visual clarity**, **anime-style images**, and **fine-grained control**.  
Built with a custom rendering pipeline that prioritizes **edge definition**, **gamma-correct brightness**, and **adaptive character selection**.

This project is designed for people who care about **how ASCII art actually looks**, not just converting pixels into characters.

---

## ✨ Features

### 🎨 High-Quality Rendering Engine
- **Gamma-correct brightness mapping** for natural tonal perception
- **Edge-aware enhancement** that sharpens contours without destroying shading
- **Adaptive charset per tile** — complex areas get richer characters, smooth areas stay clean
- **Supersampling (×1 / ×2 / ×3)** for cleaner downscaling
- **Auto scale** mode to automatically fit images to a readable ASCII width
- Stable output across all presets (no random artifacts)

### 🧠 Anime-Focused Quality
- Optimized for **anime / illustration / line-art images**
- Clean outlines with preserved soft shading
- Dedicated **anime presets** tuned for faces, hair, and line detail
- Avoids aggressive edge-first distortion

### ⚙️ Advanced Controls
- Fully **manual parameter control**:
  - Scale
  - Gamma
  - Edge bias
  - Contrast
  - Brightness
  - Sharpness
  - Tile size (down to 1 symbol)
- **Live preview** (auto-updates with debounce)
- Manual **Render** button as fallback
- Manual values + sliders work together (non-blocking)

### 🧩 Preset System
- Built-in presets + unlimited **user-defined presets**
- Save / delete presets directly from GUI
- Presets persist after restart
- Presets do **not lock manual editing** — they only set defaults

### 🔤 Character Sets
- Multiple selectable character sets
- Custom charsets supported
- Adaptive subset selection for better readability

### 🖥️ GUI
- Responsive Tkinter GUI
- Proper full-screen scaling
- Monospace preview with correct aspect ratio

---

## 🛠 Rendering Philosophy

This converter **does not** rely on naive pixel-to-character mapping.

Instead, it uses:
- **Per-tile brightness, contrast, and edge analysis**
- **Human-perception-based gamma correction**
- **Edge-as-enhancement**, not edge-replacement
- **Minimal magic constants**, maximum predictability

The result is ASCII art that remains:
- Sharp
- Readable
- Visually balanced
- Faithful to the original image

## 🚀 Usage

python ascii_converter_e8515c.py
Open an image

Choose a preset or tweak parameters manually

Adjust scale / gamma / edge bias for perfect clarity

Copy or export your ASCII art

# 🎯 Ideal For
Anime & illustration ASCII art

High-quality text art for forums / GitHub / terminals

Users who want control, not black-box conversion

Artists experimenting with ASCII aesthetics

# 📜 License
MIT License — free to use, modify, and improve.
