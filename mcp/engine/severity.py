# engine/severity.py
"""
Rule-based severity scoring for detected clashes.
100% deterministic — IF/ELSE logic based on engineering rules.
No AI involved in scoring. Identical logic to C# MockClashDetector.DetermineSeverity().
"""

SEVERITY_LABELS = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

# Engineering rules: (mep_type, arch_type) -> severity score
SEVERITY_RULES = {
    ("Duct",      "Beam"):   4,   # CRITICAL — structural interference
    ("Pipe",      "Beam"):   4,   # CRITICAL — structural interference
    ("Duct",      "Column"): 4,   # CRITICAL — structural interference
    ("Pipe",      "Column"): 4,   # CRITICAL — structural interference
    ("CableTray", "Beam"):   3,   # HIGH
    ("Conduit",   "Beam"):   3,   # HIGH
    ("Duct",      "Window"): 3,   # HIGH — facade interference
    ("Pipe",      "Window"): 3,   # HIGH — facade interference
    ("CableTray", "Window"): 2,   # MEDIUM
    ("Duct",      "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Pipe",      "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Conduit",   "Wall"):   2,   # MEDIUM
    ("CableTray", "Wall"):   2,   # MEDIUM
    ("Duct",      "Floor"):  3,   # HIGH — penetration complex
    ("Pipe",      "Floor"):  2,   # MEDIUM — can sleeve
    ("Duct",      "Pipe"):   2,   # MEDIUM — MEP coordination
    ("CableTray", "Duct"):   2,   # MEDIUM — MEP coordination
    ("CableTray", "Pipe"):   1,   # LOW
}


def score_clash(el_a: dict, el_b: dict, volume_m3: float, clash_type: str) -> int:
    """
    Score a clash from 1 (LOW) to 4 (CRITICAL) using rule-based logic.
    Checks both orderings of element types.
    Adjusts score up for large hard clashes, down for soft clashes.
    """
    type_a = el_a.get("type", "")
    type_b = el_b.get("type", "")

    # Check both orderings
    base = (SEVERITY_RULES.get((type_a, type_b))
            or SEVERITY_RULES.get((type_b, type_a))
            or 2)  # Default: MEDIUM

    # Adjust for intersection volume
    if clash_type == "hard" and volume_m3 > 0.1:
        base = min(4, base + 1)
    elif clash_type == "soft":
        base = max(1, base - 1)

    return base
