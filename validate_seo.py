from pathlib import Path
from urllib.parse import urlparse
import html as html_lib
import re
import subprocess
import sys
import datetime as dt
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent
BASE = 'https://www.chenmalifting.com/'
SITEMAP = ROOT / 'sitemap.xml'
# No language variants are currently published. Any hreflang tag is therefore invalid.
REAL_LANGUAGE_URLS = set()

errors = []
hreflang_pages = 0
hreflang_tags = 0
hreflang_invalid = 0

def read(path):
    return path.read_text(encoding='utf-8', errors='replace')

sitemap = read(SITEMAP)
try:
    sitemap_root = ET.parse(SITEMAP).getroot()
except (OSError, ET.ParseError) as exc:
    errors.append(f'Sitemap XML invalid: {exc}')
    sitemap_root = None
locs = [x.strip() for x in re.findall(r'<loc>\s*(.*?)\s*</loc>', sitemap, re.S)]
if sitemap_root is not None and sitemap_root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
    errors.append(f'Unexpected Sitemap root element: {sitemap_root.tag}')
expected_sitemap_count = len(list(ROOT.glob('*.html'))) + len(list((ROOT / 'products').glob('*.html'))) + len(list((ROOT / 'blog').glob('*.html'))) - 1
if len(locs) != expected_sitemap_count:
    errors.append(f'Sitemap URL count is {len(locs)}, expected {expected_sitemap_count}')

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
    hreflang_matches = re.findall(r'<link\s+[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']([^"\']+)["\'][^>]*>', source, re.I | re.S)
    hreflang_matches += re.findall(r'<link\s+[^>]*hreflang=["\']([^"\']+)["\'][^>]*rel=["\']alternate["\'][^>]*>', source, re.I | re.S)
    if hreflang_matches:
        hreflang_pages += 1
        hreflang_tags += len(hreflang_matches)
        for language_url in hreflang_matches:
            if language_url not in REAL_LANGUAGE_URLS:
                hreflang_invalid += 1
                errors.append(f'Invalid hreflang without published language URL: {rel} -> {language_url}')
    title_match = re.search(r'<title>(.*?)</title>', source, re.I | re.S)
    title = html_lib.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip()) if title_match else ''
    desc_tags = re.findall(r'<meta\s+[^>]*name=["\']description["\'][^>]*>', source, re.I | re.S)
    if len(desc_tags) != 1:
        errors.append(f'Meta Description tag count is {len(desc_tags)}, expected 1: {rel}')
    desc_content = ''
    if desc_tags:
        desc_tag = desc_tags[0]
        if '<meta' in desc_tag.lower()[1:] or 'content=<meta' in desc_tag.lower():
            errors.append(f'Malformed nested Meta Description tag: {rel}')
        content_match = re.search(r'content=["\'](.*?)["\']', desc_tag, re.I | re.S)
        desc_content = html_lib.unescape(content_match.group(1).strip()) if content_match else ''
        if not content_match or re.search(r'(?:follow|css\.com|s\.com)\\s*["\']?\\s*>?$', desc_tag, re.I):
            errors.append(f'Malformed Meta Description attributes: {rel}')
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
    twitter_card = re.findall(r'<meta\s+[^>]*(?:name|property)=["\']twitter:card["\'][^>]*>', source, re.I | re.S)
    if len(twitter_card) != 1:
        errors.append(f'Twitter Card tag count is {len(twitter_card)}, expected 1: {rel}')
    for twitter_name in ('twitter:title', 'twitter:description', 'twitter:image'):
        if not re.search(r'<meta\s+[^>]*name=["\']' + re.escape(twitter_name) + r'["\'][^>]*>', source, re.I | re.S):
            errors.append(f'Missing {twitter_name}: {rel}')
    for og_name in ('og:title', 'og:description'):
        if not re.search(r'<meta\s+[^>]*property=["\']' + re.escape(og_name) + r'["\'][^>]*>', source, re.I | re.S):
            errors.append(f'Missing {og_name}: {rel}')
    images = re.findall(r'<img\b[^>]*>', source, re.I | re.S)
    non_logo_seen = 0
    card_pages = {'index.html', 'blog/index.html', 'stair-climbers.html', 'electric-forklifts.html', 'semi-electric-forklifts.html', 'lift-machines.html'}
    for image in images:
        if not re.search(r'\balt=["\'][^"\']*["\']', image, re.I | re.S):
            errors.append(f'Missing image alt: {rel}')
        image_text = image.casefold()
        is_logo = 'logo' in image_text or 'h094d445ef7544ed0b8eea6b6d0d98b9bq' in image_text
        is_hero = 'hero' in image_text or 'unsplash' in image_text or 'factory image' in image_text
        is_primary = ('w-full h-96' in image_text or 'w-full h-64' in image_text or
                      'w-full h-auto' in image_text or 'max-h-96' in image_text or
                      'shadow-lg' in image_text or 'article-image' in image_text)
        first_content_image = not is_logo and non_logo_seen == 0 and rel not in card_pages
        if not is_logo:
            non_logo_seen += 1
        if not (is_logo or is_hero or is_primary or first_content_image) and not re.search(r'\bloading=["\']lazy["\']', image, re.I | re.S):
            errors.append(f'Non-primary/card image missing loading=lazy: {rel}')
    h1_count = len(re.findall(r'<h1\b', source, re.I))
    if h1_count != 1:
        errors.append(f'H1 count is {h1_count}, expected 1: {rel}')
    if re.search(r'<meta\s+[^>]*name=["\']keywords["\'][^>]*>', source, re.I | re.S):
        errors.append(f'Meta keywords remains: {rel}')
    breadcrumb_count = len(re.findall(r'"@type"\s*:\s*"BreadcrumbList"', source))
    if rel != 'index.html' and breadcrumb_count != 1:
        errors.append(f'BreadcrumbList count is {breadcrumb_count}, expected 1: {rel}')
    if breadcrumb_count > 1:
        errors.append(f'Duplicate BreadcrumbList ({breadcrumb_count}): {rel}')
    heading_levels = [int(x) for x in re.findall(r'<h([1-6])\b', source, re.I)]
    for previous, current in zip(heading_levels, heading_levels[1:]):
        if current - previous > 1:
            errors.append(f'Heading level jump h{previous}->h{current}: {rel}')
            break
    if re.search(r'(?<!www\.)https://chenmalifting\.com(?:/|["\'])', source):
        errors.append(f'Bare-domain URL remains in: {rel}')

