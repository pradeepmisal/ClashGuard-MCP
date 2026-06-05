# Autodesk MCP Publisher Declaration Draft

## External Connections and APIs
- Autodesk APS Model Derivatives API: `https://developer.api.autodesk.com`
- Autodesk Authentication API: `https://developer.api.autodesk.com`
- Anthropic Claude AI: `https://api.anthropic.com`

## MCP Runtime and Transport
- MCP transport: `stdio`
- Local development ingestion endpoint: `http://127.0.0.1:8000/ingest_model`
- Production ingestion endpoint: must be deployed behind HTTPS and authenticated using `X-API-KEY` or equivalent.

## Data Handling
- The MCP only ingests and analyzes Revit data that has been exported or ingested through the Revit add-in.
- Payloads are limited to element IDs, types, level/location, zones, and bounding boxes.
- No raw mesh geometry, no user credentials, and no personally identifiable information is sent to external services.

## AI Usage
- `suggest_resolutions` may send anonymized clash summaries to Anthropic Claude AI when explicit user consent is granted.
- Model referenced: `claude-sonnet-4-6`.
- Data sent to AI is limited to clash metadata and does not include full model geometry.

## Security Controls
- Ingestion endpoint is optional and disabled by configuration (`INGESTION_ENABLED=false`).
- Production ingestion requires `INGESTION_API_KEY`.
- All external API requests use HTTPS with request verification enabled.

## Compliance Notes
- The MCP manifest includes external services and AI provider declarations.
- Localhost ingestion is used only for development and testing; production deployments must use HTTPS.
- Report generation is local and does not transmit user data externally.
