import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import pyperclip

# Набір символів від темного до світлого
ASCII_CHARS_SETS = {
    "Стандарт": "@%#*+=-:. ",
    "Щільний": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "Простий": "#*:. "
}

class AsciiArtApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASCII Art Converter")
        self.geometry("900x600")

        self.image = None
        self.ascii_art = ""

        self.create_ui()

    def create_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # --- Головна вкладка ---
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Конвертація")

        btn_load = ttk.Button(main_frame, text="Завантажити зображення", command=self.load_image)
        btn_load.pack(pady=5)

        btn_convert = ttk.Button(main_frame, text="Створити ASCII арт", command=self.convert)
        btn_convert.pack(pady=5)

        self.text_output = tk.Text(main_frame, wrap="none", font=("Courier", 8))
        self.text_output.pack(fill="both", expand=True, padx=10, pady=10)

        btn_copy = ttk.Button(main_frame, text="Скопіювати в буфер", command=self.copy_to_clipboard)
        btn_copy.pack(pady=5)

        # --- Вкладка налаштувань ---
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Налаштування")

        ttk.Label(settings_frame, text="Ширина (символи):").pack(anchor="w", padx=10, pady=2)
        self.width_var = tk.IntVar(value=100)
        ttk.Entry(settings_frame, textvariable=self.width_var).pack(anchor="w", padx=10)

        ttk.Label(settings_frame, text="Контраст:").pack(anchor="w", padx=10, pady=2)
        self.contrast_var = tk.DoubleVar(value=1.0)
        ttk.Scale(settings_frame, from_=0.5, to=2.5, variable=self.contrast_var, orient="horizontal").pack(fill="x", padx=10)

        ttk.Label(settings_frame, text="Набір ASCII символів:").pack(anchor="w", padx=10, pady=2)
        self.charset_var = tk.StringVar(value="Стандарт")
        ttk.OptionMenu(settings_frame, self.charset_var, "Стандарт", *ASCII_CHARS_SETS.keys()).pack(anchor="w", padx=10)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.image = Image.open(path)
            messagebox.showinfo("Зображення", "Зображення успішно завантажене")

    def convert(self):
        if not self.image:
            messagebox.showerror("Помилка", "Спочатку завантажте зображення")
            return

        img = self.image.convert("L")
        img = self.apply_contrast(img, self.contrast_var.get())

        width = self.width_var.get()
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio * 0.55)
        img = img.resize((width, height))

        chars = ASCII_CHARS_SETS[self.charset_var.get()]
        self.ascii_art = self.image_to_ascii(img, chars)

        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, self.ascii_art)

    def image_to_ascii(self, img, chars):
        pixels = img.getdata()
        result = ""
        scale = len(chars) - 1
        for i, pixel in enumerate(pixels):
            result += chars[int(pixel / 255 * scale)]
            if (i + 1) % img.width == 0:
                result += "\n"
        return result

    def apply_contrast(self, img, factor):
        pixels = list(img.getdata())
        new_pixels = []
        for p in pixels:
            new_p = int(128 + factor * (p - 128))
            new_pixels.append(max(0, min(255, new_p)))
        img.putdata(new_pixels)
        return img

    def copy_to_clipboard(self):
        if self.ascii_art:
            pyperclip.copy(self.ascii_art)
            messagebox.showinfo("Буфер", "ASCII арт скопійовано")


if __name__ == "__main__":
    app = AsciiArtApp()
    app.mainloop()