for title, pages in titles.items():
    if title and len(pages) > 1:
        errors.append(f'Duplicate title ({len(pages)}): {title} -> {", ".join(pages)}')

robots = ROOT / 'robots.txt'
if robots.exists() and 'Sitemap: https://www.chenmalifting.com/sitemap.xml' not in read(robots):
    errors.append('robots.txt Sitemap does not point to the www sitemap')

# Sitemap lastmod must be a valid ISO date and cannot be in the future.
today = dt.date.today()
for loc, lastmod in re.findall(r'<url>\s*<loc>\s*(.*?)\s*</loc>\s*<lastmod>\s*(.*?)\s*</lastmod>', sitemap, re.S):
    rel = urlparse(loc).path.lstrip('/') or 'index.html'
    try:
        parsed_lastmod = dt.date.fromisoformat(lastmod)
    except ValueError:
        errors.append(f'Invalid Sitemap lastmod: {rel} -> {lastmod}')
        continue
    if parsed_lastmod > today:
        errors.append(f'Future Sitemap lastmod: {rel} -> {lastmod}, today {today.isoformat()}')

print(f'Sitemap URLs: {len(locs)}')
print(f'Pages checked: {len(required)}')
print(f'Unique titles: {len([x for x in titles if x])}')
print(f'hreflang check: pages_with_tags={hreflang_pages}, tags={hreflang_tags}, invalid={hreflang_invalid}, published_language_urls={len(REAL_LANGUAGE_URLS)}')
if errors:
    print(f'ERRORS: {len(errors)}')
    for error in errors:
        print(error)
    sys.exit(1)
print('ALL SEO OK: True')
