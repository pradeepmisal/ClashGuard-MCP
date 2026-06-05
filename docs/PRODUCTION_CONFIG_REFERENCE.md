# ClashGuard Production Configuration Reference

## File: `claude_desktop_config.json`
**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

This is the main configuration file for Claude Desktop MCP integration. Copy and update with your production values:

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

## Configuration Parameters

### Core Settings
- **INGESTION_ENABLED**: Enable/disable the ingestion endpoint (true/false)
- **INGESTION_MODE**: 
  - `dev`: Local development, no authentication required
  - `production`: HTTPS with API key authentication
- **INGESTION_HOST**: Hostname or IP of the ingestion server
- **INGESTION_PORT**: Port number (8000 for dev, 443 for production HTTPS)
- **INGESTION_API_KEY**: API key for production authentication (min 32 chars)
- **INGESTION_FILE**: Path to store the last ingested model payload (JSON)

### Optional Settings
- **ANTHROPIC_API_KEY**: Anthropic API key for Claude AI services
- **APS_CLIENT_ID**: Autodesk APS Client ID for OAuth
- **APS_CLIENT_SECRET**: Autodesk APS Client Secret for OAuth
- **CLAUDE_MODEL**: Claude model version (default: claude-sonnet-4-6)

## Revit Add-in Configuration

### User Settings Dialog
Users access "ClashGuard - Settings" command in Revit ribbon:

