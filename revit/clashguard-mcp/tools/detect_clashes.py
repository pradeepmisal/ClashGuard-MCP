# tools/detect_clashes.py
"""
Tool 3: detect_clashes
Runs AABB collision detection on the analyzed model elements.
All calculations are deterministic — no AI.
"""

import json
from engine.aabb import run_clash_detection

def run(args: dict) -> str:
    elements         = args.get("elements", [])
    systems_to_check = args.get("systems_to_check", ["HVAC", "Plumbing", "Electrical", "Structural"])
    zones            = args.get("zones", [])

    if isinstance(elements, str):
        try:
            parsed = json.loads(elements)
            if isinstance(parsed, dict):
                elements = parsed.get("elements", [])
            else:
                elements = parsed
        except:
            return json.dumps({"error": "Invalid elements data. Pass output from analyze_model."})
    elif isinstance(elements, dict):
        elements = elements.get("elements", [])

    if not elements:
        return json.dumps({"error": "No elements provided for clash detection."})

    # Filter by zone if specified
    if zones:
        elements = [e for e in elements if any(z.lower() in e.get("location", "").lower() for z in zones)]

    clashes = run_clash_detection(elements, systems_to_check)

    # Count by severity
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in clashes:
        severity_counts[c["severity_label"]] += 1

    result = {
        "total_clashes":    len(clashes),
        "severity_summary": severity_counts,
        "clashes":          clashes,
        "message": (
            f"Detected {len(clashes)} total clashes: "
            f"{severity_counts['CRITICAL']} CRITICAL, "
            f"{severity_counts['HIGH']} HIGH, "
            f"{severity_counts['MEDIUM']} MEDIUM, "
            f"{severity_counts['LOW']} LOW. "
            "Run suggest_resolutions to get AI-powered recommendations."
        )
    }
    return json.dumps(result, indent=2)
