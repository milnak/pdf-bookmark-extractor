# PDF Bookmark Extractor

Extracts pages from a PDF file based on its bookmarks. Each bookmark becomes a separate PDF file named after the bookmark title. Each output file contains all pages from that bookmark up to (but not including) the next bookmark.

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
| `-o`, `--output-dir` | Directory to write extracted files into (optional) |

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

For each bookmark (or bookmark group) found in the PDF, one file is created:

```
report_bookmarks\
  Introduction.pdf
  Chapter 1.pdf
  Chapter 2.pdf
  Conclusion.pdf
```

### Page ranges

Each output PDF contains **all pages covered by that bookmark** — from the bookmark's start page up to (but not including) the page where the next bookmark begins. The last bookmark runs to the end of the document.

For example, if `song1` starts at page 356 and `song2` starts at page 358, then `song1.pdf` contains pages 356–357.

### Numbered bookmark groups

Bookmarks whose titles end with a parenthesised number are treated as a single group and merged into one output file:

| Bookmarks in PDF | Output file |
|---|---|
| `Song (1)`, `Song (2)`, `Song (3)` | `Song.pdf` (pages from first to last) |
| `Report (1)`, `Report (2)` | `Report.pdf` |

### File naming

Output file names match the bookmark title. Characters that are invalid in file names (`\ / * ? : " < > |`) are replaced with `_`.

## Validation

The app will exit with an error if:

- The PDF contains **no bookmarks**.
- The number of bookmarks is **less than 10% of the total page count** (e.g. fewer than 10 bookmarks in a 100-page PDF). This guards against PDFs where bookmarks are sparse and unlikely to represent meaningful page-level sections.