1. **Mode Selection**: Choose between dev and production
2. **Dev Endpoint**: For local MCP server (default: http://127.0.0.1:8000/ingest_model)
3. **Production Endpoint**: For cloud-hosted MCP server (e.g., https://api.clashguard.example/ingest_model)
4. **API Key**: Required for production mode
5. **Auto-send**: Optional auto-ingestion on document changes

Settings are persisted in:
```
%APPDATA%\ClashGuard\ingestion_settings.json
```

Example settings file:
```json
{
  "mode": "production",
  "dev_endpoint": "http://127.0.0.1:8000/ingest_model",
  "production_endpoint": "https://api.clashguard.example/ingest_model",
  "api_key": "your-api-key-here",
  "auto_send": false
}
```

## Deployment Checklist

### Pre-Deployment
- [ ] Generate secure API key (minimum 32 chars, mix alphanumeric + symbols)
- [ ] Obtain/generate HTTPS SSL certificate
- [ ] Set up cloud hosting (Azure, AWS, Google Cloud)
- [ ] Configure custom domain (api.clashguard.example)
- [ ] Store secrets in vault (Azure Key Vault, AWS Secrets Manager)
- [ ] Test ingestion endpoint locally first

### Deployment
- [ ] Deploy MCP server to production endpoint
- [ ] Enable HTTPS and verify SSL certificate
- [ ] Configure environment variables on server
- [ ] Test API authentication with real API key
- [ ] Enable audit logging and monitoring
- [ ] Set up health check endpoint

### Post-Deployment
- [ ] Verify endpoint responds to health checks
- [ ] Test from Revit add-in with production settings
- [ ] Test from Claude Desktop with production config
- [ ] Monitor error rates and performance
- [ ] Set up alerts for failures
- [ ] Document known issues and workarounds

## Security Best Practices

1. **API Key Rotation**: Rotate keys every 90 days
2. **Environment Separation**: Keep dev and production keys separate
3. **Never Commit Secrets**: Use `.gitignore` to exclude `.env` files
4. **Use Vaults**: Store secrets in Azure Key Vault or equivalent
5. **HTTPS Only**: Always use HTTPS for production endpoints
6. **Rate Limiting**: Implement request rate limits (e.g., 100/min per IP)
7. **Audit Logging**: Log all ingestion events with timestamps and client IPs
8. **Input Validation**: Validate and sanitize all incoming payloads
9. **CORS**: Whitelist only trusted origins
10. **Monitoring**: Set up alerts for anomalies and failures

## Scaling Considerations

### Horizontal Scaling (Multiple Instances)
```yaml
# Docker Compose or Kubernetes example
ingestion-endpoint:
  image: clashguard-mcp:latest
  replicas: 3
  environment:
    INGESTION_MODE: production
    INGESTION_API_KEY: ${PROD_API_KEY}
  ports:
    - "8000:8000"
  resources:
    limits:
      memory: 1G
      cpu: 500m
```

### Load Balancing
- Use NGINX or AWS ALB in front of multiple MCP instances
- Enable sticky sessions for WebSocket connections (if used)
- Monitor backend health and auto-remove unhealthy instances

### Database Considerations
- Store ingested payloads in database (not just JSON files)
- Implement retention policies for old payloads
- Set up replication for high availability

## Monitoring & Observability

### Metrics to Monitor
- Request count and latency
- Error rate (4xx, 5xx responses)
- API key usage patterns
- Payload sizes and processing times
- Database query performance

### Logging
- Timestamp: ISO 8601 format
- Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Message: Clear description of event
- Context: Request ID, user ID, client IP, API key hash
- Example:
  ```
  [2026-06-05T14:30:45Z] INFO - POST /ingest_model from 203.0.113.42 | 
  Elements: 347 | Size: 2.4MB | Processing: 250ms | Status: 200 OK
  ```

### Alerting
- High error rate (>5% of requests)
- Authentication failures (>10 failed attempts per IP)
- Payload processing timeouts
- Database connectivity issues
- Certificate expiration warnings (30 days before)

## Recovery Procedures

### Backup & Restore
1. Daily automated backups to cloud storage
2. Test restore procedures monthly
3. Keep 30-day retention policy
4. Document recovery time objectives (RTO) and recovery point objectives (RPO)

### Incident Response
1. Monitor alerts continuously
2. Implement circuit breaker pattern
3. Have runbook for common issues
4. Document all incidents and resolutions
5. Conduct post-mortems for critical incidents

## Compliance & Audit

### Data Minimization
- Only send necessary clash data to Claude AI
- Never send raw geometry or coordinates
- Anonymize element IDs where possible
- Implement data retention policies

### User Consent
- Explicit opt-in for AI processing
- Clear privacy policy
- Option to opt-out at any time
- Transparency in data handling

### Audit Trail
- Log all API requests with authentication status
- Track configuration changes
- Monitor data access and modifications
- Maintain immutable audit logs (minimum 1 year)

## Support & Troubleshooting

### Common Issues

**Problem**: API returns 401 Unauthorized
```
Solution: 
1. Verify X-API-KEY header is present
2. Ensure INGESTION_MODE=production in environment
3. Check API key matches stored value
4. Verify API key hasn't expired
```

**Problem**: Connection timeout
```
Solution:
1. Check server is running: curl -I https://api.clashguard.example:443/
2. Verify firewall allows HTTPS
3. Check DNS resolution: nslookup api.clashguard.example
4. Review server logs for errors
```

**Problem**: Certificate validation fails
```
Solution:
1. Verify certificate is valid: openssl s_client -connect api.clashguard.example:443
2. Check certificate chain completeness
3. Ensure system date/time is correct
4. Add CA certificate to trusted store if using self-signed
```

**Problem**: High latency/slow responses
```
Solution:
1. Check server CPU and memory usage
2. Monitor database query performance
3. Enable compression for large payloads
4. Review logging verbosity (reduce if excessive)
5. Scale horizontally if needed
```

## Version Management

- **MCP Version**: 1.0
- **API Version**: 1.0
- **Min Python**: 3.12
- **Min Revit**: 2024
- **Min .NET**: 10.0
- **Min Claude**: Claude 3.5 Sonnet

## Change Log

### v1.0 - Production Release
- ✓ HTTPS endpoint with API key auth
- ✓ Revit add-in with configurable settings
- ✓ Auto-send on document changes (optional)
- ✓ Production deployment guide
- ✓ Security hardening and best practices
- ✓ Comprehensive monitoring and logging
- ✓ Autodesk Marketplace compliance

---

**Last Updated**: 2026-06-05
**Maintainer**: ClashGuard Development Team
**Documentation**: https://github.com/cctech/clashguard-mcp/wiki
