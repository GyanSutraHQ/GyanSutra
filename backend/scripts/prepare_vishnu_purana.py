"""Rebuild the complete canonical translation from the public-domain raw text."""

import argparse
import json
import re
from pathlib import Path

from gyansutra.config import ROOT

EXPECTED = [22, 16, 18, 24, 38, 8]


def paragraphs(value):
    return [
        re.sub(r"\s+", " ", p).strip()
        for p in re.split(r"\n\s*\n", value.replace("\r", ""))
        if p.strip()
    ]


def prepare(input_path, output_path):
    text = input_path.read_text().replace("\r", "")
    marker = "\nPART I.\n\nSECTION I.\n"
    body_start = text.find(marker, text.find("PART I.") + 1) + 1
    if body_start <= 0:
        raise ValueError("Could not locate the canonical body.")
    toc, current = [], None
    for line in text[text.find("PART I.") : body_start].splitlines():
        line = line.strip()
        match = re.match(r"^Section\s+[IVXLC]+(?:\.?[—:-]|\.)\s*(.*)$", line, re.I)
        if match:
            if current is not None:
                toc.append(" ".join(current))
            current = [match[1]]
        elif current is not None and line and not re.fullmatch(r"PART\s+[IVXLC]+[.:]?", line, re.I):
            current.append(line)
    if current is not None:
        toc.append(" ".join(current))
    if len(toc) != sum(EXPECTED):
        raise ValueError(f"Expected 126 contents entries; found {len(toc)}.")
    notes = {
        m[1]: "\n\n".join(paragraphs(m[2]))
        for m in re.finditer(
            r"^\[(\d+)\]\s+([\s\S]*?)(?=^\[\d+\]\s+|^\*\*\* END OF THE PROJECT GUTENBERG EBOOK)",
            text[body_start:],
            re.M,
        )
    }
    footnote_start = text.find("\n[1] This mystic monosyllable", body_start)
    body = text[body_start : footnote_start if footnote_start > body_start else None]
    part_matches = list(re.finditer(r"^PART\s+([IVXLC]+)\.\s*$", body, re.M))
    if len(part_matches) != 6:
        raise ValueError("Expected six parts.")
    data = json.loads((ROOT / "data/vishnu-purana.json").read_text())
    cursor = 0
    for p, part in enumerate(data["parts"]):
        part_text = body[
            part_matches[p].end() : part_matches[p + 1].start() if p + 1 < 6 else None
        ].lstrip()
        matches = list(re.finditer(r"^SECTION\s+([IVXLC]+)\.\s*$", part_text, re.M))
        if len(matches) != EXPECTED[p]:
            raise ValueError(f"Part {p + 1}: unexpected section count.")
        sections = []
        for s, match in enumerate(matches):
            raw = part_text[
                match.end() : matches[s + 1].start() if s + 1 < len(matches) else None
            ].lstrip()
            raw = re.sub(
                r"\s*THE END OF PART [IVXLC]+\.\s*$|\s*FINIS\.\s*$", "", raw, flags=re.I
            ).strip()
            synopsis = re.sub(r"\s+", " ", toc[cursor]).strip()
            cursor += 1
            title = (
                re.split(r"(?<=[.!?])\s|;|:\s", synopsis)[0].rstrip(".").strip()
                or f"Section {s + 1}"
            )
            title = title if len(title) <= 92 else title[:89].strip() + "…"
            refs = list(dict.fromkeys(re.findall(r"\[(\d+)\]", raw)))
            sections.append(
                {
                    "id": f"vishnu-purana_{p + 1}_{s + 1}",
                    "partNumber": p + 1,
                    "sectionNumber": s + 1,
                    "title": title,
                    "synopsis": synopsis,
                    "paragraphs": paragraphs(raw),
                    "footnotes": [{"number": int(n), "text": notes[n]} for n in refs if n in notes],
                }
            )
        part.update(sectionCount=len(sections), sections=sections)
    data.update(partCount=len(data["parts"]), sectionCount=cursor)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {cursor} sections to {output_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/raw/vishnu-purana/dutt-1894.txt",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "data/vishnu-purana.json")
    args = parser.parse_args()
    prepare(args.input, args.output)
