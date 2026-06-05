# ClashGuard Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying ClashGuard MCP server to production with HTTPS, API key authentication, and Claude Desktop integration.

## Architecture
```
┌─────────────────────┐
│  Claude Desktop     │
│  (MCP Client)       │
└──────────┬──────────┘
           │ stdio
           ▼
┌─────────────────────────────────┐
│   ClashGuard MCP Server          │
│   (Python + FastAPI)             │
│   - Extract Tool                 │
│   - Analyze Tool                 │
│   - Detect Clashes Tool          │
│   - Suggest Resolutions Tool     │
│   - Generate Report Tool         │
└──────────┬──────────────────────┘
           │ HTTP/HTTPS
    ┌──────┼──────┐
    ▼      ▼      ▼
  ┌───┐ ┌──────┐ ┌────────────┐
  │APS│ │Revit │ │Anthropic   │
  │   │ │Addin │ │Claude API  │
  └───┘ └──────┘ └────────────┘
```

## Prerequisites

- Python 3.12+
- Azure App Service account (or AWS Lambda, Google Cloud Run equivalent)
- SSL certificate for HTTPS (can use Let's Encrypt for free)
- Autodesk APS credentials (Client ID, Client Secret)
- Anthropic Claude API key
- Revit 2024+ with .NET 10.0 runtime
- Visual Studio 2022 (for Revit add-in compilation)

## Phase 1: HTTPS Endpoint Deployment (Azure App Service)

### 1.1 Create Azure App Service
```powershell
# Login to Azure
az login

# Create resource group
az group create --name clashguard-rg --location eastus

# Create App Service Plan (Standard tier or higher for HTTPS)
az appservice plan create --name clashguard-plan --resource-group clashguard-rg --sku S1 --is-linux

# Create Web App
az webapp create --resource-group clashguard-rg --plan clashguard-plan --name clashguard-api --runtime "python|3.12"
```

### 1.2 Configure Application Settings
```powershell
# Set environment variables
az webapp config appsettings set --resource-group clashguard-rg --name clashguard-api --settings `
  INGESTION_MODE="production" `
  INGESTION_API_KEY="<your-secure-api-key>" `
  ANTHROPIC_API_KEY="<your-anthropic-key>" `
  APS_CLIENT_ID="<your-client-id>" `
  APS_CLIENT_SECRET="<your-client-secret>"
```

### 1.3 Deploy MCP Server
```bash
# Clone/copy code to deployment directory
cd clashguard-mcp

# Create requirements.txt with all dependencies
pip freeze > requirements.txt

# Deploy using Git or ZIP
az webapp up --resource-group clashguard-rg --name clashguard-api --runtime "python:3.12"

# Or use ZIP deployment
az webapp deployment source config-zip --resource-group clashguard-rg --name clashguard-api --src dist.zip
```

### 1.4 Enable HTTPS
```powershell
# Azure automatically provides HTTPS on *.azurewebsites.net
# For custom domain:
az webapp config hostname add --resource-group clashguard-rg --webapp-name clashguard-api --hostname api.clashguard.example

# Configure SSL binding (use Azure Key Vault or upload certificate)
az webapp config ssl bind --certificate-name clashguard-cert --ssl-type SNI --resource-group clashguard-rg --name clashguard-api
```

## Phase 2: API Key Generation & Security

### 2.1 Generate Production API Key
```python
import secrets
import hashlib

# Generate 32-character alphanumeric key
api_key = secrets.token_urlsafe(24)
print(f"Production API Key: {api_key}")

# Hash for secure storage
api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
print(f"Hash (for database): {api_key_hash}")
```

### 2.2 Store in Azure Key Vault
```powershell
# Create Key Vault
az keyvault create --resource-group clashguard-rg --name clashguard-vault

# Store API key
az keyvault secret set --vault-name clashguard-vault --name ingestion-api-key --value "<api-key>"

# Grant App Service access
az webapp identity assign --resource-group clashguard-rg --name clashguard-api
az keyvault set-policy --name clashguard-vault --object-id <app-service-object-id> --secret-permissions get list
```

## Phase 3: Revit Add-in Configuration for Production

### 3.1 Build Revit Add-in
```powershell
# Navigate to ClashGuardRevit project
cd ClashGuardRevit

# Build in Release mode
dotnet build --configuration Release

# Output: bin\Release\net10.0\ClashGuardRevit.dll
```

### 3.2 Configure Add-in Settings
Users will see a "ClashGuard - Settings" command in Revit that opens a dialog where they can:

1. Select Mode: **dev** or **production**
2. Enter Dev Endpoint: `http://127.0.0.1:8000/ingest_model` (for local testing)
3. Enter Production Endpoint: `https://api.clashguard.example/ingest_model`
4. Enter API Key (production only): `<your-api-key>`
5. Enable Auto-send on document changes (optional)

Settings are persisted in: `%APPDATA%\ClashGuard\ingestion_settings.json`

### 3.3 Install Add-in
```
1. Copy ClashGuardRevit.dll to Revit add-ins folder:
   C:\ProgramData\Autodesk\Revit\Addins\2024\

2. Copy ClashGuard.addin manifest to same folder

3. Restart Revit

4. ClashGuard commands appear in the Add-ins ribbon:
   - ClashGuard - Run Check (manual clash detection + ingestion)
   - ClashGuard - Settings (configure endpoint and API key)
```

## Phase 4: Claude Desktop Configuration

### 4.1 Configure Claude Desktop Config
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clashguard": {
      "command": "python",
      "args": [
        "D:\\CC_Tech\\MCP hack cctech\\clashguard-mcp\\server.py"
      ],
      "env": {
        "INGESTION_ENABLED": "true",
        "INGESTION_MODE": "production",
        "INGESTION_HOST": "api.clashguard.example",
        "INGESTION_PORT": "443",
        "INGESTION_API_KEY": "your-production-api-key-here",
        "INGESTION_FILE": "D:\\CC_Tech\\MCP hack cctech\\clashguard-mcp\\data\\last_ingest.json"
      }
    }
  }
}
```

### 4.2 Test Connection
```powershell
# Start Claude Desktop
# In Claude, test the connection:
"Get clash detection suggestions for the last ingested model"

