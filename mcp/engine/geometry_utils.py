# engine/geometry_utils.py
"""
Deterministic spatial geometry utilities.
No AI involved — pure math.
"""
import math


def compute_centers(elements: list) -> list:
    """Add center coordinates to each element's bounding box."""
    for el in elements:
        bbox = el.get("bbox", {})
        mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
        mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
        el["center"] = {
            "x": round((mn["x"] + mx["x"]) / 2, 4),
            "y": round((mn["y"] + mx["y"]) / 2, 4),
            "z": round((mn["z"] + mx["z"]) / 2, 4),
        }
    return elements


def compute_proximity_groups(elements: list, threshold_m: float = 2.0) -> list:
    """
    Groups elements that are within threshold_m meters of each other.
    Reduces O(n²) clash detection to only nearby element pairs.
    """
    groups, used = [], set()

    for i, el_a in enumerate(elements):
        if i in used:
            continue
        group = [el_a]
        ca = el_a.get("center", {"x": 0, "y": 0, "z": 0})

        for j, el_b in enumerate(elements):
            if j <= i or j in used:
                continue
            cb = el_b.get("center", {"x": 0, "y": 0, "z": 0})
            dist = math.sqrt(sum((ca[k] - cb[k]) ** 2 for k in "xyz"))
            if dist <= threshold_m:
                group.append(el_b)
                used.add(j)

        if len(group) > 1:
            groups.append([e["id"] for e in group])
        used.add(i)

    return groups


def bbox_volume(bbox: dict) -> float:
    """Compute the volume of a bounding box in cubic meters."""
    mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
    mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
    return abs(mx["x"] - mn["x"]) * abs(mx["y"] - mn["y"]) * abs(mx["z"] - mn["z"])
