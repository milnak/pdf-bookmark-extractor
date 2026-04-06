# PDF Bookmark Extractor

Extracts pages from a PDF file based on its bookmarks. Each bookmark becomes a separate PDF file named after the bookmark title.

## Requirements

- Python 3.10 or later

## Setup

1. **Clone or download** this project, then open a terminal in the project folder.

2. **Create the virtual environment:**

   ```powershell
   python -m venv .venv
   ```

3. **Install dependencies:**

   ```powershell
   .venv\Scripts\pip install -r requirements.txt
   ```

## Usage

```powershell
.venv\Scripts\python pdf_bookmark_extractor.py <path-to-pdf> [-o <output-dir>]
```

| Argument | Description |
|---|---|
| `pdf` | Path to the source PDF file (required) |
| `-o`, `--output-dir` | Directory to write extracted pages into (optional) |

If `--output-dir` is omitted, a folder named `<pdf-name>_bookmarks` is created next to the source PDF.

### Examples

Extract pages using the default output folder:

```powershell
.venv\Scripts\python pdf_bookmark_extractor.py C:\Documents\report.pdf
# Output: C:\Documents\report_bookmarks\
```

Extract pages into a custom folder:

```powershell
.venv\Scripts\python pdf_bookmark_extractor.py C:\Documents\report.pdf -o C:\Output\sections
```

## Output

For each bookmark found in the PDF, one file is created:

```
report_bookmarks\
  Introduction.pdf
  Chapter_1.pdf
  Chapter_2.pdf
  Conclusion.pdf
```

- The file name matches the bookmark title; characters that are invalid in file names (`\ / * ? : " < > |`) are replaced with `_`.
- Each file contains the single page the bookmark points to.
- Nested bookmarks are fully supported.
- Bookmarks pointing to an out-of-range page are skipped with a warning.
