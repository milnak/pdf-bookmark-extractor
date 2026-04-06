"""
PDF Bookmark Extractor
Reads bookmarks from a PDF and extracts each referenced page into its own PDF file.
Bookmarks whose titles end with a parenthesised number — e.g. "Song (1)", "Song (2)" —
are treated as a group and combined into a single multi-page PDF named "Song.pdf".
"""

import argparse
import math
import re
import sys
from collections import OrderedDict
from pathlib import Path

import pypdf

# Matches titles like "Some Title (3)"
_NUMBERED_RE = re.compile(r"^(.*?)\s*\((\d+)\)$")


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in file names."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return sanitized or "unnamed"


def get_bookmarks(reader: pypdf.PdfReader) -> list[tuple[str, int]]:
    """
    Recursively walk the PDF outline and return (title, page_index) pairs.
    page_index is 0-based.
    """
    results = []

    def walk(outline):
        for item in outline:
            if isinstance(item, list):
                walk(item)
            else:
                try:
                    page_index = reader.get_destination_page_number(item)
                    results.append((item.title, page_index))
                except Exception:
                    pass

    if reader.outline:
        walk(reader.outline)
    return results


def group_bookmarks(
    bookmarks: list[tuple[str, int]]
) -> list[tuple[str, list[int]]]:
    """
    Collapse bookmarks whose titles end with a parenthesised number into a
    single group.  "Song (1)", "Song (2)", "Song (3)" → ("Song", [p1, p2, p3]).
    Plain bookmarks with no such suffix are left as single-page groups.
    Pages within each numbered group are sorted by their bookmark number so
    the output PDF pages are always in the correct order regardless of outline order.
    """
    # (base_title) → list of (number, page_index)
    groups: OrderedDict[str, list[tuple[int, int]]] = OrderedDict()

    for title, page_index in bookmarks:
        m = _NUMBERED_RE.match(title)
        if m:
            base = m.group(1)
            num = int(m.group(2))
            groups.setdefault(base, []).append((num, page_index))
        else:
            # Plain bookmark — treat as a group of one with sort key 0.
            groups.setdefault(title, []).append((0, page_index))

    result = []
    for base, entries in groups.items():
        entries.sort(key=lambda x: x[0])
        result.append((base, [page_index for _, page_index in entries]))
    return result


def extract_pages(pdf_path: Path, output_dir: Path) -> None:
    reader = pypdf.PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    bookmarks = get_bookmarks(reader)

    if not bookmarks:
        sys.exit("Error: the PDF contains no bookmarks.")

    min_required = total_pages * 0.10
    if len(bookmarks) < min_required:
        sys.exit(
            f"Error: only {len(bookmarks)} bookmark(s) found in a {total_pages}-page PDF "
            f"({len(bookmarks)/total_pages:.1%} of pages). "
            f"At least 10% ({math.ceil(min_required)}) are required."
        )

    groups = group_bookmarks(bookmarks)
    output_dir.mkdir(parents=True, exist_ok=True)
    total_pages = len(reader.pages)

    # Attach the start page (first PDF page of each group) then sort by it so
    # we can compute where each group ends (= one page before the next starts).
    ordered = sorted(
        [(base_title, page_indices, min(page_indices)) for base_title, page_indices in groups],
        key=lambda x: x[2],
    )

    print(
        f"Found {len(bookmarks)} bookmark(s) in {len(ordered)} group(s). "
        f"Extracting to '{output_dir}' ...\n"
    )

    for i, (base_title, _page_indices, start_page) in enumerate(ordered):
        end_page = ordered[i + 1][2] - 1 if i + 1 < len(ordered) else total_pages - 1

        writer = pypdf.PdfWriter()
        for page_index in range(start_page, end_page + 1):
            writer.add_page(reader.pages[page_index])

        filename = sanitize_filename(base_title) + ".pdf"
        out_path = output_dir / filename
        with open(out_path, "wb") as f:
            writer.write(f)

        if start_page == end_page:
            suffix = f"page {start_page + 1}"
        else:
            suffix = f"pages {start_page + 1}–{end_page + 1}"
        print(f"  [OK]   '{base_title}'  →  {out_path.name}  ({suffix})")

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract one PDF page per bookmark into separate files."
    )
    parser.add_argument("pdf", type=Path, help="Path to the source PDF file")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="Directory for output files (default: <pdf-name>_bookmarks/ next to the PDF)",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        sys.exit(f"Error: '{args.pdf}' is not a file or does not exist.")

    output_dir = args.output_dir or args.pdf.parent / (args.pdf.stem + "_bookmarks")
    extract_pages(args.pdf, output_dir)


if __name__ == "__main__":
    main()
