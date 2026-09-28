from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
DATA = ROOT / "products_full.json"

errors = []
try:
    products = json.loads(DATA.read_text(encoding="utf-8-sig"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"Cannot read {DATA.name}: {exc}")
    sys.exit(1)

json_by_id = {int(product["id"]): product for product in products}
index_by_id = {}
current_id = None
for line_number, line in enumerate(INDEX.read_text(encoding="utf-8-sig").splitlines(), 1):
    id_match = re.search(r"\{ id:(\d+), cat:\"([^\"]+)\", name:\"([^\"]*)\",", line)
    if id_match:
        current_id = int(id_match.group(1))
        index_by_id[current_id] = {
            "cat": id_match.group(2),
            "name": id_match.group(3),
            "line": line_number,
        }
    if current_id is None or "specs:" not in line:
        continue
    specs_match = re.search(r"specs:(\[\[.*\]\])\s*\},?\s*$", line)
    if not specs_match:
        errors.append(f"index.html:{line_number}: cannot parse specs array")
        continue
    try:
        index_by_id[current_id]["specs"] = dict(json.loads(specs_match.group(1)))
    except json.JSONDecodeError as exc:
        errors.append(f"index.html:{line_number}: invalid specs JSON ({exc})")

if set(index_by_id) != set(json_by_id):
    errors.append(f"product ID sets differ: index={sorted(index_by_id)} json={sorted(json_by_id)}")

for product_id, product in json_by_id.items():
    indexed = index_by_id.get(product_id)
    if not indexed:
        continue
    if indexed.get("cat") != product.get("cat"):
        errors.append(f"id={product_id}: cat differs")
    if indexed.get("name") != product.get("name"):
        errors.append(f"id={product_id}: name differs")
    expected_specs = {str(spec["k"]): str(spec["v"]) for spec in product.get("specs", [])}
    actual_specs = indexed.get("specs", {})
    if actual_specs != expected_specs:
        for key in sorted(set(actual_specs) | set(expected_specs)):
            if actual_specs.get(key) != expected_specs.get(key):
                errors.append(
                    f"id={product_id} field={key}: "
                    f"index={actual_specs.get(key)!r} json={expected_specs.get(key)!r}"
                )

if errors:
    print("Product consistency validation failed:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"Product consistency validation passed for {len(json_by_id)} product records.")
