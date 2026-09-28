from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
TARGETS = [
    ROOT / "index.html",
    ROOT / "stair-climbers.html",
    ROOT / "electric-forklifts.html",
    ROOT / "semi-electric-forklifts.html",
    ROOT / "lift-machines.html",
    ROOT / "products_full.json",
    ROOT / "products_extracted.json",
    *sorted((ROOT / "products").glob("*.html")),
]
BAD_MARKERS = ("\ufffd", "\u9225", "\u8133", "\u922e", "\u63b3", "\u951f")

errors = []
for path in TARGETS:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)}: not valid UTF-8 ({exc})")
        continue
    for marker in BAD_MARKERS:
        if marker in text:
            errors.append(f"{path.relative_to(ROOT)}: contains {marker!r}")
    if path.suffix == ".json":
        try:
            json.loads(text.lstrip("\ufeff"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")

if errors:
    print("Encoding validation failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"Encoding validation passed for {len(TARGETS)} UTF-8 HTML/JSON files.")