# Claude should:
# 1. Call extract_revit_data (reads from INGESTION_FILE)
# 2. Call analyze_model (spatial analysis)
# 3. Call detect_clashes (AABB collision detection)
# 4. Call suggest_resolutions (AI suggestions via Claude API)
# 5. Return comprehensive report
```

## Phase 5: Security Hardening

### 5.1 Implement Rate Limiting
```python
# In server.py, add rate limiting middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@ingestion_app.post("/ingest_model")
@limiter.limit("100/minute")  # 100 requests per minute per IP
def ingest_model(request: Request):
    # Handler implementation
    pass
```

### 5.2 Enable Audit Logging
```python
# Log all ingestion events
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@ingestion_app.post("/ingest_model")
async def ingest_model(payload: dict):
    logger.info(f"Ingestion request at {datetime.now()}")
    logger.info(f"Payload size: {len(json.dumps(payload))} bytes")
    logger.info(f"Client IP: {request.client.host}")
    # Process payload
    logger.info(f"Ingestion completed successfully")
```

### 5.3 Input Validation
```python
# Validate payload schema strictly
from pydantic import BaseModel, validator

class ElementData(BaseModel):
    id: str
    type: str
    bbox: dict  # {min_x, max_x, min_y, max_y, min_z, max_z}
    
    @validator('id')
    def id_must_not_be_empty(cls, v):
        if not v or len(v) > 255:
            raise ValueError('ID must be 1-255 characters')
        return v
```

### 5.4 CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

ingestion_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://api.clashguard.example"],  # Whitelist only trusted origins
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "X-API-KEY"],
)
```

## Phase 6: Monitoring & Maintenance

### 6.1 Application Insights
```powershell
# Enable Azure Application Insights
az monitor app-insights component create --app clashguard-insights --location eastus --resource-group clashguard-rg --application-type web

# Link to App Service
az webapp config appsettings set --resource-group clashguard-rg --name clashguard-api --settings `
  APPLICATIONINSIGHTS_CONNECTION_STRING="<connection-string>"
```

### 6.2 Alerts
```powershell
# Alert on high error rate
az monitor metrics alert create --name clashguard-error-alert --resource-group clashguard-rg `
  --scopes "/subscriptions/{id}/resourceGroups/clashguard-rg/providers/Microsoft.Web/sites/clashguard-api" `
  --condition "avg RequestsFailed > 10" `
  --window-size 5m `
  --evaluation-frequency 1m
```

### 6.3 Backups & Recovery
```powershell
# Enable daily backups
az webapp config backup update --name clashguard-api --resource-group clashguard-rg `
  --container-url "https://storage.azure.com/clashguard-backups" `
  --frequency "1d" `
  --retain-one $true
```

## Phase 7: Autodesk Marketplace Submission

### 7.1 Compliance Checklist
- [x] HTTPS endpoint with valid SSL certificate
- [x] API key authentication in production
- [x] Manifest includes all external endpoints
- [x] Data minimization: no raw geometry sent to AI
- [x] User consent for AI processing
- [x] Audit logging for ingestion events
- [x] Error handling and graceful degradation
- [x] Documentation and support contact

### 7.2 Publisher Declaration
See [AUTODESK_PUBLISHER_DECLARATION.md](./AUTODESK_PUBLISHER_DECLARATION.md) for full compliance statement.

## Troubleshooting

### Issue: API Key validation fails
**Solution**: Ensure `INGESTION_MODE=production` is set in environment. In dev mode, API key is ignored.

### Issue: HTTPS endpoint returns 403 Forbidden
**Solution**: Check API key matches stored key in production environment variables.

### Issue: Revit add-in won't send payloads
**Solution**: Open "ClashGuard - Settings" dialog and verify production endpoint URL and API key are correct.

### Issue: Claude Desktop can't connect to MCP server
**Solution**: 
1. Verify Python path in `claude_desktop_config.json`
2. Check INGESTION_FILE path is accessible
3. Run `python server.py` manually to check for errors

## Support & Contact
- Documentation: https://github.com/cctech/clashguard-mcp
- Issues: https://github.com/cctech/clashguard-mcp/issues
- Email: support@clashguard.example

## Appendix: Environment Variables Reference

| Variable | Mode | Example | Notes |
|----------|------|---------|-------|
| `INGESTION_ENABLED` | Both | `true` | Enable/disable ingestion endpoint |
| `INGESTION_MODE` | Both | `production` | `dev` (no auth) or `production` (API key required) |
| `INGESTION_HOST` | Both | `api.clashguard.example` | Server hostname |
| `INGESTION_PORT` | Both | `443` | 8000 for dev, 443 for production |
| `INGESTION_API_KEY` | Production | `sk-abc...xyz` | Minimum 32 characters |
| `INGESTION_FILE` | Both | `data/last_ingest.json` | Payload storage location |
| `ANTHROPIC_API_KEY` | Both | `sk-ant-...` | Claude API credentials |
| `APS_CLIENT_ID` | Both | `ClientIdXXX` | Autodesk APS credentials |
| `APS_CLIENT_SECRET` | Both | `SecretXXX` | Autodesk APS credentials |
