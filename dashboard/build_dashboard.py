"""Injects data.json into template.html -> walmart_dashboard.html (artifact) and index.html (standalone, e.g. GitHub Pages)."""
from pathlib import Path
here = Path(__file__).parent
page = (here / "template.html").read_text().replace("/*__DATA__*/null", (here / "data.json").read_text())
(here / "walmart_dashboard.html").write_text(page)
(here / "index.html").write_text('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'
                                 '<style>body{margin:0}[hidden]{display:none!important}</style></head><body>\n' + page + "\n</body></html>\n")
print("built")
