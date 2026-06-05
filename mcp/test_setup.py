#!/usr/bin/env python3
"""
Quick setup verification script for ClashGuard MCP
"""

import sys
from pathlib import Path

print("\n" + "="*60)
print("ClashGuard MCP — Setup Verification")
print("="*60)

# Test 1: Check Python version
print(f"\n✓ Python Version: {sys.version}")

# Test 2: Check imports
print("\nVerifying dependencies...")
deps = [
    "anthropic", "httpx", "requests", "trimesh", "shapely",
    "numpy", "docx", "reportlab", "dotenv", "pytest", "pytest_asyncio"
]

failed = []
for dep in deps:
    try:
        __import__(dep)
        print(f"  ✓ {dep}")
    except ImportError as e:
        print(f"  ✗ {dep} - {e}")
        failed.append(dep)

if failed:
    print(f"\n⚠ Missing dependencies: {', '.join(failed)}")
    sys.exit(1)

# Test 3: Check server loads
print("\nVerifying server configuration...")
try:
    from server import TOOLS, TOOL_HANDLERS
    print(f"  ✓ Server imported successfully")
    print(f"  ✓ {len(TOOLS)} tools defined:")
    for tool in TOOLS:
        print(f"    - {tool['name']}")
    print(f"  ✓ {len(TOOL_HANDLERS)} tool handlers registered")
except Exception as e:
    print(f"  ✗ Server import failed: {e}")
    sys.exit(1)

# Test 4: Check config
print("\nVerifying configuration...")
try:
    from config import DEMO_MODE, MOCK_DB_PATH, OUTPUT_DIR
    print(f"  ✓ Config loaded")
    print(f"  ✓ DEMO_MODE: {DEMO_MODE}")
    print(f"  ✓ MOCK_DB_PATH: {MOCK_DB_PATH}")
    print(f"  ✓ OUTPUT_DIR: {OUTPUT_DIR}")
except Exception as e:
    print(f"  ✗ Config load failed: {e}")
    sys.exit(1)

# Test 5: Check mock data
print("\nVerifying mock data...")
try:
    import json
    with open(MOCK_DB_PATH) as f:
        mock_data = json.load(f)
    print(f"  ✓ Mock data loaded")
    if "project" in mock_data:
        print(f"  ✓ Project: {str(mock_data['project'])[:50]}...")
    if "elements" in mock_data:
        elements = mock_data.get("elements", [])
        print(f"  ✓ Elements: {len(elements)}")
except Exception as e:
    print(f"  ✗ Mock data verification failed: {e}")
    sys.exit(1)

# Test 6: Test basic tool functionality
print("\nTesting basic tool functionality...")
try:
    from tools.extract_revit_data import run as extract
    result = extract({"use_demo_data": True})
    print(f"  ✓ extract_revit_data works")
    
    from tools.analyze_model import run as analyze
    import json
    elem = json.loads(result)
    if "elements" in elem:
        result2 = analyze({"elements": elem["elements"]})
        print(f"  ✓ analyze_model works")
except Exception as e:
    print(f"  ✗ Tool test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✓ All setup checks passed!")
print("="*60)
print("\nNext steps:")
print("1. Set up Claude Desktop config (see README.md)")
print("2. Configure API keys in .env (if using real APS/Claude)")
print("3. Run 'python server.py' to start the MCP server")
print("="*60 + "\n")
