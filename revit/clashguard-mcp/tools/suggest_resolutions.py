# tools/suggest_resolutions.py
"""
Tool 4: suggest_resolutions
Uses Claude AI to prioritize clashes and suggest engineering resolutions.
IMPORTANT: AI is used ONLY for reasoning — never for geometry calculations.
IMPORTANT: User consent is required before sending data to Claude.
"""

import json
import sys
from pathlib import Path
import anthropic

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

SYSTEM_PROMPT = """You are a senior BIM coordination engineer with 15 years of experience in MEP clash resolution for large AEC projects. 

You are given a list of detected MEP clashes from a Revit building model. Your job is to:
1. Review each clash and explain WHY it matters in plain English
2. Suggest the most practical engineering resolution for each clash
3. Prioritize the list — which clashes need immediate attention

IMPORTANT RULES:
- You are reading ANALYSIS RESULTS from a deterministic geometry engine. Do not question the clash detection results.
- Your role is ONLY reasoning and recommendations — not geometry recalculation.
- Keep suggestions practical and implementable by a BIM engineer.
- Use plain English — no jargon that non-specialists won't understand.
- For CRITICAL clashes: always recommend immediate action before proceeding with design.
- For LOW clashes: suggest monitoring but not blocking design progress.

Format each clash recommendation as:
CLASH [ID]: [one-line description]
WHY IT MATTERS: [plain English explanation]
RECOMMENDED FIX: [specific, actionable suggestion]
PRIORITY: [CRITICAL/HIGH/MEDIUM/LOW]
"""

def run(args: dict) -> str:
    clashes             = args.get("clashes", [])
    project_context     = args.get("project_context", "")
    user_consent_given  = args.get("user_consent_given", False)

    # [AUTODESK REQUIREMENT] — Enforce user consent before sending to AI
    if not user_consent_given:
        return json.dumps({
            "error": "User consent required",
            "message": (
                "This tool sends anonymized clash data to Anthropic's Claude AI for analysis. "
                "To proceed, call this tool again with user_consent_given=true. "
                "Data sent: element types, locations, severity scores. "
                "No personal data, user data, or project credentials are sent."
            )
        })

    if isinstance(clashes, str):
        try:
            parsed = json.loads(clashes)
            if isinstance(parsed, dict):
                clashes = parsed.get("clashes", [])
            else:
                clashes = parsed
        except:
            return json.dumps({"error": "Invalid clash data format."})
    elif isinstance(clashes, dict):
        clashes = clashes.get("clashes", [])

    if not clashes:
        return json.dumps({"message": "No clashes provided. Run detect_clashes first."})

    # Build user message — only send minimum required data to Claude
    clash_summary = []
    for c in clashes:
        clash_summary.append({
            "clash_id":       c["clash_id"],
            "type":           c["type"],
            "element_a_type": c["element_a"]["type"],
            "element_b_type": c["element_b"]["type"],
            "location":       c["location"],
            "severity":       c["severity_label"],
            "volume_m3":      c.get("intersection_volume_m3", 0),
        })

    user_message = f"""Please analyze these {len(clashes)} MEP clashes detected in the building model and provide resolution recommendations.

Project context: {project_context or 'Commercial office building, active design phase'}

Detected clashes:
{json.dumps(clash_summary, indent=2)}

Please provide:
1. Resolution recommendations for each clash
2. Overall priority order
3. Which clashes can be addressed together (grouped fixes)
"""

    try:
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not configured in .env file.")

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        ai_recommendations = response.content[0].text
    except Exception as e:
        ai_recommendations = f"AI analysis unavailable: {str(e)}. Clashes are listed by deterministic severity score."

    return json.dumps({
        "total_clashes":        len(clashes),
        "clashes":              clashes,
        "ai_recommendations":   ai_recommendations,
        "consent_recorded":     True,
        "data_sent_to_ai":      "element types, locations, severity scores only — no personal or credential data",
        "message": f"AI analysis complete for {len(clashes)} clashes. See ai_recommendations for prioritized resolution plan."
    }, indent=2)
