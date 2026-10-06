from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASE = "https://www.chenmalifting.com/"
# Redirect fixtures: legacy URLs must stay out of site links and Sitemap,
# but each must retain one explicit 301 rule in _redirects.
REDIRECT_FIXTURES = (
    ("cmlm-e02-mobile-channel-steel-lift-30000kg.html", "cmlm-e02-mobile-channel-steel-lift-300500kg.html"),
    ("cmlm-h11-hydraulic-table-lift-15000kg.html", "cmlm-h11-hydraulic-table-lift-150300kg.html"),
    ("cmlm-e14-electric-hoist-winch-30000kg.html", "cmlm-e14-electric-hoist-winch-300500kg.html"),
)
PRODUCTS = sorted((ROOT / "products").glob("*.html"))
HTML_FILES = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html")) + PRODUCTS
errors = []

for path in HTML_FILES:
    text = path.read_text(encoding="utf-8-sig")
    for old, _new in REDIRECT_FIXTURES:
        if old in text:
            errors.append(f"{path.relative_to(ROOT)}: legacy redirect slug leaked into site content: {old}")
    for url in re.findall(r"https?://[^\"'\\s<>]+", text):
        if "chenmalifting.com" in url and url not in (BASE.rstrip("/"), BASE) and not url.startswith(BASE):
            errors.append(f"{path.relative_to(ROOT)}: non-canonical site URL {url}")
    for href in re.findall(r"(?:href|src)=\"([^\"]+)\"", text):
        if href == "products/${productPath(p.id)}":
            continue
        if href.startswith(("products/", "../products/", "./products/")) and not href.split("?", 1)[0].endswith(".html"):
            errors.append(f"{path.relative_to(ROOT)}: product link lacks .html ({href})")
    if path == ROOT / "index.html" and "products/${productPath(p.id)}" not in text:
        errors.append("index.html: dynamic product link template is missing")
    if path in PRODUCTS:
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not canonical or not canonical.group(1).startswith(BASE):
            errors.append(f"{path.relative_to(ROOT)}: missing canonical URL")
        elif not canonical.group(1).endswith(f"/products/{path.name}"):
            errors.append(f"{path.relative_to(ROOT)}: canonical does not match filename")

redirects = ROOT / "_redirects"
redirect_text = redirects.read_text(encoding="utf-8-sig") if redirects.exists() else ""
for old, new in REDIRECT_FIXTURES:
    fixture = rf"^/products/{re.escape(old)} /products/{re.escape(new)} 301$"
    if not re.search(fixture, redirect_text, re.M):
        errors.append(f"_redirects: missing redirect fixture /products/{old} -> /products/{new}")

sitemap = ROOT / "sitemap.xml"
try:
    tree = ET.parse(sitemap)
    root = tree.getroot()
except (OSError, ET.ParseError) as exc:
    errors.append(f"sitemap.xml: invalid XML ({exc})")
else:
    locs = [node.text or "" for node in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    for old, _new in REDIRECT_FIXTURES:
        if any(old in loc for loc in locs):
            errors.append(f"sitemap.xml: legacy redirect slug leaked into Sitemap: {old}")
    for loc in locs:
        if "chenmalifting.com" in loc and not loc.startswith(BASE):
            errors.append(f"sitemap.xml: non-canonical URL {loc}")
        if loc.startswith(BASE + "products/") and not loc.endswith(".html"):
            errors.append(f"sitemap.xml: product URL lacks .html {loc}")

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

print(f"URL validation passed: {len(PRODUCTS)} product pages, 40 homepage targets, valid sitemap and redirects.")
