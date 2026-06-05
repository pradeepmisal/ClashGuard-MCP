# engine/severity.py
"""
Rule-based severity scoring for detected clashes.
100% deterministic — IF/ELSE logic based on engineering rules.
No AI involved in scoring.
"""

SEVERITY_LABELS = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW"}

# Rules: element type combinations and their base severity
SEVERITY_RULES = {
    # (type_a, type_b): score
    ("Duct",   "Beam"):   4,   # CRITICAL — structural interference
    ("Pipe",   "Beam"):   4,   # CRITICAL — structural interference
    ("Duct",   "Column"): 4,   # CRITICAL — structural interference
    ("Pipe",   "Column"): 4,   # CRITICAL — structural interference
    ("Duct",   "Window"): 3,   # HIGH — facade interference
    ("Pipe",   "Window"): 3,   # HIGH — facade interference
    ("Duct",   "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Pipe",   "Wall"):   2,   # MEDIUM — can penetrate with sleeve
    ("Duct",   "Pipe"):   2,   # MEDIUM — MEP coordination
    ("CableTray", "Duct"):2,   # MEDIUM — MEP coordination
}

def score_clash(el_a: dict, el_b: dict, volume_m3: float, clash_type: str) -> int:
    """
    Score a clash from 1 (low) to 4 (critical) using rule-based logic.
    Returns integer severity score.
    """
    type_a = el_a.get("type", "")
    type_b = el_b.get("type", "")

    # Look up rule (try both orderings)
    base = SEVERITY_RULES.get((type_a, type_b)) or \
           SEVERITY_RULES.get((type_b, type_a)) or 2

    # Adjust for volume (larger intersection = more severe)
    if clash_type == "hard" and volume_m3 > 0.1:
        base = min(4, base + 1)
    elif clash_type == "soft":
        base = max(1, base - 1)

    return base
