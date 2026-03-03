import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import webbrowser

try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_OK = True
except ImportError:
    HEIC_OK = False

INPUT_FORMATS  = [".heic", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"]
OUTPUT_FORMATS = ["JPG", "PNG", "WEBP", "BMP", "TIFF"]

THEMES = {
    "dark": {
        "BG":     "#0f0f13",
        "PANEL":  "#1a1a22",
        "ACCENT": "#7c6af7",
        "ACC2":   "#a89cf8",
        "TEXT":   "#e8e6ff",
        "MUTED":  "#6b6880",
        "OK":     "#4ade80",
        "ERR":    "#f87171",
        "BORD":   "#2e2b40",
        "BTN2":   "#4a4665",
    },
    "light": {
        "BG":     "#f5f5f7",
        "PANEL":  "#ffffff",
        "ACCENT": "#5b4de0",
        "ACC2":   "#7c6af7",
        "TEXT":   "#1a1a2e",
        "MUTED":  "#888899",
        "OK":     "#22a85a",
        "ERR":    "#d93025",
        "BORD":   "#d0cde8",
        "BTN2":   "#dcdaf0",
    },
}

LANG = {
    "fi": {
        "title":        "Kuvanmuunnin",
        "subtitle":     "HEIC · JPG · PNG · WEBP · BMP · TIFF",
        "src_files":    "Lähdetiedostot",
        "add":          "+ Lisää kuvat",
        "remove":       "× Poista valittu",
        "clear":        "Tyhjennä",
        "settings":     "Asetukset",
        "target_fmt":   "Kohdeformaatti",
        "quality":      "Laatu – JPG/WEBP",
        "save_loc":     "Tallennuspaikka",
        "same_dir":     "Sama kansio kuin lähde",
        "convert_btn":  "▶  Muunna kaikki",
        "log":          "Loki",
        "no_files":     "Lisää ensin kuvia listaan.",
        "no_pil":       "Pillow puuttuu.",
        "added":        "Lisätty {n} kuvaa (yht. {t})",
        "cleared":      "Lista tyhjennetty",
        "converting":   "Muunnetaan → {fmt}  ({n} kuvaa)",
        "done":         "Valmis! {ok} onnistui",
        "done_err":     "Valmis! {ok} onnistui, {err} epäonnistui",
        "heic_ok":      "HEIC-tuki käytössä",
        "heic_miss":    "HEIC-tuki puuttuu — asenna: pip install pillow-heif",
        "ready":        "Valmis! Lisää kuvia painikkeella.",
        "theme_dark":   "Tumma",
        "theme_light":  "Vaalea",
        "language":     "Kieli",
        "theme":        "Teema",
    },
    "en": {
        "title":        "Image Converter",
        "subtitle":     "HEIC · JPG · PNG · WEBP · BMP · TIFF",
        "src_files":    "Source files",
        "add":          "+ Add images",
        "remove":       "× Remove selected",
        "clear":        "Clear",
        "settings":     "Settings",
        "target_fmt":   "Target format",
        "quality":      "Quality – JPG/WEBP",
        "save_loc":     "Save location",
        "same_dir":     "Same folder as source",
        "convert_btn":  "▶  Convert all",
        "log":          "Log",
        "no_files":     "Add images to the list first.",
        "no_pil":       "Pillow is not installed.",
        "added":        "Added {n} images (total {t})",
        "cleared":      "List cleared",
        "converting":   "Converting → {fmt}  ({n} files)",
        "done":         "Done! {ok} succeeded",
        "done_err":     "Done! {ok} succeeded, {err} failed",
        "heic_ok":      "HEIC support active",
        "heic_miss":    "HEIC support missing — install: pip install pillow-heif",
        "ready":        "Ready! Add images using the button.",
        "theme_dark":   "Dark",
        "theme_light":  "Light",
        "language":     "Language",
        "theme":        "Theme",
    },
}

class App:
    def __init__(self, root):
        self.root = root
        self.files      = []
        self.output_dir = tk.StringVar()
        self.target_fmt = tk.StringVar(value="PNG")
        self.quality    = tk.IntVar(value=90)
        self.same_dir   = tk.BooleanVar(value=True)
        self.lang_var   = tk.StringVar(value="en")
        self.theme_var  = tk.StringVar(value="light")

        self._launch()

    def _launch(self, dlg=None):
        if dlg:
            dlg.destroy()
        self.T  = THEMES[self.theme_var.get()]
        self.L  = LANG[self.lang_var.get()]
        self._build()
        self._check_deps()

    def t(self, key, **kw):
        return self.L[key].format(**kw) if kw else self.L[key]

    def _check_deps(self):
        if not PIL_OK:
            messagebox.showerror("Error", "pip install Pillow")
        key = "heic_ok" if HEIC_OK else "heic_miss"
        col = self.T["OK"] if HEIC_OK else self.T["MUTED"]
        self._log(self.t(key), col)
        self._log(self.t("ready"), self.T["OK"])

    def _open_url(self, url):
        webbrowser.open(url)

    def _open_settings_panel(self):
        T = self.T
        panel = tk.Toplevel(self.root)
        panel.title("Asetukset / Settings")
        panel.geometry("300x240")
        panel.resizable(False, False)
        panel.configure(bg=T["BG"])
        panel.grab_set()

        tk.Label(panel, text="⚙  " + self.t("settings"),
                font=("Georgia", 14, "bold"), fg=T["ACC2"], bg=T["BG"]
                ).pack(pady=(20, 16))

        tk.Frame(panel, bg=T["BORD"], height=1).pack(fill="x", padx=20, pady=(0, 12))

        row1 = tk.Frame(panel, bg=T["BG"])
        row1.pack(pady=6)
        tk.Label(row1, text=self.t("language") + ":",
                font=("Georgia", 11), fg=T["TEXT"], bg=T["BG"],
                width=12, anchor="e").pack(side="left")
        lang_var = tk.StringVar(value=self.lang_var.get())
        for code, label in [("fi", "Suomi"), ("en", "English")]:
            tk.Radiobutton(row1, text=label, variable=lang_var, value=code,
                        bg=T["BG"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                        activebackground=T["BG"], font=("Georgia", 11),
                        highlightthickness=0, cursor="hand2"
                        ).pack(side="left", padx=6)

        row2 = tk.Frame(panel, bg=T["BG"])
        row2.pack(pady=6)
        tk.Label(row2, text=self.t("theme") + ":",
                font=("Georgia", 11), fg=T["TEXT"], bg=T["BG"],
                width=12, anchor="e").pack(side="left")
        theme_var = tk.StringVar(value=self.theme_var.get())
        for code, label in [("dark", self.t("theme_dark")), ("light", self.t("theme_light"))]:
            tk.Radiobutton(row2, text=label, variable=theme_var, value=code,
                        bg=T["BG"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                        activebackground=T["BG"], font=("Georgia", 11),
                        highlightthickness=0, cursor="hand2"
                        ).pack(side="left", padx=6)

        tk.Frame(panel, bg=T["BORD"], height=1).pack(fill="x", padx=20, pady=(14, 0))

        def _apply():
            changed = lang_var.get() != self.lang_var.get() or theme_var.get() != self.theme_var.get()
            self.lang_var.set(lang_var.get())
            self.theme_var.set(theme_var.get())
            panel.destroy()
            if changed:
                for widget in self.root.winfo_children():
                    widget.destroy()
                self.T = THEMES[self.theme_var.get()]
                self.L = LANG[self.lang_var.get()]
                self._build()
                self._check_deps()

        tk.Button(panel, text="OK", command=_apply,
                bg=T["ACCENT"], fg="white", font=("Georgia", 12, "bold"),
                relief="flat", cursor="hand2", padx=24, pady=6
                ).pack(pady=16)

    def _build(self):
        T = self.T
        self.root.title(self.t("title"))
        self.root.geometry("780x620")
        self.root.configure(bg=T["BG"])
        self.root.resizable(False, False)

        hdr = tk.Frame(self.root, bg=T["BG"])
        hdr.pack(fill="x", padx=28, pady=(22, 0))

        tk.Label(hdr, text=self.t("title"), font=("Georgia", 24, "bold"),
                fg=T["ACC2"], bg=T["BG"]).pack(side="left")
        tk.Label(hdr, text=f"   {self.t('subtitle')}",
                font=("Georgia", 11), fg=T["MUTED"], bg=T["BG"]).pack(side="left", pady=4)

        gear_btn = tk.Button(hdr, text="⚙️", font=("Georgia", 16), bg=T["BG"],
                            fg=T["MUTED"], activebackground=T["BG"],
                            activeforeground=T["ACC2"], relief="flat",
                            cursor="hand2", bd=0, command=self._open_settings_panel)
        gear_btn.pack(side="right", padx=(0, 0))

        body = tk.Frame(self.root, bg=T["BG"])
        body.pack(fill="both", expand=True, padx=28)

        left = tk.Frame(body, bg=T["BG"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        tk.Label(left, text=self.t("src_files"), font=("Georgia", 12, "bold"),
                 fg=T["TEXT"], bg=T["BG"]).pack(anchor="w", pady=(0, 6))

        lf = tk.Frame(left, bg=T["PANEL"], highlightthickness=1,
                      highlightbackground=T["BORD"])
        lf.pack(fill="both", expand=True)
        sb = tk.Scrollbar(lf, bg=T["PANEL"], troughcolor=T["PANEL"],
                          relief="flat", width=10)
        sb.pack(side="right", fill="y")
        self.lb = tk.Listbox(lf, bg=T["PANEL"], fg=T["TEXT"],
                             selectbackground=T["ACCENT"],
                             font=("Consolas", 10), activestyle="none",
                             borderwidth=0, highlightthickness=0,
                             yscrollcommand=sb.set, relief="flat")
        self.lb.pack(fill="both", expand=True, padx=2, pady=2)
        sb.config(command=self.lb.yview)

        br = tk.Frame(left, bg=T["BG"])
        br.pack(fill="x", pady=8)
        self._btn(br, self.t("add"),    self._add,    T["ACCENT"]).pack(side="left", padx=(0,6))
        self._btn(br, self.t("remove"), self._remove, T["BTN2"]).pack(side="left", padx=(0,6))
        self._btn(br, self.t("clear"),  self._clear,  T["BTN2"]).pack(side="left")

        right = tk.Frame(body, bg=T["BG"], width=220)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text=self.t("settings"), font=("Georgia", 12, "bold"),
                 fg=T["TEXT"], bg=T["BG"]).pack(anchor="w", pady=(0, 10))

        self._lbl(right, self.t("target_fmt"))
        ff = tk.Frame(right, bg=T["PANEL"], highlightthickness=1,
                      highlightbackground=T["BORD"])
        ff.pack(fill="x", pady=(2, 12))
        for f in OUTPUT_FORMATS:
            tk.Radiobutton(ff, text=f, variable=self.target_fmt, value=f,
                           bg=T["PANEL"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                           activebackground=T["PANEL"], activeforeground=T["ACC2"],
                           font=("Consolas", 11), highlightthickness=0,
                           cursor="hand2").pack(anchor="w", padx=10, pady=2)

        self._lbl(right, self.t("quality"))
        tk.Scale(right, from_=10, to=100, orient="horizontal", variable=self.quality,
                 bg=T["BG"], fg=T["TEXT"], troughcolor=T["PANEL"],
                 activebackground=T["ACCENT"], highlightthickness=0,
                 relief="flat", sliderrelief="flat").pack(fill="x", pady=(0, 12))

        self._lbl(right, self.t("save_loc"))
        tk.Checkbutton(right, text=self.t("same_dir"), variable=self.same_dir,
                       bg=T["BG"], fg=T["TEXT"], selectcolor=T["ACCENT"],
                       activebackground=T["BG"], font=("Georgia", 10),
                       highlightthickness=0, cursor="hand2",
                       command=self._toggle).pack(anchor="w", pady=(2, 4))

        dr = tk.Frame(right, bg=T["BG"])
        dr.pack(fill="x", pady=(0, 16))
        self.de = tk.Entry(dr, textvariable=self.output_dir, bg=T["PANEL"],
                           fg=T["MUTED"], font=("Consolas", 9), relief="flat",
                           highlightthickness=1, highlightbackground=T["BORD"],
                           state="disabled")
        self.de.pack(side="left", fill="x", expand=True, ipady=4)
        self._btn(dr, "...", self._pick_dir, T["BTN2"], pad=6).pack(side="right", padx=(4,0))

        self.cb = self._btn(right, self.t("convert_btn"), self._start,
                            T["ACCENT"], font=("Georgia", 13, "bold"))
        self.cb.pack(fill="x", pady=(6, 0), ipady=6)

        tk.Frame(self.root, bg=T["BORD"], height=1).pack(fill="x", padx=28, pady=(12,6))
        lo = tk.Frame(self.root, bg=T["BG"])
        lo.pack(fill="x", padx=28, pady=(0, 10))
        tk.Label(lo, text=self.t("log"), font=("Georgia", 10, "bold"),
                 fg=T["MUTED"], bg=T["BG"]).pack(anchor="w")
        lf2 = tk.Frame(lo, bg=T["PANEL"], highlightthickness=1,
                       highlightbackground=T["BORD"])
        lf2.pack(fill="x")
        self.log_w = tk.Text(lf2, bg=T["PANEL"], fg=T["MUTED"],
                             font=("Consolas", 9), height=5, state="disabled",
                             relief="flat", highlightthickness=0, wrap="word")
        self.log_w.pack(fill="x", padx=6, pady=4)
        self.log_w.tag_config("ok",  foreground=T["OK"])
        self.log_w.tag_config("err", foreground=T["ERR"])
        self.log_w.tag_config("hi",  foreground=T["ACC2"])
        self.log_w.tag_config("dim", foreground=T["MUTED"])

        self.pb = ttk.Progressbar(self.root, mode="determinate")
        s = ttk.Style(); s.theme_use("clam")
        s.configure("TProgressbar", troughcolor=T["PANEL"],
                    background=T["ACCENT"], bordercolor=T["PANEL"],
                    lightcolor=T["ACCENT"], darkcolor=T["ACCENT"])
        self.pb.pack(fill="x", padx=28, pady=(0, 12))

        watermark = tk.Label(self.root, text="©️ Julle98", font=("Georgia", 9),
                            fg=T["MUTED"], bg=T["BG"], cursor="hand2")
        watermark.pack(side="right", padx=28, pady=(0, 6))
        watermark.bind("<Button-1>", lambda e: self._open_url("https://github.com/Julle98"))
        watermark.bind("<Enter>", lambda e: watermark.config(fg=T["ACC2"], font=("Georgia", 9, "underline")))
        watermark.bind("<Leave>", lambda e: watermark.config(fg=T["MUTED"], font=("Georgia", 9)))

    def _btn(self, p, txt, cmd, col, pad=8, font=("Georgia", 10)):
        is_dark_btn = self._is_dark_color(col)
        fg = "#ffffff" if is_dark_btn else "#1a1a2e"
        return tk.Button(p, text=txt, command=cmd, bg=col, fg=fg,
                        activebackground=self.T["ACC2"], activeforeground="white",
                        font=font, relief="flat", cursor="hand2",
                        padx=pad, pady=4, bd=0)

    def _is_dark_color(self, hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return luminance < 0.5

    def _lbl(self, p, txt):
        tk.Label(p, text=txt, font=("Georgia", 9), fg=self.T["MUTED"],
                 bg=self.T["BG"]).pack(anchor="w", pady=(0, 2))

    def _log(self, msg, color=None):
        T = self.T
        tag = {T["OK"]:"ok", T["ERR"]:"err", T["ACC2"]:"hi", T["MUTED"]:"dim"}.get(color, "")
        self.log_w.config(state="normal")
        self.log_w.insert("end", msg + "\n", tag)
        self.log_w.see("end")
        self.log_w.config(state="disabled")

    def _toggle(self):
        self.de.config(state="disabled" if self.same_dir.get() else "normal")

    def _add(self):
        exts = " ".join(f"*{e}" for e in INPUT_FORMATS)
        paths = filedialog.askopenfilenames(
            title=self.t("add"),
            filetypes=[("Images", exts), ("All files", "*.*")])
        added = 0
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.lb.insert("end", f"  {Path(p).name}")
                added += 1
        if added:
            self._log(self.t("added", n=added, t=len(self.files)), self.T["OK"])

    def _remove(self):
        for i in reversed(self.lb.curselection()):
            self.lb.delete(i); del self.files[i]

    def _clear(self):
        self.files.clear(); self.lb.delete(0, "end")
        self._log(self.t("cleared"), self.T["MUTED"])

    def _pick_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir.set(d); self.same_dir.set(False)
            self.de.config(state="normal", fg=self.T["TEXT"])

    def _start(self):
        if not self.files:
            messagebox.showwarning("!", self.t("no_files")); return
        if not PIL_OK:
            messagebox.showerror("Error", self.t("no_pil")); return
        self.cb.config(state="disabled")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        fmt  = self.target_fmt.get()
        qual = self.quality.get()
        ext  = ".jpg" if fmt == "JPG" else f".{fmt.lower()}"
        ok = err = 0
        self.pb["maximum"] = len(self.files); self.pb["value"] = 0
        self._log(self.t("converting", fmt=fmt, n=len(self.files)), self.T["ACC2"])

        for i, src in enumerate(self.files):
            try:
                img = Image.open(src)
                if fmt == "JPG" and img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=(img.split()[-1] if img.mode in ("RGBA","LA") else None))
                    img = bg
                elif img.mode == "P":
                    img = img.convert("RGB")

                out_dir = (Path(src).parent if self.same_dir.get()
                           else Path(self.output_dir.get() or Path(src).parent))
                out_dir.mkdir(parents=True, exist_ok=True)

                out = out_dir / f"{Path(src).stem}{ext}"
                c = 1
                while out.exists() and str(out) != src:
                    out = out_dir / f"{Path(src).stem}_{c}{ext}"; c += 1

                kw = {}
                if fmt == "JPG":  kw = {"quality": qual, "optimize": True}
                if fmt == "WEBP": kw = {"quality": qual}
                img.save(str(out), "JPEG" if fmt == "JPG" else fmt, **kw)
                self._log(f"  ✓  {Path(src).name}  →  {out.name}", self.T["OK"])
                ok += 1
            except Exception as e:
                self._log(f"  ✗  {Path(src).name}  –  {e}", self.T["ERR"])
                err += 1

            self.pb["value"] = i + 1
            self.root.update_idletasks()

        key = "done_err" if err else "done"
        self._log(self.t(key, ok=ok, err=err), self.T["OK"])
        self.cb.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  
    App(root)
    root.deiconify()  
    root.mainloop()