# tests/test_tools.py
import json
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.extract_revit_data import run as extract
from tools.analyze_model       import run as analyze
from tools.detect_clashes      import run as detect
from tools.suggest_resolutions import run as suggest

def test_extract_returns_elements():
    result = json.loads(extract({}))
    assert "elements" in result
    assert result["count"] > 0

def test_analyze_adds_centers():
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    assert r2["total_elements"] > 0
    for el in r2["elements"]:
        assert "center" in el

def test_detect_finds_clashes():
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    assert r3["total_clashes"] >= 1  # Must find at least 1 clash in mock data

def test_detect_clashes_have_severity():
    r1 = json.loads(extract({}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    for clash in r3["clashes"]:
        assert clash["severity_label"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

def test_suggest_requires_consent():
    result = json.loads(suggest({"clashes": [], "user_consent_given": False}))
    assert "error" in result
    assert "consent" in result["message"].lower()

def test_full_pipeline():
    r1 = json.loads(extract({"floor_filter": "Level 3"}))
    r2 = json.loads(analyze({"elements": r1["elements"]}))
    r3 = json.loads(detect({"elements": r2["elements"]}))
    assert r3["total_clashes"] > 0
    print(f"Full pipeline: {r3['total_clashes']} clashes, severity: {r3['severity_summary']}")
