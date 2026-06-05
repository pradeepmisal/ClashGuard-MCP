# tools/suggest_resolutions.py
"""
Tool 4: AI-powered clash prioritization and resolution suggestions.

AUTODESK COMPLIANCE REQUIREMENTS:
  - User consent is checked BEFORE every AI API call.
  - Only anonymized data is sent: element types, floor names, severity scores.
  - No personal data, credentials, or full model geometry is transmitted.
  - All connections use HTTPS (enforced by default for all SDKs and API calls).
"""
import json
import httpx
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, GEMINI_API_KEY, GEMINI_MODEL

SYSTEM_PROMPT = """You are a senior BIM coordination engineer with 15 years of experience in MEP clash resolution.

You receive a list of detected MEP clashes from a deterministic geometry engine.

Your job:
1. Explain WHY each clash matters in plain English a non-technical client can understand.
2. Suggest the most practical engineering resolution for each clash.
3. Group related clashes where a single fix resolves multiple issues.
4. Rank by urgency — which must be fixed before design review.

Engineering guidelines:
- CRITICAL clashes: immediate action, cannot proceed without resolution.
- HIGH clashes: must fix before construction documents.
- MEDIUM clashes: resolve in coordination meeting, can sleeve/penetrate with approval.
- LOW clashes: flag for monitoring, not blocking.

Be specific and practical. Name the element types involved. Suggest rerouting directions where possible.
"""


def run(args: dict) -> str:
    clashes            = args.get("clashes", [])
    project_context    = args.get("project_context", "")
    user_consent_given = args.get("user_consent_given", False)

    # AUTODESK REQUIREMENT — consent gate before every AI call
    if not user_consent_given:
        return json.dumps({
            "error":   "user_consent_required",
            "message": (
                "This tool will send anonymized clash data (element types, floor "
                "identifiers, and severity scores — no personal data or credentials) "
                "to Claude AI or Gemini AI for analysis. "
                "To proceed, call this tool again with user_consent_given=true."
            )
        })

    if isinstance(clashes, str):
        try:
            clashes = json.loads(clashes)
        except Exception:
            return json.dumps({"error": "Invalid clashes JSON."})

    if not clashes:
        return json.dumps({"message": "No clashes to analyze."})

    # Minimize data — send types, locations, severity only (not full geometry)
    anonymized = [{
        "clash_id":       c["clash_id"],
        "type":           c["type"],
        "element_a_type": c["element_a"]["type"],
        "element_b_type": c["element_b"]["type"],
        "location":       c["location"],
        "severity":       c["severity_label"],
        "volume_m3":      c.get("intersection_volume_m3", 0),
    } for c in clashes]

    user_message = (
        f"Analyze {len(clashes)} MEP clashes and provide resolution recommendations.\n\n"
        f"Project context: {project_context or 'Commercial office building, active design phase'}\n\n"
        f"Detected clashes:\n{json.dumps(anonymized, indent=2)}\n\n"
        f"Provide: resolution for each clash, priority order, and grouped fixes where one action resolves multiple clashes."
    )

    ai_text = None
    engine_used = "deterministic-fallback"

    # 1. Try Anthropic (if key provided)
    if ANTHROPIC_API_KEY:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            ai_text = response.content[0].text
            engine_used = "anthropic"
        except Exception as e:
            print(f"Anthropic API failed: {e}")

    # 2. Try Gemini Free API (if Anthropic key missing or failed, and Gemini key present)
    if not ai_text and GEMINI_API_KEY:
        try:
            ai_text = _call_gemini_api(GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT, user_message)
            engine_used = "gemini-free"
        except Exception as e:
            print(f"Gemini API failed: {e}")

    # 3. Fallback to local rule-based deterministic advice (free and offline)
    if not ai_text:
        ai_text = _generate_deterministic_suggestions(clashes)
        engine_used = "deterministic-fallback"

    return json.dumps({
        "total_clashes":      len(clashes),
        "clashes":            clashes,
        "ai_recommendations": ai_text,
        "engine_used":        engine_used,
        "consent_recorded":   True,
        "data_sent_to_ai":    "anonymized: element types, floor locations, severity scores only",
        "message":            f"Analysis complete using {engine_used} engine for {len(clashes)} clashes."
    }, indent=2)


def _call_gemini_api(api_key: str, model: str, system_prompt: str, user_message: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nUser Request:\n{user_message}"}
                ]
            }
        ]
    }
    response = httpx.post(url, json=payload, headers=headers, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _generate_deterministic_suggestions(clashes: list) -> str:
    lines = [
        "### DETECTED CLASHES — ENGINEERING RESOLUTION RECOMMENDATIONS (FREE FALLBACK)",
        "*(Note: Cloud AI APIs were not configured. Showing standard BIM rule-based recommendations)*",
        "",
        "| Clash ID | Clash Type | Element A (MEP) | Element B (ARCH/STRUCT) | Severity | Engineering Recommendation |",
        "|---|---|---|---|---|---|",
    ]

    for c in clashes:
        cid = c.get("clash_id", "CLASH-???")
        ctype = c.get("type", "hard").upper()
        el_a = c.get("element_a", {})
        el_b = c.get("element_b", {})
        el_a_type = el_a.get("type", "Unknown")
        el_b_type = el_b.get("type", "Unknown")
        sev = c.get("severity_label", "MEDIUM")

        rec = "Review coordinates and adjust the smaller diameter or more flexible utility to route around the larger/rigid element."

        # Duct vs Column
        if "duct" in el_a_type.lower() and "column" in el_b_type.lower():
            rec = "CRITICAL: Reroute duct around structural column. Column penetration is strictly prohibited."
        # Duct vs Beam
        elif "duct" in el_a_type.lower() and "beam" in el_b_type.lower():
            rec = "HIGH: Lower duct centerline by 150mm to clear beam bottom flange, or coordinate structural sleeve through beam web."
        # CableTray vs Beam
        elif "cable" in el_a_type.lower() and "beam" in el_b_type.lower():
            rec = "HIGH: Lower cable tray elevation to route beneath beam. Maintain 100mm maintenance clearance."
        # Duct vs Wall
        elif "duct" in el_a_type.lower() and "wall" in el_b_type.lower():
            rec = "MEDIUM: Provide a rectangular duct penetration sleeve with fire dampers at firewall interface."
        # Pipe vs Wall
        elif "pipe" in el_a_type.lower() and "wall" in el_b_type.lower():
            rec = "MEDIUM: Provide circular pipe sleeve through wall. Seal with fire-stop sealant."
        # Pipe vs Beam
        elif "pipe" in el_a_type.lower() and "beam" in el_b_type.lower():
            rec = "HIGH: Route pipe below beam bottom flange. Offset piping using 90-degree elbows if necessary."
        # CableTray vs Duct
        elif "cable" in el_a_type.lower() and "duct" in el_b_type.lower():
            rec = "MEDIUM: Route cable tray above duct. Ensure min 150mm vertical clearance for electrical access."

        lines.append(f"| {cid} | {ctype} | {el_a_type} | {el_b_type} | {sev} | {rec} |")

    lines.append("")
    lines.append("### Recommended Action Plan")
    lines.append("1. **CRITICAL / HIGH Priority**: Coordinate with structural engineering immediately before finalizing routing.")
    lines.append("2. **MEDIUM Priority**: Standard sleeves and fire-stopping details can be applied on the sheet layouts.")
    lines.append("3. **BIM Meeting**: Schedule a 30-minute coordination check to approve duct rerouting.")

    return "\n".join(lines)
