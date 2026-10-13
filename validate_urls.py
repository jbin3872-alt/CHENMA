from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = "https://www.chenmalifting.com/"
REDIRECT_FIXTURES = (
    ("cmlm-e02-mobile-channel-steel-lift-30000kg.html", "cmlm-e02-mobile-channel-steel-lift-300500kg.html"),
    ("cmlm-h11-hydraulic-table-lift-15000kg.html", "cmlm-h11-hydraulic-table-lift-150300kg.html"),
    ("cmlm-e14-electric-hoist-winch-30000kg.html", "cmlm-e14-electric-hoist-winch-300500kg.html"),
)
HTML_FILES = sorted(set(ROOT.glob("*.html")) | set((ROOT / "blog").rglob("*.html")) | set((ROOT / "products").rglob("*.html")))
errors = []

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.jsonld = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "content"):
            value = attrs.get(key)
            if value and (key == "href" or attrs.get("property") == "og:url"):
                self.links.append((value, self.getpos()[0], key))
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self._jsonld_start = True
            self._jsonld_buffer = []

    def handle_data(self, data):
        if getattr(self, "_jsonld_start", False):
            self._jsonld_buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and getattr(self, "_jsonld_start", False):
            raw = "".join(self._jsonld_buffer).strip()
            if raw:
                self.jsonld.append((raw, self.getpos()[0]))
            self._jsonld_start = False


def internal_target(value, page):
    value = value.strip()
    if value == "products/${productPath(p.id)}":
        return None
    if value.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        if parsed.netloc.lower() not in {"www.chenmalifting.com", "chenmalifting.com"}:
            return None
        if parsed.netloc.lower() == "chenmalifting.com":
            errors.append(f"{page.relative_to(ROOT)}: bare-domain URL at internal target: {value}")
        path = parsed.path
    elif parsed.scheme or parsed.netloc:
        return None
    else:
        path = urljoin("/" + page.relative_to(ROOT).as_posix(), value).split("?", 1)[0].split("#", 1)[0]
    path = unquote(path).lstrip("/")
    if not path or path.endswith("/"):
        return None
    return Path(path)

for page in HTML_FILES:
    source = page.read_text(encoding="utf-8-sig")
    parser = LinkParser()
    try:
        parser.feed(source)
    except Exception as exc:
        errors.append(f"{page.relative_to(ROOT)}: HTML parse error: {exc}")
    for value, line, _kind in parser.links:
        target = internal_target(value, page)
        if target is None:
            continue
        if target.suffix != ".html":
            errors.append(f"{page.relative_to(ROOT)}:{line}: internal page URL lacks .html: {value}")
        target_path = ROOT / target
        if target.suffix == ".html" and not target_path.exists():
            errors.append(f"{page.relative_to(ROOT)}:{line}: internal target does not exist: {value}")
    for raw, line in parser.jsonld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{page.relative_to(ROOT)}:{line}: invalid JSON-LD: {exc}")
            continue
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                for key, value in item.items():
                    if key in {"url", "@id"} and isinstance(value, str):
                        target = internal_target(value, page)
                        if target is not None and target.suffix == ".html" and not (ROOT / target).exists():
                            errors.append(f"{page.relative_to(ROOT)}:{line}: JSON-LD target does not exist: {value}")
                    elif isinstance(value, (dict, list)):
                        stack.append(value)
            elif isinstance(item, list):
                stack.extend(item)

for old, _new in REDIRECT_FIXTURES:
    for page in HTML_FILES:
        if old in page.read_text(encoding="utf-8-sig"):
            errors.append(f"{page.relative_to(ROOT)}: redirect fixture leaked into site content: {old}")

redirect_text = (ROOT / "_redirects").read_text(encoding="utf-8-sig") if (ROOT / "_redirects").exists() else ""
for old, new in REDIRECT_FIXTURES:
    fixture = rf"^/products/{re.escape(old)} /products/{re.escape(new)} 301$"
    if not re.search(fixture, redirect_text, re.M):
        errors.append(f"_redirects: missing redirect fixture /products/{old} -> /products/{new}")

sitemap = ROOT / "sitemap.xml"
try:
    tree = ET.parse(sitemap)
    root = tree.getroot()
except (OSError, ET.ParseError) as exc:
    errors.append(f"sitemap.xml: invalid XML: {exc}")
    locs = []
else:
    locs = [node.text or "" for node in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    for loc in locs:
        parsed = urlparse(loc)
        if parsed.netloc.lower() == "chenmalifting.com":
            errors.append(f"sitemap.xml: bare-domain URL: {loc}")
        if parsed.netloc.lower() == "www.chenmalifting.com" and (parsed.query or parsed.fragment):
            errors.append(f"sitemap.xml: query or fragment: {loc}")
        if parsed.netloc.lower() == "www.chenmalifting.com" and parsed.path not in {"", "/"} and not parsed.path.endswith(".html"):
            errors.append(f"sitemap.xml: page URL lacks .html: {loc}")
        if any(old in loc for old, _new in REDIRECT_FIXTURES):
            errors.append(f"sitemap.xml: redirect fixture leaked into Sitemap: {loc}")

index = (ROOT / "index.html").read_text(encoding="utf-8-sig")
product_paths = re.findall(r'\d+: "([^"]+\.html)"', index)
if len(product_paths) != 40:
    errors.append(f"index.html: expected 40 product paths, found {len(product_paths)}")
for rel in product_paths:
    if not (ROOT / "products" / rel).exists():
        errors.append(f"index.html: missing product target products/{rel}")

if errors:
    print("URL validation failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"URL validation passed: {len(HTML_FILES)} HTML pages, {len(product_paths)} homepage targets, {len(locs)} Sitemap URLs, valid redirects.")
