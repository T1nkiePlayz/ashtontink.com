#!/usr/bin/env python3
"""Static checks for the www_website repo."""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "source", "track", "wbr",
}

problems = []


class Checker(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.classes = set()
        self.links = []
        self.ids = []
        self.has_title = False
        self.has_desc = False
        self.canonical = None
        self.lang = None
        self.viewport = False
        self.main_id = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self.has_title = True
        if tag == "meta" and a.get("name") == "description":
            self.has_desc = True
        if tag == "meta" and a.get("name") == "viewport":
            self.viewport = True
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if "class" in a:
            self.classes.update(a["class"].split())
        if "id" in a:
            self.ids.append(a["id"])
            if tag == "main" and a["id"] == "main":
                self.main_id = True
        if tag in ("a", "link", "script", "img"):
            for k in ("href", "src"):
                if a.get(k):
                    self.links.append((k, a[k]))
        if tag == "a":
            if not a.get("href"):
                problems.append(f"{self.path}: <a> without href")
            href = a.get("href", "")
            if href.startswith("http") and "ashtontink.com" not in href and "github.com" not in href:
                if "rel" not in a or "noopener" not in a["rel"]:
                    problems.append(f"{self.path}: external link missing rel=noopener: {href}")
            if href.startswith("http") and a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                problems.append(f"{self.path}: target=_blank without noopener: {href}")
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            problems.append(f"{self.path}:{self.getpos()[0]}: stray </{tag}>")
            return
        open_tag, pos = self.stack.pop()
        if open_tag != tag:
            problems.append(
                f"{self.path}:{self.getpos()[0]}: </{tag}> closes <{open_tag}> opened at line {pos[0]}"
            )


# --- gather files ---
html_files, css_files = [], []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d != ".git"]
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        if fn.endswith(".html"):
            html_files.append(p)
        elif fn.endswith(".css"):
            css_files.append(p)

rel = lambda p: os.path.relpath(p, ROOT)

# --- HTML checks ---
all_classes = set()
for path in sorted(html_files):
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    c = Checker(rel(path))
    c.feed(src)
    c.close()
    if c.stack:
        problems.append(f"{rel(path)}: unclosed tags: {[t for t, _ in c.stack]}")
    if not c.has_title:
        problems.append(f"{rel(path)}: missing <title>")
    if not c.has_desc and "404" not in path:
        problems.append(f"{rel(path)}: missing meta description")
    if not c.lang:
        problems.append(f"{rel(path)}: missing lang attribute")
    if not c.viewport:
        problems.append(f"{rel(path)}: missing viewport")
    if not c.main_id and "404" not in path:
        problems.append(f"{rel(path)}: missing <main id=\"main\"> for skip link")
    if len(c.ids) != len(set(c.ids)):
        dupes = {i for i in c.ids if c.ids.count(i) > 1}
        problems.append(f"{rel(path)}: duplicate ids: {dupes}")
    # link resolution
    for attr, href in c.links:
        if href.startswith(("http", "mailto:", "#", "//")):
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        full = os.path.join(ROOT, target.lstrip("/"))
        if target.endswith("/"):
            full = os.path.join(full, "index.html")
        if not os.path.exists(full):
            problems.append(f"{rel(path)}: broken internal link {href}")
    all_classes |= c.classes

# --- CSS checks ---
css_classes = set()
for path in sorted(css_files):
    with open(path, encoding="utf-8") as fh:
        css = fh.read()
    name = rel(path)
    if "```" in css:
        problems.append(f"{name}: markdown code fence (```) present — {css.count('```')} occurrence(s)")
    if css.count("{") != css.count("}"):
        problems.append(f"{name}: unbalanced braces {{ {css.count('{')} vs }} {css.count('}')}")
    css_classes.update(re.findall(r"\.([A-Za-z][\w-]*)", css))

# classes used in HTML but not defined in CSS
missing = sorted(c for c in all_classes - css_classes if not c.startswith("js-"))
if missing:
    problems.append(f"classes used in HTML with no CSS rule: {missing}")

unused = sorted(c for c in css_classes - all_classes if not c.startswith(("a", "h", "p")) )
# keep this informational only
print(f"HTML files : {len(html_files)}")
print(f"CSS rules  : {len(css_classes)} classes")
print(f"HTML classes: {len(all_classes)}")
print(f"unused CSS classes (info): {unused}")

if problems:
    print("\nPROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("\nAll checks passed.")
