from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(frozen=True)
class PdfDateReplaceResult:
    replacements: int
    pages_changed: int
    pages_total: int


def _is_same_label(manufacture_rect: fitz.Rect, expiry_rect: fitz.Rect) -> bool:
    """Match date fields that belong to the same visual label.

    Labels can be repeated several times on one PDF page. Manufacture and expiry
    dates on one label are normally close vertically, while the next label starts
    much farther away. The horizontal guard also prevents accidental cross-column
    matches when a page contains several labels side by side.
    """
    vertical_distance = abs(manufacture_rect.y0 - expiry_rect.y0)
    horizontal_distance = abs(manufacture_rect.x0 - expiry_rect.x0)
    return vertical_distance <= 90 and horizontal_distance <= 260


def replace_expiry_date(
    source_path: str | Path,
    output_path: str | Path,
    manufacture_date: str,
    current_expiry_date: str,
    new_expiry_date: str,
) -> PdfDateReplaceResult:
    """Replace expiry dates only on labels with the requested manufacture date.

    Dates must already exist in the PDF text layer and are expected in DD.MM.YYYY
    form. DataMatrix and barcode graphics are not modified.
    """
    source_path = Path(source_path)
    output_path = Path(output_path)

    document = fitz.open(source_path)
    replacements = 0
    pages_changed = 0

    try:
        for page in document:
            manufacture_hits = page.search_for(manufacture_date)
            if not manufacture_hits:
                continue

            expiry_hits = page.search_for(current_expiry_date)
            if not expiry_hits:
                continue

            targets = [
                expiry_rect
                for expiry_rect in expiry_hits
                if any(_is_same_label(manufacture_rect, expiry_rect) for manufacture_rect in manufacture_hits)
            ]
            if not targets:
                continue

            # First remove the old text. A very small horizontal/vertical padding
            # hides antialiasing remnants without touching neighbouring labels.
            for rect in targets:
                padded = fitz.Rect(rect.x0 - 1.5, rect.y0 - 1.0, rect.x1 + 2.0, rect.y1 + 1.0)
                page.add_redact_annot(padded, fill=(1, 1, 1))
            page.apply_redactions()

            # Date strings have the same length, so reusing the original rectangle
            # gives a stable visual result. Helvetica is used as a safe PDF core font.
            for rect in targets:
                font_size = max(6.0, rect.height * 0.78)
                page.insert_text(
                    (rect.x0, rect.y1 - 1.0),
                    new_expiry_date,
                    fontsize=font_size,
                    fontname='helv',
                    color=(0, 0, 0),
                    overlay=True,
                )

            replacements += len(targets)
            pages_changed += 1

        document.save(output_path, garbage=3, deflate=True)
        return PdfDateReplaceResult(
            replacements=replacements,
            pages_changed=pages_changed,
            pages_total=document.page_count,
        )
    finally:
        document.close()
