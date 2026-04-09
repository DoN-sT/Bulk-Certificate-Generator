# 🎓 Bulk Certificate Generator

> Generate hundreds of personalised certificates in seconds — fully offline, no internet required.

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| **Bulk generation** | 100–500 certificates in seconds using multiprocessing |
| **CSV & Excel input** | Drop in any spreadsheet with Name, Course, Date columns |
| **Visual editor** | Drag-and-position text fields with live preview |
| **PNG & PDF output** | Choose your format; ZIP download of the entire batch |
| **100% offline** | Zero external API calls; all fonts & libs bundled locally |
| **Cross-platform** | Windows · macOS · Linux |

---

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites

- **Python 3.9 or newer** — [download here](https://www.python.org/downloads/)
- **pip** (bundled with Python)

Verify:
```bash
python --version   # Should print Python 3.9.x or newer
pip --version
```

---

### 2. Clone / Download

```bash
# Option A — git clone
git clone https://github.com/DoN-sT/Bulk-Certificate-Generator.git
cd BulkCertificateGenerator

# Option B — download ZIP, extract, then:
cd certificate_generator
```

---

### 3. (Recommended) Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected install time: ~60 seconds (downloads ~50 MB of packages).

---

### 5. Run the App

```bash
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**.  
If it does not, open that URL manually.

---

## 🗺️ Workflow (Step-by-Step)

```
📤 Upload → 🎨 Design → 👁 Preview → ⚙️ Generate → ⬇️ Download
  Step 1      Step 2      Step 3       Step 4         Step 5
```

### Step 1 — Upload Participant Data

- Click **"Browse files"** and select your `.csv` or `.xlsx` file.
- Required columns: **Name**, **Course**, **Date**
- Optional enrichment columns: `Grade`, `Instructor`, `Venue` (or any custom column)
- A preview table and field-detection report are shown immediately.

**Sample CSV format:**
```csv
Name,Course,Date,Grade,Instructor
Alice Johnson,Python Programming,2024-12-15,A+,Dr. Smith
Bob Williams,Data Science,2024-12-15,A,Prof. Jones
```

A pre-built `sample_data.csv` is included in the project root.

---

### Step 2 — Design the Certificate

1. Choose **"Use built-in template"** (navy & gold design) or upload your own PNG/JPG.
2. Each text field appears as a collapsible editor panel.
3. Use sliders to set **X %** and **Y %** position (0 = left/top, 100 = right/bottom).
4. Set font size, colour, bold, and alignment.
5. Click **"+ Add a new field"** to insert custom static text or data placeholders like `{Grade}`.
6. Select output format: **PNG** or **PDF**.

**Available placeholders** are automatically derived from your column names:  
`{Name}`, `{Course}`, `{Date}`, `{Grade}`, `{Instructor}`, etc.

---

### Step 3 — Preview

- Select any participant from the dropdown to see their certificate rendered live.
- Download the sample for a closer look.
- Click **"← Back to Design"** to make adjustments.

---

### Step 4 — Generate All Certificates

- Click **"🚀 Generate N Certificates"**.
- A real-time progress bar shows: current name, speed (certs/sec), and ETA.
- Generation uses all available CPU cores (multiprocessing).

Typical speeds:
| Batch size | PNG time | PDF time |
|------------|----------|----------|
| 50         | ~4s      | ~8s      |
| 200        | ~14s     | ~30s     |
| 500        | ~35s     | ~75s     |

*(On a modern 4-core machine)*

---

### Step 5 — Download

- **ZIP download** — one click to download all certificates as a `.zip` archive.
- **Individual downloads** — paginated list with per-certificate download buttons.
- **Save to disk** — optionally write certificates to the `output/` folder on your machine.

---

## 📁 Project Structure

```
certificate_generator/
│
├── app.py                   # Main Streamlit entry point (wizard orchestrator)
├── data_handler.py          # CSV/Excel parsing, validation, preview table
├── template_handler.py      # Template loading, field-placement editor, preview renderer
├── certificate_engine.py    # Pillow PNG + fpdf2 PDF generation, multiprocessing pool
├── export_handler.py        # ZIP builder, download buttons, save-to-disk
│
├── assets/
│   └── fonts/                     # Drop .ttf / .otf fonts here for custom typography
│
├── output/                  # Auto-created when "Save to disk" is used
├── sample_data.csv          # 5 test participant records
├── requirements.txt         # Pinned Python dependencies
└── README.md                # This file
```

---

## 🔤 Adding Custom Fonts

1. Copy `.ttf` or `.otf` font files into `assets/fonts/`.
2. Bold variants should contain "Bold" in the filename (e.g. `Montserrat-Bold.ttf`).
3. Restart the app — fonts are auto-detected.

---

## 📦 Build an Offline Executable (PyInstaller)

To distribute the app as a standalone `.exe` / binary (no Python installation required):

```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build (Windows)
pyinstaller --onefile --windowed --name CertGen \
  --add-data "assets;assets" \
  --add-data "sample_data.csv;." \
  --hidden-import streamlit \
  --hidden-import pandas \
  --hidden-import PIL \
  --hidden-import fpdf \
  app.py

# 2. Build (macOS / Linux)
pyinstaller --onefile --name CertGen \
  --add-data "assets:assets" \
  --add-data "sample_data.csv:." \
  --hidden-import streamlit \
  --hidden-import pandas \
  --hidden-import PIL \
  --hidden-import fpdf \
  app.py
```

> **Note:** The PyInstaller approach bundles the Streamlit dev server.  
> The resulting executable opens the app in the user's default browser.  
> Executable size: ~150–250 MB.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: streamlit` | Run `pip install -r requirements.txt` |
| `Port 8501 already in use` | Run `streamlit run app.py --server.port 8502` |
| Excel file not loading | Ensure `openpyxl` is installed: `pip install openpyxl` |
| Fonts look blurry on PDF | Add a high-quality TTF to `assets/fonts/` |
| Multiprocessing freeze (Windows) | Add `if __name__ == "__main__":` guard (already present) |
| App slow on first load | Streamlit caches templates on second run — normal behaviour |

---

## 📄 Licence

MIT — free for personal and commercial use.
