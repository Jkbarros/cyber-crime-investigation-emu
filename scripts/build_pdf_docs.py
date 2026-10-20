#!/usr/bin/env python3
"""Build markdown for mitigation examination PDF."""

from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "canvas-submissions"
SHOTS = ROOT / "docs" / "screenshots"
DOCS = ROOT / "docs"

PDF_NAME = "Examination of the Event and How It Could Have Been Mitigate.pdf"
OUT_NAME = "examination-event-mitigation.md"


def slugify(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")[:80]


def main() -> None:
    pdf = ARCHIVE / PDF_NAME
    if not pdf.exists():
        print(f"missing {PDF_NAME}")
        return

    SHOTS.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(pdf)
    base = slugify(pdf.stem)
    for pi, page in enumerate(reader.pages, start=1):
        for ii, img in enumerate(page.images, start=1):
            ext = ".png" if img.name.lower().endswith(".png") else ".jpg"
            (SHOTS / f"{base}-p{pi}-img{ii}{ext}").write_bytes(img.data)

    rel = pdf.relative_to(ROOT).as_posix().replace(" ", "%20")
    lines: list[str] = [
        f"# {pdf.stem}",
        "",
        f"**Source:** [`{pdf.name}`](../{rel})  ",
        "**Course:** Cyber Crime Investigation (EMU)  ",
        "**Author:** Julio Barros",
        "",
    ]
    for pi, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        imgs = sorted(p.name for p in SHOTS.glob(f"{base}-p{pi}-img*"))
        if text or imgs:
            lines.extend([f"## Page {pi}", ""])
        if text:
            lines.append(text)
            lines.append("")
        for img in imgs:
            lines.append(f"![{pdf.stem} page {pi}](screenshots/{img})")
            lines.append("")

    (DOCS / OUT_NAME).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"wrote docs/{OUT_NAME}")


if __name__ == "__main__":
    main()
