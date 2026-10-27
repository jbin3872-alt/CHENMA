from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).parent
SITEMAP = ROOT / 'sitemap.xml'
PRODUCT_SOURCE = ROOT / 'generate_products.ps1'
PILLAR_SOURCE = ROOT / 'regenerate_pillars.ps1'
PRODUCT_DIR = ROOT / 'products'
PILLAR_FILES = ('stair-climbers.html', 'electric-forklifts.html', 'semi-electric-forklifts.html', 'lift-machines.html')

errors = []

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='replace')

def require(source, pattern, label):
    if not re.search(pattern, source, re.I | re.S):
        errors.append(f'missing source rule: {label}')

def check_source(path, patterns):
    source = read(path)
    print(f'{path.name}: source_rules={len(patterns)}')
    for label, pattern in patterns:
        require(source, pattern, f'{path.name}::{label}')

def sitemap_paths():
    sitemap = read(SITEMAP)
    return [urlparse(x).path.lstrip('/') or 'index.html' for x in re.findall(r'<loc>\s*(.*?)\s*</loc>', sitemap)]

def check_page(path, kind):
    source = read(path)
    failures = []
    if not re.search(r'<meta\s+[^>]*property=["\']og:title["\'][^>]*>', source, re.I | re.S):
        failures.append('og:title')
    if not re.search(r'<meta\s+[^>]*property=["\']og:description["\'][^>]*>', source, re.I | re.S):
        failures.append('og:description')
    if len(re.findall(r'<meta\s+[^>]*(?:name|property)=["\']twitter:card["\'][^>]*>', source, re.I | re.S)) != 1:
        failures.append('twitter:card')
    if not re.search(r'<meta\s+[^>]*name=["\']twitter:image["\'][^>]*>', source, re.I | re.S):
        failures.append('twitter:image')
    images = re.findall(r'<img\b[^>]*>', source, re.I | re.S)
    if any(not re.search(r'\balt=["\'][^"\']*["\']', image, re.I | re.S) for image in images):
        failures.append('img-alt')
    non_logo_seen = 0
    card_pages = {'index.html', 'blog/index.html', 'stair-climbers.html', 'electric-forklifts.html', 'semi-electric-forklifts.html', 'lift-machines.html'}
    for image in images:
        image_text = image.casefold()
        is_logo = 'logo' in image_text or 'h094d445ef7544ed0b8eea6b6d0d98b9bq' in image_text
        is_hero = 'hero' in image_text or 'unsplash' in image_text or 'factory image' in image_text
        is_primary = ('w-full h-96' in image_text or 'w-full h-64' in image_text or
                      'w-full h-auto' in image_text or 'max-h-96' in image_text or
                      'shadow-lg' in image_text or 'article-image' in image_text)
        first_content_image = not is_logo and non_logo_seen == 0 and path.name not in card_pages
        if not is_logo:
            non_logo_seen += 1
        if not (is_logo or is_hero or is_primary or first_content_image) and not re.search(r'\bloading=["\']lazy["\']', image, re.I | re.S):
            failures.append('lazy')
            break
    if len(re.findall(r'"@type"\s*:\s*"BreadcrumbList"', source)) != 1:
        failures.append('BreadcrumbList')
    if len(re.findall(r'<h1\b', source, re.I)) != 1:
        failures.append('h1')
    if kind == 'pillar' and re.search(r'<h4\b', source, re.I):
        failures.append('pillar-h4')
    return failures

check_source(PRODUCT_SOURCE, [
    ('OG title', r'<meta property="og:title"'),
    ('OG description', r'<meta property="og:description"'),
    ('Twitter card', r'<meta name="twitter:card"'),
    ('Twitter image', r'<meta name="twitter:image"'),
    ('related image alt', r'\$r\.name \+ \'" loading="lazy"'),
    ('footer logo alt', r'CHENMA LIFTING logo.*loading="lazy"'),
    ('BreadcrumbList', r'"@type": "BreadcrumbList"'),
    ('specification description variable', r'\$specDescription\s*=\s*\(\(\$p\.specs\s*\|\s*ForEach-Object'),
    ('Product Schema uses specification description', r'"description": "\' \+ \$desc \+ \'"'),
])
check_source(PILLAR_SOURCE, [
    ('OG title', r'<meta property="og:title"'),
    ('OG description', r'<meta property="og:description"'),
    ('Twitter card', r'<meta name="twitter:card"'),
    ('Twitter image', r'<meta name="twitter:image"'),
    ('card image lazy', r'\$p\.name \+ \'" loading="lazy"'),
    ('footer logo alt', r'CHENMA LIFTING logo.*loading="lazy"'),
    ('BreadcrumbList', r'"@type": "BreadcrumbList"'),
    ('card heading h3', r'<h3 class="font-bold'),
])

product_pages = sorted(PRODUCT_DIR.glob('*.html'))
product_failures = sum(1 for path in product_pages if check_page(path, 'product'))
pillar_failures = sum(1 for name in PILLAR_FILES if check_page(ROOT / name, 'pillar'))
print(f'product pages checked={len(product_pages)}, pages_with_rule_failures={product_failures}')
print(f'pillar pages checked={len(PILLAR_FILES)}, pages_with_rule_failures={pillar_failures}')

if product_failures or pillar_failures:
    for path in product_pages:
        failures = check_page(path, 'product')
        if failures:
            errors.append(f'{path}: {", ".join(failures)}')
    for name in PILLAR_FILES:
        failures = check_page(ROOT / name, 'pillar')
        if failures:
            errors.append(f'{name}: {", ".join(failures)}')

print(f'generated pages checked={len(product_pages) + len(PILLAR_FILES)}, generated pages passing={len(product_pages) + len(PILLAR_FILES) - product_failures - pillar_failures}')
if errors:
    print(f'CONSISTENCY_ERRORS: {len(errors)}')
    for error in errors:
        print(error)
    sys.exit(1)
print('SOURCE_PRODUCT_CONSISTENCY_OK: True')
