# ClashGuard MCP — Integration & Change Log

Purpose: track all changes made to the MCP server side to support live Revit pushes and replace mock data.

Status key: TODO / WIP / DONE

## Summary
We will add an HTTP ingestion API so a Revit add-in can POST a minimal model payload. The server will persist the payload, run the deterministic pipeline (analyze → detect → suggest → report), and serve queries from Claude Desktop against the live model.

## High-level tasks
- Define `POST /ingest_model` endpoint to accept minimal payload (JSON) — TODO
- Implement a lightweight ingestion API in `server.py` that can accept payloads from a Revit add-in. For development/demo, local `http://localhost:PORT/ingest_model` is allowed, but production Marketplace delivery must use HTTPS and a secure authentication mechanism. — TODO
- Update `tools/extract_revit_data.py` to accept incoming payloads and use them instead of `data/mock_db.json` when live model data is available. — TODO
- Add persistence: save the last ingested payload to `data/last_ingest.json` and load it during MCP operations. — TODO
- Add production-ready authentication for ingestion endpoint (API key or OAuth), while keeping local dev mode simple but clearly documented as demo-only. — TODO
- Update `demo.py` to include an `--ingest` mode to simulate a Revit push and validate both dev and prod ingestion flows. — TODO
- Update tests to cover ingestion, authentication, and the live payload pipeline. — TODO

## File-level plan (clashguard-mcp)
- `server.py` — integrate an HTTP server (background) and add graceful shutdown hooks. (TODO)
- `tools/extract_revit_data.py` — add branch: if `data/last_ingest.json` exists use it. (TODO)
- `data/last_ingest.json` — runtime file created by ingestion handler. (WIP)
- `demo.py` — add `--ingest sample` to POST `data/mock_db.json` to ingestion endpoint. (TODO)
- `requirements.txt` — may add `fastapi` and `uvicorn` or `flask` for the HTTP endpoint. (TODO)
- `tests/test_tools.py` — add tests to validate ingestion flow. (TODO)

## Minimal ingestion payload schema (version 1)
```json
{
  "project": "Project name",
  "source": "revit-addin|revit-export|aps",
  "timestamp": "2026-06-05T12:00:00Z",
  "elements": [
    {
      "id": "string",
      "type": "Duct|Pipe|Beam|Window|...",
      "name": "string",
      "location": "Level 3",
      "zone": "South Facade",
      "bbox": { "min": {"x":0,"y":0,"z":0}, "max": {"x":1,"y":1,"z":1} },
      "properties": {}
    }
  ]
}
```

## Security & Compliance
- Do not include user credentials, emails, or full raw geometry. Keep only bounding boxes and selected properties. (TODO)
- In `tools/suggest_resolutions.py`, ensure `user_consent_given=true` before sending any data to AI and strip any identifiers. (DONE)

## MCP Marketplace Compliance (Autodesk)

Notes from the Autodesk MCP Publisher Guide:
- The MCP Tool Manifest must list every tool, resource, prompt, external endpoint, Autodesk API used, and AI/LLM provider.
- All tool descriptions must be plain language and may not include instructions, internal implementation references, or sensitive data details.
- All external endpoints must be declared. Production endpoints must use HTTPS. Local development endpoints may be used for demos but must be documented as dev-only.
- Any external call to an AI service must be declared and described, and user consent must be explicit before sending data.
- Data minimization is required: only send the minimum data needed for the requested action.
- Security must be strong: no insecure transport, no logging of secrets, and no hard-coded credentials in source files.

Conflicts found with the current plan:
- The current plan uses a local-only ingestion endpoint (`http://localhost:PORT/ingest_model`). This is acceptable for demo/development, but Autodesk submission must clearly separate dev-only usage from production and use HTTPS for production ingestion.
- The plan does not yet explicitly declare the production ingestion endpoint or explain the dev/local mode in the manifest and submission docs.
- The current plan uses an AI provider, but the manifest and docs need a more explicit description of what data is sent to AI and how consent is obtained.
- The add-in plan currently uses `http://localhost:PORT` for POSTing model payloads. For Marketplace readiness, that must be optional and fallback-only; the default production workflow should favor a secure HTTPS endpoint.
- The plan references Autodesk APIs but should explicitly map them to the manifest and declaration form.

Required updates to resolve conflicts:
1. Document two modes clearly:
   - `dev/demo` mode: local ingestion via `http://localhost:PORT/ingest_model`. This mode is for development and demos only.
   - `production/marketplace` mode: secure ingestion via HTTPS with API key or OAuth authentication. This mode should be the default for marketplace submission.
2. Keep `manifest.json` production-focused. Do not expose dev-only localhost endpoints as production endpoints, but document them separately in developer notes.
3. Add a compliance checklist file for the Publisher Declaration that includes manifest, security, data access, AI provider declarations, and consent flow.
4. Update tool descriptions in `server.py` and `manifest.json` to remain plain and factual. Remove any instruction-like wording.
5. Ensure the MCP server uses HTTPS for external AI calls in production and never disables TLS verification.
6. Add a secure token requirement for production ingestion requests (e.g., `X-CLASHGUARD-API-KEY`) and document it in the manifest as an external connection requirement.
7. Add a privacy note to the Revit add-in plan: only bounding boxes and minimal metadata may be sent; no raw geometry, user metadata, or credentials.
8. Add a submission checklist file and annotate the plan with required MCP Publisher Guide steps.

## Revised high-priority implementation plan
1. Create a production-ready ingestion API in `server.py` with a secure auth mode.
2. Keep local ingestion as demo-only, documented separately. 
3. Update `tools/extract_revit_data.py` to prefer live payloads when available.
4. Update `manifest.json` and create `AUTODESK_COMPLIANCE.md` with explicit marketplace checklist.
5. Update `ClashGuardRevit/INTEGRATION_CHANGES.md` with HTTPS production endpoint guidance and with explicit user consent requirements.
6. Add tests validating production ingestion authentication and consent flow.

---

Last updated: 2026-06-05

Maintainer: ClashGuard MCP team


Next implementation steps (priority):
- Implement HTTPS-ready ingestion support in `server.py` (FastAPI + Uvicorn behind TLS or use proxy). (TODO)
- Add manifest.json updates and `AUTODESK_PUBLISHER_DECLARATION.md` draft. (TODO)
- Update tests to validate `production` ingestion requiring API key and HTTPS. (TODO)

## Next actions
1. Add HTTP ingestion handler to `server.py` and add `fastapi`/`flask` to `requirements.txt`. (I can implement this.)
2. Update `tools/extract_revit_data.py` to prefer `data/last_ingest.json` when present. (I can implement this.)
3. Provide a sample C# Revit add-in POST example (next file). (I will add the add-in plan in the other MD.)

---

Last updated: 2026-06-05

Maintainer: ClashGuard MCP team
