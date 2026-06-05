# engine/aabb.py
"""
Axis-Aligned Bounding Box (AABB) Collision Detection Engine.
100% deterministic — no AI involved.
Identical algorithm to C# MockClashDetector.BoundingBoxesOverlap().
"""
from engine.severity import score_clash, SEVERITY_LABELS

MEP_TYPES    = {"Duct", "Pipe", "CableTray", "Conduit", "MechanicalEquipment", "PlumbingFixture", "ElectricalEquipment"}
STRUCT_TYPES = {"Beam", "Column"}
ARCH_TYPES   = {"Wall", "Window", "Floor", "Ceiling", "Roof", "Door"}
ALL_NON_MEP  = STRUCT_TYPES | ARCH_TYPES


def aabb_intersects(a_min: dict, a_max: dict, b_min: dict, b_max: dict) -> bool:
    """Returns True if two AABBs intersect on all 3 axes."""
    return (
        a_min["x"] <= b_max["x"] and a_max["x"] >= b_min["x"] and
        a_min["y"] <= b_max["y"] and a_max["y"] >= b_min["y"] and
        a_min["z"] <= b_max["z"] and a_max["z"] >= b_min["z"]
    )


def intersection_volume(a_min: dict, a_max: dict, b_min: dict, b_max: dict) -> float:
    """Calculate the volume of intersection of two AABBs in m³."""
    ox = max(0, min(a_max["x"], b_max["x"]) - max(a_min["x"], b_min["x"]))
    oy = max(0, min(a_max["y"], b_max["y"]) - max(a_min["y"], b_min["y"]))
    oz = max(0, min(a_max["z"], b_max["z"]) - max(a_min["z"], b_min["z"]))
    return ox * oy * oz


def run_clash_detection(elements: list, systems_to_check: list, tolerance_mm: float = 50) -> list:
    """
    Main clash detection function.
    Checks all MEP vs Architecture/Structural pairs.
    Returns clashes sorted by severity (highest first).
    """
    tolerance_m = tolerance_mm / 1000.0
    clashes     = []
    clash_id    = 1
    seen_pairs  = set()

    for i, el_a in enumerate(elements):
        for j, el_b in enumerate(elements):
            if j <= i:
                continue

            pair_key = tuple(sorted([el_a["id"], el_b["id"]]))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Only check MEP vs Structural/Architecture
            a_mep   = el_a["type"] in MEP_TYPES
            b_mep   = el_b["type"] in MEP_TYPES
            a_other = el_a["type"] in ALL_NON_MEP
            b_other = el_b["type"] in ALL_NON_MEP

            if not ((a_mep and b_other) or (b_mep and a_other)):
                continue

            bbox_a = el_a.get("bbox", {})
            bbox_b = el_b.get("bbox", {})
            a_min  = bbox_a.get("min", {})
            a_max  = bbox_a.get("max", {})
            b_min  = bbox_b.get("min", {})
            b_max  = bbox_b.get("max", {})

            if not (a_min and a_max and b_min and b_max):
                continue

            # Expanded bbox for soft clash (clearance check)
            a_min_soft = {k: a_min[k] - tolerance_m for k in a_min}
            a_max_soft = {k: a_max[k] + tolerance_m for k in a_max}

            # Hard clash — actual physical overlap
            if aabb_intersects(a_min, a_max, b_min, b_max):
                vol   = intersection_volume(a_min, a_max, b_min, b_max)
                score = score_clash(el_a, el_b, vol, "hard")
                clashes.append({
                    "clash_id":               f"CG-{clash_id:03d}",
                    "type":                   "hard",
                    "element_a":              {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":              {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":               el_a.get("location", "Unknown"),
                    "intersection_volume_m3": round(vol, 6),
                    "severity_score":         score,
                    "severity_label":         SEVERITY_LABELS[score],
                    "center":                 el_a.get("center", {}),
                })
                clash_id += 1

            # Soft clash — within clearance tolerance but not overlapping
            elif aabb_intersects(a_min_soft, a_max_soft, b_min, b_max):
                score = score_clash(el_a, el_b, 0, "soft")
                clashes.append({
                    "clash_id":               f"CG-{clash_id:03d}",
                    "type":                   "soft",
                    "element_a":              {"id": el_a["id"], "type": el_a["type"], "name": el_a.get("name", "")},
                    "element_b":              {"id": el_b["id"], "type": el_b["type"], "name": el_b.get("name", "")},
                    "location":               el_a.get("location", "Unknown"),
                    "intersection_volume_m3": 0,
                    "clearance_violation_mm": tolerance_mm,
                    "severity_score":         score,
                    "severity_label":         SEVERITY_LABELS[score],
                    "center":                 el_a.get("center", {}),
                })
                clash_id += 1

    # Sort by severity descending (CRITICAL first)
    return sorted(clashes, key=lambda c: c["severity_score"], reverse=True)
