# tools/detect_clashes.py
"""Tool 3: Runs AABB clash detection. 100% deterministic — no AI."""
import json
from engine.aabb import run_clash_detection


def run(args: dict) -> str:
    elements         = args.get("elements", [])
    systems_to_check = args.get("systems_to_check", ["HVAC", "Plumbing", "Electrical", "Structural"])
    zones            = args.get("zones", [])

    if isinstance(elements, str):
        try:
            elements = json.loads(elements)
        except Exception:
            return json.dumps({"error": "Invalid elements JSON."})

    if not elements:
        return json.dumps({"error": "No elements provided."})

    # Optional zone filter
    if zones:
        elements = [e for e in elements
                    if any(z.lower() in e.get("location", "").lower() for z in zones)]

    clashes = run_clash_detection(elements, systems_to_check)

    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c["severity_label"]] += 1

    hard_count = sum(1 for c in clashes if c["type"] == "hard")
    soft_count = sum(1 for c in clashes if c["type"] == "soft")

    return json.dumps({
        "total_clashes":    len(clashes),
        "hard_clashes":     hard_count,
        "soft_clashes":     soft_count,
        "severity_summary": severity_counts,
        "clashes":          clashes,
        "message": (
            f"Detected {len(clashes)} total clashes "
            f"({hard_count} hard, {soft_count} soft clearance violations). "
            f"Severity: {severity_counts['CRITICAL']} CRITICAL, "
            f"{severity_counts['HIGH']} HIGH, "
            f"{severity_counts['MEDIUM']} MEDIUM, "
            f"{severity_counts['LOW']} LOW."
        )
    }, indent=2)
