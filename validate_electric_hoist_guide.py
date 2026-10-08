from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "blog" / "electric-hoist-winch-buying-guide.html"
SITEMAP = ROOT / "sitemap.xml"
PRODUCT_FILES = {
    "CMLM-E05": ROOT / "products" / "cmlm-e05-wire-rope-hoist-lift-230kg-42m.html",
    "CMLM-E06": ROOT / "products" / "cmlm-e06-mini-crane-electric-hoist-05-ton.html",
    "CMLM-E14": ROOT / "products" / "cmlm-e14-electric-hoist-winch-300500kg.html",
}
EXPECTED_LINKS = [
    "../products/cmlm-e05-wire-rope-hoist-lift-230kg-42m.html",
    "../products/cmlm-e06-mini-crane-electric-hoist-05-ton.html",
    "../products/cmlm-e14-electric-hoist-winch-300500kg.html",
]
FAQ = {
    "What is the difference between a wire rope hoist and a winch?": "A wire rope hoist is a lifting device category that raises a suspended load with wire rope. A winch is a broader pulling or lifting device whose suitability depends on the specified load, rope, speed, control and application configuration. Confirm the intended duty and installation with the engineering team.",
    "Which verified Chenma model is the most straightforward starting point for a 230 kg lift?": "CMLM-E05 lists a 230 kg load capacity, 4.2 m lifting height, 2200 W power and 3–5 m/min lifting speed. It also lists wired and wireless remote operation. Confirm the complete application before ordering.",
    "How should I interpret CMLM-E06 single-rope and double-rope data?": "The product data lists single rope at 300 kg and 12 m/min, and double rope at 500 kg. Treat these as configuration-specific operating figures, not as a universal rating for every setup. Confirm the selected configuration and installation.",
    "Does the CMLM-E06 product title prove a 1 ton rated capacity?": "No. The product title includes 0.5–1 Ton, but the verified operating fields list 300 kg for single rope and 500 kg for double rope. Do not treat 1 ton as a confirmed rated lifting condition without written configuration confirmation.",
    "What rope information should I include in a quotation request?": "Include the required rope length, rope diameter, single-rope or double-rope configuration, target load, lifting height, speed requirement and control method. The verified examples list 5 mm rope for CMLM-E05, 4 mm × 12 m for CMLM-E06 and 5 mm × 30–60 m for CMLM-E14.",
    "Can rated power be used to calculate the load rating?": "No. The listed product data shows power and load fields, but it does not establish a one-to-one relationship between them. For CMLM-E14, do not infer which power corresponds to which load. Ask for the exact configuration.",
    "What should a factory or warehouse verify before purchase?": "Verify the actual load and center of gravity, lifting height, rope length and diameter, single-rope or double-rope setup, speed, control method, available power and the intended installation. Request written confirmation for any field not stated in the product data.",
    "Is the E05 steel cable load the same as the machine load capacity?": "No. E05 lists 230 kg as Load Capacity and 600 kg as Steel Cable Load. These are separate product fields. The 600 kg figure must not be presented as the complete machine rated lifting capacity; confirm its meaning with the engineering team.",
}
errors = []
if not PAGE.exists():
    errors.append("article page is missing")
    sys.exit(1)
text = PAGE.read_text(encoding="utf-8-sig")
if "�" in text or "鈥" in text or "脳" in text or "鈮" in text or "掳" in text:
    errors.append("article contains an encoding marker")
if "https://www.chenmalifting.com/blog/electric-hoist-winch-buying-guide.html" not in text:
    errors.append("article canonical URL is missing")
for link in EXPECTED_LINKS:
    if link not in text:
        errors.append(f"article link is missing: {link}")
    elif not (PAGE.parent / link).resolve().exists():
        errors.append(f"article link target is missing: {link}")
for required in ["Direct answer", "Decision flow", "Factory and warehouse safety check", "Important:", "Request a configuration-specific quotation"]:
    if required.lower() not in text.lower():
        errors.append(f"required section is missing: {required}")
for model, path in PRODUCT_FILES.items():
    if not path.exists():
        errors.append(f"source product page is missing: {model}")

scripts = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', text, re.S)
ld = []
for raw in scripts:
    try:
        ld.append(json.loads(raw))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON-LD: {exc}")
article_ld = next((item for item in ld if item.get("@type") == "Article"), None)
faq_ld = next((item for item in ld if item.get("@type") == "FAQPage"), None)
org_ld = next((item for item in ld if item.get("@type") == "Organization"), None)
if article_ld is None:
    errors.append("Article JSON-LD is missing")
if faq_ld is None:
    errors.append("FAQPage JSON-LD is missing")
if org_ld is None:
    errors.append("Organization JSON-LD is missing")

if faq_ld:
    json_faq = {item.get("name"): item.get("acceptedAnswer", {}).get("text") for item in faq_ld.get("mainEntity", [])}
    if json_faq != FAQ:
        errors.append("FAQPage JSON-LD does not match the expected FAQ set")
    visible_faq = {}
    for match in re.finditer(r'<h3[^>]*>(.*?)</h3>\s*<p[^>]*>(.*?)</p>', text, re.S):
        question = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        answer = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if question in FAQ:
            visible_faq[question] = answer
    if visible_faq != FAQ:
        errors.append("visible FAQ does not match FAQPage JSON-LD")

try:
    data = json.loads((ROOT / "products_full.json").read_text(encoding="utf-8-sig"))
    by_id = {int(item["id"]): item for item in data}
    expected = {
        35: {"Load Capacity": "230 kg", "Lifting Height": "4.2 m", "Power": "2200 W", "Wire Rope": "5 mm", "Lifting Speed": "3–5 m/min"},
        36: {"Single Rope": "300 kg / 12 m/min", "Double Rope": "500 kg", "Wire Rope": "4mm × 12m"},
        44: {"Load Capacity": "300 / 400 / 500 kg", "Lifting Speed": "14 m/min", "Wire Rope": "5mm × 30–60m"},
    }
    for product_id, fields in expected.items():
        specs = {item["k"]: item["v"] for item in by_id[product_id]["specs"]}
        for key, value in fields.items():
            if specs.get(key) != value:
                errors.append(f"source mismatch for ID {product_id}: {key}")
except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
    errors.append(f"cannot validate product source data: {exc}")

try:
    sitemap_root = ET.parse(SITEMAP).getroot()
    locs = [node.text or "" for node in sitemap_root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    expected_url = "https://www.chenmalifting.com/blog/electric-hoist-winch-buying-guide.html"
    if expected_url not in locs:
        errors.append("article URL is missing from Sitemap")
except (OSError, ET.ParseError) as exc:
    errors.append(f"invalid Sitemap: {exc}")

if errors:
    print("Electric hoist guide validation failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)
print("Electric hoist guide validation passed: page, JSON-LD, FAQ parity, source fields, links and Sitemap.")
