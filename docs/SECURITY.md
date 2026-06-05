# Security Guidance

This document summarizes the security posture for the ClashGuard codebase.

## Secrets and configuration

- Keep all secret keys out of source control.
- Use `clashguard-mcp/.env.example` as the template.
- Do not commit `clashguard-mcp/.env` or any `.env` file containing real keys.
- Use local environment variables for production secrets instead of hard-coded values.

## Endpoint security

- Local development can use `http://localhost` only for demo mode.
- Production ingestion must use HTTPS and a validated API key.
- The backend should reject unauthorized ingestion attempts with `401 Unauthorized`.

## Data minimization

- The Revit add-in must send only minimal payloads: element IDs, categories, types, levels, and bounding boxes.
- Do not send raw geometry, linked document internals, or user-identifying metadata to AI providers.
- AI analysis should be based on anonymized element metadata and severity scores.

## Code hygiene

- Ignore generated files and local artifacts using `.gitignore`.
- Do not commit `venv/`, `__pycache__/`, `bin/`, `obj/`, or local IDE files.
- Keep runtime logs in `logs/` and exclude them from source control.

## Production readiness

- Use signed Revit add-in manifests for marketplace deployment.
- Document all external endpoints in the Autodesk manifest and publisher declaration.
- Validate every inbound request before processing.
- Keep authentication logic separate from business logic.

## Recommended cleanup

- Remove legacy or duplicate content from the active code tree.
- Keep `archive/` for historical copies only.
- Keep the main architecture in `clashguard-mcp/` and `ClashGuardRevit/`.
