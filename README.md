# 📂 Basic FileChanger by Julle98

## Overview 

A small GUI app to convert images, audio and video using Python and ffmpeg.  

---

## Requirements 

- Python 3.8+
- ffmpeg installed and available on PATH  
  (e.g. `brew install ffmpeg` on macOS, `choco install ffmpeg` on Windows)
- Install Python deps: `pip install -r requirements.txt`

---

## PySimpleGUI private PyPI

PySimpleGUI is hosted on a private PyPI server. Use these commands to install:

### Uninstall previous version (optional but recommended):
```bash
python -m pip uninstall PySimpleGUI
python -m pip cache purge
```

### Install/upgrade from private server:
```bash
python -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
# or force reinstall
python -m pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
```

> If using `pip install -r requirements.txt`, add `-i https://PySimpleGUI.net/install` to ensure the package is found.

---

## Usage 
```bash
python src/main.py
```

1. Choose a file 
2. Pick an output folder 
3. Select target format 
4. Click **Convert** 

### Language

The app supports **English** and **Finnish** — switch from the settings menu at startup.  
Sovellus tukee **englantia** ja **suomea** — vaihda kieltä asetusvalikosta käynnistyksessä.

### Themes 

Choose between **Dark** (default) and **Light** themes in the settings.  
Valitse **tumma** (oletus) tai **vaalea** teema asetuksista.

---

## Supported Formats 

| Type / Tyyppi | Formats / Formaatit |
|---|---|
| 🖼 Images / Kuvat | HEIC, JPG, PNG, WEBP, BMP, TIFF |
| 🎵 Audio / Ääni | MP3, WAV, AAC, FLAC, OGG |
| 🎬 Video | MP4, MKV, AVI, MOV, WEBM |

---

## Notes 

- HEIC support requires `pillow-heif`: `pip install pillow-heif`
- Video/audio conversion uses the `ffmpeg` CLI
- HEIC-tuki vaatii `pillow-heif`-paketin
- Video/äänimuunnos käyttää `ffmpeg`-komentorivityökalua

---

## License 

See the [LICENSE](__LICENSE__) file.

---

## Credits 

Created by **Julle98** with assistance from Copilot and Claude.