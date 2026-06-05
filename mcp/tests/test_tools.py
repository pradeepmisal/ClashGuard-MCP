# tests/test_tools.py
"""
ClashGuard MCP — Test Suite
Validates all 5 tools and the full pipeline.
Run: pytest tests/ -v
All 6 tests must pass before Autodesk submission.
"""
import json
import sys

sys.path.insert(0, ".")

from tools.extract_revit_data import run as extract
from tools.analyze_model       import run as analyze
from tools.detect_clashes      import run as detect
from tools.suggest_resolutions import run as suggest
from tools.generate_report     import run as generate_report


def test_extract_returns_elements():
    """Tool 1: Must return elements list with at least 1 element."""
    result = json.loads(extract({}))
    assert "elements" in result, "Missing 'elements' key"
    assert result["count"] > 0, "Expected at least 1 element"
    print(f"\n  ✓ Tool 1: {result['count']} elements from {result['source']}")


def test_extract_with_floor_filter():
    """Tool 1: Floor filter must reduce element count."""
    all_result      = json.loads(extract({}))
    filtered_result = json.loads(extract({"floor_filter": "Level 3"}))
    assert filtered_result["count"] <= all_result["count"]
    print(f"\n  ✓ Tool 1 filter: {filtered_result['count']} elements on Level 3")


def test_analyze_adds_centers():
    """Tool 2: Every element must have a center after analysis."""
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    assert r2["total_elements"] > 0
    for el in r2["elements"]:
        assert "center" in el, f"Element {el['id']} missing center"
        assert all(k in el["center"] for k in "xyz")
    print(f"\n  ✓ Tool 2: {r2['total_elements']} elements analyzed, {r2['summary']['total_groups']} groups")


def test_detect_finds_clashes():
    """Tool 3: Must detect at least 1 clash in the demo data."""
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    assert r3["total_clashes"] >= 1, "Expected at least 1 clash in demo data"
    print(f"\n  ✓ Tool 3: {r3['total_clashes']} clashes — {r3['severity_summary']}")


def test_detect_severity_labels_valid():
    """Tool 3: All severity_label values must be in the allowed set."""
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
    for c in r3["clashes"]:
        assert c["severity_label"] in valid, f"Invalid severity: {c['severity_label']}"
    print(f"\n  ✓ Tool 3 severity: all labels valid")


def test_suggest_requires_consent():
    """Tool 4: Must block AI call when consent is false."""
    result = json.loads(suggest({"clashes": [], "user_consent_given": False}))
    assert "error" in result, "Expected error without consent"
    assert "consent" in result["message"].lower(), "Expected consent mention in message"
    print(f"\n  ✓ Tool 4 consent gate: working correctly")


def test_full_pipeline():
    """End-to-end: extract -> analyze -> detect must find clashes with valid structure."""
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))

    assert r3["total_clashes"] > 0, "Full pipeline must find at least 1 clash"
    for c in r3["clashes"]:
        assert "clash_id" in c
        assert "severity_label" in c
        assert "element_a" in c
        assert "element_b" in c

    print(
        f"\n  ✓ Full pipeline: {r3['total_clashes']} clashes | "
        f"Severity: {r3['severity_summary']}"
    )


def test_generate_report():
    """Tool 5: Must generate PDF and Word files correctly."""
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    
    rep_res = json.loads(generate_report({
        "clashes": r3["clashes"],
        "project_name": "Test Project",
        "format": "both"
    }))
    
    assert rep_res["success"] is True, f"Report generation failed: {rep_res.get('errors')}"
    assert len(rep_res["files_generated"]) == 2, "Expected 2 generated files (PDF & DOCX)"
    
    for f in rep_res["files_generated"]:
        import os
        assert os.path.exists(f), f"File {f} was not written to disk"
        
    print(f"\n  ✓ Tool 5: Generated reports: {rep_res['files_generated']}")


def test_suggest_deterministic_fallback():
    """Tool 4: Must return deterministic recommendations when no API keys are present and consent is given."""
    import config
    orig_anthropic = config.ANTHROPIC_API_KEY
    orig_gemini = config.GEMINI_API_KEY
    config.ANTHROPIC_API_KEY = ""
    config.GEMINI_API_KEY = ""
    
    try:
        r1 = json.loads(extract({}))
        r2 = json.loads(analyze({"elements": r1["elements"]}))
        r3 = json.loads(detect({"elements": r2["elements"]}))
        
        rep = json.loads(suggest({"clashes": r3["clashes"], "user_consent_given": True}))
        assert "ai_recommendations" in rep
        assert "FREE FALLBACK" in rep["ai_recommendations"]
        assert rep["engine_used"] == "deterministic-fallback"
        print(f"\n  ✓ Tool 4 fallback: verified rule-based coordination recommendations")
    finally:
        config.ANTHROPIC_API_KEY = orig_anthropic
        config.GEMINI_API_KEY = orig_gemini
