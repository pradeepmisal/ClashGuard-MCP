# Autodesk MCP Marketplace Compliance Checklist

This checklist maps the ClashGuard MCP implementation to the Autodesk MCP Publisher Guide requirements and lists action items to achieve compliance.

## Manifest & Declarations
- [ ] `manifest.json` includes:
  - `mcp_manifest_version`, `app_model`, `mcp_spec_version`
  - `server.transport` set correctly (e.g., `stdio`)
  - `tools`: all tool names and plain-language descriptions (no instructions)
  - `external_endpoints`: list dev and prod endpoints (dev: http://localhost:PORT, prod: https://api.clashguard.example/ingest_model)
  - `autodesk_apis_used`: list APS Revit/Data Management/Model Derivatives where applicable
  - `ai_llm_providers`: list Anthropic/Gemini and short description of data sent

## Security & Data Access
- [ ] All production external endpoints must use HTTPS (TLS). No `verify=False`.
- [ ] Minimal data only: bounding boxes, element types, level/zone, and selected properties. No raw meshes, no PII.
- [ ] User consent required and recorded before sending data to AI providers (`user_consent_given=true`).
- [ ] Ingestion endpoint requires authentication in production (API key or OAuth). Localhost accepted for dev only.
- [ ] Local developer workflow uses `http://127.0.0.1:8000/ingest_model` and is marked as disabled in production if `INGESTION_ENABLED=false`.
- [ ] Log redaction: do not log tokens, secrets, or PII.

## Tool Descriptions
- [ ] Ensure tool descriptions are factual, plain-language, and do not contain procedural instructions or references to sensitive data.

## External Connections
- [ ] Declare all external domains in manifest and declaration form.
- [ ] Use HTTPS for all outbound calls. Document retry/backoff and failure modes.

## Publisher Declaration Form
- [ ] Complete the Publisher Declaration Form with security attestations and list of external endpoints and AI providers.

## Testing & Validation
- [ ] Run static code analysis and dependency vulnerability scans.
- [ ] Perform a privacy review to ensure no PII is sent.
- [ ] Run integration tests with a production HTTPS endpoint (staging) before submission.

## Packaging & Submission
- [ ] Prepare source code package and README for submission.
- [ ] Include `manifest.json`, `AUTODESK_COMPLIANCE.md`, and Publisher Declaration draft with submission.

## Notes and Rationale
- Local dev workflow using `http://localhost` is permitted for development and demo, but the marketplace submission must reference a production HTTPS endpoint. We will support both modes and clearly document the difference.

---

Last updated: 2026-06-05

Maintainer: ClashGuard MCP team
