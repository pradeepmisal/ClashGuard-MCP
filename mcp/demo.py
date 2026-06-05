#!/usr/bin/env python3
"""
ClashGuard MCP — Complete End-to-End Demo
Runs all 5 tools with mock data and generates reports
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

import requests


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_subheader(title):
    print(f"\n{title}")
    print("-" * 70)


def ingest_mock_payload(url: str, api_key: str | None = None):
    print_subheader("Live Ingestion Setup")
    print(f"→ Posting mock model payload to {url}")
    with open(Path(__file__).parent / "data" / "mock_db.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    body = {
        "source": "mock_revit_payload",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "elements": payload.get("elements", []),
    }
    headers = {}
    if api_key:
        headers["X-API-KEY"] = api_key

    response = requests.post(url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()
    print(f"  ✓ Ingestion response: {result}")


def main():
    parser = argparse.ArgumentParser(description="Run the ClashGuard MCP demo flow")
    parser.add_argument("--ingest", action="store_true", help="Post mock Revit payload to local ingestion endpoint before running the demo")
    parser.add_argument("--ingest-url", default="http://127.0.0.1:8000/ingest_model", help="Local ingestion endpoint URL")
    parser.add_argument("--ingestion-api-key", default="", help="API key for the ingestion endpoint in production mode")
    args = parser.parse_args()

    print_header("ClashGuard MCP — Complete Demo (End-to-End)")
    
    try:
        # Import tools
        from tools.extract_revit_data import run as extract
        from tools.analyze_model import run as analyze
        from tools.detect_clashes import run as detect
        from tools.suggest_resolutions import run as suggest
        from tools.generate_report import run as generate_report
        from config import OUTPUT_DIR

        if args.ingest:
            ingest_mock_payload(args.ingest_url, args.ingestion_api_key)
        
        # ────────────────────────────────────────────────────────────────
        # TOOL 1: Extract Revit Data
        # ────────────────────────────────────────────────────────────────
        print_subheader("TOOL 1: Extract Revit Data")
        print("→ Extracting MEP elements from mock Revit model...")
        print("  Floor Filter: Level 3")
        print("  Element Types: Duct, Pipe, CableTray, Window, Beam")
        
        extract_result = json.loads(extract({
            "use_demo_data": True,
            "floor_filter": "Level 3",
            "element_types": ["Duct", "Pipe", "CableTray", "Window", "Beam"]
        }))
        
        elements = extract_result.get("elements", [])
        print(f"\n✓ Extracted {len(elements)} elements:")
        print(f"  - Ducts: {sum(1 for e in elements if e.get('type') == 'Duct')}")
        print(f"  - Pipes: {sum(1 for e in elements if e.get('type') == 'Pipe')}")
        print(f"  - Cable Trays: {sum(1 for e in elements if e.get('type') == 'CableTray')}")
        print(f"  - Windows: {sum(1 for e in elements if e.get('type') == 'Window')}")
        print(f"  - Beams: {sum(1 for e in elements if e.get('type') == 'Beam')}")
        
        # Show sample element
        if elements:
            sample = elements[0]
            print(f"\nSample Element:")
            print(f"  ID: {sample.get('id')}")
            print(f"  Type: {sample.get('type')}")
            print(f"  Name: {sample.get('name')}")
            print(f"  Location: {sample.get('location', 'N/A')}")
        
        # ────────────────────────────────────────────────────────────────
        # TOOL 2: Analyze Model
        # ────────────────────────────────────────────────────────────────
        print_subheader("TOOL 2: Analyze Model")
        print("→ Computing spatial centers and proximity relationships...")
        print("  Clearance Tolerance: 50mm")
        
        analyze_result = json.loads(analyze({
            "elements": elements,
            "clearance_tolerance_mm": 50
        }))
        
        summary = analyze_result.get("summary", {})
        print(f"\n✓ Analysis Complete:")
        print(f"  - Total Elements: {summary.get('total_elements', 0)}")
        print(f"  - Proximity Groups: {summary.get('proximity_groups', 0)}")
        print(f"  - Potential Collision Pairs: {summary.get('potential_collisions', 0)}")
        
        # ────────────────────────────────────────────────────────────────
        # TOOL 3: Detect Clashes
        # ────────────────────────────────────────────────────────────────
        print_subheader("TOOL 3: Detect Clashes")
        print("→ Running AABB collision detection...")
        print("  Algorithm: Axis-Aligned Bounding Box (AABB)")
        print("  Severity: Rule-based scoring (deterministic)")
        
        detect_result = json.loads(detect({
            "elements": analyze_result.get("elements", elements),
            "systems_to_check": ["Duct", "Pipe", "CableTray", "Window", "Beam"],
            "tolerance_mm": 50
        }))
        
        clashes = detect_result.get("clashes", [])
        total_clashes = detect_result.get("total_clashes", 0)
        
        print(f"\n✓ Clash Detection Complete:")
        print(f"  - Total Clashes: {total_clashes}")
        
        # Severity breakdown
        severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for clash in clashes:
            sev = clash.get("severity_label", "LOW")
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        for sev, count in severity_count.items():
            if count > 0:
                icon = "🔴" if sev == "CRITICAL" else "🟠" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢"
                print(f"  {icon} {sev}: {count}")
        
        # Show top 3 clashes
        if clashes:
            print(f"\nTop Clashes (by severity):")
            for i, clash in enumerate(clashes[:3], 1):
                print(f"\n  [{i}] {clash.get('id')} — {clash.get('severity_label')}")
                elem_a = clash.get('elements', [None, None])[0]
                elem_b = clash.get('elements', [None, None])[1]
                print(f"      {elem_a} × {elem_b}")
                print(f"      Volume: {clash.get('intersection_volume_m3', 0):.4f} m³")
                print(f"      Location: {clash.get('location', 'N/A')}")
        
        # ────────────────────────────────────────────────────────────────
        # TOOL 4: Suggest Resolutions (Optional - requires user consent)
        # ────────────────────────────────────────────────────────────────
        print_subheader("TOOL 4: Suggest Resolutions (AI-Powered)")
        print("→ Generating engineering recommendations for clashes...")
        print("  Using: Claude AI (Anthropic) or Gemini (Google)")
        print("  Mode: AI reasoning only (geometry is deterministic)")
        
        try:
            suggest_result = json.loads(suggest({
                "clashes": clashes[:3],  # Top 3 clashes
                "user_consent_given": False  # First check consent
            }))
            
            if "error" in suggest_result:
                print(f"\n⚠ {suggest_result.get('error')}")
                print(f"  Message: {suggest_result.get('message')}")
                print(f"\n  This is expected behavior — showing that user consent is required.")
                
                # Now try with consent
                print(f"\n→ Retrying with user consent granted...")
                suggest_result = json.loads(suggest({
                    "clashes": clashes[:3],
                    "user_consent_given": True
                }))
                
                if "recommendations" in suggest_result:
                    recs = suggest_result.get("recommendations", [])
                    print(f"\n✓ Generated {len(recs)} recommendations:")
                    for i, rec in enumerate(recs[:2], 1):
                        print(f"\n  [{i}] {rec.get('clash_id')}")
                        print(f"      Priority: {rec.get('priority')}")
                        print(f"      Suggested Fix: {rec.get('suggested_fix')}")
            else:
                print(f"\n✓ Recommendations generated (top 3):")
                print(suggest_result.get("summary", ""))
        
        except Exception as e:
            print(f"\n⚠ Skipping suggest_resolutions (requires API key)")
            print(f"  To enable: Set ANTHROPIC_API_KEY or GEMINI_API_KEY in .env")
            print(f"  For demo purposes, this is optional.")
        
        # ────────────────────────────────────────────────────────────────
        # TOOL 5: Generate Report
        # ────────────────────────────────────────────────────────────────
        print_subheader("TOOL 5: Generate Report")
        print("→ Creating professional PDF and Word reports...")
        print(f"  Output Directory: {OUTPUT_DIR}")
        
        report_result = json.loads(generate_report({
            "clashes": clashes,
            "project_name": "Magarpatta Tower — Level 3",
            "export_format": "both"  # both PDF and DOCX
        }))
        
        if "error" not in report_result:
            files = report_result.get("files", [])
            print(f"\n✓ Reports generated ({len(files)} files):")
            for file in files:
                filepath = Path(file)
                if filepath.exists():
                    size_mb = filepath.stat().st_size / (1024*1024)
                    print(f"  ✓ {filepath.name} ({size_mb:.2f} MB)")
                    print(f"    Path: {filepath}")
        else:
            print(f"\n⚠ {report_result.get('error')}")
        
        # ────────────────────────────────────────────────────────────────
        # SUMMARY
        # ────────────────────────────────────────────────────────────────
        print_header("Demo Complete! 🎉")
        
        print(f"Summary:")
        print(f"  ✓ Extracted: {len(elements)} MEP elements")
        print(f"  ✓ Analyzed: {summary.get('total_elements', 0)} spatial relationships")
        print(f"  ✓ Detected: {total_clashes} clashes")
        print(f"  ✓ Categorized: {sum(severity_count.values())} by severity")
        print(f"  ✓ Generated: Professional reports")
        
        print(f"\nKey Insights:")
        print(f"  • Most severe clash: {clashes[0].get('severity_label') if clashes else 'N/A'}")
        print(f"  • Total clash volume: {sum(c.get('intersection_volume_m3', 0) for c in clashes):.4f} m³")
        print(f"  • Recommended priority: Fix CRITICAL and HIGH clashes first")
        
        print(f"\nNext Steps:")
        print(f"  1. Review generated reports in: {OUTPUT_DIR}")
        print(f"  2. Set up Claude Desktop config (see SETUP_GUIDE.md)")
        print(f"  3. Try live scenarios in Claude Desktop")
        print(f"  4. Configure API keys for real APS/Claude integration")
        
        print(f"\n{'='*70}\n")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
