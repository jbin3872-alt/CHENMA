from pathlib import Path
import json
import re
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

INCOMPLETE = re.compile(
    r"–\s*(?:hours|years|cm|kg|m(?:/min)?|kW)|\(3–\)|\(2–\s|\(4–\s|"
    r"20–0|345–30|94–13|12–6|3– m/min|4– 20m|6–4m|12–6m|14–8m|"
    r"200– 300kg|1560–600"
)
for path in TARGETS:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for line_number, line in enumerate(text.splitlines(), 1):
        if INCOMPLETE.search(line):
            errors.append(f"{path.relative_to(ROOT)}:{line_number}: incomplete specification")

if errors:
    print("Encoding/specification validation failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"Encoding/specification validation passed for {len(TARGETS)} UTF-8 HTML/JSON files.")
