# Architecture Overview

This document describes the active repository structure and the responsibility of each folder.

## Active components

### `clashguard-mcp/`

The Python backend and MCP toolset.

- `server.py` — MCP entry point and optional HTTP ingestion server.
- `adapter.py` — payload normalization for Revit ingest data.
- `config.py` — environment-driven configuration and runtime flags.
- `tools/` — five tool implementations for extraction, analysis, clash detection, report generation, and AI suggestions.
- `aps/` — optional Autodesk Platform Services helper code and API wrappers.
- `tests/` — automated test suite that validates ingestion, extraction, analysis, and detection.
- `requirements.txt` — Python dependencies.
- `.env.example` — secret template. Use `.env` locally only.

### `ClashGuardRevit/`

The Revit add-in codebase.

- `ClashGuardCommand.cs` — main external command that sends data to the MCP backend and visualizes results.
- `ClashGuardApp.cs` — add-in application lifecycle and event handler registration.
- `Services/` — HTTP API client, clash visualization, and other shared services.
- `Collectors/` — Revit element collection logic.
- `EventHandlers/` — document change / open event handlers.
- `Models/` — C# data contracts for clash results, payloads, and settings.
- `Settings/` — persisted add-in configuration.
- `UI/` — settings dialog and user-facing UI components.

### `docs/`

Documentation and compliance artifacts.

- `ARCHITECTURE.md` — this architecture map.
- `DOCUMENTATION_INDEX.md` — central index of all docs.
- `SECURITY.md` — security and production-readiness guidance.
- `PROJECT_PLAN.md` — product requirements and execution plan.
- Additional marketplace and deployment documentation.

### `logs/`

Runtime diagnostics, separated from source.

### `archive/`

Legacy or duplicate code copies that are not part of the active architecture.

## Production-grade design goals

- separate add-in and backend responsibilities clearly
- centralize documentation outside application source trees
- isolate local secrets and runtime logs from tracked code
- archive duplicates instead of mixing them into active folders
- enforce clean source control with `.gitignore`

## How to use this architecture

1. Use `clashguard-mcp/` for backend development and Python tool validation.
2. Use `ClashGuardRevit/` for Revit add-in development and package builds.
3. Use `docs/` for onboarding, compliance, production deployment, and security review.
4. Keep `archive/` for reference only; do not restore it into the active build process.
