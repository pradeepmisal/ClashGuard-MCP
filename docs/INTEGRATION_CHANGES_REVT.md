# ClashGuard Revit Add-in — Integration & Change Log

Purpose: track all changes required in the Revit add-in (`ClashGuardRevit`) to push minimal model payloads to the MCP server when a model is opened or when the user clicks the "Add" button.

Status key: TODO / WIP / DONE

## Summary
We will implement a lightweight Revit add-in (C#) that serializes a minimal, sanitized payload and POSTs it to the MCP ingestion endpoint `http://localhost:PORT/ingest_model`. The add-in will run on user action (button click) and optionally on `DocumentOpened` events.

## High-level tasks
- Create an ExternalCommand or PushButton in the add-in UI to trigger payload creation — TODO
- Implement event handlers for `DocumentOpened` and `DocumentChanged` that can optionally auto-push based on user preference — TODO
- Implement JSON serialization of selected elements or whole model into the minimal ingestion schema — TODO
- Implement HTTP POST with retry/backoff to `http://localhost:PORT/ingest_model` for local development and to a configurable HTTPS endpoint for production. Require API key or OAuth authentication in production mode. — TODO
- Add user settings (checkbox) to enable/disable automatic pushes and to select scope (current view / selected elements / whole model). For marketplace submissions, the default should be explicit push only, not automatic background upload. — TODO
- Provide a sample export path fallback `clashguard_payloads.json` on the user's Desktop when the endpoint is unreachable, and document that fallback clearly. — TODO

## File-level plan (ClashGuardRevit)
- `ClashGuardCommand.cs` — add command to UI to "Push to ClashGuard" and call serializer + HTTP post. (TODO)
- `DocumentChangeListener.cs` / `DocumentOpened` handler — call push on open if enabled in settings. (TODO)
- `MepElementCollector.cs` — reuse to gather elements; add a sanitized serializer. (WIP)
- `app.config` / `addin` manifest — add new button id, name, tooltip and security note. (TODO)
- `ClashGuardRevit.csproj` — add `Newtonsoft.Json` and `System.Net.Http` package references if needed. (TODO)

## Minimal push workflow (button click)
1. User opens Revit model or selects elements.
2. User clicks `ClashGuard → Push to MCP` button.
3. Add-in collects minimal properties for the selected scope (AABB, id, type, level, key properties).
4. Add-in POSTs JSON to `http://localhost:PORT/ingest_model` with header `X-API-KEY: <optional>`.
5. On success, add-in shows notification: "Payload delivered to ClashGuard — analysis starting.". On failure, save `clashguard_payloads.json` to Desktop. (TODO)

## Security & Privacy
- Default behavior: do not auto-push; require explicit user action.
- Strip all user-identifying metadata before sending.
- Allow enterprise API key setting for internal deployments. (TODO)

## Autodesk MCP Marketplace Requirements

Considerations derived from the Autodesk MCP Publisher Guide:
- The MCP manifest and publisher declaration must declare all external endpoints, Autodesk APIs used, and AI providers. If the add-in posts to a hosted ingestion endpoint, that endpoint must be listed in the manifest and documented.
- Production ingestion endpoints must use HTTPS. `http://localhost:PORT` may be used only for local development and demos.
- Any data sent to AI providers must be minimized and sent only after explicit user consent. The add-in should never send raw geometry or PII to AI. Only bounding boxes, element metadata, and summary properties should be sent.
- The default production integration should be opt-in and user-initiated. Automatic background pushes should be disabled or clearly marked as experimental.
- A fallback export path (`clashguard_payloads.json`) is required if the production endpoint is unreachable, and the user should be informed.

Conflicts and required changes:
- The add-in currently assumes a local HTTP ingestion endpoint. For Autodesk Marketplace readiness, the architecture must support a secure HTTPS production endpoint and must not rely on local HTTP as the sole integration path.
- The add-in plan must include explicit consent capture before data can be sent to the MCP server if that data may be used for AI analysis.
- The Revit add-in must support a configurable endpoint and credentials, separate from the developer-only local `localhost` endpoint.

Implementation tasks (priority):
1. Add explicit user consent UI in `ClashGuardCommand.cs` for any payload that will be analyzed by AI.
2. Add settings to configure a production HTTPS ingestion endpoint and API key or OAuth token.
3. Keep local `http://localhost:PORT` only for dev/demo mode and document it as such.
4. Ensure HTTP POST uses TLS for production, and fallback to `clashguard_payloads.json` when the endpoint is unreachable.
5. Add privacy/help text with a clear statement of what data is shared and how it is protected.

## Next actions
1. I will implement the MCP HTTP ingestion endpoint in the MCP project (clashguard-mcp). (Offer: I can implement now.)
2. After that, I will provide a complete sample C# code snippet for the `ExternalCommand` that serializes and POSTs the payload. (I will add code and usage instructions.)

---

Last updated: 2026-06-05

Maintainer: ClashGuard Revit add-in team
