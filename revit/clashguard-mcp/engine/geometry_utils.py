# engine/geometry_utils.py
"""
Utility functions for spatial geometry operations.
All deterministic — no AI involved.
"""

def compute_centers(elements: list) -> list:
    """Add center coordinates to each element's bounding box."""
    result = []
    for el in elements:
        bbox = el.get("bbox", {})
        mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
        mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
        el["center"] = {
            "x": (mn["x"] + mx["x"]) / 2,
            "y": (mn["y"] + mx["y"]) / 2,
            "z": (mn["z"] + mx["z"]) / 2,
        }
        result.append(el)
    return result

def compute_proximity_groups(elements: list, threshold_m: float = 2.0) -> list:
    """
    Group elements that are within threshold_m meters of each other.
    Reduces O(n^2) clash detection to only nearby element pairs.
    """
    import math
    groups = []
    used = set()

    for i, el_a in enumerate(elements):
        if i in used:
            continue
        group = [el_a]
        ca = el_a.get("center", {"x": 0, "y": 0, "z": 0})
        for j, el_b in enumerate(elements):
            if j <= i or j in used:
                continue
            cb = el_b.get("center", {"x": 0, "y": 0, "z": 0})
            dist = math.sqrt(
                (ca["x"] - cb["x"]) ** 2 +
                (ca["y"] - cb["y"]) ** 2 +
                (ca["z"] - cb["z"]) ** 2
            )
            if dist <= threshold_m:
                group.append(el_b)
                used.add(j)
        if len(group) > 1:
            groups.append(group)
        used.add(i)
    return groups

def bbox_volume(bbox: dict) -> float:
    """Compute the volume of a bounding box in cubic meters."""
    mn = bbox.get("min", {"x": 0, "y": 0, "z": 0})
    mx = bbox.get("max", {"x": 0, "y": 0, "z": 0})
    dx = abs(mx["x"] - mn["x"])
    dy = abs(mx["y"] - mn["y"])
    dz = abs(mx["z"] - mn["z"])
    return dx * dy * dz
