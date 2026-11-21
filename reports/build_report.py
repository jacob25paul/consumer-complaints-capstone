"""Build reports/project_report.pdf from reports/project_report.md.

Markdown -> HTML (python-markdown) -> PDF (headless Google Chrome, which is already installed on most machines).
No LaTeX or pandoc needed.

    python reports/build_report.py                # uses Chrome at its default macOS location
    CHROME="/path/to/chrome" python reports/build_report.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
SRC = HERE / "project_report.md"
OUT = HERE / "project_report.pdf"

CSS = """
@page { size: A4; margin: 18mm 17mm 18mm 17mm; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 10.2pt; line-height: 1.42; color: #1d1d1f; }
h1 { font-size: 20pt; margin: 0 0 4pt 0; line-height: 1.2; }
h2 { font-size: 13.5pt; margin: 16pt 0 5pt 0; padding-bottom: 2pt; border-bottom: 1.5px solid #4C78A8; break-after: avoid; }
h3 { font-size: 11pt; margin: 11pt 0 4pt 0; break-after: avoid; }
p, li { margin: 3pt 0; }
ul, ol { margin: 3pt 0 3pt 0; padding-left: 16pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 8pt 0; font-size: 8.6pt; break-inside: avoid; }
th, td { border: 1px solid #c8ccd2; padding: 2.5pt 4.5pt; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
td.num, th.num { text-align: right; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.6pt; background: #f3f4f6; padding: 0 2px; border-radius: 2px; }
figure { margin: 8pt 0 10pt 0; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 112mm; }
figcaption { font-size: 8.6pt; color: #555; margin-top: 3pt; text-align: left; }
blockquote { margin: 6pt 0; padding: 4pt 8pt; background: #f6f8fb; border-left: 3px solid #4C78A8; }
.subtitle { color: #555; margin-bottom: 10pt; }
.pagebreak { break-before: page; }
"""


def find_chrome():
    candidates = [os.environ.get("CHROME"),
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chrome")]
    for c in candidates:
        if c and Path(c).exists():
            return c
    sys.exit("Google Chrome / Chromium not found. Set the CHROME environment variable to its executable.")


def main():
    body = markdown.markdown(SRC.read_text(encoding="utf-8"), extensions=["tables", "attr_list", "md_in_html", "sane_lists"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>Project report</title><style>{CSS}</style></head><body>{body}</body></html>"
    # The HTML is written next to the Markdown so that relative image paths (figures/...) resolve; it is removed afterwards.
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=HERE, delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={OUT}", tmp.as_uri()],
                       check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"Wrote {OUT.relative_to(HERE.parent)} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
