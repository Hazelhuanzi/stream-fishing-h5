"""Extract readable text from a WordprocessingML document.xml.

Usage:
    py -I tools/docx_to_text.py path/to/document.xml > out.txt

Only paragraphs and table cells are emitted, each on its own line; the
original order is preserved. This is a read-only helper for reviewing a
.docx without opening Word.
"""

import sys
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def paragraph_text(p):
    parts = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            parts.append(node.text or "")
        elif node.tag == f"{{{W}}}tab":
            parts.append("\t")
        elif node.tag == f"{{{W}}}br":
            parts.append("\n")
    return "".join(parts)


def main(path):
    root = ET.parse(path).getroot()
    body = root.find(f"{{{W}}}body")
    lines = []
    for p in body.iter(f"{{{W}}}p"):
        text = paragraph_text(p).strip()
        if text:
            lines.append(text)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
