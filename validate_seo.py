from pathlib import Path
from urllib.parse import urlparse
import html as html_lib
import re
import sys

ROOT = Path(__file__).parent
BASE = 'https://www.chenmalifting.com/'
SITEMAP = ROOT / 'sitemap.xml'

errors = []

def read(path):
    return path.read_text(encoding='utf-8', errors='replace')

sitemap = read(SITEMAP)
locs = [x.strip() for x in re.findall(r'<loc>\s*(.*?)\s*</loc>', sitemap, re.S)]
if len(locs) != 67:
    errors.append(f'Sitemap URL count is {len(locs)}, expected 67')

sitemap_paths = []
for loc in locs:
    parsed = urlparse(loc)
    rel = parsed.path.lstrip('/') or 'index.html'
    sitemap_paths.append(rel)
    expected_loc = BASE if rel == 'index.html' else BASE + rel
    if loc != expected_loc:
        errors.append(f'Sitemap URL is not canonical www URL: {loc}')
    if parsed.query or parsed.fragment:
        errors.append(f'Sitemap URL has query or fragment: {loc}')

# Every sitemap HTML page and every existing blog page must have metadata.
required = sorted(set(sitemap_paths) | {p.relative_to(ROOT).as_posix() for p in (ROOT / 'blog').glob('*.html')})
titles = {}
for rel in required:
    path = ROOT / rel
    if not path.exists():
        errors.append(f'Sitemap/blog file missing: {rel}')
        continue
    source = read(path)
    title_match = re.search(r'<title>(.*?)</title>', source, re.I | re.S)
    title = html_lib.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip()) if title_match else ''
    desc_match = re.search(r'<meta\s+[^>]*name=["\']description["\'][^>]*>', source, re.I | re.S)
    desc_content = ''
    if desc_match:
        content_match = re.search(r'content=["\'](.*?)["\']', desc_match.group(0), re.I | re.S)
        desc_content = html_lib.unescape(content_match.group(1).strip()) if content_match else ''
    canon_match = re.search(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*>', source, re.I | re.S)
    canonical = ''
    if canon_match:
        href_match = re.search(r'href=["\'](.*?)["\']', canon_match.group(0), re.I | re.S)
        canonical = href_match.group(1).strip() if href_match else ''
    expected = BASE if rel == 'index.html' else BASE + rel
    if not title:
        errors.append(f'Missing title: {rel}')
    elif len(title) > 65:
        errors.append(f'Title too long ({len(title)}): {rel} -> {title}')
    titles.setdefault(title.casefold(), []).append(rel)
    if not desc_content:
        errors.append(f'Missing description: {rel}')
    elif not (80 <= len(desc_content) <= 180):
        errors.append(f'Description length {len(desc_content)} outside 80-180: {rel}')
    if canonical != expected:
        errors.append(f'Canonical mismatch: {rel} -> {canonical!r}, expected {expected!r}')
    if 'https://chenmalifting.com/' in source:
        errors.append(f'Bare-domain URL remains in: {rel}')

for title, pages in titles.items():
    if title and len(pages) > 1:
        errors.append(f'Duplicate title ({len(pages)}): {title} -> {", ".join(pages)}')

robots = ROOT / 'robots.txt'
if robots.exists() and 'Sitemap: https://www.chenmalifting.com/sitemap.xml' not in read(robots):
    errors.append('robots.txt Sitemap does not point to the www sitemap')

print(f'Sitemap URLs: {len(locs)}')
print(f'Pages checked: {len(required)}')
print(f'Unique titles: {len([x for x in titles if x])}')
if errors:
    print(f'ERRORS: {len(errors)}')
    for error in errors:
        print(error)
    sys.exit(1)
print('ALL SEO OK: True')
