# TGS → GIF Converter

A local web app to convert Telegram sticker packs (`.tgs`) to animated GIFs. Runs on your machine via Flask — no uploads, no cloud, everything stays local.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat-square&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Features

- Convert entire sticker packs or individual `.tgs` files
- Drag & drop folders or files directly into the app
- Native Windows folder/file picker (modern UI)
- Live progress bar with per-file status log
- Stop conversion at any time
- Open output folder directly from the app
- No internet required after setup

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| msys64 + Cairo | latest | Required for rendering |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/tgs-converter.git
cd tgs-converter
```

### 2. Install Python dependencies

```bash
pip install flask lottie pillow cairosvg
```

### 3. Install Cairo (Windows)

Download and install [msys64](https://www.msys64.org/), then open the msys64 terminal and run:

```bash
pacman -S mingw-w64-ucrt-x86_64-cairo
```

Then copy the DLL to your Python folder:

```powershell
copy C:\msys64\ucrt64\bin\libcairo-2.dll C:\Users\<YourName>\AppData\Local\Programs\Python\Python3xx\
```

### 4. Run the app

```powershell
python app.py
```

The app opens automatically at `http://127.0.0.1:5000`

---

## Usage

1. **Select stickers** — choose Folder mode to convert a whole pack, or Individual files mode to pick specific stickers. Use the Browse button, drag & drop, or type the path directly.
2. **Set output folder** — where GIFs will be saved.
3. **Click Convert** — watch the live log as files are processed.
4. **Done** — click "Open output folder" to see your GIFs.

---

## Project Structure

```
tgs-converter/
├── app.py                  # Flask backend
├── templates/
│   └── index.html          # Frontend UI
├── requirements.txt
└── README.md
```

---

## Requirements File

```
flask
lottie
pillow
cairosvg
```

---

## How It Works

Telegram stickers use the `.tgs` format — gzip-compressed [Lottie](https://airbnb.design/lottie/) JSON animations. This app:

1. Decompresses the `.tgs` file
2. Passes it to `lottie_convert.py` (from the `lottie` Python package)
3. `lottie` renders each frame using Cairo as the SVG backend
4. Frames are assembled into an animated GIF

---

## Troubleshooting

**`Unknown exporter` error**
Cairo is not installed or the DLL is not found. Make sure you copied `libcairo-2.dll` to your Python directory.

**`No module named 'lottie'`**
Run `pip install lottie` using the exact Python you're running the app with:
```powershell
C:\Users\<YourName>\AppData\Local\Programs\Python\Python3xx\python.exe -m pip install lottie
```

**App opens but folder picker doesn't appear**
Make sure PowerShell is available on your system (it is by default on Windows 10/11).

---

## License

MIT — do whatever you want with it.

---

<p align="center">Built to scratch a personal itch — converting a Telegram sticker pack and being too stubborn to do it manually.</p>